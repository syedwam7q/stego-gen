import numpy as np
from PIL import Image
import cv2
import struct
import os


def encode_dct(carrier_path: str, payload: bytes, output_path: str, strength: float = 10.0) -> dict:
    if not os.path.exists(carrier_path):
        raise FileNotFoundError(f"Carrier image not found: {carrier_path}")
    
    if strength < 1.0 or strength > 100.0:
        raise ValueError(f"strength must be between 1.0 and 100.0, got {strength}")
    
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
    
    img_array = np.array(img, dtype=np.float32)
    
    if len(img_array.shape) != 3:
        raise ValueError(f"Invalid image dimensions: {img_array.shape}")
    
    height, width, channels = img_array.shape
    
    if channels != 3:
        raise ValueError(f"Image must have 3 color channels (RGB), got {channels}")
    
    block_size = 8
    if height < block_size or width < block_size:
        raise ValueError(f"Image too small. Minimum size: {block_size}x{block_size}")
    
    blocks_h = height // block_size
    blocks_w = width // block_size
    total_blocks = blocks_h * blocks_w * channels
    
    max_bytes = total_blocks // 8
    
    payload_length = len(payload)
    header_size = 4
    required_bytes = payload_length + header_size
    
    if required_bytes > max_bytes:
        raise ValueError(
            f"Payload too large for carrier image.\n"
            f"Required: {required_bytes} bytes (payload: {payload_length} + header: {header_size})\n"
            f"Available: {max_bytes} bytes\n"
            f"Try using a larger image"
        )
    
    if payload_length > 2**32 - 1:
        raise ValueError(f"Payload too large: {payload_length} bytes (max: {2**32 - 1})")
    
    length_bytes = struct.pack('>I', payload_length)
    full_payload = length_bytes + payload
    
    payload_bits = []
    for byte in full_payload:
        for i in range(8):
            payload_bits.append((byte >> (7 - i)) & 1)
    
    stego_img = img_array.copy()
    bit_index = 0
    
    for c in range(channels):
        if bit_index >= len(payload_bits):
            break
        
        for i in range(blocks_h):
            if bit_index >= len(payload_bits):
                break
            
            for j in range(blocks_w):
                if bit_index >= len(payload_bits):
                    break
                
                y_start = i * block_size
                y_end = y_start + block_size
                x_start = j * block_size
                x_end = x_start + block_size
                
                block = stego_img[y_start:y_end, x_start:x_end, c]
                
                dct_block = cv2.dct(block)
                
                if payload_bits[bit_index] == 1:
                    dct_block[4, 4] = strength
                else:
                    dct_block[4, 4] = -strength
                
                idct_block = cv2.idct(dct_block)
                
                stego_img[y_start:y_end, x_start:x_end, c] = idct_block
                bit_index += 1
    
    stego_img = np.clip(stego_img, 0, 255).astype('uint8')
    stego_pil = Image.fromarray(stego_img, 'RGB')
    
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        stego_pil.save(output_path, 'PNG', optimize=False)
    except Exception as e:
        raise IOError(f"Failed to save stego image: {str(e)}")
    
    return {
        'success': True,
        'payload_size': payload_length,
        'capacity_used': (required_bytes / max_bytes) * 100,
        'strength': strength,
        'dimensions': f"{width}x{height}",
        'blocks': f"{blocks_w}x{blocks_h}",
        'max_capacity_bytes': max_bytes,
        'algorithm': 'DCT'
    }
