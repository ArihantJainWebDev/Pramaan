from fastapi import APIRouter, UploadFile, File
from forensic.verifier import verify_leak
from crypto.keystore import LocalKeystore
import os

router = APIRouter(prefix="/forensics", tags=["Forensics"])

@router.post("/verify")
async def verify_leaked_document(file: UploadFile = File(...)):
    contents = await file.read()
    
    # Gather candidate IDs
    keystore = LocalKeystore()
    candidate_ids = []
    if keystore.recipients_dir.exists():
        candidate_ids = os.listdir(keystore.recipients_dir)
        
    # In a real system, fingerprint_id is derived, or we test candidate recipients
    # Since our Layer B extract simulated the ID, we pass candidate_ids as well as arbitrary hashes
    
    # Actually, the unified_extract uses candidate_ids to check Layer A and C
    # But wait, candidate_ids should be a list of *fingerprint_ids*, not recipient_ids.
    # We will simulate this by checking all events from the ledger, but for this prototype,
    # let's assume candidate_ids are recipient_ids + session_ids hashes.
    # To keep it simple, verifier will just test some known candidates or the verifier itself 
    # queries the local DB for generated fingerprint IDs.
    
    # Mocking a list of all known fingerprint IDs for the prototype:
    # In practice, this would be a local index mapping or we extract directly.
    # For now, we will just use a generic list or rely on extraction directly.
    known_fingerprints = ["test-fingerprint-123"] # Placeholder
    
    report = await verify_leak(contents, known_fingerprints)
    
    return report
