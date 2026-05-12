from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json
import requests
from datetime import datetime, timezone
import os
from __init__ import app, db
from models import Crypto, Poll, Settings, User, PortfolioItem, WatchlistItem, PredictionVote, PollVote, PortfolioHistory, TradeHistory
from security import encrypt_data, decrypt_data
import ccxt
import hashlib

# --- HELPERS ---

BINANCE_US_SUPPORTED_SYMBOLS = set()
def get_binance_us_symbols():
    """Fetches and caches supported base symbols from Binance US to filter searches."""
    global BINANCE_US_SUPPORTED_SYMBOLS
    if not BINANCE_US_SUPPORTED_SYMBOLS:
        try:
            exchange = ccxt.binanceus()
            exchange.load_markets()
            for market in exchange.symbols:
                base = market.split('/')[0]
                BINANCE_US_SUPPORTED_SYMBOLS.add(base.upper())
            BINANCE_US_SUPPORTED_SYMBOLS.add('USD')
        except Exception as e:
            print(f"Failed to load Binance US markets for filtering: {e}")
    return BINANCE_US_SUPPORTED_SYMBOLS

def get_trending_coins(limit=3):
    """Returns a list of top trending coins from CoinGecko for the dashboard."""
    trending = []
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        response = requests.get(url, timeout=5)
        data = response.json()
        for item in data.get('coins', [])[:limit]:
            coin = item.get('item', {})
            trending.append({
                'name': coin.get('name'),
                'symbol': coin.get('symbol').upper(),
                'thumb': coin.get('thumb'),
                'market_cap_rank': coin.get('market_cap_rank')
            })
    except Exception as e:
        print(f"Trending Fetch Error: {e}")
    return trending

def get_currency_data(currency_code):
    """Returns the symbol and the conversion rate relative to 1 USD"""
    rates = {
        'USD': {'symbol': '$', 'rate': 1.0},
        'EUR': {'symbol': '€', 'rate': 0.85},
        'GBP': {'symbol': '£', 'rate': 0.74}
    }
    return rates.get(currency_code, {'symbol': '$', 'rate': 1.0})

# --- PAGE ROUTES ---

@app.route('/', endpoint='portfolio_index')
def portfolio_index_view(): # Renamed function to be unique
    config = Settings.query.first()
    if not config:
        config = Settings()
        db.session.add(config)
        db.session.commit()

    curr_data = get_currency_data(config.currency)
    currency_symbol = curr_data['symbol']
    rate = curr_data['rate']
    trending_coins_data = get_trending_coins()

    if 'user_id' not in session:
        return render_template('index.html', 
                               current_user=None,
                               portfolio_items=[], 
                               watchlist_items=[],
                               alerts=[], 
                               trending_coins=trending_coins_data,
                               settings=config, 
                               currency_symbol=currency_symbol,
                               conversion_rate=rate)

    user_id = session['user_id']
    current_user = User.query.get(user_id)
    portfolio_items = PortfolioItem.query.filter_by(user_id=user_id).all()
    watchlist_items = WatchlistItem.query.filter_by(user_id=user_id).all()
    
    alerts = []
    alerts_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'alerts_{user_id}.json')
    if os.path.exists(alerts_file):
        with open(alerts_file, 'r') as f:
            try:
                alerts = json.load(f)
            except json.JSONDecodeError:
                pass

    return render_template('index.html', 
                           current_user=current_user,
                           portfolio_items=portfolio_items, 
                           watchlist_items=watchlist_items,
                           alerts=alerts, 
                           trending_coins=trending_coins_data,
                           settings=config, 
                           currency_symbol=currency_symbol,
                           conversion_rate=rate)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('portfolio_index'))

# --- PREDICTION MARKETS & POLLS ---

@app.route('/api/polymarket_polls')
def get_manifold_polls_sidebar():
    """Fetches a limited set (10) for the sidebar dashboard"""
    try:
        # Increased limit to ensure we have enough polls after filtering out political ones
        url = "https://api.manifold.markets/v0/search-markets?term=Crypto&limit=30&sort=score&filter=open"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        polls = []
        political_keywords = ['trump', 'biden', 'election', 'harris', 'democrat', 'republican', 'politics', 'president', 'senate', 'house', 'congress', 'voter', 'kamala', 'gop']
        
        for market in data:
            if market.get('outcomeType') != 'BINARY': continue
            prob = market.get('probability')
            if prob is None: continue

            # Filter out questions containing political keywords
            question_lower = market.get('question', '').lower()
            if any(keyword in question_lower for keyword in political_keywords):
                continue

            polls.append({
                'question': market.get('question'),
                'yes_price': float(prob),
                'no_price': 1.0 - float(prob),
                'id': market.get('slug'),
                'url': market.get('url'),
                'volume': f"${int(market.get('volume', 0)):,}"
            })
            
            # Stop once we have 10 clean, non-political crypto polls
            if len(polls) >= 10:
                break
                
        return jsonify(polls)
    except Exception as e:
        print(f"Sidebar Fetch Error: {e}")
        return jsonify([])

@app.route('/api/all_manifold_polls')
def get_all_manifold_polls():
    """Fetches a large list of crypto markets for the dedicated 'All Polls' page"""
    try:
        # Increase limit to fetch a large pool to filter from
        url = "https://api.manifold.markets/v0/search-markets?term=Crypto&limit=200&sort=score&filter=open"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        polls = []
        political_keywords = ['trump', 'biden', 'election', 'harris', 'democrat', 'republican', 'politics', 'president', 'senate', 'house', 'congress', 'voter', 'kamala', 'gop']
        
        for market in data:
            if market.get('outcomeType') != 'BINARY': continue
            prob = market.get('probability')
            if prob is None: continue

            # Filter out questions containing political keywords
            question_lower = market.get('question', '').lower()
            if any(keyword in question_lower for keyword in political_keywords):
                continue

            polls.append({
                'question': market.get('question'),
                'yes_price': float(prob),
                'no_price': 1.0 - float(prob),
                'id': market.get('slug'),
                'url': market.get('url'),
                'volume': f"${int(market.get('volume', 0)):,}"
            })
            
            # Stop once we have up to 100 clean polls for the grid
            if len(polls) >= 100:
                break
                
        return jsonify(polls)
    except Exception as e:
        print(f"All Polls Fetch Error: {e}")
        return jsonify([])

@app.route('/all_polls')
def all_polls():
    config = Settings.query.first()
    return render_template('all_polls.html', settings=config)

# --- TRENDING COINS ---

@app.route('/trending_coins')
def trending_coins():
    config = Settings.query.first()
    trending_coins = []
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        response = requests.get(url, timeout=10)
        data = response.json()
        for item in data.get('coins', []):
            coin = item.get('item', {})
            trending_coins.append({
                'id': coin.get('id'),
                'name': coin.get('name'),
                'symbol': coin.get('symbol'),
                'thumb': coin.get('thumb'),
                'market_cap_rank': coin.get('market_cap_rank')
            })
    except Exception as e:
        print(f"Trending Fetch Error: {e}")
        
    return render_template('trending_coins.html', trending_coins=trending_coins, settings=config)

# --- PORTFOLIO MANAGEMENT ---

@app.route('/add_portfolio_item', methods=['POST'])
def add_portfolio_item():
    if 'user_id' not in session:
        flash('Please log in to add items to your portfolio.', 'error')
        return redirect(url_for('login'))

    coin_id = request.form.get('coin_id', '').strip().lower()
    amount_str = request.form.get('amount', '0')
    target_str = request.form.get('target_price', '').strip()
    trade_amount_str = request.form.get('trade_amount', '0')
    auto_trade_enabled = True if request.form.get('auto_trade') == 'on' else False

    try: trade_amount = float(trade_amount_str)
    except ValueError: trade_amount = 0.0

    target_price = None
    if target_str:
        try: target_price = float(target_str)
        except ValueError: pass

    try: amount = float(amount_str)
    except ValueError:
        flash('Invalid amount entered.', 'error')
        return redirect(url_for('portfolio_index'))

    if not coin_id:
        flash('Coin ID cannot be empty.', 'error')
        return redirect(url_for('portfolio_index'))

    # Automatically resolve the exact CoinGecko ID (e.g., 'doge' -> 'dogecoin')
    if coin_id == 'usd':
        coin_symbol = 'USD'
    else:
        try:
            url = f"https://api.coingecko.com/api/v3/search?query={coin_id}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('coins') and len(data['coins']) > 0:
                coin_id = data['coins'][0]['id']
                coin_symbol = data['coins'][0]['symbol'].upper()
            else:
                flash(f"Could not find a coin matching '{coin_id}'.", 'error')
                return redirect(url_for('portfolio_index'))
        except Exception as e:
            coin_symbol = coin_id.upper()
            print(f"Search API error: {e}")
            
    # Reject and remove the coin from being added if it is not supported by Binance US
    if coin_symbol != 'USD':
        try:
            exchange = ccxt.binanceus()
            exchange.load_markets()
            market_symbol_usd = f"{coin_symbol}/USD"
            market_symbol_usdt = f"{coin_symbol}/USDT"
            if market_symbol_usd not in exchange.symbols and market_symbol_usdt not in exchange.symbols:
                flash(f"Error: The coin {coin_symbol} is not supported by Binance US.", 'error')
                return redirect(url_for('portfolio_index'))
        except Exception as e:
            print(f"Failed to validate Binance US markets: {e}")

    # Check if we already have this coin by symbol (to prevent Unique Constraint crashes) or name
    crypto = Crypto.query.filter(Crypto.symbol.ilike(coin_symbol)).first()
    if not crypto:
        crypto = Crypto.query.filter(Crypto.name.ilike(coin_id)).first()
        
    if not crypto:
        crypto = Crypto(name=coin_id, symbol=coin_symbol)
        db.session.add(crypto)
        db.session.commit()
    elif crypto.name != coin_id:
        # Auto-heal the database name if the API found a better official ID (e.g., doge -> dogecoin)
        crypto.name = coin_id
        db.session.commit()

    user_id = session['user_id']
    item = PortfolioItem.query.filter_by(user_id=user_id, crypto_id=crypto.id).first()
    if item:
        item.amount_owned = amount
        if target_price: item.target_price = target_price
        item.auto_trade_enabled = auto_trade_enabled
        item.trade_amount = trade_amount
        flash(f'Updated {crypto.name} amount to {amount}.', 'success')
    else:
        new_item = PortfolioItem(user_id=user_id, crypto_id=crypto.id, amount_owned=amount, target_price=target_price, auto_trade_enabled=auto_trade_enabled, trade_amount=trade_amount)
        db.session.add(new_item)
        db.session.add(TradeHistory(user_id=user_id, crypto_symbol=crypto.symbol, trade_type='BUY', amount=amount))
        flash(f'Added {crypto.name} to your portfolio.', 'success')
        
    db.session.commit()
    return redirect(url_for('portfolio_index'))

@app.route('/edit_portfolio_item/<int:item_id>', methods=['POST'])
def edit_portfolio_item(item_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    item = PortfolioItem.query.get(item_id)
    if item and item.user_id == session['user_id']:
        target_str = request.form.get('target_price', '').strip()
        trade_str = request.form.get('trade_amount', '0')
        item.auto_trade_enabled = True if request.form.get('auto_trade') == 'on' else False
        
        try: item.target_price = float(target_str) if target_str else None
        except ValueError: item.target_price = None
        
        try: item.trade_amount = float(trade_str)
        except ValueError: item.trade_amount = 0.0
        
        db.session.commit()
        flash('Portfolio auto-trade settings updated.', 'success')
    return redirect(url_for('portfolio_index'))

@app.route('/delete_portfolio_item/<int:item_id>', methods=['POST'])
def delete_portfolio_item(item_id):
    if 'user_id' not in session:
        flash('Please log in to manage your portfolio.', 'error')
        return redirect(url_for('login'))
        
    item = PortfolioItem.query.get(item_id)
    if item and item.user_id == session['user_id']:
        db.session.delete(item)
        db.session.commit()
        flash('Coin removed from your portfolio.', 'success')
        
    return redirect(url_for('portfolio_index'))

@app.route('/manual_trade', methods=['POST'])
def manual_trade():
    if 'user_id' not in session:
        flash('Please log in to trade.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user.encrypted_api_key or not user.encrypted_api_secret:
        flash('API keys not configured. Please add them in Settings.', 'error')
        return redirect(url_for('settings'))

    coin_id = request.form.get('coin_id', '').strip().lower()
    trade_type = request.form.get('trade_type', '').strip().upper()
    
    try:
        amount = float(request.form.get('amount', '0'))
        if amount <= 0: raise ValueError
    except ValueError:
        flash('Invalid trade amount.', 'error')
        return redirect(url_for('portfolio_index'))
        
    if not coin_id:
        flash('Coin ID cannot be empty.', 'error')
        return redirect(url_for('portfolio_index'))

    # Automatically resolve the exact CoinGecko ID to get the symbol for the exchange
    if coin_id == 'usd':
        symbol = 'USD'
    else:
        try:
            url = f"https://api.coingecko.com/api/v3/search?query={coin_id}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('coins') and len(data['coins']) > 0:
                symbol = data['coins'][0]['symbol'].upper()
            else:
                symbol = coin_id.upper()
        except Exception as e:
            symbol = coin_id.upper()
            print(f"Search API error: {e}")

    try:
        api_key = decrypt_data(user.encrypted_api_key)
        api_secret = decrypt_data(user.encrypted_api_secret)
        exchange = ccxt.binanceus({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        
        # NOTE: Binance US does not have a Sandbox mode. The global testnet blocks US IPs.
        # This is now connecting to the LIVE exchange.
        
        # Dynamically load available markets from Binance US
        exchange.load_markets()
        
        market_symbol_usd = f"{symbol}/USD"
        market_symbol_usdt = f"{symbol}/USDT"
        
        if market_symbol_usd in exchange.symbols:
            market_symbol = market_symbol_usd
        elif market_symbol_usdt in exchange.symbols:
            market_symbol = market_symbol_usdt
        else:
            # Self-healing: Remove unsupported coin from the database entirely
            crypto_to_remove = Crypto.query.filter(Crypto.symbol.ilike(symbol)).first()
            if crypto_to_remove:
                PortfolioItem.query.filter_by(crypto_id=crypto_to_remove.id).delete()
                WatchlistItem.query.filter_by(crypto_id=crypto_to_remove.id).delete()
                PredictionVote.query.filter_by(coin_symbol=crypto_to_remove.symbol).delete()
                db.session.delete(crypto_to_remove)
                db.session.commit()
            raise ValueError(f"The coin {symbol} is not supported by Binance US. It has been completely removed from your account.")
            
        if trade_type == 'BUY':
            order = exchange.create_market_buy_order(market_symbol, amount)
            db.session.add(TradeHistory(user_id=user.id, crypto_symbol=symbol, trade_type='BUY', amount=amount))
        elif trade_type == 'SELL':
            order = exchange.create_market_sell_order(market_symbol, amount)
            db.session.add(TradeHistory(user_id=user.id, crypto_symbol=symbol, trade_type='SELL', amount=amount))
        else:
            raise ValueError("Invalid trade type.")
            
        db.session.commit()
        flash(f"Successfully executed {trade_type} order for {amount} {symbol}. Order ID: {order.get('id', 'N/A')}", "success")
        
    except Exception as e:
        error_msg = str(e)
        if "MIN_NOTIONAL" in error_msg:
            flash("Trade failed: The total dollar value of this trade is too small. Binance US requires a minimum trade size (usually $10).", "error")
        elif "insufficient" in error_msg.lower() or "-2010" in error_msg:
            flash("Trade execution failed: You have insufficient funds.", "error")
        elif "market_lot_size" in error_msg.lower() or "-1013" in error_msg:
            flash("Trade execution failed: You do not have this coin.", "error")
        elif "does not have market symbol" in error_msg.lower() or "not supported by binance" in error_msg.lower():
            flash(f"Trade execution failed: The coin is not supported by Binance US.", "error")
        else:
            flash(f"Trade execution failed: {error_msg}", "error")
        
    return redirect(url_for('portfolio_index'))


# --- WATCHLIST MANAGEMENT ---

@app.route('/add_watchlist_item', methods=['POST'])
def add_watchlist_item():
    if 'user_id' not in session:
        flash('Please log in to add items to your watchlist.', 'error')
        return redirect(url_for('login'))

    coin_id = request.form.get('coin_id', '').strip().lower()
    target_str = request.form.get('target_price', '').strip()
    amount_str = request.form.get('trade_amount', '0')
    auto_trade_enabled = True if request.form.get('auto_trade') == 'on' else False

    try: trade_amount = float(amount_str)
    except ValueError: trade_amount = 0.0

    target_price = None
    if target_str:
        try: target_price = float(target_str)
        except ValueError: pass

    if not coin_id:
        flash('Coin ID cannot be empty.', 'error')
        return redirect(url_for('portfolio_index'))

    # Automatically resolve the exact CoinGecko ID (e.g., 'doge' -> 'dogecoin')
    if coin_id == 'usd':
        coin_symbol = 'USD'
    else:
        try:
            url = f"https://api.coingecko.com/api/v3/search?query={coin_id}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('coins') and len(data['coins']) > 0:
                coin_id = data['coins'][0]['id']
                coin_symbol = data['coins'][0]['symbol'].upper()
            else:
                flash(f"Could not find a coin matching '{coin_id}'.", 'error')
                return redirect(url_for('portfolio_index'))
        except Exception as e:
            coin_symbol = coin_id.upper()
            print(f"Search API error: {e}")
            
    # Reject and remove the coin from being added if it is not supported by Binance US
    if coin_symbol != 'USD':
        try:
            exchange = ccxt.binanceus()
            exchange.load_markets()
            market_symbol_usd = f"{coin_symbol}/USD"
            market_symbol_usdt = f"{coin_symbol}/USDT"
            if market_symbol_usd not in exchange.symbols and market_symbol_usdt not in exchange.symbols:
                flash(f"Error: The coin {coin_symbol} is not supported by Binance US.", 'error')
                return redirect(url_for('portfolio_index'))
        except Exception as e:
            print(f"Failed to validate Binance US markets: {e}")

    # Check if we already have this coin by symbol (to prevent Unique Constraint crashes) or name
    crypto = Crypto.query.filter(Crypto.symbol.ilike(coin_symbol)).first()
    if not crypto:
        crypto = Crypto.query.filter(Crypto.name.ilike(coin_id)).first()
        
    if not crypto:
        crypto = Crypto(name=coin_id, symbol=coin_symbol)
        db.session.add(crypto)
        db.session.commit()
    elif crypto.name != coin_id:
        # Auto-heal the database name if the API found a better official ID
        crypto.name = coin_id
        db.session.commit()

    user_id = session['user_id']
    item = WatchlistItem.query.filter_by(user_id=user_id, crypto_id=crypto.id).first()
    if item:
        if target_price: item.target_price = target_price
        item.auto_trade_enabled = auto_trade_enabled
        item.trade_amount = trade_amount
        flash(f'Updated {crypto.name} target price.', 'success')
    else:
        new_item = WatchlistItem(user_id=user_id, crypto_id=crypto.id, target_price=target_price, auto_trade_enabled=auto_trade_enabled, trade_amount=trade_amount)
        db.session.add(new_item)
        flash(f'Added {crypto.name} to your watchlist.', 'success')
        
    db.session.commit()
    return redirect(url_for('portfolio_index'))

@app.route('/edit_watchlist_item/<int:item_id>', methods=['POST'])
def edit_watchlist_item(item_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    item = WatchlistItem.query.get(item_id)
    if item and item.user_id == session['user_id']:
        target_str = request.form.get('target_price', '').strip()
        trade_str = request.form.get('trade_amount', '0')
        item.auto_trade_enabled = True if request.form.get('auto_trade') == 'on' else False
        
        try: item.target_price = float(target_str) if target_str else None
        except ValueError: item.target_price = None
        
        try: item.trade_amount = float(trade_str)
        except ValueError: item.trade_amount = 0.0
        
        db.session.commit()
        flash('Watchlist auto-buy settings updated.', 'success')
    return redirect(url_for('portfolio_index'))

@app.route('/delete_watchlist_item/<int:item_id>', methods=['POST'])
def delete_watchlist_item(item_id):
    if 'user_id' not in session:
        flash('Please log in to manage your watchlist.', 'error')
        return redirect(url_for('login'))
        
    item = WatchlistItem.query.get(item_id)
    if item and item.user_id == session['user_id']:
        db.session.delete(item)
        db.session.commit()
        flash('Coin removed from your watchlist.', 'success')
        
    return redirect(url_for('portfolio_index'))

# --- API ROUTES ---

@app.route('/api/portfolio_data')
def portfolio_data():
    if 'user_id' not in session:
        return jsonify({'portfolio_items': [], 'total_value': 0})

    user_id = session['user_id']
    portfolio_items = PortfolioItem.query.filter_by(user_id=user_id).all()

    config = Settings.query.first()
    rate = get_currency_data(config.currency if config else 'USD')['rate']

    data = []
    total_value = 0
    for item in portfolio_items:
        raw_price = item.crypto.price
        
        # Override price for Fiat USD
        if item.crypto.symbol.upper() == 'USD':
            raw_price = 1.0
            item.crypto.change_24h = 0.0
            
        holding_val = (raw_price or 0) * (item.amount_owned or 0)
        total_value += holding_val
        
        data.append({
            'item_id': item.id,
            'symbol': item.crypto.symbol,
            'price': (raw_price * rate) if raw_price is not None else None,
            'change_24h': item.crypto.change_24h,
            'market_cap': (item.crypto.market_cap or 0) * rate,
            'last_updated': item.crypto.last_updated.isoformat() if item.crypto.last_updated else None
        })
    
    return jsonify({'portfolio_items': data, 'total_value': total_value * rate})

@app.route('/api/watchlist_data')
def watchlist_data():
    if 'user_id' not in session:
        return jsonify({'watchlist_items': []})

    user_id = session['user_id']
    watchlist_items = WatchlistItem.query.filter_by(user_id=user_id).all()

    config = Settings.query.first()
    rate = get_currency_data(config.currency if config else 'USD')['rate']

    data = []
    for item in watchlist_items:
        raw_price = item.crypto.price
        
        # Override price for Fiat USD
        if item.crypto.symbol.upper() == 'USD':
            raw_price = 1.0
            item.crypto.change_24h = 0.0
            
        data.append({
            'item_id': item.id,
            'symbol': item.crypto.symbol,
            'price': (raw_price * rate) if raw_price is not None else None,
            'target_price': (item.target_price * rate) if item.target_price else None,
            'change_24h': item.crypto.change_24h,
            'market_cap': (item.crypto.market_cap or 0) * rate,
            'last_updated': item.crypto.last_updated.isoformat() if item.crypto.last_updated else None
        })
    
    return jsonify({'watchlist_items': data})

@app.route('/api/search_coins')
def search_coins():
    query = request.args.get('query', '').strip()
    if not query: return jsonify([])

    try:
        url = f"https://api.coingecko.com/api/v3/search?query={query}"
        response = requests.get(url, timeout=10)
        data = response.json().get('coins', [])
        
        supported = get_binance_us_symbols()
        if supported:
            # Filter results so only Binance US compatible coins appear in the dropdown
            data = [coin for coin in data if coin.get('symbol', '').upper() in supported]
            
        return jsonify(data)
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify([]), 500

@app.route('/api/chart_data')
def chart_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    config = Settings.query.first()
    rate = get_currency_data(config.currency if config else 'USD')['rate']
    
    pf_history = PortfolioHistory.query.filter_by(user_id=user_id).order_by(PortfolioHistory.timestamp.asc()).all()
    
    # If no history exists yet, generate an initial snapshot instantly so the chart isn't blank
    if not pf_history:
        pf_items = PortfolioItem.query.filter_by(user_id=user_id).all()
        total_val = sum(((1.0 if p.crypto.symbol.upper() == 'USD' else (p.crypto.price or 0)) * p.amount_owned) for p in pf_items)
        if total_val > 0:
            new_snap = PortfolioHistory(user_id=user_id, total_value=total_val)
            db.session.add(new_snap)
            db.session.commit()
            pf_history = [new_snap]
            
    pf_labels = [h.timestamp.strftime('%m-%d %H:%M') for h in pf_history]
    pf_values = [h.total_value * rate for h in pf_history]
    
    trades = TradeHistory.query.filter_by(user_id=user_id, trade_type='BUY').order_by(TradeHistory.timestamp.asc()).all()
    trade_labels = [t.timestamp.strftime('%m-%d %H:%M') for t in trades]
    trade_amounts = [t.amount for t in trades]
    trade_symbols = [t.crypto_symbol for t in trades]
    
    return jsonify({
        'portfolio': {'labels': pf_labels, 'values': pf_values},
        'trades': {'labels': trade_labels, 'amounts': trade_amounts, 'symbols': trade_symbols}
    })

# --- PREDICTION MARKET API ---

@app.route('/api/get_votes/<symbol>')
def get_votes(symbol):
    symbol = symbol.upper()
    up_count = PredictionVote.query.filter_by(coin_symbol=symbol, vote_type='up').count()
    down_count = PredictionVote.query.filter_by(coin_symbol=symbol, vote_type='down').count()
    
    total = up_count + down_count
    if total == 0:
        return jsonify({'up_pct': 50, 'down_pct': 50, 'total': 0})
    
    up_pct = round((up_count / total) * 100)
    return jsonify({'up_pct': up_pct, 'down_pct': 100 - up_pct, 'total': total})

@app.route('/api/cast_vote', methods=['POST'])
def cast_vote():
    if 'user_id' not in session:
        return jsonify({'error': 'You must be logged in to vote!'}), 401
    
    data = request.get_json()
    symbol = data.get('symbol').upper()
    vote_type = data.get('type')
    user_id = session['user_id']

    existing = PredictionVote.query.filter_by(user_id=user_id, coin_symbol=symbol).first()
    if existing:
        return jsonify({'error': 'Already placed a prediction for this coin.'}), 400

    new_vote = PredictionVote(user_id=user_id, coin_symbol=symbol, vote_type=vote_type)
    db.session.add(new_vote)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/create_poll', methods=['POST'])
def create_poll():
    data = request.get_json()
    new_question = data.get('question')
    if not new_question:
        return jsonify({'error': 'Question cannot be empty'}), 400
        
    poll = Poll(question=new_question)
    db.session.add(poll)
    db.session.commit()
    return jsonify({'message': 'Poll created successfully!', 'id': poll.id})

@app.route('/api/cast_poll_vote', methods=['POST'])
def cast_poll_vote():
    if 'user_id' not in session:
        return jsonify({'error': 'Login required!'}), 401
    
    data = request.get_json()
    poll_id = data.get('poll_id')
    vote_choice = data.get('vote')
    user_id = session['user_id']

    existing = PollVote.query.filter_by(user_id=user_id, poll_id=poll_id).first()
    if existing:
        return jsonify({'error': 'Already voted on this poll.'}), 400

    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({'error': 'Poll not found'}), 404

    db.session.add(PollVote(user_id=user_id, poll_id=poll_id, choice=vote_choice))

    if vote_choice == 'yes':
        poll.yes_votes = (poll.yes_votes or 0) + 1
    else:
        poll.no_votes = (poll.no_votes or 0) + 1
    
    db.session.commit()
    return jsonify({'success': True})

# --- PAGE VIEWS ---

@app.route('/predictive_market/<symbol>')
def predictive_market(symbol):
    query = symbol.strip().lower()
    
    # Automatically resolve the exact CoinGecko ID and Symbol
    if query == 'usd':
        resolved_id = 'usd'
        resolved_symbol = 'USD'
    else:
        try:
            url = f"https://api.coingecko.com/api/v3/search?query={query}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('coins') and len(data['coins']) > 0:
                resolved_id = data['coins'][0]['id']
                resolved_symbol = data['coins'][0]['symbol'].upper()
            else:
                resolved_id = query
                resolved_symbol = query.upper()
        except Exception as e:
            resolved_id = query
            resolved_symbol = query.upper()
            print(f"Search API error: {e}")

    # Check if we already have this coin by symbol or name
    crypto = Crypto.query.filter(Crypto.symbol.ilike(resolved_symbol)).first()
    if not crypto:
        crypto = Crypto.query.filter(Crypto.name.ilike(resolved_id)).first()
        
    if not crypto:
        crypto = Crypto(name=resolved_id, symbol=resolved_symbol)
        db.session.add(crypto)
        db.session.commit()
    elif crypto.name != resolved_id:
        # Auto-heal the database name if a legacy broken coin exists
        crypto.name = resolved_id
        db.session.commit()

    all_polls = Poll.query.order_by(Poll.created_at.desc()).all() 
    config = Settings.query.first()
    
    return render_template('predictive_market.html', 
                           crypto=crypto, 
                           polls=all_polls,
                           settings=config)

# --- ADMIN DASHBOARD ---

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('portfolio_index'))
        
    all_users = User.query.all()
    config = Settings.query.first()
    
    return render_template('admin.html', users=all_users, settings=config)

@app.route('/admin/delete_user/<int:target_user_id>', methods=['POST'])
def delete_user(target_user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    current_user = User.query.get(session['user_id'])
    if not current_user or not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('portfolio_index'))
        
    if target_user_id == current_user.id:
        flash('You cannot delete your own admin account!', 'error')
        return redirect(url_for('admin_dashboard'))
        
    target_user = User.query.get(target_user_id)
    if target_user:
        # Clean up their portfolio, watchlist, and votes to prevent database constraints from crashing
        PortfolioItem.query.filter_by(user_id=target_user.id).delete()
        WatchlistItem.query.filter_by(user_id=target_user.id).delete()
        PredictionVote.query.filter_by(user_id=target_user.id).delete()
        PollVote.query.filter_by(user_id=target_user.id).delete()
        
        db.session.delete(target_user)
        db.session.commit()
        flash(f'User {target_user.username} has been deleted.', 'success')
        
    return redirect(url_for('admin_dashboard'))

# --- AUTH & SETTINGS ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username exists.', 'error')
            return redirect(url_for('register'))
        
        secure_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=secure_hash)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('portfolio_index'))
            
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/import_exchange', methods=['POST'])
def import_exchange():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user.encrypted_api_key or not user.encrypted_api_secret:
        return redirect(url_for('settings'))

    api_key = decrypt_data(user.encrypted_api_key)
    api_secret = decrypt_data(user.encrypted_api_secret)
    try:
        exchange = ccxt.binanceus({'apiKey': api_key, 'secret': api_secret})
        balances = exchange.fetch_balance()
        totals = balances.get('total', {})
            
        # Fetch CoinGecko's master list to translate Binance symbols (like 'DOGE') to IDs ('dogecoin')
        cg_mapping = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'DOGE': 'dogecoin', 
            'SOL': 'solana', 'ADA': 'cardano', 'USDT': 'tether',
            'BNB': 'binancecoin', 'XRP': 'ripple', 'LTC': 'litecoin',
            'USD': 'usd'
        }
        try:
            cg_list = requests.get("https://api.coingecko.com/api/v3/coins/list", timeout=10).json()
            for coin in cg_list:
                if coin['symbol'].upper() not in cg_mapping:
                    cg_mapping[coin['symbol'].upper()] = coin['id']
        except Exception as e:
            print(f"Failed to fetch CoinGecko list: {e}")
            
        for symbol, amount in totals.items():
            amt = float(amount or 0)
            if amt <= 0: continue
            
            # Translate the ID, falling back to lowercased symbol if not found
            resolved_id = cg_mapping.get(symbol.upper(), symbol.lower())
            
            crypto = Crypto.query.filter_by(symbol=symbol.upper()).first()
            if not crypto:
                crypto = Crypto(name=resolved_id, symbol=symbol.upper())
                db.session.add(crypto)
                db.session.commit()
            elif crypto.name != resolved_id and resolved_id != symbol.lower():
                # Fix any existing broken coins from previous imports automatically
                crypto.name = resolved_id
                db.session.commit()
                
            item = PortfolioItem.query.filter_by(user_id=user.id, crypto_id=crypto.id).first()
            if item: 
                item.amount_owned = amt
            else:
                db.session.add(PortfolioItem(user_id=user.id, crypto_id=crypto.id, amount_owned=amt))
        db.session.commit()
        flash("Exchange balances imported successfully!", "success")
    except Exception as e:
        flash(f'Import failed: {e}', 'error')
    return redirect(url_for('settings'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # SAFETY CHECK: If the session has an ID but the database doesn't find the user
    if not user:
        session.clear() # Clear the invalid session
        flash("User session expired or account not found. Please login again.", "error")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        api_key = request.form.get('api_key', '').strip()
        api_secret = request.form.get('api_secret', '').strip()
        email = request.form.get('email', '').strip()
        
        user.email = email if email else None
        
        if api_key: 
            user.encrypted_api_key = encrypt_data(api_key)
        if api_secret: 
            user.encrypted_api_secret = encrypt_data(api_secret)
        db.session.commit()
        flash("Settings updated successfully!", "success")

    config = Settings.query.first() or Settings()
    decrypted_api_key = decrypt_data(user.encrypted_api_key) if user.encrypted_api_key else ''
    return render_template('settings.html', 
                           settings=config,
                           user=user,
                           has_api_secret=bool(user.encrypted_api_secret), 
                           api_key=decrypted_api_key)

@app.route('/delete_api_keys', methods=['POST'])
def delete_api_keys():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if user:
        user.encrypted_api_key = None
        user.encrypted_api_secret = None
        db.session.commit()
        flash("API keys deleted successfully.", "success")
        
    return redirect(url_for('settings'))

@app.route('/test_email', methods=['POST'])
def test_email():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user.email:
        flash("Please save an email address first.", "error")
        return redirect(url_for('settings'))
        
    from sync_engine import send_email_alert
    success, error_msg = send_email_alert(user.email, "Test Email from Crypto Dashboard", "If you are reading this, your email configuration is working perfectly!")
    
    if success:
        flash("Test email sent successfully! Please check your inbox (and spam folder).", "success")
    else:
        flash(f"Failed to send test email: {error_msg}", "error")
        
    return redirect(url_for('settings'))

@app.route('/api/save_settings', methods=['POST'])
def save_settings():
    data = request.get_json()
    config = Settings.query.first() or Settings()
    config.theme = data.get('theme')
    config.currency = data.get('currency')
    config.alert_enabled = data.get('alert_enabled')
    config.refresh_rate = int(data.get('refresh_rate'))
    db.session.add(config)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Settings updated!'})