# 🛡️ Cipher-Embedded Steganographic Shield

> **Innovative Task**: Cipher-Embedded Steganographic Shield  
> **Task Definition**: Design and implement a dual-layer security system that encrypts sensitive information and then conceals the encrypted data inside a digital image. The system should allow authorized users to embed, extract, decrypt, and verify the integrity of the hidden information. Students must demonstrate why combining cryptography with steganography provides stronger protection than using either technique independently.

---

## 📑 Table of Contents
1. [Academic Rationale: Why Dual-Layer Security?](#-academic-rationale-why-dual-layer-security)
2. [Dual-Layer Security Architecture](#-dual-layer-security-architecture)
3. [Cryptographic & Steganographic Specifications](#-cryptographic--steganographic-specifications)
4. [Image Quality & Steganalysis Metrics (MSE & PSNR)](#-image-quality--steganalysis-metrics-mse--psnr)
5. [System Features](#-system-features)
6. [Directory Structure](#-directory-structure)
7. [Getting Started & Installation](#-getting-started--installation)
8. [Application Usage Guide](#-application-usage-guide)

---

## 🎓 Academic Rationale: Why Dual-Layer Security?

A core objective of this project is demonstrating why combining cryptography with steganography yields exponentially stronger protection than employing either technique independently.

```
+-----------------------------------------------------------------------------------------+
|                                    DEFENSE POSTURES                                     |
+------------------------------------+------------------------------------+---------------+
| 1. Steganography Alone             | 2. Cryptography Alone              | 3. Dual-Layer |
|    (Stealth without Privacy)       |    (Privacy without Stealth)       |    (SHIELD)   |
+------------------------------------+------------------------------------+---------------+
| • Inconspicuous image carrier      | • Ciphertext is unreadable         | • Stealth     |
| • Fails Kerckhoffs's Principle     | • High entropy flags wire/disk     | • Privacy     |
| • Extraction reveals plaintext     | • Invites surveillance/interception| • Integrity   |
+------------------------------------+------------------------------------+---------------+
```

### 1. The Vulnerability of Steganography Alone
Steganography conceals the **existence** of communication. However, traditional steganography relies on **security through obscurity**:
- If an adversary detects the carrier or uses standard automated steganalysis tools (e.g., `zsteg`, bit-plane analysis, Chi-square statistical testing), the hidden payload is immediately recovered in **plain, unencrypted cleartext**.
- It directly violates **Kerckhoffs's Principle**, which states that a system must remain secure even if everything about the system (except the secret key) is public knowledge.

### 2. The Vulnerability of Cryptography Alone
Cryptography protects the **content** of communication through mathematical scrambling (e.g., AES-128). However, cryptography does **not hide transmission**:
- Transmitting encrypted ciphertext blobs across a network or storing them on disk produces distinct high-entropy bitstreams.
- In adversarial environments (e.g., state censorship, border crossings, hostile corporate networks), the mere presence of ciphertext flags the user for deep-packet inspection, communication blocking, or coerced key disclosure (*"rubber-hose cryptanalysis"*).

### 3. The Synergy of the Dual-Layer Shield
The **Cipher-Embedded Steganographic Shield** combines both paradigms into an integrated defense pipeline:
$$\text{Security} = \text{Stealth (Steganography)} \times \text{Confidentiality (Cryptography)} \times \text{Integrity (SHA-256)}$$

1. **Invisibility / Plausible Deniability**: The carrier image is indistinguishable from standard media (Peak Signal-to-Noise Ratio $\text{PSNR} > 60\text{ dB}$).
2. **Unbreakable Confidentiality**: Even if an attacker suspects steganographic manipulation and dumps the raw bitstream, they obtain an authenticated AES-128 ciphertext derived with 100,000 iterations of PBKDF2HMAC. Decryption requires $2^{128}$ operations.
3. **Bit-Exact Integrity Verification**: Every payload is sealed with a SHA-256 cryptographic digest and authenticated with HMAC-SHA256, immediately flagging any transmission tampering or bit corruption.

---

## 🏛️ Dual-Layer Security Architecture

### Encoding Pipeline (Embed)
```
[Sensitive Plaintext]
        │
        ▼
[Integrity Envelope Engine] ──── Computes SHA-256 Digest
        │
        ▼  Formatted: SHIELD_INTEGRITY:<SHA256_HEX>:<DATA>
[Layer 1: Cryptographic Engine]
        │  • PBKDF2HMAC (SHA-256, 100k iterations, 16-byte random salt)
        │  • Fernet AES-128-CBC + PKCS7 + HMAC-SHA256
        ▼
[Encrypted Authenticated Token]
        │
        ▼
[Layer 2: Steganographic Engine]
        │  • PNG: 1-Bit Lossless LSB RGB Substitution
        │  • JPG: Safe EOF Marker (0xFFD9) Metadata Encapsulation
        ▼
[Natural Stego-Image] (Visually Lossless, PSNR > 70 dB)
```

### Decoding Pipeline (Extract, Decrypt & Verify)
```
[Stego-Image Carrier]
        │
        ▼
[Layer 2: Steganographic Extractor]
        │  • Extracts embedded binary payload & flags
        ▼
[Ciphertext Token]
        │
        ▼
[Layer 1: Cryptographic Decryptor]
        │  • Derives 256-bit key from passphrase & extracted salt
        │  • Authenticates HMAC and decrypts AES-128-CBC
        ▼
[Integrity Verification Engine]
        │  • Unwraps stored SHA-256 digest
        │  • Computes fresh SHA-256 digest of decrypted message
        │  • Compares hashes bit-for-bit
        ▼
[Verified Authentic Plaintext] + [🟢 Green Integrity Verification Badge]
```

---

## 🔐 Cryptographic & Steganographic Specifications

### Layer 1: Cryptographic Specifications (`core/crypto.py`)
| Parameter | Specification | Purpose |
|---|---|---|
| **Key Derivation (KDF)** | `PBKDF2HMAC` | Thwarts GPU brute-force and dictionary attacks |
| **KDF Hash Function** | `SHA-256` | Cryptographically secure PRF |
| **KDF Iterations** | `100,000` | Exceeds OWASP minimum recommendations |
| **KDF Salt** | `16 bytes` (`os.urandom`) | Prevents precomputed rainbow table attacks |
| **Symmetric Cipher** | `Fernet (AES-128-CBC)` | Industrial-strength symmetric encryption |
| **Cipher Padding** | `PKCS7` | Standard block alignment |
| **Message Authentication** | `HMAC-SHA256` | Guarantees ciphertext integrity against bit-flipping |
| **Payload Integrity** | `SHA-256 (256-bit)` | End-to-end payload authenticity verification |

### Layer 2: Steganographic Specifications
#### PNG LSB Substitution (`core/lsb_handler.py`)
- Modifies only the least significant bit of Red, Green, and Blue color channels ($3 \text{ bits/pixel}$).
- Pixel component modification is bounded: $\Delta \in \{0, 1\}$ out of 255.
- Binary Header Layout:
  `[8B MAGIC "STEG_PNG"] + [1B ENCRYPT_FLAG] + [4B LENGTH (Big-Endian uint32)] + [PAYLOAD]`
- Usable Byte Capacity:
  $$\text{Capacity}_{\text{PNG}} = \left\lfloor \frac{\text{Width} \times \text{Height} \times 3}{8} \right\rfloor - 13\text{ bytes}$$

#### JPG EOF Encapsulation (`core/jpg_handler.py`)
- Lossy DCT compression in JPEG destroys pixel-level LSB data. The shield appends structured metadata cleanly after the standard JPEG EOF marker (`0xFFD9`).
- Image rendering software displays the image normally up to `0xFFD9`, ignoring auxiliary data.
- Binary Layout:
  `[JPEG Bytes to 0xFFD9] + [8B "JPEG_STG"] + [1B FLAG] + [4B SIZE] + [PAYLOAD] + [8B "END_JPEG"]`

---

## 📊 Image Quality & Steganalysis Metrics (MSE & PSNR)

To scientifically demonstrate that steganographic embedding produces imperceptible modifications, the system computes the following metrics (`utils/metrics.py`):

### 1. Mean Squared Error (MSE)
Measures the average squared difference between original carrier pixels $I_1$ and stego pixels $I_2$:
$$\text{MSE} = \frac{1}{M \times N \times 3} \sum_{x=0}^{M-1} \sum_{y=0}^{N-1} \sum_{c=0}^{2} [I_1(x, y, c) - I_2(x, y, c)]^2$$

### 2. Peak Signal-to-Noise Ratio (PSNR)
Quantifies the reconstruction quality in decibels ($\text{dB}$):
$$\text{PSNR} = 10 \cdot \log_{10} \left( \frac{255^2}{\text{MSE}} \right) = 20 \cdot \log_{10} \left( \frac{255}{\sqrt{\text{MSE}}} \right)$$

### Human Visual System (HVS) Scale:
- **$\text{PSNR} > 60\text{ dB}$**: Imperceptible to human vision (Standard for ShieldStego LSB embedding, typically $70\text{--}80\text{ dB}$).
- **$\text{PSNR} > 40\text{ dB}$**: Excellent quality; indistinguishable without microscopic pixel inspection.
- **$\text{PSNR} < 30\text{ dB}$**: Visible noise or distortion.

---

## ✨ System Features

1. 🔒 **Dual-Layer Encoder**:
   - Live payload capacity progress bar with visual thresholds ($<80\%$ Green, $80\text{--}100\%$ Orange, $>100\%$ Red).
   - Dynamic real-time SHA-256 hash generation as the user types.
   - Text input and direct `.txt` file import.
2. 🔓 **Dual-Layer Decoder & Authenticator**:
   - Automatic format detection (PNG LSB vs. JPG EOF).
   - AES-128 Fernet decryption with passphrase.
   - Dynamic **Integrity Badge** (🟢 Authentic vs. 🔴 Tampered).
   - Direct export of extracted payload to `.txt`.
3. 📊 **Defense Analysis & Academic Demonstration**:
   - **Interactive 3-Way Threat Model Simulator**: Live sandbox testing Stego Alone vs. Crypto Alone vs. Dual-Layer Shield.
   - **Comparative Security Matrix**: Side-by-side feature comparison across all core security dimensions.
   - **Image Quality Benchmarking Tool**: Live calculation of MSE, PSNR (dB), modified pixel count, and maximum channel delta.
4. 📋 **Real-Time Security Audit Console**:
   - Timestamped operations log tracking cryptographic and steganographic processes.

---

## 📁 Directory Structure

```
Security/
├── main.py                     # Application entry point
├── requirements.txt            # Package dependencies
├── README.md                   # Academic and technical documentation
├── core/
│   ├── __init__.py             # Package initializer & exports
│   ├── crypto.py               # Layer 1: AES-128 Fernet, PBKDF2HMAC, SHA-256 integrity
│   ├── lsb_handler.py          # Layer 2: PNG 1-bit LSB substitution
│   └── jpg_handler.py          # Layer 2: JPG EOF metadata encapsulation
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Modern CustomTkinter container & navigation
│   ├── encode_frame.py         # Dual-Layer Encoder UI
│   ├── decode_frame.py         # Extractor, Decryptor & Verification UI
│   └── demo_frame.py           # Academic Threat Simulator & PSNR/MSE Metrics
└── utils/
    ├── validators.py           # File validation & capacity checks
    └── metrics.py              # MSE, PSNR, and pixel distortion analyzer
```

---

## 🚀 Getting Started & Installation

### Prerequisites
- Python 3.10+ installed.

### Installation
1. Clone repository or navigate to directory:
   ```bash
   cd Security
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Application Usage Guide

Launch the application:
```bash
python main.py
```

### 1. Encoding (Hide Data)
1. Navigate to **Dual-Layer Encoder**.
2. Select a carrier image (PNG or JPG).
3. Type secret data or click **Load .txt File**.
4. Observe the live SHA-256 hash and capacity bar.
5. Enter an encryption passphrase.
6. Click **⚡ Encrypt & Conceal (Generate Stego-Image)** and choose save location.

### 2. Decoding (Extract & Verify)
1. Navigate to **Extractor & Decryptor**.
2. Select the stego-image.
3. Enter the secret passphrase.
4. Click **🔍 Extract, Decrypt & Verify**.
5. Observe the **🟢 INTEGRITY VERIFIED** badge, extracted text, and matching SHA-256 digests.

### 3. Defense Analysis & Demonstration
1. Navigate to **Defense Analysis & Demo**.
2. Test the **3-Way Attack Simulator** with custom inputs to inspect adversary views.
3. Review the **Comparative Security Feature Matrix**.
4. In the **Image Quality Metrics** section, load the original carrier image and the generated stego-image, then click **Compute PSNR & Imperceptibility Report** to view the MSE and PSNR (dB).
