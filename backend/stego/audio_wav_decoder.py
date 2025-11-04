import numpy as np
import wave
import struct
import os


def decode_audio_lsb(audio_path: str, bits_per_sample: int = 1) -> bytes:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if bits_per_sample < 1 or bits_per_sample > 4:
        raise ValueError(f"bits_per_sample must be between 1 and 4, got {bits_per_sample}")
    
    try:
        with wave.open(audio_path, 'rb') as audio:
            params = audio.getparams()
            sample_width = params.sampwidth
            n_frames = params.nframes
            
            if sample_width not in [1, 2, 3]:
                raise ValueError(f"Only 8-bit, 16-bit, and 24-bit audio supported, got {sample_width * 8}-bit")
            
            audio_data = audio.readframes(n_frames)
    except Exception as e:
        raise ValueError(f"Failed to open audio file: {str(e)}")
    
    if sample_width == 1:
        samples = np.frombuffer(audio_data, dtype=np.uint8)
    elif sample_width == 2:
        samples = np.frombuffer(audio_data, dtype=np.int16)
    else:  # 24-bit audio
        raw_samples = np.frombuffer(audio_data, dtype=np.uint8)
        num_samples = len(raw_samples) // 3
        samples = np.zeros(num_samples, dtype=np.int32)
        for i in range(num_samples):
            b1, b2, b3 = raw_samples[i*3:(i+1)*3]
            # Combine 3 bytes into 24-bit value (little-endian)
            value = (int(b3) << 16) | (int(b2) << 8) | int(b1)
            # Convert unsigned 24-bit to signed if necessary (sign bit check)
            if value & 0x800000:
                value = value - 0x1000000
            samples[i] = value
    
    bit_mask = (1 << bits_per_sample) - 1
    
    max_extractable_bytes = (len(samples) * bits_per_sample) // 8
    
    if max_extractable_bytes < 4:
        raise ValueError(
            f"Audio too small to contain hidden data. "
            f"Can extract only {max_extractable_bytes} bytes (need at least 4 for header)"
        )
    
    extracted_bits = []
    for sample_value in samples:
        bits = sample_value & bit_mask
        for i in range(bits_per_sample - 1, -1, -1):
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
        raise ValueError("Payload length is zero. Audio may not contain hidden data.")
    
    if payload_length > max_extractable_bytes - 4:
        raise ValueError(
            f"Invalid payload length: {payload_length} bytes. "
            f"Maximum extractable: {max_extractable_bytes - 4} bytes. "
            f"This may indicate wrong bits_per_sample value or corrupted data."
        )
    
    if payload_length > 100 * 1024 * 1024:
        raise ValueError(
            f"Payload length suspiciously large: {payload_length} bytes. "
            f"This likely indicates wrong decoding parameters."
        )
    
    total_bits_needed = 32 + (payload_length * 8)
    if total_bits_needed > len(extracted_bits):
        raise ValueError(
            f"Not enough bits in audio to extract payload. "
            f"Need {total_bits_needed} bits, have {len(extracted_bits)} bits. "
            f"Check if bits_per_sample value is correct."
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
