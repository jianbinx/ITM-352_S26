from cryptography.fernet import Fernet
from config import Config

# Initialize Fernet with the key from config
f = Fernet(Config.FERNET_KEY.encode())

def encrypt_data(data: str) -> str:
    """Encrypts a string and returns it as a string."""
    if not data:
        return ""
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts a string and returns it."""
    if not encrypted_data:
        return ""
    try:
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception:
        # Handle cases where decryption fails (e.g., invalid token)
        return ""