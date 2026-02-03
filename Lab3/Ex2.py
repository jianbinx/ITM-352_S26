from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_suite = Fernet(key)

encoded_text = cipher_suite.encrypt(b"Secret Message")
print(f"Encoded Text: {encoded_text}")

#Use the cryptography to encode and decode a message.
decoded_text = cipher_suite.decrypt(encoded_text)
print(f"Decoded Text: {decoded_text.decode()}")
