from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
import hashlib


def validate_key(key: str) -> None:
    if not key:
        raise ValueError("Encryption key cannot be empty")
    
    if len(key) < 8:
        raise ValueError(
            f"Encryption key too weak. Minimum length: 8 characters, got {len(key)}. "
            "Use a strong passphrase for security."
        )
    
    if len(key) > 1000:
        raise ValueError(f"Encryption key too long. Maximum: 1000 characters, got {len(key)}")


def derive_key(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = b'SteganoGen2024'
    
    key = PBKDF2(password, salt, dkLen=32, count=100000)
    return key, salt


def encrypt_payload(data: bytes, key: str) -> dict:
    validate_key(key)
    
    if not data:
        raise ValueError("Cannot encrypt empty data")
    
    try:
        key_bytes, salt = derive_key(key)
        
        iv = get_random_bytes(16)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        
        return {
            'encrypted_data': encrypted_data,
            'iv': iv
        }
    except Exception as e:
        raise RuntimeError(f"Encryption failed: {str(e)}")


def decrypt_payload(encrypted_data: bytes, iv: bytes, key: str) -> bytes:
    validate_key(key)
    
    if not encrypted_data:
        raise ValueError("Cannot decrypt empty data")
    
    if not iv or len(iv) != 16:
        raise ValueError(f"Invalid IV. Expected 16 bytes, got {len(iv) if iv else 0}")
    
    if len(encrypted_data) % AES.block_size != 0:
        raise ValueError(
            f"Invalid encrypted data length. Must be multiple of {AES.block_size}, "
            f"got {len(encrypted_data)}. Data may be corrupted."
        )
    
    try:
        key_bytes, salt = derive_key(key)
        
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        try:
            unpadded_data = unpad(decrypted_data, AES.block_size)
            return unpadded_data
        except ValueError as e:
            raise ValueError(
                "Decryption failed: Invalid padding. "
                "This usually means the decryption key is incorrect or the data is corrupted."
            )
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Decryption failed: {str(e)}")
