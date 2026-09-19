from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import hashlib
from crypto.aes_gcm import generate_dek, encrypt_document
from pydantic import BaseModel

router = APIRouter(prefix="/documents", tags=["Documents"])

# In-memory mock database for prototype (replace with SQLite if needed)
DOCUMENTS_DB = {}

class EncryptResponse(BaseModel):
    document_id: str
    document_hash: str
    message: str

@router.post("/encrypt", response_model=EncryptResponse)
async def encrypt_doc(file: UploadFile = File(...)):
    contents = await file.read()
    doc_hash = hashlib.sha256(contents).hexdigest()
    
    dek = generate_dek()
    ciphertext, nonce = encrypt_document(dek, contents)
    
    doc_id = str(uuid.uuid4())
    
    DOCUMENTS_DB[doc_id] = {
        "ciphertext": ciphertext,
        "nonce": nonce,
        "dek": dek, # Kept server side for the encrypt-once flow before wrapping
        "hash": doc_hash
    }
    
    return EncryptResponse(
        document_id=doc_id,
        document_hash=doc_hash,
        message="Document encrypted successfully once using AES-256-GCM."
    )
