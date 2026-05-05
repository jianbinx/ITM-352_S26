# Crypto Dashboard & Auto-Trader

A comprehensive, Flask-based cryptocurrency portfolio tracker, watchlist, and automated trading platform. It integrates with CoinGecko for live price tracking, Binance US for real-time order execution, and Manifold for prediction market polling.

## Features
- **Live Portfolio & Watchlist:** Track your crypto holdings and prospective coins with real-time price, 24h change, and market cap updates.
- **Smart Auto-Trading:** Configure "Auto-Buy" (buy the dip) and "Auto-Sell" (take profit) targets with customizable trade amounts. The background engine will execute live trades via Binance US when targets are hit.
- **Quick Trade UI:** Execute manual trades instantly with a built-in live USD cost calculator.
- **Military-Grade Security:** User API keys and secrets are encrypted using AES-128 (Fernet) before being saved to the database.
- **Smart Alerts:** Receive audio chimes and automated email notifications (with built-in test diagnostic tools) when trades execute or prices hit your targets.
- **Prediction Markets:** Participate in global crypto prediction polls powered by the Manifold Markets API.
- **Admin Dashboard:** A secure administrative panel to view and manage registered users.

## Installation & Setup

### 1. Install Prerequisites
Ensure you have Python 3 installed. It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory of the project. You must define a `SECRET_KEY` for Flask sessions and a `FERNET_KEY` for database encryption.

To generate a secure Fernet key, run this in your Python shell:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Add the following to your `.env` file:
```env
# Application Secrets
SECRET_KEY=your-secure-flask-secret-key
FERNET_KEY=your-generated-fernet-key-here

# Email Alert Configuration (Optional, but required for email alerts)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
```

### 3. Initialize the Database & Run the App
The application uses SQLite by default. When you run the application for the first time, it will automatically build the database tables and create a default admin account.

```bash
python run.py
```

The server will start on port `5001`. Open your browser and navigate to:
**http://127.0.0.1:5001**

## Default Accounts
On the very first startup, the system generates a default Admin account:
- **Username:** `admin`
- **Password:** `admin123`

*Note: It is highly recommended to log in and change these credentials if deploying to a production environment.*

## How the Auto-Trader Works
1. The app runs a background daemon thread (`sync_engine.py`) alongside the Flask web server.
2. Every X seconds (configurable in User Settings), it fetches live prices from CoinGecko.
3. It checks your Portfolio and Watchlist for any items with `auto_trade_enabled=True`.
4. If a target condition is met, it decrypts your Binance US API keys, executes a Market Order for the specified amount via `ccxt` on the **live** exchange, updates your database balances, and emails you a success log.

## Disclaimer
This software connects to live financial exchanges (**Binance US Production, not Sandbox**). Always test your strategies with small amounts and ensure your API keys are tightly permissioned. The developers assume no responsibility for financial losses incurred while using the auto-trading bots.