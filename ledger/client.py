import httpx
import json
from config.settings import settings

class LedgerClient:
    """
    Python client that communicates with the small Node.js/Go Fabric Gateway adapter.
    Because there is no official Python SDK for Fabric v3 Gateway, we use an HTTP adapter.
    """
    def __init__(self):
        # We assume the gateway adapter is running locally on port 3000
        self.adapter_url = "http://localhost:3000"

    async def commit_decrypt_request(self, event_id: str, document_id: str, recipient_id: str, timestamp: int, payload_str: str):
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.adapter_url}/transactions/CreateDecryptRequest", json={
                "event_id": event_id,
                "document_id": document_id,
                "recipient_id": recipient_id,
                "timestamp": str(timestamp),
                "payload_str": payload_str
            })
            resp.raise_for_status()

    async def commit_attestation(self, event_id: str, document_id: str, recipient_id: str, fingerprint_id: str, timestamp: int, payload_str: str):
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.adapter_url}/transactions/CommitDecryptAttestation", json={
                "event_id": event_id,
                "document_id": document_id,
                "recipient_id": recipient_id,
                "fingerprint_id": fingerprint_id,
                "timestamp": str(timestamp),
                "payload_str": payload_str
            })
            resp.raise_for_status()

    async def get_event_by_fingerprint(self, fingerprint_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.adapter_url}/queries/GetEventByFingerprint/{fingerprint_id}")
            if resp.status_code == 404:
                raise Exception(f"No event found for fingerprint {fingerprint_id}")
            resp.raise_for_status()
            return resp.json()
