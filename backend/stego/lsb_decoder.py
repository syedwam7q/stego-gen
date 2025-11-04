import numpy as np
from PIL import Image
import struct
import os


def decode_lsb(stego_path: str, bits_per_channel: int = 1) -> bytes:
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego image not found: {stego_path}")
    
    if bits_per_channel < 1 or bits_per_channel > 4:
        raise ValueError(f"bits_per_channel must be between 1 and 4, got {bits_per_channel}")
    
    try:
        img = Image.open(stego_path)
    except Exception as e:
        raise ValueError(f"Failed to open stego image: {str(e)}")
    
    if img.format not in ['PNG', None]:
        raise ValueError(
            f"Stego image must be in PNG format (lossless). Got: {img.format}. "
            "JPEG and other lossy formats will corrupt hidden data."
        )
    
    if img.mode not in ['RGB', 'RGBA', 'L']:
        try:
            img = img.convert('RGB')
        except Exception as e:
            raise ValueError(f"Failed to convert image to RGB: {str(e)}")
    elif img.mode == 'RGBA':
        img = img.convert('RGB')
    elif img.mode == 'L':
        img = img.convert('RGB')
    
    img_array = np.array(img)
    
    if len(img_array.shape) != 3:
        raise ValueError(f"Invalid image dimensions: {img_array.shape}")
    
    height, width, channels = img_array.shape
    
    if channels != 3:
        raise ValueError(f"Image must have 3 color channels (RGB), got {channels}")
    
    flat_img = img_array.flatten()
    
    bit_mask = (1 << bits_per_channel) - 1
    
    max_extractable_bytes = (len(flat_img) * bits_per_channel) // 8
    
    if max_extractable_bytes < 4:
        raise ValueError(
            f"Image too small to contain hidden data. "
            f"Can extract only {max_extractable_bytes} bytes (need at least 4 for header)"
        )
    
    extracted_bits = []
    for pixel_value in flat_img:
        bits = pixel_value & bit_mask
        for i in range(bits_per_channel - 1, -1, -1):
            extracted_bits.append((bits >> i) & 1)
    
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
            f"This may indicate wrong bits_per_channel value or corrupted data."
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
            f"Need {total_bits_needed} bits, have {len(extracted_bits)} bits. "
            f"Check if bits_per_channel value is correct."
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
