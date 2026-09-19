# Architecture

PRAMAAN is built on a backend-first architecture.
- **Backend:** FastAPI (Python 3.12)
- **Cryptography:** liboqs-python (ML-KEM-768, ML-DSA-65), AES-256-GCM.
- **Ledger:** Hyperledger Fabric v3 with SmartBFT.
- **Watermarking:** PyMuPDF, PyWavelets, OpenCV.
- **UI:** Streamlit.

All decryption requests and attestations are signed using ML-DSA-65 and committed to the BFT ledger before keys are released.
