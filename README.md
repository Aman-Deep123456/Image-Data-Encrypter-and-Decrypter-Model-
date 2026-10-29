# 🖼️ Image Steganography Engine

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pillow](https://img.shields.io/badge/Library-Pillow-brightgreen.svg)](https://python-pillow.org/)
[![NumPy](https://img.shields.io/badge/Library-NumPy-orange.svg?logo=numpy&logoColor=white)](https://numpy.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

A flexible, high-capacity image steganography tool built in Python. It allows you to **hide any arbitrary file** (audio, documents, archives, or other images) inside a cover image using **configurable 2-bit channel substitution** (LSB, Mid-bit, or MSB) and reconstruct the original file with its name and format intact.

---

##  Key Features

- **Universal Payload Support**: Embed any file type (`.mp3`, `.pdf`, `.zip`, `.png`, `.txt`, `.docx`, etc.) directly into an image.
- **Customizable Bit Position**:
  - **LSB (Least Significant Bit)**: Minimum visual perturbation (virtually imperceptible to the human eye).
  - **Mid-Bit**: Moderate distortion for testing robustness and visual artifacts.
  - **MSB (Most Significant Bit)**: Maximum distortion, ideal for educational demonstrations and visual comparisons.
- **Self-Describing Binary Header**: Bundles original metadata (magic bytes, file size, original filename) into the payload, enabling 100% automated extraction without manual renaming.
- **Vectorized Bitwise Operations**: Uses NumPy arrays for fast, memory-efficient bit manipulation across millions of pixels.
- **Capacity Calculator**: Instantly inspects any cover image and reports the exact byte storage capacity available.

---

##  How It Works

### 1. Payload Structure
When embedding a secret file, the engine constructs a binary payload containing:

```text
+----------------+-----------------------+---------------------+--------------------+--------------------+
|  Magic Bytes   | Payload Length (size) | Filename Length (N) | Original Filename  |    Secret Data     |
| 4 Bytes (STEG) |   8 Bytes (uint64)    |  2 Bytes (uint16)   |    N Bytes (UTF-8) |     Raw Bytes      |
+----------------+-----------------------+---------------------+--------------------+--------------------+
```

### 2. 2-Bit Channel Substitution
Each RGB pixel contains 3 color channels (Red, Green, Blue), totaling 24 bits. With 2 bits injected per channel, every pixel stores **6 bits of hidden data**.

```text
Pixel Byte (e.g., 8-bit Red channel):
[ b7 | b6 | b5 | b4 | b3 | b2 | b1 | b0 ]
  │    │    │    │    │    │    └───┴─── LSB  (mask: 0b11111100, shift: 0)
  │    │    │    │    └───┴──────────── MID  (mask: 0b11110011, shift: 2)
  └───┴──────────────────────────────── MSB  (mask: 0b00111111, shift: 6)
```

> **Note**: Stego images are saved strictly as lossless **PNG** files. Lossy compression formats (such as JPEG) alter pixel values and will corrupt embedded bits.

---

##  Repository Structure

```text
Image-Data-Encrypter-and-Decrypter-Model-/
├── cli.py                    # Command-line interface and argument parser
├── core/
│   ├── __init__.py
│   └── steganography.py      # Core embedding, extraction, and bitwise logic
├── io_utils/
│   ├── __init__.py
│   └── file_handler.py       # Path normalization and binary I/O utilities
├── requirements.txt          # Python dependencies
└── README.md
```

---

##  Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Aman-Deep123456/Image-Data-Encrypter-and-Decrypter-Model-.git
   cd Image-Data-Encrypter-and-Decrypter-Model-
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

##  CLI Usage Guide

The CLI provides three primary subcommands: `info`, `embed`, and `extract`.

### 1. Check Image Capacity (`info`)

Calculate the maximum file size you can hide in a given cover image:

```bash
python cli.py info --cover cover.jpg
```

**Example Output:**
```text
Cover image: cover.jpg
Dimensions: 7680 x 4320
Approx capacity: 24.88 MB
```

---

### 2. Embed a File into an Image (`embed`)

Hide any file inside an image:

```bash
python cli.py embed --cover cover.jpg --secret document.pdf --out stego_output.png
```

**Options:**
- `--cover`: Path to host image (JPG or PNG recommended).
- `--secret`: Path to file you want to hide (any file type).
- `--out`: *(Optional)* Path for the output stego image (default: `stego_output.png`).

**Interactive Prompt:**
```text
Choose bit position to modify:
1 → Least significant bits (LSB, least visible)
2 → Middle bits
3 → Most significant bits (MSB, most visible)
Enter your choice (1/2/3): 1
```
*Choose `1` (LSB) for undetectable embedding.*

---

### 3. Extract the Hidden File (`extract`)

Recover the hidden file from a steganographic PNG:

```bash
python cli.py extract --stego stego_output.png --out ./extracted_files
```

**Options:**
- `--stego`: Path to the stego PNG image containing hidden data.
- `--out`: *(Optional)* Destination directory where the extracted file will be saved (default: current directory).

**Interactive Prompt:**
```text
Enter the same bit position used during embedding:
1 → LSB
2 → Middle bits
3 → MSB
Enter your choice (1/2/3): 1
```
*The extractor will read the embedded metadata and automatically recreate the file with its original name and extension.*

---

##  Security & Best Practices

| Aspect | Steganography vs. Cryptography |
| :--- | :--- |
| **Steganography** *(This tool)* | Conceals the **existence** of the message. To an outside observer, the file appears as an innocent image. |
| **Cryptography** | Conceals the **content** of the message. Anyone can see encrypted data, but cannot read it without the key. |

> **Pro Tip**: For maximum security, encrypt sensitive files using AES-256 before embedding them into the image. This guarantees confidentiality even if the stego image is subjected to steganalysis.

---

## Roadmap & Planned Enhancements

- [ ] **Cryptographic Layer**: Add optional AES-GCM / ChaCha20 password protection to payload before embedding.
- [ ] **Header Flag for Bit Position**: Store the bit position in the binary header to remove manual input during extraction.
- [ ] **Audio Carrier Support**: Extend steganography to support embedding data into `.wav` audio PCM samples.
- [ ] **Graphical User Interface (GUI)**: Modern desktop or web UI for drag-and-drop embedding and visual diff preview.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
