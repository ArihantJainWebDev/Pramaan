import hashlib
import json
from typing import Dict, Any, List

from watermark.extract import unified_extract
from ledger.client import LedgerClient
from crypto.keystore import LocalKeystore
from crypto.identity import RecipientIdentity, verify_certificate
from provenance.events import DecryptAttestationEvent
from provenance.attestation import verify_attestation

async def verify_leak(pdf_bytes: bytes, candidate_ids: List[str]) -> Dict[str, Any]:
    """
    Forensic verification engine.
    """
    report = {
        "status": "UNVERIFIED",
        "document_id": None,
        "fingerprint_id": None,
        "recipient_id": None,
        "session_id": None,
        "event_id": None,
        "signature_valid": False,
        "ledger_inclusion_valid": False,
        "fingerprint_confidence": 0.0,
        "layers_recovered": [],
        "limitations": [
            "Cannot prove which human physically leaked the document.",
            "Attribution is limited to the recipient and session."
        ],
        "leaked_file_hash": hashlib.sha256(pdf_bytes).hexdigest()
    }

    # 1-5. Extract watermark
    ext_results = unified_extract(pdf_bytes, candidate_ids)
    
    report["layers_recovered"] = ext_results["layers_recovered"]
    report["fingerprint_confidence"] = ext_results["confidence"]
    fingerprint_id = ext_results["fingerprint_id"]
    
    if not fingerprint_id:
        return report
        
    report["fingerprint_id"] = fingerprint_id
    
    # 6. Query ledger
    try:
        ledger = LedgerClient()
        ledger_event_data = await ledger.get_event_by_fingerprint(fingerprint_id)
        report["ledger_inclusion_valid"] = True
    except Exception as e:
        report["limitations"].append(f"Ledger error: {str(e)}")
        return report

    # 7. Retrieve signed event
    payload_str = ledger_event_data.get("payload_str", "{}")
    event_dict = json.loads(payload_str)
    
    try:
        attestation = DecryptAttestationEvent(**event_dict)
    except Exception:
        report["limitations"].append("Invalid event format in ledger.")
        return report
        
    report["document_id"] = attestation.document_id
    report["recipient_id"] = attestation.recipient_id
    report["session_id"] = attestation.session_id
    report["event_id"] = ledger_event_data.get("event_id")
    
    # 8. Verify recipient certificate
    keystore = LocalKeystore()
    try:
        cert_str = keystore.load_recipient_certificate(attestation.recipient_id)
        cert = RecipientIdentity.model_validate_json(cert_str)
        root_pub = keystore.load_root_ca_public_key()
        if not verify_certificate(cert, root_pub):
            report["limitations"].append("Recipient certificate invalid.")
            return report
    except Exception:
        report["limitations"].append("Could not load or verify recipient certificate.")
        return report
        
    # 9. Verify ML-DSA signature
    try:
        recipient_pub = bytes.fromhex(cert.ml_dsa_public_key)
        sig_valid = verify_attestation(attestation, recipient_pub)
        report["signature_valid"] = sig_valid
    except Exception:
        sig_valid = False
        
    if sig_valid and report["ledger_inclusion_valid"]:
        report["status"] = "VERIFIED"
    elif sig_valid:
        report["status"] = "AMBIGUOUS"
        
    return report
