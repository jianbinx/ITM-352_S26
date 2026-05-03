import time
import requests
import json
import os
import ccxt
from datetime import datetime, timezone
from __init__ import app, db
from models import Crypto, PortfolioItem
from security import decrypt_data


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

def execute_auto_trade(user, crypto_symbol, amount, trade_type="SELL"):
    """
    Executes an automated trade using the user's encrypted API secret.
    """
    if not user.encrypted_api_secret:
        return False, "No API key configured."
        
    try:
        # Decrypt the military-grade encrypted API key
        api_secret = decrypt_data(user.encrypted_api_secret)
        
        if not api_secret:
            return False, "Failed to decrypt API key."
            
        # Initialize the Binance exchange connection using ccxt
        # Note: Exchanges require both an API Key and Secret. 
        exchange = ccxt.binance({
            'apiKey': user.api_key,                 # Pulled dynamically from the database
            'secret': api_secret,                   # Our decrypted military-grade secret
            'enableRateLimit': True,
        })
        
        # Enable Binance Testnet (Sandbox Mode)
        exchange.set_sandbox_mode(True)
        
        # Binance typically trades crypto against USDT (Tether) for USD equivalents
        market_symbol = f"{crypto_symbol.upper()}/USDT"
        
        if trade_type.upper() == "SELL":
            order = exchange.create_market_sell_order(market_symbol, amount)
        elif trade_type.upper() == "BUY":
            order = exchange.create_market_buy_order(market_symbol, amount)
        else:
            return False, f"Unsupported trade type: {trade_type}"
            
        return True, f"Successfully executed {trade_type} order for {amount} {crypto_symbol.upper()} on Binance. Order ID: {order['id']}"
        
    except Exception as e:
        return False, f"Trade execution failed: {str(e)}"

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
                    
                    db.session.commit()
                
                # Check for smart alerts
                items = PortfolioItem.query.all()
                alerts_triggered = False
                for item in items:
                    if item.target_price and item.crypto.price:
                        if item.crypto.price >= item.target_price:
                            alert_msg = f"🎯 TARGET HIT: {item.crypto.name} reached your target of ${item.target_price}! Current price: ${item.crypto.price}"
                            
                            # Trigger Auto-Trading if user has configured an API Key and actually owns some
                            if item.amount_owned > 0 and item.user.encrypted_api_secret:
                                success, trade_msg = execute_auto_trade(item.user, item.crypto.symbol, item.amount_owned, "SELL")
                                alert_msg += f" | 🤖 AUTO-TRADE: {trade_msg}"
                                if success:
                                    item.amount_owned = 0.0  # Reset amount since it was sold
                                    
                            log_alert(item.user_id, alert_msg)
                            item.target_price = None  # Clear the target so it doesn't spam
                            alerts_triggered = True
                
                if alerts_triggered:
                    db.session.commit()

                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Successfully synced {len(data)} cryptocurrency prices.")
                
            except Exception as e:
                print(f"Error occurred during sync: {e}")
            
            time.sleep(30)  # Wait for 30 seconds before syncing again

if __name__ == '__main__':
    sync_crypto_prices()