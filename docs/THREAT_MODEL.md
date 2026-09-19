# Threat Model

- **Threat:** Administrator modifies logs.
  **Mitigation:** Distributed permissioned ledger (SmartBFT).
- **Threat:** Recipient denies decryption.
  **Mitigation:** Recipient signs attestation with ML-DSA-65.
- **Threat:** Metadata stripped from leaked PDF.
  **Mitigation:** Structural (Layer B) and Rendered DWT (Layer C) watermarks.
- **Threat:** Single ledger administrator controls nodes.
  **Mitigation:** In production, use independent Fabric organizations.
