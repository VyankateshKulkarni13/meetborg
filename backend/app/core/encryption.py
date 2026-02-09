"""
Encryption Utilities
AES-256 encryption for sensitive data
"""
from cryptography.fernet import Fernet
from app.core.config import settings
import base64
from typing import Optional


class EncryptionService:
    """Handle encryption and decryption of sensitive data"""
    
    def __init__(self):
        # Generate key from SECRET_KEY
        # In production, use a dedicated encryption key
        key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'0'))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted string"""
        if not encrypted_data:
            return ""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


# Global encryption service instance
encryption_service = EncryptionService()


def encrypt_credential(credential: str) -> str:
    """Encrypt a credential"""
    return encryption_service.encrypt(credential)


def decrypt_credential(encrypted_credential: str) -> Optional[str]:
    """Decrypt a credential"""
    try:
        return encryption_service.decrypt(encrypted_credential)
    except Exception:
        return None
