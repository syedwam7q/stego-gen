import numpy as np
from PIL import Image
import pywt
import struct
import os


def decode_dwt(stego_path: str, wavelet: str = 'haar', strength: float = 0.1) -> bytes:
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego image not found: {stego_path}")
    
    if strength < 0.01 or strength > 10.0:
        raise ValueError(f"strength must be between 0.01 and 10.0, got {strength}")
    
    if wavelet not in pywt.wavelist():
        raise ValueError(f"Invalid wavelet: {wavelet}. Use one of: {', '.join(pywt.wavelist()[:10])}")
    
    try:
        img = Image.open(stego_path)
    except Exception as e:
        raise ValueError(f"Failed to open stego image: {str(e)}")
    
    if img.mode not in ['RGB', 'RGBA', 'L']:
        try:
            img = img.convert('RGB')
        except Exception as e:
            raise ValueError(f"Failed to convert image to RGB: {str(e)}")
    elif img.mode == 'RGBA':
        img = img.convert('RGB')
    elif img.mode == 'L':
        img = img.convert('RGB')
    
    img_array = np.array(img, dtype=np.float32)
    
    if len(img_array.shape) != 3:
        raise ValueError(f"Invalid image dimensions: {img_array.shape}")
    
    height, width, channels = img_array.shape
    
    if channels != 3:
        raise ValueError(f"Image must have 3 color channels (RGB), got {channels}")
    
    if height < 32 or width < 32:
        raise ValueError(f"Image too small. Minimum size: 32x32")
    
    max_extractable_bytes = (height * width * channels) // (8 * 4)
    
    if max_extractable_bytes < 4:
        raise ValueError(
            f"Image too small to contain hidden data. "
            f"Can extract only {max_extractable_bytes} bytes (need at least 4 for header)"
        )
    
    extracted_bits = []
    
    for c in range(channels):
        channel_data = img_array[:, :, c]
        
        coeffs = pywt.dwt2(channel_data, wavelet)
        cA, (cH, cV, cD) = coeffs
        
        cH_flat = cH.flatten()
        
        for value in cH_flat:
            if value > 0:
                extracted_bits.append(1)
            else:
                extracted_bits.append(0)
    
    if len(extracted_bits) < 32:
        raise ValueError("Not enough bits to extract payload length header")
    
    length_bits = extracted_bits[:32]
    length_bytes = []
    for i in range(0, 32, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | length_bits[i + j]
        length_bytes.append(byte)
    
    try:
        payload_length = struct.unpack('>I', bytes(length_bytes))[0]
    except struct.error as e:
        raise ValueError(f"Failed to unpack payload length: {str(e)}")
    
    if payload_length == 0:
        raise ValueError("Payload length is zero. Image may not contain hidden data.")
    
    if payload_length > max_extractable_bytes - 4:
        raise ValueError(
            f"Invalid payload length: {payload_length} bytes. "
            f"Maximum extractable: {max_extractable_bytes - 4} bytes. "
            f"This may indicate wrong wavelet or strength value."
        )
    
    if payload_length > 100 * 1024 * 1024:
        raise ValueError(
            f"Payload length suspiciously large: {payload_length} bytes. "
            f"This likely indicates wrong decoding parameters."
        )
    
    total_bits_needed = 32 + (payload_length * 8)
    if total_bits_needed > len(extracted_bits):
        raise ValueError(
            f"Not enough bits in image to extract payload. "
            f"Need {total_bits_needed} bits, have {len(extracted_bits)} bits."
        )
    
    payload_bits = extracted_bits[32:32 + (payload_length * 8)]
    
    payload_bytes = []
    for i in range(0, len(payload_bits), 8):
        if i + 8 <= len(payload_bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | payload_bits[i + j]
            payload_bytes.append(byte)
    
    if len(payload_bytes) != payload_length:
        raise ValueError(
            f"Extracted byte count mismatch. Expected {payload_length}, got {len(payload_bytes)}"
        )
    
    return bytes(payload_bytes)
