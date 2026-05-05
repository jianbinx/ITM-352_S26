from datetime import datetime, timezone
from __init__ import db

# 1. CRYPTO MARKET DATA MODEL
class Crypto(db.Model):
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=True)
    change_24h = db.Column(db.Float, nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Crypto {self.symbol}: ${self.price}>"

# 2. USER ACCOUNT MODEL
class User(db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    api_key = db.Column(db.String(256), nullable=True)
    encrypted_api_secret = db.Column(db.String(256), nullable=True)
    sound_alerts_enabled = db.Column(db.Boolean, default=True) 
    
    is_admin = db.Column(db.Boolean, default=False)
    
    portfolio = db.relationship('PortfolioItem', backref='user', lazy=True)
    watchlist = db.relationship('WatchlistItem', backref='user', lazy=True)

# 3. PORTFOLIO & WATCHLIST MODEL
class PortfolioItem(db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crypto_id = db.Column(db.Integer, db.ForeignKey('crypto.id'), nullable=False)
    
    amount_owned = db.Column(db.Float, default=0.0)
    target_price = db.Column(db.Float, nullable=True)
    auto_trade_enabled = db.Column(db.Boolean, default=False)
    trade_amount = db.Column(db.Float, default=0.0)
    
    crypto = db.relationship('Crypto')

# 3.5. WATCHLIST MODEL
class WatchlistItem(db.Model):
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crypto_id = db.Column(db.Integer, db.ForeignKey('crypto.id'), nullable=False)
    
    target_price = db.Column(db.Float, nullable=True)
    auto_trade_enabled = db.Column(db.Boolean, default=False)
    trade_amount = db.Column(db.Float, default=0.0)
    
    crypto = db.relationship('Crypto')

# 4. PREDICTION MARKET VOTING MODEL (For Up/Down on specific coins)
class PredictionVote(db.Model):
    __table_args__ = (
        db.UniqueConstraint('user_id', 'coin_symbol', name='_user_coin_uc'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coin_symbol = db.Column(db.String(10), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False) # 'up' or 'down'

# 5. COMMUNITY POLL MODELS (For Yes/No questions)
class Poll(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    
    # Updated to match the Yes/No UI
    yes_votes = db.Column(db.Integer, default=0)
    no_votes = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class PollVote(db.Model):
    """Prevents users from voting more than once on a specific poll question"""
    __table_args__ = (
        db.UniqueConstraint('user_id', 'poll_id', name='_user_poll_uc'),
        {'extend_existing': True}
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    choice = db.Column(db.String(10), nullable=False) # 'yes' or 'no'

# 6. APP SETTINGS MODEL
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(10), default='light')
    currency = db.Column(db.String(3), default='USD')
    alert_enabled = db.Column(db.Boolean, default=True)
    refresh_rate = db.Column(db.Integer, default=10)