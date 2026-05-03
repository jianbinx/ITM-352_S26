from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initializes the app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db = SQLAlchemy(app)

# Import routes after app initialization to avoid circular imports
import routes
import models