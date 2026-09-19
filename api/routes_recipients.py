from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import time
from crypto.identity import RecipientIdentity, sign_certificate
from crypto.mldsa import generate_dsa_keypair
from crypto.mlkem import generate_kem_keypair
from crypto.keystore import LocalKeystore

router = APIRouter(prefix="/recipients", tags=["Recipients"])

class RegisterRequest(BaseModel):
    display_name: str
    organization: str
    role: str

class RegisterResponse(BaseModel):
    recipient_id: str
    certificate_serial: str
    message: str

@router.post("/register", response_model=RegisterResponse)
async def register_recipient(req: RegisterRequest):
    recipient_id = str(uuid.uuid4())
    
    # Generate PQC keys
    kem_pub, kem_sec = generate_kem_keypair()
    dsa_pub, dsa_sec = generate_dsa_keypair()
    
    keystore = LocalKeystore()
    
    # Ensure Root CA exists
    try:
        root_sec = keystore.load_root_ca_secret_key()
        root_pub = keystore.load_root_ca_public_key()
    except Exception:
        root_pub, root_sec = generate_dsa_keypair()
        keystore.save_root_ca_keys(root_pub, root_sec)
        
    cert = RecipientIdentity(
        recipient_id=recipient_id,
        display_name=req.display_name,
        organization=req.organization,
        role=req.role,
        ml_kem_public_key=kem_pub.hex(),
        ml_dsa_public_key=dsa_pub.hex(),
        certificate_serial=str(uuid.uuid4()),
        issued_at=int(time.time()),
        expires_at=int(time.time()) + 31536000,
        issuer="PRAMAAN ROOT CA"
    )
    
    signed_cert = sign_certificate(cert, root_sec)
    
    keystore.save_recipient_keys(recipient_id, kem_pub, kem_sec, dsa_pub, dsa_sec)
    keystore.save_recipient_certificate(recipient_id, signed_cert.model_dump_json())
    
    return RegisterResponse(
        recipient_id=recipient_id,
        certificate_serial=cert.certificate_serial,
        message="Recipient registered with PQC identities."
    )
