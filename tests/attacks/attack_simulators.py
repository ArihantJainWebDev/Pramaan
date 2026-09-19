import cv2
import numpy as np
import fitz
import io

def simulate_screenshot(pdf_bytes: bytes) -> bytes:
    """Simulates a screenshot by rendering to a lower DPI and re-saving."""
    doc = fitz.open("pdf", pdf_bytes)
    out_doc = fitz.open()
    
    for page in doc:
        # Lower DPI to simulate screen
        pix = page.get_pixmap(dpi=72)
        img_data = pix.tobytes("png")
        
        # Insert back
        new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=img_data)
        
    res = out_doc.write()
    doc.close()
    out_doc.close()
    return res

def simulate_jpeg_compression(pdf_bytes: bytes, quality: int = 50) -> bytes:
    """Simulates saving the document pages as heavy JPEG compression."""
    doc = fitz.open("pdf", pdf_bytes)
    out_doc = fitz.open()
    
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        if pix.n == 4:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
            
        # JPEG compress
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR), encode_param)
        
        # Insert back
        new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=buffer.tobytes())
        
    res = out_doc.write()
    doc.close()
    out_doc.close()
    return res

def simulate_print_scan(pdf_bytes: bytes) -> bytes:
    """Simulates print-scan by adding noise, slight rotation, and re-compression."""
    doc = fitz.open("pdf", pdf_bytes)
    out_doc = fitz.open()
    
    for page in doc:
        pix = page.get_pixmap(dpi=200) # Scanner resolution
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        if pix.n == 4:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
            
        # Add gaussian noise
        row, col, ch = img_np.shape
        mean = 0
        var = 10
        sigma = var ** 0.5
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        noisy = img_np + gauss
        noisy = np.clip(noisy, 0, 255).astype(np.uint8)
        
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(noisy, cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        
        new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=buffer.tobytes())
        
    res = out_doc.write()
    doc.close()
    out_doc.close()
    return res
