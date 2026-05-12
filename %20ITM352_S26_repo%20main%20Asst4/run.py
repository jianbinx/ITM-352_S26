# run.py
import socket

# Force Python to use IPv4 for all network requests to avoid IPv6 blocking issues with Binance
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [res for res in responses if res[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

import threading
from __init__ import app, db
import routes
from models import User
from werkzeug.security import generate_password_hash
from sync_engine import sync_crypto_prices
from sqlalchemy import text

def start_background_worker():
    """Starts the price syncing and alert engine in a separate thread."""
    # daemon=True ensures the thread exits when the main program stops
    worker_thread = threading.Thread(target=sync_crypto_prices, daemon=True)
    worker_thread.start()

if __name__ == '__main__':
    # Initialize the database and seed data if necessary
    with app.app_context():
        db.create_all()
        
        # Safely add the email column to the existing database
        try:
            db.session.execute(text('ALTER TABLE user ADD COLUMN email VARCHAR(120)'))
            db.session.commit()
        except Exception:
            db.session.rollback() # Ignored if the column already exists

        # Safely add the encrypted_api_key column
        try:
            db.session.execute(text('ALTER TABLE user ADD COLUMN encrypted_api_key VARCHAR(256)'))
            db.session.commit()
        except Exception:
            db.session.rollback() # Ignored if the column already exists

        # Safely add the new is_admin column to the existing database
        try:
            db.session.execute(text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0'))
            db.session.commit()
        except Exception:
            db.session.rollback() # Ignored if the column already exists
            
        # Safely add the new auto_trade_enabled column to the existing database
        try:
            db.session.execute(text('ALTER TABLE portfolio_item ADD COLUMN auto_trade_enabled BOOLEAN DEFAULT 0'))
            db.session.commit()
        except Exception:
            db.session.rollback() # Ignored if the column already exists
            
        try:
            db.session.execute(text('ALTER TABLE portfolio_item ADD COLUMN trade_amount FLOAT DEFAULT 0.0'))
            db.session.commit()
        except Exception:
            db.session.rollback() # Ignored if the column already exists
            
        # Safely add Watchlist Auto-Buy columns to the existing database
        try:
            db.session.execute(text('ALTER TABLE watchlist_item ADD COLUMN auto_trade_enabled BOOLEAN DEFAULT 0'))
            db.session.commit()
        except Exception:
            db.session.rollback() # Ignored if the columns already exist
            
        try:
            db.session.execute(text('ALTER TABLE watchlist_item ADD COLUMN trade_amount FLOAT DEFAULT 0.0'))
            db.session.commit()
        except Exception:
            db.session.rollback() # Ignored if the columns already exist
            
        # Create a default admin user if one doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            secure_hash = generate_password_hash('admin123')
            admin_user = User(username='admin', password_hash=secure_hash, is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
        print("--- Database Tables Verified ---")
    
    # Start the background sync engine before launching the web server
    start_background_worker()
    
    # Explicitly print the access link for better visibility
    print("\n" + "="*40)
    print("  CRYPTO DASHBOARD ACTIVE")
    print("  Local URL: http://127.0.0.1:5001")
    print("  Network URL: http://0.0.0.0:5001")
    print("="*40 + "\n")
    
    # use_reloader=False prevents the background thread from starting twice
    app.run(host='0.0.0.0', debug=True, use_reloader=False, port=5001)