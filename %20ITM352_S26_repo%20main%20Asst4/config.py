import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # App settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    # To generate a new Fernet key, run this in a Python shell:
    # from cryptography.fernet import Fernet
    # Fernet.generate_key().decode()
    FERNET_KEY = os.environ.get('FERNET_KEY')
    if not FERNET_KEY:
        raise ValueError("No FERNET_KEY set for Flask application. Please generate one and set it in your .env file.")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'crypto.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')