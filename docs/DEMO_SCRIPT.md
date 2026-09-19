# Demo Script (5 minutes)

1. **Sender:** Upload `CONFIDENTIAL_REPORT.pdf`. Click 'Encrypt Once'. Show that AES-256-GCM ciphertext is generated.
2. **Recipient:** Register 3 recipients (Alice, Bob, Charlie) with ML-KEM and ML-DSA keys.
3. **Distribution:** Show that all three access the exact same encrypted blob.
4. **Decryption (Alice):** Alice signs a `DECRYPT_REQUEST`. It commits to the Fabric Ledger. Key is wrapped and released. Alice decrypts and applies 3-layer watermark. Signs `DECRYPT_ATTESTATION`.
5. **Leakage:** Export Bob's fingerprinted PDF.
6. **Forensics:** Upload leaked PDF to Investigator tab. Run extraction. 
7. **Verification:** System extracts DWT payload, queries Fabric, verifies ML-DSA signature, and attributes the leak to Bob's session.
8. **Attack Demo:** Run the "Attack Lab" OCR/Retyping test to show a technically honest failure where attribution is lost, proving the system understands its limits.
