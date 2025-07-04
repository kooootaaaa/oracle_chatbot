import os
from cryptography.fernet import Fernet
import base64

def decrypt_credential(encrypted_value, key):
    """暗号化された値を復号化"""
    f = Fernet(key.encode())
    decoded = base64.urlsafe_b64decode(encrypted_value.encode())
    decrypted = f.decrypt(decoded)
    return decrypted.decode()

def get_oracle_config():
    """暗号化されたOracle接続情報を復号化して返す"""
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        raise ValueError("ENCRYPTION_KEY not found in environment variables")
    
    return {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': decrypt_credential(os.getenv('DB_NAME_ENCRYPTED'), key),
        'USER': decrypt_credential(os.getenv('DB_USER_ENCRYPTED'), key),
        'PASSWORD': decrypt_credential(os.getenv('DB_PASSWORD_ENCRYPTED'), key),
        'HOST': decrypt_credential(os.getenv('DB_HOST_ENCRYPTED'), key),
        'PORT': os.getenv('DB_PORT', '1521'),
    }