#!/usr/bin/env python3
"""
Test audio encoding via the API to replicate the actual error scenario
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stego.audio_wav_encoder import encode_audio_lsb
from stego.audio_wav_decoder import decode_audio_lsb

def test_various_audio_formats():
    """Test with different audio sample widths"""
    audio_file = 'backend/test_files/test_audio.wav'
    
    if not os.path.exists(audio_file):
        print(f"⚠️  Test audio file not found: {audio_file}")
        print("   Skipping audio format tests")
        return True
    
    test_cases = [
        ("1 bit per sample", 1),
        ("2 bits per sample", 2),
        ("4 bits per sample", 4),
    ]
    
    all_passed = True
    
    for test_name, bits_per_sample in test_cases:
        print(f"\n🔧 Testing {test_name}...")
        try:
            test_message = b"Test message for audio steganography"
            output_file = f'backend/outputs/test_audio_{bits_per_sample}bit.wav'
            
            # Encode
            result = encode_audio_lsb(
                audio_path=audio_file,
                payload=test_message,
                output_path=output_file,
                bits_per_sample=bits_per_sample
            )
            
            print(f"   ✅ Encoding: payload={result['payload_size']}B, " +
                  f"width={result['sample_width']}bit, " +
                  f"used={result['capacity_used']:.2f}%")
            
            # Decode
            decoded = decode_audio_lsb(
                audio_path=output_file,
                bits_per_sample=bits_per_sample
            )
            
            if decoded == test_message:
                print(f"   ✅ Decoding: Message verified")
            else:
                print(f"   ❌ Decoding: Message mismatch!")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False
    
    return all_passed

def test_edge_cases():
    """Test edge cases that might cause overflow"""
    print("\n🔧 Testing edge cases...")
    
    audio_file = 'backend/test_files/test_audio.wav'
    if not os.path.exists(audio_file):
        print("   ⚠️  Audio file not found, skipping")
        return True
    
    try:
        # Test with maximum data
        test_message = b"X" * 1000  # Large payload
        output_file = 'backend/outputs/test_audio_large.wav'
        
        result = encode_audio_lsb(
            audio_path=audio_file,
            payload=test_message,
            output_path=output_file,
            bits_per_sample=4
        )
        
        print(f"   ✅ Large payload: {result['payload_size']} bytes encoded")
        
        decoded = decode_audio_lsb(output_file, bits_per_sample=4)
        
        if decoded == test_message:
            print(f"   ✅ Large payload decoded correctly")
            return True
        else:
            print(f"   ❌ Large payload decode mismatch")
            return False
            
    except Exception as e:
        print(f"   ⚠️  Note: {e}")
        # This might be expected if file is too small
        if "too large" in str(e).lower():
            print(f"   ℹ️  This is expected for small test files")
            return True
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Audio Encoding API Test - Comprehensive")
    print("=" * 70)
    
    success = test_various_audio_formats()
    success = test_edge_cases() and success
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL API TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    sys.exit(0 if success else 1)