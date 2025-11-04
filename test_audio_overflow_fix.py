#!/usr/bin/env python3
"""
Test script to verify audio encoding/decoding overflow fix
Tests all sample widths (8-bit, 16-bit, 24-bit) with various bit depths
"""

import os
import sys
import numpy as np
import wave

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stego.audio_wav_encoder import encode_audio_lsb
from stego.audio_wav_decoder import decode_audio_lsb


def create_test_audio(filename, sample_width, duration=1.0, sample_rate=44100):
    """Create a test audio file with specified sample width"""
    n_channels = 1
    n_frames = int(sample_rate * duration)
    
    # Generate sine wave
    frequency = 440  # A4 note
    t = np.linspace(0, duration, n_frames, endpoint=False)
    wave_data = np.sin(2 * np.pi * frequency * t)
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        
        if sample_width == 1:
            # 8-bit unsigned
            samples = ((wave_data + 1) * 127.5).astype(np.uint8)
            wav_file.writeframes(samples.tobytes())
        elif sample_width == 2:
            # 16-bit signed
            samples = (wave_data * 32767).astype(np.int16)
            wav_file.writeframes(samples.tobytes())
        elif sample_width == 3:
            # 24-bit signed (stored as bytes)
            samples = (wave_data * 8388607).astype(np.int32)
            output_bytes = bytearray()
            for sample in samples:
                # Clamp to 24-bit range
                if sample < -8388608:
                    sample = -8388608
                elif sample > 8388607:
                    sample = 8388607
                # Convert to unsigned for byte extraction
                if sample < 0:
                    sample = (sample + 0x1000000) & 0xFFFFFF
                else:
                    sample = sample & 0xFFFFFF
                # Little-endian byte order
                byte1 = sample & 0xFF
                byte2 = (sample >> 8) & 0xFF
                byte3 = (sample >> 16) & 0xFF
                output_bytes.extend([byte1, byte2, byte3])
            wav_file.writeframes(bytes(output_bytes))


def test_encoding_decoding(sample_width, bits_per_sample):
    """Test encoding and decoding for given sample width and bits per sample"""
    sample_width_bits = sample_width * 8
    
    print(f"\n{'='*60}")
    print(f"Testing {sample_width_bits}-bit audio with {bits_per_sample} bits per sample")
    print(f"{'='*60}")
    
    # Create test audio
    carrier_path = f"backend/test_files/test_audio_{sample_width_bits}bit.wav"
    create_test_audio(carrier_path, sample_width)
    print(f"✓ Created test audio: {carrier_path}")
    
    # Test payload with various patterns
    test_payloads = [
        b"Hello, World!",
        b"A" * 100,  # Repeated pattern
        bytes(range(256)),  # All byte values
        b"Test message with special chars: @#$%^&*()",
    ]
    
    for idx, payload in enumerate(test_payloads):
        print(f"\n  Test {idx + 1}: Payload size = {len(payload)} bytes")
        
        try:
            # Encode
            output_path = f"backend/outputs/test_overflow_{sample_width_bits}bit_{bits_per_sample}bps_{idx}.wav"
            result = encode_audio_lsb(carrier_path, payload, output_path, bits_per_sample)
            print(f"    ✓ Encoding succeeded")
            print(f"      - Capacity used: {result['capacity_used']:.2f}%")
            print(f"      - Max capacity: {result['max_capacity_bytes']} bytes")
            
            # Decode
            decoded = decode_audio_lsb(output_path, bits_per_sample)
            print(f"    ✓ Decoding succeeded")
            
            # Verify
            if decoded == payload:
                print(f"    ✓ Payload verification PASSED")
            else:
                print(f"    ✗ Payload verification FAILED")
                print(f"      Expected: {payload[:50]}...")
                print(f"      Got:      {decoded[:50]}...")
                return False
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n✓ All tests passed for {sample_width_bits}-bit audio!")
    return True


def main():
    print("="*60)
    print("Audio Encoding/Decoding Overflow Fix Test")
    print("="*60)
    
    # Ensure test directories exist
    os.makedirs("backend/test_files", exist_ok=True)
    os.makedirs("backend/outputs", exist_ok=True)
    
    test_cases = [
        (1, 1),  # 8-bit, 1 bit per sample
        (1, 2),  # 8-bit, 2 bits per sample
        (2, 1),  # 16-bit, 1 bit per sample
        (2, 2),  # 16-bit, 2 bits per sample
        (2, 4),  # 16-bit, 4 bits per sample
        (3, 1),  # 24-bit, 1 bit per sample (CRITICAL - this was failing)
        (3, 2),  # 24-bit, 2 bits per sample
        (3, 4),  # 24-bit, 4 bits per sample
    ]
    
    all_passed = True
    for sample_width, bits_per_sample in test_cases:
        if not test_encoding_decoding(sample_width, bits_per_sample):
            all_passed = False
            break
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Audio overflow bug is FIXED!")
    else:
        print("❌ SOME TESTS FAILED - Bug still exists")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())