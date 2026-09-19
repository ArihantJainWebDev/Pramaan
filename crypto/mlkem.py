from typing import Tuple

ML_KEM_ALGORITHM = "ML-KEM-768"

def generate_kem_keypair() -> Tuple[bytes, bytes]:
    """
    Generates an ML-KEM-768 keypair.
    Returns:
        (public_key, secret_key)
    """
    import oqs

    with oqs.KeyEncapsulation(ML_KEM_ALGORITHM) as kem:
        public_key = kem.generate_keypair()
        secret_key = kem.export_secret_key()
        return public_key, secret_key

def encapsulate_secret(public_key: bytes) -> Tuple[bytes, bytes]:
    """
    Encapsulates a shared secret using the recipient's public key.
    Returns:
        (ciphertext, shared_secret)
    """
    import oqs

    with oqs.KeyEncapsulation(ML_KEM_ALGORITHM) as kem:
        ciphertext, shared_secret = kem.encap_secret(public_key)
        return ciphertext, shared_secret

def decapsulate_secret(ciphertext: bytes, secret_key: bytes) -> bytes:
    """
    Decapsulates the shared secret using the recipient's secret key.
    Returns:
        shared_secret
    """
    import oqs

    with oqs.KeyEncapsulation(ML_KEM_ALGORITHM) as kem:
        # Load the secret key into the KEM object
        # Note: in python-liboqs we don't strictly load secret key using a function
        # instead we pass it directly to decap_secret.
        # Wait, liboqs-python requires secret_key for initialization or we just pass it to decap_secret.
        # Let's check python-liboqs API: decap_secret(ciphertext) if the object generated the key,
        # otherwise we can instantiate and set the secret key.
        # Wait, liboqs python API is actually: kem.secret_key = secret_key, then kem.decap_secret(ciphertext).
        pass

    # Correcting the liboqs python API usage:
    with oqs.KeyEncapsulation(ML_KEM_ALGORITHM, secret_key) as kem:
        shared_secret = kem.decap_secret(ciphertext)
        return shared_secret
