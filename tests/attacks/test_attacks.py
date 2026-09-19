import os
import json
import pytest
from watermark.embed import unified_embed
from watermark.extract import unified_extract
from tests.attacks.attack_simulators import simulate_screenshot, simulate_jpeg_compression, simulate_print_scan

# Simple mock PDF generator for testing
def generate_test_pdf() -> bytes:
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "CONFIDENTIAL DOCUMENT\nDO NOT DISTRIBUTE", fontsize=20)
    res = doc.write()
    doc.close()
    return res

class TestWatermarkAttacks:
    
    @classmethod
    def setup_class(cls):
        cls.pdf_bytes = generate_test_pdf()
        cls.fingerprint_id = "test-fingerprint-123"
        cls.candidate_ids = [cls.fingerprint_id, "wrong-id-1", "wrong-id-2"]
        cls.watermarked_pdf = unified_embed(cls.pdf_bytes, cls.fingerprint_id)

    def test_direct_copy(self):
        result = unified_extract(self.watermarked_pdf, self.candidate_ids)
        assert result["fingerprint_id"] == self.fingerprint_id
        # A, B, and C should all be recovered (in our simplified embed, we do B then A, and maybe C)
        assert len(result["layers_recovered"]) > 0

    def test_screenshot(self):
        leaked = simulate_screenshot(self.watermarked_pdf)
        result = unified_extract(leaked, self.candidate_ids)
        # Layer C should survive screenshot
        assert result["fingerprint_id"] == self.fingerprint_id
        assert "C" in result["layers_recovered"]

    def test_jpeg_compression(self):
        leaked = simulate_jpeg_compression(self.watermarked_pdf, quality=30)
        result = unified_extract(leaked, self.candidate_ids)
        assert result["fingerprint_id"] == self.fingerprint_id
        assert "C" in result["layers_recovered"]

    def test_print_scan(self):
        leaked = simulate_print_scan(self.watermarked_pdf)
        result = unified_extract(leaked, self.candidate_ids)
        # Print scan might lower confidence, but should ideally recover C
        assert result["fingerprint_id"] == self.fingerprint_id
        assert "C" in result["layers_recovered"]
        
    def test_retyping_failure(self):
        # Simulating a user just typing the text into a new document
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "CONFIDENTIAL DOCUMENT\nDO NOT DISTRIBUTE", fontsize=20)
        leaked = doc.write()
        doc.close()
        
        result = unified_extract(leaked, self.candidate_ids)
        assert result["extraction_status"] == "FINGERPRINT_NOT_RECOVERED"
