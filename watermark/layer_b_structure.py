import re
import hashlib
import struct
import fitz
from typing import Optional

def _derive_shifts(fingerprint_id: str, length: int) -> list:
    """Derive deterministic subtle shifts based on the fingerprint ID."""
    h = hashlib.sha256(fingerprint_id.encode()).digest()
    shifts = []
    for i in range(length):
        # use bits of hash to decide a shift: +0.01 or -0.01
        bit = (h[i % 32] >> (i % 8)) & 1
        shifts.append(0.01 if bit else -0.01)
    return shifts

def embed_structure(pdf_bytes: bytes, fingerprint_id: str) -> bytes:
    """
    Layer B: Structural Watermark.
    Modifies TJ-array / glyph-spacing subtly in the PDF content streams.
    """
    doc = fitz.open("pdf", pdf_bytes)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        xrefs = page.get_contents()
        
        for xref in xrefs:
            stream = doc.xref_stream(xref)
            if not stream:
                continue
                
            # A very simplistic heuristic: find 'Td' (text position) or 'Tw' (word spacing) 
            # and append a deterministic tiny word spacing 'Tw' before text shows.
            # Real TJ array manipulation is complex, so we inject Tw (word spacing)
            
            shifts = _derive_shifts(fingerprint_id + str(page_num), 10)
            
            # We look for BT (Begin Text) and inject a Tw operator
            # This is a prototype approximation of glyph-spacing perturbation.
            
            new_stream = bytearray()
            parts = stream.split(b"BT\n")
            
            new_stream.extend(parts[0])
            for i, part in enumerate(parts[1:]):
                shift = shifts[i % len(shifts)]
                # Add BT, then our tiny word spacing shift, then the rest
                new_stream.extend(b"BT\n")
                new_stream.extend(f"{shift:.3f} Tw\n".encode())
                new_stream.extend(part)
                
            doc.update_stream(xref, bytes(new_stream))
            
    out_bytes = doc.write()
    doc.close()
    return out_bytes

def extract_structure(pdf_bytes: bytes) -> Optional[str]:
    """
    Extracts Layer B structural watermark.
    Because we used a deterministic hash for embedding, blind extraction requires 
    knowing the fingerprint ID to verify, or we could encode bits directly.
    For this prototype, if it's blind, we should extract the injected Tw values.
    """
    doc = fitz.open("pdf", pdf_bytes)
    
    extracted_bits = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        xrefs = page.get_contents()
        
        for xref in xrefs:
            stream = doc.xref_stream(xref)
            if not stream:
                continue
                
            # Find all injected Tw values
            matches = re.findall(rb"([+-]?0\.[0-9]{3}) Tw", stream)
            for m in matches:
                val = float(m)
                if val > 0:
                    extracted_bits.append(1)
                elif val < 0:
                    extracted_bits.append(0)
                    
    doc.close()
    
    # In a full implementation, these bits would decode to the fingerprint ID.
    # For prototype simulation of recovery, we return a hash of the bits if enough are found.
    # We will simulate the lookup in the forensic layer.
    if len(extracted_bits) > 10:
        # Reconstruct fingerprint_id hash from bits (mocked for prototype)
        # Real implementation would use error correction (BCH/Reed-Solomon)
        return "structural_recovery_simulated" 
        
    return None
