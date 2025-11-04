import numpy as np
import wave
import struct
import os


def encode_audio_lsb(audio_path: str, payload: bytes, output_path: str, bits_per_sample: int = 1) -> dict:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if bits_per_sample < 1 or bits_per_sample > 4:
        raise ValueError(f"bits_per_sample must be between 1 and 4, got {bits_per_sample}")
    
    if not payload:
        raise ValueError("Payload cannot be empty")
    
    try:
        with wave.open(audio_path, 'rb') as audio:
            params = audio.getparams()
            n_channels = params.nchannels
            sample_width = params.sampwidth
            frame_rate = params.framerate
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
            # Convert numpy uint8 to Python int before bitwise operations
            value = (int(b3) << 16) | (int(b2) << 8) | int(b1)
            # Convert unsigned 24-bit to signed if sign bit is set
            if value & 0x800000:
                value = value - 0x1000000
            samples[i] = value
    
    max_bytes = (len(samples) * bits_per_sample) // 8
    
    payload_length = len(payload)
    header_size = 4
    required_bytes = payload_length + header_size
    
    if required_bytes > max_bytes:
        raise ValueError(
            f"Payload too large for audio file.\n"
            f"Required: {required_bytes} bytes (payload: {payload_length} + header: {header_size})\n"
            f"Available: {max_bytes} bytes\n"
            f"Try using a longer audio file or increasing bits_per_sample (current: {bits_per_sample})"
        )
    
    if payload_length > 2**32 - 1:
        raise ValueError(f"Payload too large: {payload_length} bytes (max: {2**32 - 1})")
    
    length_bytes = struct.pack('>I', payload_length)
    full_payload = length_bytes + payload
    
    payload_bits = []
    for byte in full_payload:
        for i in range(8):
            payload_bits.append((byte >> (7 - i)) & 1)
    
    samples_copy = samples.copy()
    
    bit_mask = (1 << bits_per_sample) - 1
    
    if sample_width == 1:
        clear_mask = ~bit_mask & 0xFF
    elif sample_width == 2:
        clear_mask = ~bit_mask & 0xFFFF
    else:
        clear_mask = ~bit_mask & 0xFFFFFFFF
    
    bit_index = 0
    for i in range(len(samples_copy)):
        if bit_index >= len(payload_bits):
            break
        
        bits_to_embed = 0
        for j in range(bits_per_sample):
            if bit_index < len(payload_bits):
                bits_to_embed = (bits_to_embed << 1) | payload_bits[bit_index]
                bit_index += 1
            else:
                bits_to_embed = bits_to_embed << 1
        
        # Get current sample value
        sample_val = int(samples_copy[i])
        
        # For signed types, convert to unsigned for bitwise operations
        if sample_width == 1:
            # uint8 - already unsigned
            new_val = (sample_val & clear_mask) | bits_to_embed
        elif sample_width == 2:
            # int16 - convert to unsigned, do operation, convert back
            if sample_val < 0:
                sample_val = sample_val + 0x10000
            new_val = (sample_val & clear_mask) | bits_to_embed
            if new_val >= 0x8000:
                new_val = new_val - 0x10000
        else:
            # int32 (24-bit audio) - convert to unsigned, do operation, convert back to signed
            if sample_val < 0:
                sample_val = sample_val + 0x100000000
            new_val = (sample_val & clear_mask) | bits_to_embed
            # Convert back to signed int32 range
            if new_val >= 0x80000000:
                new_val = new_val - 0x100000000
        
        samples_copy[i] = new_val
    
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        with wave.open(output_path, 'wb') as output_audio:
            output_audio.setparams(params)
            if sample_width == 3:
                output_bytes = bytearray()
                for sample in samples_copy:
                    # Use .item() to extract Python int from numpy scalar
                    sample_val = sample.item() if hasattr(sample, 'item') else int(sample)
                    # Convert signed to unsigned 24-bit
                    if sample_val < 0:
                        sample_val = (sample_val + 0x1000000) & 0xFFFFFF
                    else:
                        sample_val = sample_val & 0xFFFFFF
                    # Extract 3 bytes (little-endian)
                    byte1 = sample_val & 0xFF
                    byte2 = (sample_val >> 8) & 0xFF
                    byte3 = (sample_val >> 16) & 0xFF
                    output_bytes.extend([byte1, byte2, byte3])
                output_audio.writeframes(bytes(output_bytes))
            else:
                output_audio.writeframes(samples_copy.tobytes())
    except Exception as e:
        raise IOError(f"Failed to save stego audio: {str(e)}")
    
    duration = n_frames / frame_rate
    
    return {
        'success': True,
        'payload_size': payload_length,
        'capacity_used': (required_bytes / max_bytes) * 100,
        'bits_per_sample': bits_per_sample,
        'channels': n_channels,
        'sample_rate': frame_rate,
        'duration': round(duration, 2),
        'sample_width': sample_width * 8,
        'max_capacity_bytes': max_bytes
    }
