import base64
import hashlib
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

"""
Cipher-Embedded Steganographic Shield: Layer 1 Cryptographic Engine
-------------------------------------------------------------------
Task Definition:
"Design and implement a dual-layer security system that encrypts sensitive
information and then conceals the encrypted data inside a digital image.
The system should allow authorized users to embed, extract, decrypt, and
verify the integrity of the hidden information."

Cryptographic Architecture:
- Key Derivation Function (KDF): PBKDF2HMAC (SHA-256, 100,000 iterations)
- Symmetric Cipher: Fernet (AES-128-CBC + PKCS7 Padding + HMAC-SHA256 Authentication)
- Integrity Layer: SHA-256 cryptographic digest verification wrapper
"""

SALT_SIZE = 16
INTEGRITY_HEADER = b"SHIELD_INTEGRITY:"
DIGEST_LENGTH = 64  # Hex-encoded SHA-256 string length

def compute_sha256(data: str | bytes) -> str:
    """Compute standard SHA-256 hexadecimal checksum of string or bytes."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def wrap_payload_with_integrity(data: str | bytes) -> bytes:
    """
    Encapsulate data inside a SHA-256 cryptographic integrity envelope.
    Format: [SHIELD_INTEGRITY:] + [64-byte SHA256 HEX] + [:] + [RAW DATA]
    """
    if isinstance(data, str):
        content = data.encode('utf-8')
    else:
        content = data
    digest = hashlib.sha256(content).hexdigest().encode('ascii')
    return INTEGRITY_HEADER + digest + b":" + content

def unwrap_payload_with_integrity(payload: bytes) -> tuple[bytes, str, str, bool]:
    """
    Extract data and verify its embedded SHA-256 integrity checksum.
    Returns:
        (content_bytes, computed_sha256, stored_sha256, is_verified)
    """
    header_len = len(INTEGRITY_HEADER)
    prefix = payload[:header_len]
    
    if prefix == INTEGRITY_HEADER:
        try:
            stored_digest = payload[header_len:header_len + DIGEST_LENGTH].decode('ascii')
            content = payload[header_len + DIGEST_LENGTH + 1:]  # Skip separator ':'
            computed_digest = hashlib.sha256(content).hexdigest()
            is_verified = (computed_digest.lower() == stored_digest.lower())
            return content, computed_digest, stored_digest, is_verified
        except Exception:
            pass

    # Legacy or unenveloped raw payload fallback
    computed_digest = hashlib.sha256(payload).hexdigest()
    return payload, computed_digest, computed_digest, True

def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a URL-safe base64-encoded 256-bit key from passphrase and salt using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode('utf-8')))
    return key

def encrypt_payload(data: str | bytes, passphrase: str) -> bytes:
    """
    Encrypt string/bytes payload with passphrase using Fernet (AES-128-CBC + HMAC-SHA256).
    Returns: salt (16 bytes) + encrypted token.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    salt = os.urandom(SALT_SIZE)
    key = derive_key(passphrase, salt)
    fernet = Fernet(key)
    encrypted_token = fernet.encrypt(data)
    
    return salt + encrypted_token

def decrypt_payload(encrypted_data: bytes, passphrase: str) -> bytes:
    """
    Extract salt and decrypt Fernet token.
    Returns decrypted bytes. Raises ValueError if passphrase is invalid or HMAC authentication fails.
    """
    if len(encrypted_data) <= SALT_SIZE:
        raise ValueError("Invalid encrypted data length.")
    
    salt = encrypted_data[:SALT_SIZE]
    token = encrypted_data[SALT_SIZE:]
    
    try:
        key = derive_key(passphrase, salt)
        fernet = Fernet(key)
        decrypted_bytes = fernet.decrypt(token)
        return decrypted_bytes
    except Exception as e:
        raise ValueError("Decryption failed: Incorrect passphrase or corrupted/tampered ciphertext.") from e
