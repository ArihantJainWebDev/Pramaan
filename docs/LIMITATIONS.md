# Limitations

This prototype has explicit boundaries:
1. **Endpoint Compromise:** We do not claim full endpoint security. If malware captures the document before watermarking, attribution may fail.
2. **OCR/Retyping:** Semantic reconstruction (retyping the text into a new document) destroys the visual and structural watermarks.
3. **Collusion:** Multi-recipient collusion (averaging copies) is not mitigated in this MVP. Future extension: Tardos-style fingerprint codes.
4. **Physical Leakage Identity:** The system attributes a leak to a specific *recipient decryption session*. It cannot prove which human physically held the camera or distributed it.
