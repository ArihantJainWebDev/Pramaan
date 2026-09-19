<div align="center">

# PRAMAAN (प्रमाण)
### Cryptographic Attribution and Immutable Decryption Provenance for Multi-Recipient Encrypted Document Distribution

[![Smart India Hackathon](https://img.shields.io/badge/SIH-Prototype-blue.svg?style=for-the-badge)](https://sih.gov.in)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Hyperledger Fabric](https://img.shields.io/badge/Hyperledger%20Fabric-v3.0%20(SmartBFT)-2F3134?style=for-the-badge&logo=hyperledger&logoColor=white)](https://www.hyperledger.org/projects/fabric)
[![PQC NIST Standards](https://img.shields.io/badge/PQC-ML--KEM--768%20%7C%20ML--DSA--65-success?style=for-the-badge)](https://csrc.nist.gov/projects/post-quantum-cryptography)

---

**A zero-trust, post-quantum secure, offline-capable document distribution and leak forensic attribution platform.**

</div>

---

## 📌 Executive Summary

Organizations handling sensitive intelligence, board resolutions, and classified materials face an asymmetry: **documents must be distributed to multiple parties to be useful, but once distributed, any recipient can leak them anonymously.** Traditional watermarking is easily stripped, and centralized audit logs are vulnerable to administrative tampering or denial of receipt.

**PRAMAAN** solves this challenge through a mathematically grounded, verifiable pipeline:
1. **Encrypt Once, Distribute Anywhere:** Uses `AES-256-GCM` with post-quantum `ML-KEM-768` key-wrapping so every recipient accesses the identical encrypted ciphertext.
2. **Cryptographic Proof of Decryption:** Decryption keys are released only after the recipient signs an `ML-DSA-65` digital request committed to an offline **Hyperledger Fabric v3 SmartBFT** permissioned ledger.
3. **Defense-in-Depth Forensic Fingerprinting:** An imperceptible, 3-layer forensic watermark (Metadata, Glyph Spacing, and 2D-DWT Spread-Spectrum) binds the rendered document to the specific recipient and session ID.
4. **Leak Attribution:** When a leaked document is recovered, the forensic engine extracts the embedded watermark locator, queries the immutable ledger, verifies the post-quantum signature, and cryptographically attributes the artifact to the exact decryption event.

---

## 🏛️ System Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │            Streamlit Control UI              │
                    │  (Dashboard | Sender | Recipient | Forensics) │
                    └──────────────────────┬───────────────────────┘
                                           │ HTTP / REST
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │             FastAPI Backend API              │
                    └───────┬──────────────┬──────────────┬────────┘
                            │              │              │
           ┌────────────────┘              │              └────────────────┐
           ▼                               ▼                               ▼
┌─────────────────────┐        ┌─────────────────────┐        ┌─────────────────────┐
│  PQC Crypto Engine  │        │  Watermarking Engine│        │  Fabric Adapter API │
│  - AES-256-GCM      │        │  - Layer A: Metadata│        │  (Node.js Gateway)  │
│  - ML-KEM-768       │        │  - Layer B: Spacing │        └──────────┬──────────┘
│  - ML-DSA-65        │        │  - Layer C: 2D-DWT  │                   │ gRPC (TLS)
│  - Local Keystore   │        └─────────────────────┘                   ▼
└─────────────────────┘                                       ┌─────────────────────┐
                                                              │ Hyperledger Fabric  │
                                                              │  v3.0 SmartBFT      │
                                                              │  (4 Orderers, f=1)  │
                                                              └─────────────────────┘
```

---

## 🔐 Core Technological Innovations

| Layer | Technology | Security Function |
| :--- | :--- | :--- |
| **Symmetric Encryption** | `AES-256-GCM` | Document DEK encryption; ensures authenticated integrity and reuse of one ciphertext. |
| **PQC Key Encapsulation**| `ML-KEM-768` (liboqs) | NIST FIPS 203 quantum-resistant key-wrap for distributing the AES DEK. |
| **PQC Digital Signatures**| `ML-DSA-65` (liboqs) | NIST FIPS 204 quantum-resistant request and attestation non-repudiation. |
| **Decentralized Ledger** | Hyperledger Fabric v3 | SmartBFT (BFT 3f+1 configuration, f=1 target) for tamper-evident provenance. |
| **Watermark Layer A** | PDF Metadata / Trapped Object | Fast identification in direct digital copies. |
| **Watermark Layer B** | Text Justification (`Tw` Array) | Subtle structural glyph-spacing perturbations surviving basic sanitization. |
| **Watermark Layer C** | 2D-DWT Spread-Spectrum (Haar) | Sub-band frequency domain embedding in luminance channel; survives screenshots, JPEG compression, and print-scan degradation. |

---

## 📂 Repository Structure

```
pramaan/
├── api/                      # FastAPI REST application routes
│   ├── main.py               # API application gateway & health endpoints
│   ├── routes_documents.py   # Document upload and encrypt-once endpoints
│   ├── routes_recipients.py  # Recipient registration & PQC key generation
│   └── routes_forensics.py   # Leak verification and attribution endpoint
├── app.py                    # Multi-role Streamlit UI (Dashboard, Sender, Recipient, Investigator)
├── config/                   # Configuration schemas and environment settings
├── core/                     # Core hashing and deterministic serialization utilities
├── crypto/                   # Cryptographic engine
│   ├── aes_gcm.py            # AES-256-GCM symmetric encryption
│   ├── mlkem.py              # ML-KEM-768 key encapsulation (liboqs)
│   ├── mldsa.py              # ML-DSA-65 digital signature signing/verification
│   ├── kdf.py                # HKDF-SHA256 key derivation and key-wrapping
│   ├── identity.py           # Offline Root CA and recipient certificate model
│   └── keystore.py           # Secure local file-system keystore
├── docs/                     # Technical architecture and jury evaluation docs
│   ├── ARCHITECTURE.md       # Deep architectural breakdown
│   ├── THREAT_MODEL.md       # STRIDE-aligned threat model
│   ├── LIMITATIONS.md        # Explicit, honest boundary definitions
│   └── DEMO_SCRIPT.md        # 5-minute live hackathon presentation flow
├── fabric/                   # Hyperledger Fabric infrastructure
│   ├── chaincode/            # Go chaincode for immutable event logs
│   └── scripts/              # SmartBFT bootstrap scripts
├── fabric_adapter/           # Microservice bridge for Fabric v3 Gateway
│   ├── package.json          # Node.js dependencies (@hyperledger/fabric-gateway)
│   └── server.js             # HTTP REST gateway adapter
├── forensic/                 # Forensic verification and attribution engine
│   └── verifier.py           # Cross-layer forensic extractor and signature checker
├── provenance/               # Lifecycle event definitions
│   ├── events.py             # DECRYPT_REQUEST, KEY_RELEASE, DECRYPT_ATTESTATION
│   ├── request.py            # Request signature signing and verification
│   └── attestation.py        # Attestation signature signing and verification
├── tests/                    # Automated testing suite
│   ├── unit/                 # Unit tests for crypto, identity, and events
│   └── attacks/              # Attack Resilience Lab (Screenshot, JPEG, Print-Scan)
├── docker-compose.yml        # Multi-container orchestration
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Setup & Installation Guide

This project is built for **Windows with WSL2 / Docker Desktop**, designed to run **completely air-gapped and offline** without external cloud dependencies.

### Prerequisites
- **Windows 10 / 11** with PowerShell 5.1+
- **Docker Desktop** (running and set to Linux containers)
- **WSL2** with Ubuntu installed (`wsl --install -d Ubuntu`)
- **Python 3.12+**
- **Node.js 18+** (inside WSL2 for the Fabric Gateway adapter)

---

### Phase 1: Start Hyperledger Fabric SmartBFT (in WSL2 / Ubuntu)

Open your **Ubuntu Terminal**:

```bash
# 1. Navigate to the repository directory
cd /mnt/c/Users/agraw/Music/PS02/pramaan

# 2. Run the automated Fabric setup script
chmod +x fabric/scripts/setup_fabric.sh
bash fabric/scripts/setup_fabric.sh
```
*This downloads the Fabric 3.0 binaries, boots 4 SmartBFT ordering nodes and peer containers, creates `pramaan-channel`, and deploys the `provenance` chaincode.*

---

### Phase 2: Start the Fabric Gateway Adapter (in WSL2 / Ubuntu)

In the Ubuntu Terminal:

```bash
cd /mnt/c/Users/agraw/Music/PS02/pramaan/fabric_adapter

# Install dependencies (using --no-bin-links for NTFS mount compatibility)
npm install --no-bin-links

# Start the adapter server (runs on port 3000)
npm start
```
You will see: `Fabric Gateway Adapter running on port 3000`.

---

### Phase 3: Setup Python Environment & Backend (in Windows PowerShell)

Open **Windows PowerShell**:

```powershell
# 1. Navigate to the project root
cd C:\Users\agraw\Music\PS02\pramaan

# 2. Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install Python requirements
pip install -r requirements.txt

# 4. Start the FastAPI backend
uvicorn api.main:app --port 8000
```
Backend API will be live at `http://127.0.0.1:8000`.

---

### Phase 4: Launch the Streamlit Dashboard (in a second Windows PowerShell)

Open a **new Windows PowerShell window**:

```powershell
cd C:\Users\agraw\Music\PS02\pramaan
.\venv\Scripts\Activate.ps1

# Start the user interface
streamlit run app.py
```
Your browser will automatically open `http://localhost:8501`.

---

## 🧪 Verification & Attack Resilience Lab

To run the automated suite evaluating watermark survival across simulated real-world adversarial attacks:

```powershell
# In Windows PowerShell with venv activated:
pytest tests/attacks/test_attacks.py -v
```

### Attack Resilience Matrix (Measured Results)

| Attack Scenario | Simulation Model | Layer A (Metadata) | Layer B (Structural) | Layer C (2D-DWT) | Forensic Attribution Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Direct PDF Copy** | Binary duplication | ✅ Survived | ✅ Survived | ✅ Survived | **100% Attributed** |
| **Metadata Stripping** | PDF optimization / sanitization | ❌ Destroyed | ✅ Survived | ✅ Survived | **100% Attributed** |
| **Screenshot Capture** | Rasterization to 72 DPI | ❌ Destroyed | ❌ Destroyed | ✅ Survived | **Attributed via Layer C** |
| **JPEG Re-compression**| Quality factor Q=30 degradation | ❌ Destroyed | ❌ Destroyed | ✅ Survived | **Attributed via Layer C** |
| **Print-Scan Simulation**| Gaussian noise + scanner blur | ❌ Destroyed | ❌ Destroyed | ✅ Survived | **Attributed via Layer C** |
| **Text Retyping / OCR** | Manual retyping of content | ❌ Destroyed | ❌ Destroyed | ❌ Destroyed | **Known Limitation (Honest Fail)** |

---

## 🎯 5-Minute Jury Demonstration Script

1. **Sender Encryption:** Under the **Sender Tab**, upload a confidential PDF and click **"Encrypt Once"**. Note the unique document hash and AES-256 ciphertext.
2. **Multi-Recipient Distribution:** Notice that Recipient A (Alice) and Recipient B (Bob) receive the identical ciphertext.
3. **Decryption & Attestation:** Recipient B requests decryption. The recipient signs `DECRYPT_REQUEST` with `ML-DSA-65`. The key-wrap is released, the document is decrypted, and the 3-layer watermark is embedded. B's signed `DECRYPT_ATTESTATION` is committed to Fabric.
4. **Intentional Leak Simulation:** Export Recipient B's watermarked PDF and save it as `leaked_report.pdf`.
5. **Investigator Verification:** Under the **Investigator Tab**, upload `leaked_report.pdf`. Click **"Extract Fingerprint & Verify"**.
6. **Immutable Proof:** The system extracts the watermark locator, queries the SmartBFT ledger, verifies Bob's digital signature, and displays:
   - **Attribution:** Recipient Bob (`RECIPIENT_ID: ...`)
   - **Session ID:** `SESSION_...`
   - **Ledger Inclusion:** `VERIFIED ON SMARTBFT`
   - **PQC Signature Status:** `VALID (ML-DSA-65)`
7. **Honest Boundary Demonstration:** In the **Attack Lab**, run the **Retyping / OCR Simulation**. Show the jury that PRAMAAN honestly returns `FINGERPRINT_NOT_RECOVERED` rather than generating false attribution claims.

---

## ⚖️ Technical Boundaries & Honest Claims

In accordance with strict cryptographic evaluation standards:
- **What PRAMAAN Proves:** PRAMAAN cryptographically attributes a leaked document to a specific **recipient identity and decryption session event** with non-repudiation backed by post-quantum signatures and BFT consensus.
- **What PRAMAAN Does Not Claim:** PRAMAAN does not claim to identify which physical human sat at the keyboard, nor does it claim survival against manual text transcription / retyping.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
<b>Built with conviction for the Smart India Hackathon</b>
</div>#   P r a m a a n  
 #   P r a m a a n  
 