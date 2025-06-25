# Blockchain-DotChainVerify
## 🛡️ Secure Documents Using Blockchain with Face Verification and NIDS

A robust digital document verification and authentication system that leverages blockchain technology, live face verification, and a Network Intrusion Detection System (NIDS) to ensure secure, tamper-proof digital document processing.

##  Features

- Blockchain-Based Document Authentication
  - Hashes (via BLAKE3) of uploaded documents are stored on the blockchain for integrity and verification.
- Real-Time Face Verification
  - Captures a live selfie and compares it to ID/passport photos for user identity validation.
- QR Code Generation
  - Generates unique QR codes for each verified document for easy and secure validation.
- NIDS (Network Intrusion Detection System)
  - Detects cyber threats such as DDoS attacks, malware injections, and unauthorized access.
- Admin Verification Dashboard
  - Admins can verify document hashes, user identity, and manage the blockchain verification flow.

##  Tech Stack

| Layer        | Tools / Languages                              |
|--------------|------------------------------------------------|
| Frontend     | HTML, CSS, JavaScript                          |
| Backend      | Python (Flask)                                 |
| Blockchain   | Solidity Smart Contracts (via Remix IDE)       |
| Hashing      | BLAKE3                                         |
| QR Codes     | Python QR libraries (e.g., `qrcode`)           |
| Face Match   | OpenCV, FaceNet , InsightFace                  |
| Security     | Custom IDS Rules + Blockchain Audit Trails     |

##  Project Structure

```bash
.
├── backend/
│   ├── app.py                 # Flask backend for uploads and face verification
│   ├── blake3_hash.py         # BLAKE3 hashing implementation
│   ├── qr_generator.py        # QR code creation for document verification
│   └── face_verification.py   # Real-time selfie vs ID photo matcher
├── smart_contract/
│   └── document_verifier.sol  # Solidity smart contract
├── frontend/
│   ├── index.html             # Main UI for user interaction
│   ├── upload.html            # File and selfie upload page
│   └── verify.html            # Document and face verification page
├── nids/
│   └── custom_nids.py         # Intrusion detection logic
├── static/
│   └── qr_codes/              # Saved QR codes
├── templates/
│   └── *.html                 # Flask templates
└── README.md
