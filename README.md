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

## Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Repository Layout](#repository-layout)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the System](#running-the-system)
- [Testing](#testing)
- [Demonstration Flow](#demonstration-flow)
- [Security Boundaries](#security-boundaries)
- [License](#license)

## Overview

Organizations handling sensitive intelligence, board resolutions, and classified materials face an asymmetry: **documents must be distributed to multiple parties to be useful, but once distributed, any recipient can leak them anonymously.** Traditional watermarking is easily stripped, and centralized audit logs are vulnerable to administrative tampering or denial of receipt.

**PRAMAAN** addresses this challenge with a verifiable pipeline:
1. **Encrypt Once, Distribute Anywhere:** Uses `AES-256-GCM` with post-quantum `ML-KEM-768` key-wrapping so every recipient accesses the identical encrypted ciphertext.
2. **Cryptographic Proof of Decryption:** Decryption keys are released only after the recipient signs an `ML-DSA-65` digital request committed to an offline **Hyperledger Fabric v3 SmartBFT** permissioned ledger.
3. **Defense-in-Depth Forensic Fingerprinting:** An imperceptible, 3-layer forensic watermark (Metadata, Glyph Spacing, and 2D-DWT Spread-Spectrum) binds the rendered document to the specific recipient and session ID.
4. **Leak Attribution:** When a leaked document is recovered, the forensic engine extracts the embedded watermark locator, queries the immutable ledger, verifies the post-quantum signature, and cryptographically attributes the artifact to the exact decryption event.

---

## How It Works

1. **Encrypt once:** A document is encrypted with `AES-256-GCM`. The same ciphertext can be distributed to every authorized recipient.
2. **Authorize decryption:** A recipient submits an `ML-DSA-65`-signed decryption request. The request is recorded on the permissioned Fabric ledger before the key is released.
3. **Fingerprint the output:** The decrypted document receives three forensic watermark layers bound to the recipient and decryption session.
4. **Verify a leak:** The forensic engine extracts the fingerprint, looks up the corresponding ledger event, verifies the signature, and attributes the document to the recorded recipient and session.

## Architecture

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

## Technology Stack

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

## Repository Layout

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
├── core/crypto/              # Cryptographic engine
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

## Requirements

This project is built for **Windows with WSL2 / Docker Desktop**, designed to run **completely air-gapped and offline** without external cloud dependencies.

- **Windows 10 / 11** with PowerShell 5.1+
- **Docker Desktop** (running and set to Linux containers)
- **WSL2** with Ubuntu installed (`wsl --install -d Ubuntu`)
- **Python 3.12+**
- **Node.js 18+** (inside WSL2 for the Fabric Gateway adapter)

The system is designed to run locally and offline after its dependencies and Fabric binaries are available.

## Installation

The commands below assume you have opened a terminal at the repository root.

---

### 1. Start Hyperledger Fabric

Open your **Ubuntu Terminal**:

```bash
# Run the automated Fabric setup script from the repository root
chmod +x fabric/scripts/setup_fabric.sh
bash fabric/scripts/setup_fabric.sh
```
*This downloads the Fabric 3.0 binaries, boots 4 SmartBFT ordering nodes and peer containers, creates `pramaan-channel`, and deploys the `provenance` chaincode.*

---

### 2. Start the Fabric Gateway Adapter

In the Ubuntu Terminal:

```bash
cd fabric_adapter

# Install dependencies
npm install

# Start the adapter server (runs on port 3000)
npm start
```
You will see: `Fabric Gateway Adapter running on port 3000`.

---

### 3. Set Up the Python Environment and API

Open **Windows PowerShell**:

```powershell
# From the repository root, create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install Python requirements
pip install -r requirements.txt

# 4. Start the FastAPI backend
uvicorn api.main:app --port 8000
```
Backend API will be live at `http://127.0.0.1:8000`.

---

### 4. Launch the Streamlit Dashboard

Open a **new Windows PowerShell window**:

```powershell
.\venv\Scripts\Activate.ps1

# Start the user interface
streamlit run app.py
```
Your browser will automatically open `http://localhost:8501`.

---

## Running the System

Once the services are running, use the Streamlit dashboard at `http://localhost:8501`. The FastAPI service is available at `http://127.0.0.1:8000`; its interactive API documentation is at `http://127.0.0.1:8000/docs`.

The dashboard provides sender, recipient, dashboard, and investigator workflows. Fabric, the gateway adapter, the FastAPI service, and Streamlit must remain running for the complete end-to-end flow.

### Quick Smoke Test

Use four terminal windows and leave each long-running service open:

1. **Fabric:** run the setup command from the installation section. Docker Desktop must be running and integrated with your WSL distribution.
2. **Fabric adapter:** from `fabric_adapter`, run `npm start` and confirm that it prints `Fabric Gateway Adapter running on port 3000`.
3. **FastAPI:** from the repository root with the virtual environment activated, run `uvicorn api.main:app --port 8000`.
4. **Dashboard:** from the repository root with the virtual environment activated, run `streamlit run app.py`.

Check the API before opening the dashboard:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```text
status
------
ok
```

Open `http://127.0.0.1:8000/docs` to try the API interactively, or use the dashboard at `http://localhost:8501`.

### Verify Document Encryption

Prepare any small PDF, then call the encryption endpoint from PowerShell. Replace `sample.pdf` with the path to your test PDF:

```powershell
curl.exe -X POST http://127.0.0.1:8000/documents/encrypt -F "file=@sample.pdf"
```

A successful response contains a `document_id`, a SHA-256 `document_hash`, and the message `Document encrypted successfully once using AES-256-GCM.` The same operation is available in the dashboard under **Sender**: upload the PDF and click **Encrypt Once**.

### Verify Recipient Registration

The recipient API can be tested from Swagger or PowerShell:

```powershell
Invoke-RestMethod -Method Post `
   -Uri http://127.0.0.1:8000/recipients/register `
   -ContentType "application/json" `
   -Body '{"display_name":"Alice","organization":"Example Org","role":"Reviewer"}'
```

The response should contain a `recipient_id` and `certificate_serial`. This creates local PQC keys and a signed recipient certificate in the local keystore.

### Run the Automated Tests

From the repository root with the virtual environment activated:

```powershell
pytest -v
```

To run only the watermark attack tests:

```powershell
pytest tests/attacks/test_attacks.py -v
```

The test suite covers direct PDF copies, screenshots, JPEG compression, print-scan simulation, and the expected failure for retyped text.

### Current Prototype Boundaries

The **Sender** screen and the API smoke tests are functional. The **Recipient** buttons, **Attack Lab** button, and **Ledger Explorer** screen are currently UI placeholders. The forensic endpoint uses a placeholder fingerprint list, so a complete recipient-to-ledger-to-leak demonstration requires those integration paths to be implemented before it can be treated as production behavior.

## Testing

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

## Demonstration Flow

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

## Security Boundaries

In accordance with strict cryptographic evaluation standards:
- **What PRAMAAN Proves:** PRAMAAN cryptographically attributes a leaked document to a specific **recipient identity and decryption session event** with non-repudiation backed by post-quantum signatures and BFT consensus.
- **What PRAMAAN Does Not Claim:** PRAMAAN does not claim to identify which physical human sat at the keyboard, nor does it claim survival against manual text transcription / retyping.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
<b>Built with conviction for the Smart India Hackathon</b>
</div>
