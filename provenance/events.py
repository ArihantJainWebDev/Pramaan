import json
import hashlib
from typing import Optional, Any
from pydantic import BaseModel, Field

class BaseEvent(BaseModel):
    """
    Base event model providing deterministic serialization and hashing.
    """
    def serialize_for_signature(self) -> bytes:
        data = self.model_dump(exclude={"signature", "request_id", "event_id", "key_wrap_id"})
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return json_str.encode('utf-8')

    def get_hash(self) -> str:
        return hashlib.sha256(self.serialize_for_signature()).hexdigest()

class DecryptRequestEvent(BaseEvent):
    document_id: str
    recipient_id: str
    session_id: str
    request_nonce: str
    request_timestamp: int
    recipient_certificate_hash: str
    signature: Optional[str] = None # ML-DSA-65 signature hex

class KeyReleaseEvent(BaseEvent):
    request_id: str # derived from DecryptRequestEvent hash
    recipient_id: str
    document_id: str
    key_wrap_id: str
    release_timestamp: int
    previous_event_hash: str # Hash of the DecryptRequestEvent

class DecryptAttestationEvent(BaseEvent):
    document_id: str
    recipient_id: str
    session_id: str
    request_id: str
    fingerprint_id: str
    watermark_version: str
    marked_copy_hash: str
    original_document_hash: str
    decryption_timestamp: int
    signature: Optional[str] = None # ML-DSA-65 signature hex
