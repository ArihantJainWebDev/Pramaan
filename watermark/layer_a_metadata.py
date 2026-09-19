import fitz # PyMuPDF
from typing import Optional

def embed_metadata(pdf_bytes: bytes, fingerprint_id: str) -> bytes:
    """
    Embeds the fingerprint ID as a custom metadata property.
    This is Layer A: fast, easily extracted natively, but easily stripped.
    """
    doc = fitz.open("pdf", pdf_bytes)
    
    # Get existing metadata
    meta = doc.metadata
    
    # Inject custom locator (using a subtle naming to avoid immediate suspicion, 
    # though it's security-through-obscurity on this layer alone)
    meta["trapped"] = fingerprint_id # often used for print trapping, here repurposed
    meta["author"] = meta.get("author", "") # touch to force update
    
    doc.set_metadata(meta)
    
    # Save to bytes
    out_bytes = doc.write()
    doc.close()
    return out_bytes

def extract_metadata(pdf_bytes: bytes) -> Optional[str]:
    """
    Extracts the fingerprint ID from metadata if present.
    """
    try:
        doc = fitz.open("pdf", pdf_bytes)
        meta = doc.metadata
        doc.close()
        return meta.get("trapped")
    except Exception:
        return None
