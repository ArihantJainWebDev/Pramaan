import os
import json
from pathlib import Path
from typing import Tuple, Dict, Any

from config.settings import settings

class LocalKeystore:
    def __init__(self, keystore_dir: str = settings.keystore_dir):
        self.keystore_dir = Path(keystore_dir)
        self.keystore_dir.mkdir(parents=True, exist_ok=True)
        
        self.root_ca_dir = self.keystore_dir / "root_ca"
        self.recipients_dir = self.keystore_dir / "recipients"
        
        self.root_ca_dir.mkdir(exist_ok=True)
        self.recipients_dir.mkdir(exist_ok=True)

    def save_root_ca_keys(self, public_key: bytes, secret_key: bytes):
        with open(self.root_ca_dir / "root_mldsa_pub.bin", "wb") as f:
            f.write(public_key)
        # In a real environment, this should be heavily protected and air-gapped
        with open(self.root_ca_dir / "root_mldsa_sec.bin", "wb") as f:
            f.write(secret_key)
            
    def load_root_ca_public_key(self) -> bytes:
        with open(self.root_ca_dir / "root_mldsa_pub.bin", "rb") as f:
            return f.read()

    def load_root_ca_secret_key(self) -> bytes:
        with open(self.root_ca_dir / "root_mldsa_sec.bin", "rb") as f:
            return f.read()

    def save_recipient_keys(self, recipient_id: str, kem_pub: bytes, kem_sec: bytes, dsa_pub: bytes, dsa_sec: bytes):
        rec_dir = self.recipients_dir / recipient_id
        rec_dir.mkdir(exist_ok=True)
        
        with open(rec_dir / "kem_pub.bin", "wb") as f:
            f.write(kem_pub)
        with open(rec_dir / "kem_sec.bin", "wb") as f:
            f.write(kem_sec)
        with open(rec_dir / "dsa_pub.bin", "wb") as f:
            f.write(dsa_pub)
        with open(rec_dir / "dsa_sec.bin", "wb") as f:
            f.write(dsa_sec)
            
    def load_recipient_kem_keys(self, recipient_id: str) -> Tuple[bytes, bytes]:
        rec_dir = self.recipients_dir / recipient_id
        with open(rec_dir / "kem_pub.bin", "rb") as f:
            pub = f.read()
        with open(rec_dir / "kem_sec.bin", "rb") as f:
            sec = f.read()
        return pub, sec

    def load_recipient_dsa_keys(self, recipient_id: str) -> Tuple[bytes, bytes]:
        rec_dir = self.recipients_dir / recipient_id
        with open(rec_dir / "dsa_pub.bin", "rb") as f:
            pub = f.read()
        with open(rec_dir / "dsa_sec.bin", "rb") as f:
            sec = f.read()
        return pub, sec
        
    def save_recipient_certificate(self, recipient_id: str, cert_json: str):
        rec_dir = self.recipients_dir / recipient_id
        rec_dir.mkdir(exist_ok=True)
        with open(rec_dir / "certificate.json", "w") as f:
            f.write(cert_json)
            
    def load_recipient_certificate(self, recipient_id: str) -> str:
        rec_dir = self.recipients_dir / recipient_id
        with open(rec_dir / "certificate.json", "r") as f:
            return f.read()
