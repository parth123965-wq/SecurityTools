# 🛡️ ShieldStego — Steganography & Encryption Tool

**ShieldStego** is a modern desktop application built in Python that combines **Least Significant Bit (LSB)** and **End-Of-File (EOF)** steganography with **Fernet (AES-128-CBC + HMAC-SHA256)** encryption. It allows users to hide secret textual data inside PNG and JPG images, with optional passphrase protection and real-time payload capacity tracking.

---

## ✨ Features

- 🔒 **Authenticated Cryptography**: Encrypts secret messages using **AES-128-CBC** in Fernet mode with **PBKDF2HMAC (SHA-256)** key derivation (100,000 iterations & 16-byte salt).
- 🖼️ **PNG LSB Steganography**: Embeds secret payloads directly into the least significant bits of RGB image channels, producing visually imperceptible modifications.
- 📸 **JPG EOF Steganography**: Appends metadata payloads cleanly after the JPEG End-of-File (`0xFFD9`) marker, bypassing DCT compression corruption while keeping the image readable by all standard image viewers.
- 🎨 **Modern Desktop GUI**: Crafted with `CustomTkinter` for a sleek dark/light mode responsive desktop interface.
- 📊 **Real-time Capacity Calculation**: Measures image dimensions and calculates payload fit/used percentage dynamically before encoding.
- 🔍 **Auto-Detection Decoding**: Automatically identifies image format, payload structure, and encryption state during extraction.

---

## 📁 Project Structure

```
security feature/
├── main.py                 # Application entry point
├── requirements.txt        # Python package dependencies
├── README.md               # Documentation
├── core/
│   ├── __init__.py
│   ├── crypto.py           # PBKDF2 key derivation & Fernet encryption logic
│   ├── lsb_handler.py      # PNG LSB embedding and extraction algorithm
│   └── jpg_handler.py      # JPG EOF appending and extraction algorithm
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Main CustomTkinter UI container & navigation tabs
│   ├── encode_frame.py    # UI frame for image encoding & payload hiding
│   └── decode_frame.py    # UI frame for payload extraction & decryption
└── utils/
    └── validators.py       # File validation and steganographic capacity checks
```

---

## 🔐 Technical & Cryptographic Specifications

### Cryptographic Security Model (`core/crypto.py`)
- **Key Derivation Function (KDF)**: `PBKDF2HMAC`
  - Hash algorithm: `SHA-256`
  - Key length: `32 bytes` (256-bit URL-safe base64 key)
  - Iterations: `100,000`
  - Salt: `16-byte` cryptographically random salt (`os.urandom`)
- **Encryption Algorithm**: `Fernet` (AES-128-CBC with PKCS7 padding + HMAC-SHA256 authentication)

### PNG LSB Embedding Binary Layout (`core/lsb_handler.py`)
| Magic Header (8B) | Encrypted Flag (1B) | Payload Length (4B) | Payload Data (N Bytes) |
|---|---|---|---|
| `STEG_PNG` | `0x01` (Encrypted) / `0x00` (Plain) | Uint32 Big-Endian | Secret Message / Encrypted Token |

- **Capacity**: `(Width × Height × 3 channels) // 8 - Header Overhead`

### JPG EOF Embedding Binary Layout (`core/jpg_handler.py`)
| Original JPG (`0xFFD9`) | Magic Header (8B) | Encrypted Flag (1B) | Payload Size (4B) | Payload Data | Footer Magic (8B) |
|---|---|---|---|---|---|
| Standard Image Bytes | `JPEG_STG` | `0x01` / `0x00` | Uint32 Big-Endian | Encrypted Payload | `END_JPEG` |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** installed on your system.

### Installation

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/parth123965-wq/Security-Feature.git
   cd Security-Feature
   ```

2. **Set up a Virtual Environment** (Optional but Recommended):
   ```bash
   python -m venv .venv
   # On Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage

Run the main application entry point:

```bash
python main.py
```

Or run directly using the virtual environment Python executable:

```cmd
.venv\Scripts\python.exe main.py
```

### Encoding a Hidden Message
1. Navigate to the **Encode** tab.
2. Select a target **PNG** or **JPG** image.
3. Enter your **Secret Message**.
4. (Optional) Enable **Password Protection** and supply a passphrase.
5. Click **Encode & Save Image** to output the steganographic image file.

### Decoding a Hidden Message
1. Navigate to the **Decode** tab.
2. Load an encoded steganographic image.
3. If password protected, input the matching passphrase.
4. Click **Extract Message** to view the hidden payload.

---

## 📦 Dependencies

- [`customtkinter`](https://github.com/TomSchimansky/CustomTkinter) — Modern GUI toolkit for Tkinter.
- [`Pillow`](https://python-pillow.org/) — Python Imaging Library for image processing.
- [`cryptography`](https://cryptography.io/) — Symmetric encryption and KDF primitives.
