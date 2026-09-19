from provenance.events import DecryptRequestEvent
from crypto.mldsa import sign_message, verify_signature

def sign_decrypt_request(request: DecryptRequestEvent, secret_key: bytes) -> DecryptRequestEvent:
    """Signs the decrypt request with the recipient's ML-DSA secret key."""
    payload = request.serialize_for_signature()
    sig = sign_message(payload, secret_key)
    request.signature = sig.hex()
    return request

def verify_decrypt_request(request: DecryptRequestEvent, public_key: bytes) -> bool:
    """Verifies the decrypt request signature using the recipient's public key."""
    if not request.signature:
        return False
    payload = request.serialize_for_signature()
    sig_bytes = bytes.fromhex(request.signature)
    return verify_signature(payload, sig_bytes, public_key)
