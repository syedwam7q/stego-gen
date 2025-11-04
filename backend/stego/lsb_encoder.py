import numpy as np
from PIL import Image
import struct
import os


def encode_lsb(carrier_path: str, payload: bytes, output_path: str, bits_per_channel: int = 1) -> dict:
    if not os.path.exists(carrier_path):
        raise FileNotFoundError(f"Carrier image not found: {carrier_path}")
    
    if bits_per_channel < 1 or bits_per_channel > 4:
        raise ValueError(f"bits_per_channel must be between 1 and 4, got {bits_per_channel}")
    
    if not payload:
        raise ValueError("Payload cannot be empty")
    
    try:
        img = Image.open(carrier_path)
    except Exception as e:
        raise ValueError(f"Failed to open carrier image: {str(e)}")
    
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
    
    max_bytes = (height * width * channels * bits_per_channel) // 8
    
    payload_length = len(payload)
    header_size = 4
    required_bytes = payload_length + header_size
    
    if required_bytes > max_bytes:
        raise ValueError(
            f"Payload too large for carrier image.\n"
            f"Required: {required_bytes} bytes (payload: {payload_length} + header: {header_size})\n"
            f"Available: {max_bytes} bytes\n"
            f"Try using a larger image or increasing bits_per_channel (current: {bits_per_channel})"
        )
    
    if payload_length > 2**32 - 1:
        raise ValueError(f"Payload too large: {payload_length} bytes (max: {2**32 - 1})")
    
    length_bytes = struct.pack('>I', payload_length)
    full_payload = length_bytes + payload
    
    payload_bits = []
    for byte in full_payload:
        for i in range(8):
            payload_bits.append((byte >> (7 - i)) & 1)
    
    flat_img = img_array.flatten().copy()
    
    bit_mask = (1 << bits_per_channel) - 1
    clear_mask = ~bit_mask & 0xFF
    
    bit_index = 0
    for i in range(len(flat_img)):
        if bit_index >= len(payload_bits):
            break
        
        bits_to_embed = 0
        for j in range(bits_per_channel):
            if bit_index < len(payload_bits):
                bits_to_embed = (bits_to_embed << 1) | payload_bits[bit_index]
                bit_index += 1
            else:
                bits_to_embed = bits_to_embed << 1
        
        flat_img[i] = (flat_img[i] & clear_mask) | bits_to_embed
    
    stego_array = flat_img.reshape(img_array.shape)
    stego_img = Image.fromarray(stego_array.astype('uint8'), 'RGB')
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        stego_img.save(output_path, 'PNG', optimize=False)
    except Exception as e:
        raise IOError(f"Failed to save stego image: {str(e)}")
    
    return {
        'success': True,
        'payload_size': payload_length,
        'capacity_used': (required_bytes / max_bytes) * 100,
        'bits_per_channel': bits_per_channel,
        'dimensions': f"{width}x{height}",
        'max_capacity_bytes': max_bytes
    }
