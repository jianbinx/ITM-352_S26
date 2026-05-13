import time
import requests
import json
import os
import ccxt
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone
from __init__ import app, db
from models import Crypto, PortfolioItem, WatchlistItem, User, PredictionVote, PortfolioHistory, TradeHistory
from security import decrypt_data
from config import Config

def send_email_alert(to_email, subject, body):
    """Sends an email notification via SMTP."""
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        print("Email not sent: MAIL_USERNAME or MAIL_PASSWORD not configured.")
        return False, "MAIL_USERNAME or MAIL_PASSWORD is not configured in your .env file."
        
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = Config.MAIL_USERNAME
    msg['To'] = to_email
    
    try:
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        if Config.MAIL_USE_TLS:
            server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully."
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False, f"SMTP Error: {str(e)}"


def log_alert(user_id, message):
    """Writes an alert to the user's specific JSON log file."""
    alerts_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'alerts_{user_id}.json')
    alerts = []
    if os.path.exists(alerts_file):
        with open(alerts_file, 'r') as f:
            try:
                alerts = json.load(f)
            except json.JSONDecodeError:
                pass
    
    alerts.insert(0, {
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        "user_id": user_id,
        "message": message
    })
    
    alerts = alerts[:100]  # Keep only the latest 100 alerts per user
    
    with open(alerts_file, 'w') as f:
        json.dump(alerts, f, indent=4)
        
    # Send an email alert if the user has an email configured
    with app.app_context():
        user = User.query.get(user_id)
        if user and user.email:
            send_email_alert(user.email, "Crypto Dashboard Alert", message)

def execute_auto_trade(user, crypto_symbol, amount, trade_type="SELL"):
    """
    Executes an automated trade using the user's encrypted API secret.
    """
    if not user.encrypted_api_secret:
        return False, "No API key configured."
        
    try:
        # Decrypt the military-grade encrypted API credentials
        api_key = decrypt_data(user.encrypted_api_key)
        api_secret = decrypt_data(user.encrypted_api_secret)
        
        if not api_key or not api_secret:
            return False, "Failed to decrypt API credentials."
            
        # Initialize the Binance US exchange connection using ccxt
        # Note: Exchanges require both an API Key and Secret. 
        exchange = ccxt.binanceus({
            'apiKey': api_key,                      # Decrypted API key
            'secret': api_secret,                   # Our decrypted military-grade secret
            'enableRateLimit': True,
        })
        
        # NOTE: Binance US does not have a Sandbox mode. The global testnet blocks US IPs.
        # This is now connecting to the LIVE exchange.
        
        # Load available markets to ensure the coin is supported by Binance US
        try:
            exchange.load_markets()
        except Exception as e:
            return False, f"Failed to load exchange markets: {e}"
            
        market_symbol_usd = f"{crypto_symbol.upper()}/USD"
        market_symbol_usdt = f"{crypto_symbol.upper()}/USDT"
        
        if market_symbol_usd in exchange.symbols:
            market_symbol = market_symbol_usd
        elif market_symbol_usdt in exchange.symbols:
            market_symbol = market_symbol_usdt
        else:
            return False, f"Trade failed: The coin {crypto_symbol.upper()} is not supported by Binance US."
            
        if trade_type.upper() == "SELL":
            order = exchange.create_market_sell_order(market_symbol, amount)
        elif trade_type.upper() == "BUY":
            order = exchange.create_market_buy_order(market_symbol, amount)
        else:
            return False, f"Unsupported trade type: {trade_type}"
            
        return True, f"Successfully executed {trade_type} order for {amount} {crypto_symbol.upper()} on Binance US. Order ID: {order['id']}"
        
    except Exception as e:
        error_msg = str(e)
        if "MIN_NOTIONAL" in error_msg:
            return False, "Trade failed: The total dollar value is below the Binance US minimum (usually $10)."
        elif "insufficient" in error_msg.lower() or "-2010" in error_msg:
            return False, "Trade execution failed: You have insufficient funds."
        elif "market_lot_size" in error_msg.lower() or "-1013" in error_msg:
            return False, "Trade failed: You do not have this coin."
        elif "does not have market symbol" in error_msg.lower() or "not supported by binance" in error_msg.lower():
            return False, "Trade failed: The coin is not supported by Binance US."
        return False, f"Trade execution failed: {error_msg}"

# THE BACKGROUND WORKER
def sync_crypto_prices():
    """
    Fetches the latest prices for tracked cryptocurrencies from the CoinGecko API
    and updates the database.
    """
    print("Starting background sync worker...")
    
    # Provide the application context since we are interacting with the database outside of a web request
    with app.app_context():
        while True:
            try:
                # Get all cryptocurrencies currently in our database
                cryptos = Crypto.query.all()
                
                if cryptos:
                    # Auto-heal legacy misnamed coins in the background
                    for c in cryptos:
                        if c.symbol == 'DOGE' and c.name != 'dogecoin':
                            c.name = 'dogecoin'
                            db.session.commit()
                            
                    # Create a mapping from lowercase name to our Crypto objects
                    # Note: CoinGecko API expects lowercase names (e.g., 'bitcoin', 'ethereum')
                    crypto_map = {c.name.lower(): c for c in cryptos}
                    crypto_ids = ",".join(crypto_map.keys())
                    
                    # Fetch live prices from CoinGecko
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_ids}&vs_currencies=usd&include_market_cap=true&include_24hr_change=true"
                    response = requests.get(url, timeout=10)
                    data = response.json()
                    
                    # Update prices in the database
                    for coin_id, price_info in data.items():
                        if coin_id in crypto_map and 'usd' in price_info:
                            crypto_map[coin_id].price = price_info['usd']
                            crypto_map[coin_id].market_cap = price_info.get('usd_market_cap')
                            crypto_map[coin_id].change_24h = price_info.get('usd_24h_change')
                            crypto_map[coin_id].last_updated = datetime.now(timezone.utc)
                    
                    # Force fiat USD to always remain at $1
                    if 'usd' in crypto_map:
                        crypto_map['usd'].price = 1.0
                        crypto_map['usd'].change_24h = 0.0
                        crypto_map['usd'].last_updated = datetime.now(timezone.utc)
                    
                    db.session.commit()
                    
                    # Take Portfolio Snapshots for analytics
                    users = User.query.all()
                    for u in users:
                        pf_items = PortfolioItem.query.filter_by(user_id=u.id).all()
                        if not pf_items: continue
                        
                        total_val = sum(((1.0 if p.crypto.symbol.upper() == 'USD' else (p.crypto.price or 0)) * p.amount_owned) for p in pf_items)
                        if total_val > 0:
                            last_snap = PortfolioHistory.query.filter_by(user_id=u.id).order_by(PortfolioHistory.timestamp.desc()).first()
                            # Snapshot if no previous snapshot or > 1 hour has passed
                            if not last_snap or (datetime.now(timezone.utc) - last_snap.timestamp.replace(tzinfo=timezone.utc)).total_seconds() > 60:
                                db.session.add(PortfolioHistory(user_id=u.id, total_value=total_val))
                                
                    db.session.commit()
                
                # Check for smart alerts
                items = PortfolioItem.query.all()
                watchlist_items = WatchlistItem.query.all()
                alerts_triggered = False
                for item in items:
                    if item.target_price and item.crypto.price:
                        if item.crypto.price >= item.target_price:
                            alert_msg = f"🎯 TARGET HIT: {item.crypto.name} reached your target of ${item.target_price}! Current price: ${item.crypto.price}"
                            
                            is_unsupported = False
                            # Trigger Auto-Trading if user has configured an API Key and actually owns some
                            if item.auto_trade_enabled and item.amount_owned > 0 and item.user.encrypted_api_secret:
                                # Safely default to selling all if no specific amount was configured prior to this update
                                sell_amt = item.trade_amount if (item.trade_amount and item.trade_amount > 0) else item.amount_owned
                                if item.amount_owned >= sell_amt:
                                    success, trade_msg = execute_auto_trade(item.user, item.crypto.symbol, sell_amt, "SELL")
                                    alert_msg += f" | 🤖 AUTO-TRADE: {trade_msg}"
                                    if success:
                                        db.session.add(TradeHistory(user_id=item.user_id, crypto_symbol=item.crypto.symbol, trade_type='SELL', amount=sell_amt, price_usd=item.crypto.price))
                                        item.amount_owned -= sell_amt  # Subtract sold amount
                                        item.auto_trade_enabled = False # Turn off auto-trade after execution
                                    else:
                                        if "not supported by binance" in trade_msg.lower():
                                            is_unsupported = True
                                        else:
                                            item.auto_trade_enabled = False
                                else:
                                    alert_msg += f" | 🤖 AUTO-TRADE FAILED: Insufficient portfolio holding to sell {sell_amt} coins."
                                    item.auto_trade_enabled = False
                                    
                            log_alert(item.user_id, alert_msg)
                            
                            if is_unsupported:
                                crypto_id_to_remove = item.crypto_id
                                crypto_sym_to_remove = item.crypto.symbol
                                PortfolioItem.query.filter_by(crypto_id=crypto_id_to_remove).delete()
                                WatchlistItem.query.filter_by(crypto_id=crypto_id_to_remove).delete()
                                PredictionVote.query.filter_by(coin_symbol=crypto_sym_to_remove).delete()
                                Crypto.query.filter_by(id=crypto_id_to_remove).delete()
                                alerts_triggered = True
                                continue
                                
                            item.target_price = None  # Clear the target so it doesn't spam
                            alerts_triggered = True
                            
                for item in watchlist_items:
                    if item.target_price and item.crypto.price:
                        # Auto-Buy ("Buy the dip") triggers if price drops to or below target
                        if item.auto_trade_enabled and item.crypto.price <= item.target_price:
                            alert_msg = f"🎯 WATCHLIST AUTO-BUY TRIGGERED: {item.crypto.name} dropped to ${item.crypto.price} (Target: ${item.target_price})"
                            
                            is_unsupported = False
                            if item.trade_amount > 0 and item.user.encrypted_api_secret:
                                success, trade_msg = execute_auto_trade(item.user, item.crypto.symbol, item.trade_amount, "BUY")
                                alert_msg += f" | 🤖 {trade_msg}"
                                if success:
                                    db.session.add(TradeHistory(user_id=item.user_id, crypto_symbol=item.crypto.symbol, trade_type='BUY', amount=item.trade_amount, price_usd=item.crypto.price))
                                    # Add to portfolio automatically!
                                    pf_item = PortfolioItem.query.filter_by(user_id=item.user_id, crypto_id=item.crypto_id).first()
                                    if pf_item:
                                        pf_item.amount_owned += item.trade_amount
                                    else:
                                        db.session.add(PortfolioItem(user_id=item.user_id, crypto_id=item.crypto_id, amount_owned=item.trade_amount))
                                else:
                                    if "not supported by binance" in trade_msg.lower():
                                        is_unsupported = True
                            
                            log_alert(item.user_id, alert_msg)
                            
                            if is_unsupported:
                                crypto_id_to_remove = item.crypto_id
                                crypto_sym_to_remove = item.crypto.symbol
                                PortfolioItem.query.filter_by(crypto_id=crypto_id_to_remove).delete()
                                WatchlistItem.query.filter_by(crypto_id=crypto_id_to_remove).delete()
                                PredictionVote.query.filter_by(coin_symbol=crypto_sym_to_remove).delete()
                                Crypto.query.filter_by(id=crypto_id_to_remove).delete()
                                alerts_triggered = True
                                continue
                                
                            item.target_price = None
                            item.auto_trade_enabled = False
                            alerts_triggered = True
                            
                        # Regular Watchlist alert triggers if price goes ABOVE target (breakout)
                        elif not item.auto_trade_enabled and item.crypto.price >= item.target_price:
                            alert_msg = f"🎯 WATCHLIST TARGET HIT: {item.crypto.name} reached your target of ${item.target_price}! Current price: ${item.crypto.price}"
                            
                            log_alert(item.user_id, alert_msg)
                            item.target_price = None
                            alerts_triggered = True
                
                if alerts_triggered:
                    db.session.commit()

                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Successfully synced {len(data)} cryptocurrency prices.")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error occurred during sync: {e}")
            
            time.sleep(10)  # Wait for 10 seconds before syncing again

if __name__ == '__main__':
    sync_crypto_prices()