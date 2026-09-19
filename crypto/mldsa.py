from typing import Tuple

ML_DSA_ALGORITHM = "ML-DSA-65"

def generate_dsa_keypair() -> Tuple[bytes, bytes]:
    """
    Generates an ML-DSA-65 keypair.
    Returns:
        (public_key, secret_key)
    """
    import oqs

    with oqs.Signature(ML_DSA_ALGORITHM) as signer:
        public_key = signer.generate_keypair()
        secret_key = signer.export_secret_key()
        return public_key, secret_key

def sign_message(message: bytes, secret_key: bytes) -> bytes:
    """
    Signs a message using the secret key.
    """
    import oqs

    with oqs.Signature(ML_DSA_ALGORITHM, secret_key) as signer:
        signature = signer.sign(message)
        return signature

def verify_signature(message: bytes, signature: bytes, public_key: bytes) -> bool:
    """
    Verifies a signature using the public key.
    """
    import oqs

    with oqs.Signature(ML_DSA_ALGORITHM) as verifier:
        return verifier.verify(message, signature, public_key)
