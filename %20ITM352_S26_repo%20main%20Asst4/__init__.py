from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initializes the app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db = SQLAlchemy(app)

# to ensure the SQLAlchemy metadata is ready and avoid circular crashes.
from models import Crypto, User, PortfolioItem, WatchlistItem, PredictionVote
