import io
import hashlib
import numpy as np
import pywt
import cv2
import fitz
from typing import Optional, Tuple
from config.settings import settings

def _generate_spread_spectrum_signal(fingerprint_id: str, length: int) -> np.ndarray:
    """Generate a pseudo-random zero-mean sequence based on the fingerprint."""
    h = hashlib.sha256(fingerprint_id.encode()).digest()
    # Seed numpy random with hash for deterministic sequence
    seed = int.from_bytes(h[:4], "little")
    np.random.seed(seed)
    # Generate sequence of -1 and 1
    signal = np.random.choice([-1, 1], size=length)
    return signal

def _embed_dwt(image_np: np.ndarray, fingerprint_id: str, strength: float = settings.watermark_strength) -> np.ndarray:
    """
    Embeds DWT spread-spectrum watermark into a grayscale image representation.
    Returns the watermarked image.
    """
    # Use YCrCb and embed in Y channel for luminance
    ycrcb = cv2.cvtColor(image_np, cv2.COLOR_RGB2YCrCb)
    y_channel = ycrcb[:, :, 0].astype(np.float32)

    # 2D DWT
    coeffs2 = pywt.dwt2(y_channel, 'haar')
    LL, (LH, HL, HH) = coeffs2

    # Embed in HL and LH bands (middle frequencies, more robust)
    flat_HL = HL.flatten()
    flat_LH = LH.flatten()
    
    signal_len = min(len(flat_HL), 4096) # Embed up to 4096 bits
    signal = _generate_spread_spectrum_signal(fingerprint_id, signal_len)
    
    # Additive embedding: v' = v + alpha * v * signal (multiplicative spread spectrum)
    # For simplicity and stability: v' = v + alpha * signal
    
    flat_HL[:signal_len] += strength * signal
    flat_LH[:signal_len] += strength * signal
    
    # Reshape back
    HL = flat_HL.reshape(HL.shape)
    LH = flat_LH.reshape(LH.shape)
    
    # Inverse DWT
    y_watermarked = pywt.idwt2((LL, (LH, HL, HH)), 'haar')
    
    # Clip and reconstruct
    ycrcb[:, :, 0] = np.clip(y_watermarked, 0, 255).astype(np.uint8)
    watermarked_rgb = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
    
    return watermarked_rgb

def embed_dwt_pdf(pdf_bytes: bytes, fingerprint_id: str) -> bytes:
    """
    Renders PDF pages, embeds DWT watermark, and replaces the page with the watermarked image.
    Maintains page dimensions.
    """
    doc = fitz.open("pdf", pdf_bytes)
    out_doc = fitz.open() # New document to hold image pages
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Render at 150 DPI (compromise between quality and speed for prototype)
        pix = page.get_pixmap(dpi=150)
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        # If RGBA, convert to RGB
        if pix.n == 4:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
            
        watermarked_np = _embed_dwt(img_np, fingerprint_id)
        
        # Convert back to bytes for insertion
        is_success, buffer = cv2.imencode(".png", cv2.cvtColor(watermarked_np, cv2.COLOR_RGB2BGR))
        if not is_success:
            continue
            
        # Create a new page in out_doc with exact dimensions
        new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=buffer.tobytes())
        
    out_bytes = out_doc.write()
    doc.close()
    out_doc.close()
    return out_bytes

def _extract_dwt(image_np: np.ndarray, candidate_id: str) -> float:
    """
    Attempts to extract the spread-spectrum watermark for a candidate ID.
    Returns a confidence score (correlation coefficient).
    """
    ycrcb = cv2.cvtColor(image_np, cv2.COLOR_RGB2YCrCb)
    y_channel = ycrcb[:, :, 0].astype(np.float32)

    coeffs2 = pywt.dwt2(y_channel, 'haar')
    LL, (LH, HL, HH) = coeffs2

    flat_HL = HL.flatten()
    flat_LH = LH.flatten()
    
    signal_len = min(len(flat_HL), 4096)
    expected_signal = _generate_spread_spectrum_signal(candidate_id, signal_len)
    
    # Calculate normalized correlation
    corr_HL = np.corrcoef(flat_HL[:signal_len], expected_signal)[0, 1]
    corr_LH = np.corrcoef(flat_LH[:signal_len], expected_signal)[0, 1]
    
    avg_corr = (corr_HL + corr_LH) / 2.0
    return avg_corr

def extract_dwt_pdf(pdf_bytes: bytes, candidate_ids: list[str]) -> Tuple[Optional[str], float]:
    """
    Extracts Layer C watermark and tests against candidate IDs.
    Returns (matched_id, confidence) or (None, 0.0)
    """
    doc = fitz.open("pdf", pdf_bytes)
    
    best_id = None
    best_confidence = 0.0
    
    if len(doc) == 0:
        return None, 0.0
        
    # Test on the first page for speed
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    if pix.n == 4:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
        
    for cid in candidate_ids:
        conf = _extract_dwt(img_np, cid)
        if conf > best_confidence:
            best_confidence = conf
            best_id = cid
            
    doc.close()
    
    if best_confidence > 0.15: # Threshold for detection
        return best_id, best_confidence
        
    return None, best_confidence
