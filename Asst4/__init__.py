from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config  # <-- FIXED: use relative import

# Initializes the app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db = SQLAlchemy(app)

# Import routes after app initialization to avoid circular imports
import Asst4.routes
import Asst4.model