from datetime import datetime, timezone
from __init__ import db

# Database blueprints
class Crypto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=True)
    change_24h = db.Column(db.Float, nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Crypto {self.symbol}: ${self.price}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Preparing for Sprint 8 (Auto Trading / Encryption)
    api_key = db.Column(db.String(256), nullable=True)
    encrypted_api_secret = db.Column(db.String(256), nullable=True)
    
    # Relationship to track user's portfolio/watchlist
    portfolio = db.relationship('PortfolioItem', backref='user', lazy=True)

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crypto_id = db.Column(db.Integer, db.ForeignKey('crypto.id'), nullable=False)
    amount_owned = db.Column(db.Float, default=0.0)
    target_price = db.Column(db.Float, nullable=True)
    crypto = db.relationship('Crypto')