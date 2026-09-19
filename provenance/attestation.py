from provenance.events import DecryptAttestationEvent
from crypto.mldsa import sign_message, verify_signature

def sign_attestation(attestation: DecryptAttestationEvent, secret_key: bytes) -> DecryptAttestationEvent:
    """Signs the decryption attestation with the recipient's ML-DSA secret key."""
    payload = attestation.serialize_for_signature()
    sig = sign_message(payload, secret_key)
    attestation.signature = sig.hex()
    return attestation

def verify_attestation(attestation: DecryptAttestationEvent, public_key: bytes) -> bool:
    """Verifies the attestation signature using the recipient's public key."""
    if not attestation.signature:
        return False
    payload = attestation.serialize_for_signature()
    sig_bytes = bytes.fromhex(attestation.signature)
    return verify_signature(payload, sig_bytes, public_key)
