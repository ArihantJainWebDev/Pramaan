import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "DEBUG"

    # Data paths
    keystore_dir: str = "./data/keystore"
    db_path: str = "./data/pramaan.sqlite"
    
    # Watermarking
    watermark_strength: int = 10
    watermark_version: str = "1.0"
    
    # Fabric
    fabric_mspid: str = "Org1MSP"
    fabric_cert_path: str = "./fabric/network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp/signcerts/cert.pem"
    fabric_key_path: str = "./fabric/network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp/keystore/"
    fabric_tls_cert_path: str = "./fabric/network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"
    fabric_peer_endpoint: str = "localhost:7051"
    fabric_channel_name: str = "pramaan-channel"
    fabric_chaincode_name: str = "provenance"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.keystore_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)
