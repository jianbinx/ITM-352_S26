from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json
import requests
from datetime import datetime
import os
from __init__ import app, db
from models import Crypto, User, PortfolioItem
from security import encrypt_data, decrypt_data
import ccxt

# Website pages
@app.route('/')
def index():
    # Show a public homepage for anonymous visitors.
    if 'user_id' not in session:
        return render_template('index.html', portfolio_items=[], alerts=[])

    # Fetch the portfolio items for the logged-in user
    user_id = session['user_id']
    portfolio_items = PortfolioItem.query.filter_by(user_id=user_id).all()
    
    # Load alerts for the user
    alerts = []
    alerts_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'alerts_{user_id}.json')
    if os.path.exists(alerts_file):
        with open(alerts_file, 'r') as f:
            try:
                alerts = json.load(f)
            except json.JSONDecodeError:
                pass

    # Render the index.html template, passing in our crypto data
    return render_template('index.html', portfolio_items=portfolio_items, alerts=alerts)

@app.route('/add_portfolio_item', methods=['POST'])
def add_portfolio_item():
    # Protect the route
    if 'user_id' not in session:
        flash('Please log in to add items to your portfolio.', 'error')
        return redirect(url_for('login'))

    coin_id = request.form.get('coin_id', '').strip().lower()
    amount_str = request.form.get('amount', '0')
    target_str = request.form.get('target_price', '').strip()

    target_price = None
    if target_str:
        try:
            target_price = float(target_str)
        except ValueError:
            pass

    try:
        amount = float(amount_str)
    except ValueError:
        flash('Invalid amount entered.', 'error')
        return redirect(url_for('index'))

    if not coin_id:
        flash('Coin ID cannot be empty.', 'error')
        return redirect(url_for('index'))

    # Check if the crypto is already tracked in our database
    crypto = Crypto.query.filter(Crypto.name.ilike(coin_id)).first()
    if not crypto:
        # Add to DB; the sync_engine will update price/market_cap on its next run
        crypto = Crypto(name=coin_id, symbol=coin_id.upper())
        db.session.add(crypto)
        db.session.commit()

    user_id = session['user_id']
    item = PortfolioItem.query.filter_by(user_id=user_id, crypto_id=crypto.id).first()
    if item:
        item.amount_owned = amount
        if target_price:
            item.target_price = target_price
        flash(f'Updated {crypto.name} amount to {amount}.', 'success')
    else:
        new_item = PortfolioItem(user_id=user_id, crypto_id=crypto.id, amount_owned=amount, target_price=target_price)
        db.session.add(new_item)
        flash(f'Added {crypto.name} to your watchlist/portfolio.', 'success')
        
    db.session.commit()
    return redirect(url_for('index'))

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
        
    return redirect(url_for('index'))

@app.route('/api/portfolio_data')
def portfolio_data():
    if 'user_id' not in session:
        return jsonify({'portfolio_items': [], 'total_value': 0})

    user_id = session['user_id']
    portfolio_items = PortfolioItem.query.filter_by(user_id=user_id).all()

    data = []
    total_value = 0
    for item in portfolio_items:
        holding_value = (item.crypto.price or 0) * (item.amount_owned or 0)
        total_value += holding_value
        data.append({
            'item_id': item.id,
            'symbol': item.crypto.symbol,
            'price': item.crypto.price,
            'holding_value': holding_value,
            'change_24h': item.crypto.change_24h,
            'market_cap': item.crypto.market_cap,
            'last_updated': item.crypto.last_updated.isoformat() if item.crypto.last_updated else None
        })
    
    response_data = {'portfolio_items': data, 'total_value': total_value}
    return jsonify(response_data)

@app.route('/api/search_coins')
def search_coins():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([]) # Return empty list if no query

    try:
        # Call CoinGecko's search API
        url = f"https://api.coingecko.com/api/v3/search?query={query}"
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        
        # We only care about the 'coins' part of the response
        return jsonify(data.get('coins', []))
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling CoinGecko search API: {e}")
        return jsonify({"error": "Failed to fetch search results"}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))
            
        # Create the new user and save to the database
        new_user = User(
            username=username, 
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
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
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        flash('Please log in to access settings.', 'error')
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        api_key = request.form.get('api_key', '').strip()
        api_secret = request.form.get('api_secret', '').strip()
        
        if api_key or api_secret:
            if api_key:
                user.api_key = api_key
            if api_secret:
                # Encrypt the API secret using military-grade Fernet encryption before saving
                user.encrypted_api_secret = encrypt_data(api_secret)
            db.session.commit()
            flash('API credentials successfully saved!', 'success')
        else:
            flash('No API credentials provided.', 'error')
            
    # Just pass a boolean flag to the template for the secret for security
    has_api_secret = bool(user.encrypted_api_secret)
    # It is safe to pass the public API Key back to the template
    return render_template('settings.html', has_api_secret=has_api_secret, api_key=user.api_key)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/import_exchange', methods=['POST'])
def import_exchange():
    """Imports holdings from the user's linked exchange (Binance) using ccxt and saved API keys."""
    if 'user_id' not in session:
        flash('Please log in to import holdings.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user.api_key or not user.encrypted_api_secret:
        flash('Please save your API credentials in Settings before importing.', 'error')
        return redirect(url_for('settings'))

    # Decrypt secret
    api_secret = decrypt_data(user.encrypted_api_secret)
    if not api_secret:
        flash('Failed to decrypt API secret. Re-enter your API credentials.', 'error')
        return redirect(url_for('settings'))

    try:
        exchange = ccxt.binance({
            'apiKey': user.api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        # Do not enable sandbox here — assume user API corresponds to desired environment
        balances = exchange.fetch_balance()
        totals = balances.get('total', {})

        imported = 0
        for symbol, amount in totals.items():
            # Skip zero balances and non-numeric
            try:
                amt = float(amount or 0)
            except Exception:
                continue
            if amt <= 0:
                continue

            # symbol is like 'BTC', try to find matching Crypto by symbol
            crypto = Crypto.query.filter_by(symbol=symbol.upper()).first()
            if not crypto:
                # Create a minimal Crypto record; name uses lowercase id suitable for CoinGecko syncing
                crypto = Crypto(name=symbol.lower(), symbol=symbol.upper())
                db.session.add(crypto)
                db.session.commit()

            # Add or update PortfolioItem for this user
            item = PortfolioItem.query.filter_by(user_id=user.id, crypto_id=crypto.id).first()
            if item:
                item.amount_owned = amt
            else:
                item = PortfolioItem(user_id=user.id, crypto_id=crypto.id, amount_owned=amt)
                db.session.add(item)
            imported += 1

        db.session.commit()
        flash(f'Imported {imported} holdings from exchange.', 'success')
    except Exception as e:
        flash(f'Failed to import holdings: {e}', 'error')

    return redirect(url_for('settings'))