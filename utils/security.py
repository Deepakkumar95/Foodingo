# src/utils/security.py
import hashlib
import hmac
import secrets
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SecurityUtils:
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or self.generate_secret_key()
        
    @staticmethod
    def generate_secret_key(length: int = 32) -> str:
        """Generate a secure random secret key"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2-SHA256 with a secure salt."""
        iterations = 260000
        salt = secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations
        )
        return f"pbkdf2_sha256${iterations}${salt.hex()}${key.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against a stored PBKDF2-SHA256 hash."""
        try:
            algorithm, iterations, salt_hex, key_hex = hashed.split('$')
            if algorithm != 'pbkdf2_sha256':
                logger.warning("Unsupported password hashing algorithm")
                return False

            iterations = int(iterations)
            salt = bytes.fromhex(salt_hex)
            key = bytes.fromhex(key_hex)
            
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                iterations
            )
            
            return hmac.compare_digest(key, new_key)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate API key for user"""
        timestamp = str(secrets.randbits(64))
        data = f"{user_id}:{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"fd_{user_id}_{timestamp}_{signature[:16]}"
    
    def verify_api_key(self, api_key: str, user_id: str) -> bool:
        """Verify API key for user"""
        try:
            parts = api_key.split('_')
            if len(parts) != 4 or parts[0] != 'fd':
                return False
            
            key_user_id = parts[1]
            timestamp = parts[2]
            provided_signature = parts[3]
            
            if key_user_id != user_id:
                return False
            
            data = f"{user_id}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(
                provided_signature, 
                expected_signature[:16]
            )
        except Exception as e:
            logger.error(f"API key verification failed: {e}")
            return False
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token: str, expected: str) -> bool:
        """Verify CSRF token"""
        return hmac.compare_digest(token, expected)
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        import html
        
        # Escape HTML characters
        sanitized = html.escape(input_str)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", ';', '(', ')', '`']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        
        # Basic international phone number validation
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone) is not None
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data (simplified version)"""
        # In production, use proper encryption like AES
        import base64
        
        # Simple XOR encryption for demo (not secure for production)
        key = self.secret_key.encode()
        data_bytes = data.encode()
        
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key[i % len(key)])
        
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        import base64
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
            key = self.secret_key.encode()
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key[i % len(key)])
            
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            return ""
    
    def generate_secure_random_string(self, length: int = 16) -> str:
        """Generate secure random string"""
        return secrets.token_urlsafe(length)
    
    def calculate_hmac(self, data: str) -> str:
        """Calculate HMAC for data integrity"""
        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_hmac(self, data: str, expected_hmac: str) -> bool:
        """Verify HMAC for data integrity"""
        calculated_hmac = self.calculate_hmac(data)
        return hmac.compare_digest(calculated_hmac, expected_hmac)
