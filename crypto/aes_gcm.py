import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Tuple

def generate_dek() -> bytes:
    """Generates a 256-bit (32 byte) AES DEK."""
    return AESGCM.generate_key(bit_length=256)

def encrypt_document(dek: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
    """
    Encrypts the document using AES-256-GCM.
    Returns:
        (ciphertext, nonce)
        Note: The cryptography library appends the 16-byte authentication tag
        to the end of the ciphertext.
    """
    aesgcm = AESGCM(dek)
    nonce = os.urandom(12) # 96-bit nonce is standard for GCM
    
    # encrypt(nonce, data, associated_data)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, None)
    return ciphertext_with_tag, nonce

def decrypt_document(dek: bytes, nonce: bytes, ciphertext_with_tag: bytes) -> bytes:
    """
    Decrypts the document using AES-256-GCM.
    Raises InvalidTag if authentication fails.
    """
    aesgcm = AESGCM(dek)
    plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    return plaintext
