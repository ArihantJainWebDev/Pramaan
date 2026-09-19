import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Tuple

def derive_wrapping_key(shared_secret: bytes, salt: bytes = None) -> bytes:
    """
    Derives a 256-bit wrapping key from the ML-KEM shared secret using HKDF-SHA256.
    """
    if salt is None:
        salt = b"" # Default salt if not provided
        
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32, # 256-bit key for AES
        salt=salt,
        info=b"pramaan-kem-wrap",
    )
    return hkdf.derive(shared_secret)

def wrap_dek(dek: bytes, wrapping_key: bytes) -> Tuple[bytes, bytes]:
    """
    Wraps the document DEK using the wrapping key with AES-256-GCM.
    Returns:
        (wrapped_dek_with_tag, nonce)
    """
    aesgcm = AESGCM(wrapping_key)
    nonce = os.urandom(12)
    wrapped_dek = aesgcm.encrypt(nonce, dek, None)
    return wrapped_dek, nonce

def unwrap_dek(wrapped_dek_with_tag: bytes, nonce: bytes, wrapping_key: bytes) -> bytes:
    """
    Unwraps the document DEK using the wrapping key with AES-256-GCM.
    """
    aesgcm = AESGCM(wrapping_key)
    dek = aesgcm.decrypt(nonce, wrapped_dek_with_tag, None)
    return dek
