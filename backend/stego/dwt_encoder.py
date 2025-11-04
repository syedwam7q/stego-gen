import numpy as np
from PIL import Image
import pywt
import struct
import os


def encode_dwt(carrier_path: str, payload: bytes, output_path: str, wavelet: str = 'haar', strength: float = 0.1) -> dict:
    if not os.path.exists(carrier_path):
        raise FileNotFoundError(f"Carrier image not found: {carrier_path}")
    
    if strength < 0.01 or strength > 10.0:
        raise ValueError(f"strength must be between 0.01 and 10.0, got {strength}")
    
    if not payload:
        raise ValueError("Payload cannot be empty")
    
    if wavelet not in pywt.wavelist():
        raise ValueError(f"Invalid wavelet: {wavelet}. Use one of: {', '.join(pywt.wavelist()[:10])}")
    
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
    
    if height < 32 or width < 32:
        raise ValueError(f"Image too small. Minimum size: 32x32")
    
    payload_length = len(payload)
    header_size = 4
    required_bytes = payload_length + header_size
    
    max_bytes = (height * width * channels) // (8 * 4)
    
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
        
        channel_data = stego_img[:, :, c]
        
        coeffs = pywt.dwt2(channel_data, wavelet)
        cA, (cH, cV, cD) = coeffs
        
        cH_flat = cH.flatten()
        
        for i in range(len(cH_flat)):
            if bit_index >= len(payload_bits):
                break
            
            embedding_strength = strength * 100.0
            
            if payload_bits[bit_index] == 1:
                cH_flat[i] = embedding_strength
            else:
                cH_flat[i] = -embedding_strength
            
            bit_index += 1
        
        cH = cH_flat.reshape(cH.shape)
        
        reconstructed = pywt.idwt2((cA, (cH, cV, cD)), wavelet)
        
        if reconstructed.shape != channel_data.shape:
            reconstructed = reconstructed[:channel_data.shape[0], :channel_data.shape[1]]
        
        stego_img[:, :, c] = reconstructed
    
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
        'wavelet': wavelet,
        'dimensions': f"{width}x{height}",
        'max_capacity_bytes': max_bytes,
        'algorithm': 'DWT'
    }
