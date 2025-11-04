# StegoGen - Multi-Algorithm AI-Assisted Steganography System

A comprehensive steganography platform supporting **5 different algorithms** (LSB, DCT, DWT, Audio, Video) with AI-powered optimization. Hide text or binary files in images, audio, and video with military-grade encryption.

## Features

### **Multiple Steganography Algorithms**
- **LSB (Least Significant Bit)**: Classic spatial domain steganography for images
- **DCT (Discrete Cosine Transform)**: Frequency domain embedding resistant to JPEG compression
- **DWT (Discrete Wavelet Transform)**: Wavelet-based embedding with excellent imperceptibility
- **Audio Steganography**: Hide data in WAV audio samples (inaudible modifications)
- **Video Steganography**: Embed data across video frames (MP4, AVI, MOV, MKV)

### **Advanced Capabilities**
- **Binary File Support**: Hide any file type (images, documents, archives, etc.)
- **AI-Powered Recommendations**: Grok AI analyzes carriers and suggests optimal parameters
- **AES-256 Encryption**: Military-grade encryption for payload security
- **Quality Metrics**: Automatic PSNR and SSIM calculation
- **Modern Web Interface**: React-based UI with intuitive algorithm selection
- **RESTful API**: 15+ FastAPI endpoints for all operations
- **CLI Tool**: Command-line interface for batch processing

## Architecture

```
Frontend (React) ──→ Backend (FastAPI) ──→ AI Adapter (Grok)
                              │
                              ├──→ LSB Encoder/Decoder
                              ├──→ DCT Encoder/Decoder  
                              ├──→ DWT Encoder/Decoder
                              ├──→ Audio Encoder/Decoder
                              ├──→ Video Encoder/Decoder
                              ├──→ Crypto Module (AES-256)
                              ├──→ Metrics Calculator
                              └──→ Image Analyzer
```

## 📁 Project Structure

```
steganoGen/
├── backend/
│   ├── main.py                    # FastAPI application (15+ endpoints)
│   ├── config.py                  # Configuration management
│   ├── logger.py                  # Logging setup
│   ├── cli.py                     # Command-line interface
│   ├── requirements.txt           # Dependencies
│   ├── .env.example              # Environment template
│   ├── stego/
│   │   ├── lsb_encoder.py        # LSB encoding
│   │   ├── lsb_decoder.py        # LSB decoding
│   │   ├── dct_encoder.py        # DCT encoding
│   │   ├── dct_decoder.py        # DCT decoding
│   │   ├── dwt_encoder.py        # DWT encoding
│   │   ├── dwt_decoder.py        # DWT decoding
│   │   ├── audio_encoder.py      # Audio encoding
│   │   ├── audio_decoder.py      # Audio decoding
│   │   ├── video_encoder.py      # Video encoding
│   │   ├── video_decoder.py      # Video decoding
│   │   ├── crypto.py             # AES-256 encryption
│   │   ├── analyzer.py           # Image analysis
│   │   ├── metrics.py            # PSNR/SSIM metrics
│   │   └── ai_adapter.py         # Grok AI integration
│   ├── uploads/                  # Temporary uploads
│   ├── outputs/                  # Generated files
│   └── test_files/               # Test data
├── frontend/
│   ├── src/
│   │   ├── App.js               # Main application
│   │   ├── App.css              # Enhanced styles
│   │   └── components/
│   │       ├── Home.js          # Landing page
│   │       ├── Encode.js        # Multi-algorithm encoding
│   │       └── Decode.js        # Multi-algorithm decoding
│   └── package.json
└── docs/
    ├── API_ENHANCEMENTS.md      # Detailed API documentation
    └── IMPROVEMENTS.md          # Implementation notes
```

## 🚀 Setup Instructions

### Backend Setup

1. **Navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Dependencies include:
   - FastAPI, uvicorn
   - OpenCV, Pillow, numpy, scipy
   - PyWavelets (for DWT)
   - Cryptography (AES-256)
   - ffmpeg-python (video processing)

4. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```env
   GROK_API_KEY=your_grok_api_key_here
   UPLOAD_DIR=uploads
   OUTPUT_DIR=outputs
   MAX_FILE_SIZE=52428800
   ```

5. **Run backend**:
   ```bash
   python main.py
   ```
   Server runs at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run frontend**:
   ```bash
   npm start
   ```
   Opens at `http://localhost:3000`

## 📖 Usage Guide

### Web Interface

#### Encoding
1. Select algorithm (LSB/DCT/DWT/Audio/Video)
2. Upload carrier file (image/audio/video)
3. Choose payload type:
   - Text message
   - Binary file upload
4. (Optional) Set encryption key
5. Adjust algorithm parameters:
   - LSB: bits per channel (1-4)
   - DCT: strength (1-100)
   - DWT: strength (0.01-10)
6. Click "Analyze with AI" for recommendations
7. Click "Encode Now"
8. Download stego file
9. **Save settings for decoding!**

#### Decoding
1. Select same algorithm used for encoding
2. Upload stego file
3. Enter same parameters:
   - LSB: bits per channel
   - DCT/DWT: strength
4. (If encrypted) Enter decryption key
5. Click "Decode Message"
6. View/copy extracted data

### Command-Line Interface

```bash
# Encode with LSB
python cli.py encode -c image.png -p "secret" -a lsb -b 1

# Encode with DCT
python cli.py encode -c image.jpg -p "secret" -a dct -s 10 -k password

# Encode with DWT
python cli.py encode -c image.png -p "secret" -a dwt -s 15

# Encode audio
python cli.py encode -c audio.wav -p "secret" -a audio -k password

# Encode video
python cli.py encode -c video.mp4 -p "secret" -a video

# Decode
python cli.py decode -s stego.png -a lsb -b 1 -k password

# Get help
python cli.py --help
```

## 🔌 API Reference

### Core Endpoints

#### `POST /api/analyze`
Analyzes carrier and provides AI recommendations.

**Form Data**:
- `carrier` (file): Image file
- `payload_text` (string): Payload for size estimation
- `goal` (string): "max_invisibility" | "max_capacity"

**Response**:
```json
{
  "file_id": "uuid",
  "image_stats": {
    "dimensions": [1920, 1080],
    "entropy": 7.45,
    "variance": 1234.56,
    "edge_density": 0.23
  },
  "recommendation": {
    "algorithm": "LSB",
    "bits_per_channel": 1,
    "region_hint": "smooth_areas",
    "explanation": "AI recommendation...",
    "confidence": 0.85,
    "source": "grok"
  }
}
```

### LSB Endpoints

#### `POST /api/encode`
LSB encoding for images.

**Form Data**:
- `carrier` (file): Image
- `payload_text` (string) OR `payload_file` (file): Payload
- `bits_per_channel` (int): 1-4 (default: 1)
- `encryption_key` (string, optional): Encryption key

**Response**:
```json
{
  "output_filename": "stego_abc123.png",
  "download_url": "/api/download/stego_abc123.png",
  "metrics": {
    "psnr": 79.89,
    "ssim": 1.0000
  },
  "encode_info": {
    "algorithm": "LSB",
    "bits_per_channel": 1,
    "payload_size": 123,
    "capacity_used": 0.05
  }
}
```

#### `POST /api/decode`
LSB decoding for images.

**Form Data**:
- `stego_image` (file): Stego image
- `bits_per_channel` (int): Must match encoding
- `decryption_key` (string, optional): If encrypted

**Response**:
```json
{
  "payload": "decoded message",
  "payload_size": 123,
  "was_encrypted": true,
  "is_binary": false,
  "payload_base64": "68656c6c6f"
}
```

### DCT Endpoints

#### `POST /api/encode/dct`
DCT frequency domain encoding.

**Form Data**:
- `carrier` (file): Image
- `payload_text` OR `payload_file`: Payload
- `strength` (int): 1-50 (default: 10)
- `encryption_key` (optional)

#### `POST /api/decode/dct`
DCT decoding.

**Form Data**:
- `stego_image` (file)
- `strength` (int): Must match encoding
- `decryption_key` (optional)

### DWT Endpoints

#### `POST /api/encode/dwt`
DWT wavelet domain encoding.

**Form Data**:
- `carrier` (file): Image
- `payload_text` OR `payload_file`: Payload
- `strength` (int): 1-50 (default: 10)
- `encryption_key` (optional)

#### `POST /api/decode/dwt`
DWT decoding.

**Form Data**:
- `stego_image` (file)
- `strength` (int): Must match encoding
- `decryption_key` (optional)

### Audio Endpoints

#### `POST /api/encode/audio`
Audio steganography (WAV).

**Form Data**:
- `carrier_file` (file): WAV audio
- `payload_text` OR `payload_file`: Payload
- `encryption_key` (optional)

#### `POST /api/decode/audio`
Audio decoding.

**Form Data**:
- `stego_file` (file): Stego WAV
- `decryption_key` (optional)

### Video Endpoints

#### `POST /api/encode/video`
Video steganography (MP4/AVI/MOV/MKV).

**Form Data**:
- `carrier_file` (file): Video
- `payload_text` OR `payload_file`: Payload
- `encryption_key` (optional)

#### `POST /api/decode/video`
Video decoding.

**Form Data**:
- `stego_file` (file): Stego video
- `decryption_key` (optional)

### Utility Endpoints

#### `GET /api/download/{filename}`
Download generated stego files.

#### `GET /health`
Health check endpoint.

## 🔬 Algorithm Details

### LSB (Least Significant Bit)
**Domain**: Spatial  
**Best For**: Natural images with textures  
**Pros**: Simple, high capacity, fast  
**Cons**: Fragile to compression, detectable by steganalysis  
**Parameters**: `bits_per_channel` (1-4)

**Technical**:
- Modifies least significant bits of RGB channels
- 1 bit/channel = 3 bits per pixel
- Typical PSNR: 70-80 dB
- Capacity: ~37.5% of image size per bit

### DCT (Discrete Cosine Transform)
**Domain**: Frequency  
**Best For**: Images that may be compressed  
**Pros**: Resistant to JPEG compression, robust  
**Cons**: Lower capacity, more complex  
**Parameters**: `strength` (1-50)

**Technical**:
- Embeds in mid-frequency coefficients
- Uses 8x8 blocks, modifies coefficient (4,4)
- Sign-based embedding (±strength)
- Typical PSNR: 50-55 dB
- Capacity: ~5-10% of image size

### DWT (Discrete Wavelet Transform)
**Domain**: Wavelet  
**Best For**: Maximum imperceptibility  
**Pros**: Excellent quality, robust  
**Cons**: Moderate capacity, slower  
**Parameters**: `strength` (1-50)

**Technical**:
- Uses Haar wavelet decomposition
- Embeds in horizontal detail coefficients
- Sign-based embedding
- Typical PSNR: 55-60 dB
- Capacity: ~0.5-1% of image size

### Audio Steganography
**Domain**: Spatial (audio samples)  
**Best For**: Voice recordings, music  
**Pros**: Large capacity, inaudible  
**Cons**: WAV format only, sensitive to re-encoding  

**Technical**:
- Modifies LSBs of 16-bit audio samples
- Works with any sample rate (44.1kHz recommended)
- Typical SNR: >40 dB (inaudible)
- Capacity: ~0.1-0.5% of audio size

### Video Steganography
**Domain**: Spatial (frame pixels)  
**Best For**: Large payloads  
**Pros**: Huge capacity, distributed across frames  
**Cons**: Slow processing, format sensitive  

**Technical**:
- Embeds in I-frames (keyframes)
- LSB modification per frame
- Typical capacity: 1-5% of video size
- Processing: 5-10 seconds per minute of video

## 📊 Performance Metrics

| Algorithm | PSNR (dB) | SSIM | Capacity | Speed | Robustness |
|-----------|-----------|------|----------|-------|------------|
| LSB       | 70-80     | 1.00 | ★★★★★    | ★★★★★ | ★★☆☆☆     |
| DCT       | 50-55     | 0.99 | ★★☆☆☆    | ★★★☆☆ | ★★★★☆     |
| DWT       | 55-60     | 0.99 | ★★☆☆☆    | ★★☆☆☆ | ★★★★★     |
| Audio     | N/A (SNR) | N/A  | ★★★☆☆    | ★★★★☆ | ★★☆☆☆     |
| Video     | 40-50     | 0.98 | ★★★★★    | ★☆☆☆☆ | ★★☆☆☆     |

## 🔐 Security Features

### Encryption
- **Algorithm**: AES-256-CBC
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **IV**: Random 16-byte initialization vector
- **Metadata**: `STEGANO|encrypted|<iv>|<data>` format

### Best Practices
1. Use strong encryption keys (16+ characters, mixed case, symbols)
2. Never reuse carrier files
3. Use PNG for images (lossless)
4. Keep original files secure
5. Document encoding parameters
6. Test decode before sharing

## 🎯 Use Cases

- **Secure Communication**: Hide messages in innocent-looking files
- **Digital Watermarking**: Embed copyright information
- **Data Exfiltration Testing**: Security research and penetration testing
- **Steganography Research**: Academic studies on data hiding
- **Privacy**: Avoid censorship by hiding sensitive data

## ⚠️ Important Notes

1. **File Formats**:
   - Images: Use PNG (lossless). JPEG corrupts data
   - Audio: WAV only. MP3 will corrupt data
   - Video: Original format recommended

2. **Parameter Matching**: Decoding requires exact parameters used in encoding

3. **Capacity Limits**: Check capacity before encoding large files

4. **Steganalysis**: LSB is detectable by statistical analysis

5. **Legal**: Use responsibly. Some jurisdictions restrict steganography

## 🐛 Troubleshooting

### Common Errors

**"Payload too large"**: 
- Reduce payload size
- Use higher bits_per_channel (LSB)
- Use video for large files

**"Decoding failed"**:
- Verify algorithm matches encoding
- Check parameters (bits/strength)
- Verify file is unmodified
- Check encryption key

**"Import errors"**:
```bash
pip install --upgrade -r requirements.txt
```

**"Port in use"**:
```bash
lsof -ti:8000 | xargs kill -9
```

## 📈 Future Enhancements

- [x] DCT/DWT implementation
- [x] Audio/Video support
- [x] Binary file payloads
- [x] CLI tool
- [ ] Batch processing
- [ ] Steganalysis detection mode
- [ ] Mobile app
- [ ] Advanced AI features
- [ ] Custom encryption algorithms

## 📄 License

Educational and research purposes. Use responsibly.

## 👥 Contributors

Syed Wamiq [https://syedwamiq.framer.website]
Project demonstrating advanced steganography techniques with AI integration.

## 📚 References

- LSB Steganography: Classical spatial domain technique
- DCT: Based on JPEG compression principles
- DWT: Haar wavelet decomposition
- AES-256: NIST FIPS 197 standard
- PSNR/SSIM: Image quality metrics (IEEE standards)

---

**Version**: 2.0  
**Last Updated**: November 2025  
**API Version**: v1
