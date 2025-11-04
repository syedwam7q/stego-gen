#!/usr/bin/env python3
"""
Test script to verify audio encoding/decoding fix for 24-bit audio
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stego.audio_wav_encoder import encode_audio_lsb
from stego.audio_wav_decoder import decode_audio_lsb

def test_audio_encoding():
    """Test audio encoding with a sample message"""
    audio_file = 'backend/test_files/test_audio.wav'
    output_file = 'backend/outputs/test_audio_stego.wav'
    
    if not os.path.exists(audio_file):
        print(f"❌ Test audio file not found: {audio_file}")
        return False
    
    # Test message
    test_message = b"Hello, this is a test message for 24-bit audio steganography!"
    
    try:
        print("🔧 Testing audio encoding...")
        result = encode_audio_lsb(
            audio_path=audio_file,
            payload=test_message,
            output_path=output_file,
            bits_per_sample=2
        )
        
        print(f"✅ Encoding successful!")
        print(f"   - Payload size: {result['payload_size']} bytes")
        print(f"   - Sample width: {result['sample_width']} bits")
        print(f"   - Capacity used: {result['capacity_used']:.2f}%")
        print(f"   - Duration: {result['duration']} seconds")
        
        print("\n🔧 Testing audio decoding...")
        decoded_message = decode_audio_lsb(
            audio_path=output_file,
            bits_per_sample=2
        )
        
        if decoded_message == test_message:
            print(f"✅ Decoding successful! Message matches.")
            print(f"   Original:  {test_message.decode('utf-8')}")
            print(f"   Decoded:   {decoded_message.decode('utf-8')}")
            return True
        else:
            print(f"❌ Decoding failed: Message mismatch")
            print(f"   Original: {test_message}")
            print(f"   Decoded:  {decoded_message}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Audio Encoding/Decoding Test")
    print("=" * 60)
    
    success = test_audio_encoding()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)