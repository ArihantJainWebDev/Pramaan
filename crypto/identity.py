import json
import time
import hashlib
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from crypto.mldsa import sign_message, verify_signature

class RecipientIdentity(BaseModel):
    recipient_id: str
    display_name: str
    organization: str
    role: str
    ml_kem_public_key: str  # hex encoded
    ml_dsa_public_key: str  # hex encoded
    certificate_serial: str
    issued_at: int
    expires_at: int
    issuer: str
    signature: Optional[str] = None # hex encoded signature by root CA

    def serialize_for_signature(self) -> bytes:
        """
        Deterministic serialization for signing.
        Excludes the signature field.
        """
        data = self.model_dump(exclude={"signature"})
        # Sort keys to ensure deterministic JSON
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return json_str.encode('utf-8')

    def get_hash(self) -> str:
        """
        Returns SHA-256 hash of the serialized payload.
        """
        return hashlib.sha256(self.serialize_for_signature()).hexdigest()

def sign_certificate(cert: RecipientIdentity, root_secret_key: bytes) -> RecipientIdentity:
    """
    Signs the recipient identity using the Root CA's ML-DSA secret key.
    """
    payload = cert.serialize_for_signature()
    sig = sign_message(payload, root_secret_key)
    cert.signature = sig.hex()
    return cert

def verify_certificate(cert: RecipientIdentity, root_public_key: bytes) -> bool:
    """
    Verifies the certificate signature using the Root CA's public key.
    """
    if not cert.signature:
        return False
    payload = cert.serialize_for_signature()
    sig_bytes = bytes.fromhex(cert.signature)
    return verify_signature(payload, sig_bytes, root_public_key)

def generate_certificate_serial() -> str:
    """Generates a random serial number for the certificate."""
    import uuid
    return str(uuid.uuid4())
