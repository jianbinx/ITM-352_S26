from __init__ import app, db
from models import Crypto

# Starts the project
if __name__ == '__main__':
    # Create the database tables if they don't exist yet
    with app.app_context():
        db.create_all()
        
        # Add some initial dummy data if the database is completely empty
        if not Crypto.query.first():
            btc = Crypto(name="Bitcoin", symbol="BTC", price=64500.00)
            eth = Crypto(name="Ethereum", symbol="ETH", price=3450.00)
            db.session.add_all([btc, eth])
            db.session.commit()
            print("Added initial dummy data to the database.")
            
    app.run(debug=True)