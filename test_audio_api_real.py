#!/usr/bin/env python3
"""
Test real audio API endpoint to verify overflow fix
"""

import requests
import os
import sys
import wave
import numpy as np

def create_test_audio(filename, sample_width=3, duration=1.0):
    """Create test audio with specified sample width"""
    sample_rate = 44100
    n_frames = int(sample_rate * duration)
    frequency = 440
    t = np.linspace(0, duration, n_frames, endpoint=False)
    wave_data = np.sin(2 * np.pi * frequency * t)
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        
        if sample_width == 3:
            # 24-bit audio - the problematic one
            samples = (wave_data * 8388607).astype(np.int32)
            output_bytes = bytearray()
            for sample in samples:
                if sample < -8388608:
                    sample = -8388608
                elif sample > 8388607:
                    sample = 8388607
                if sample < 0:
                    sample = (sample + 0x1000000) & 0xFFFFFF
                else:
                    sample = sample & 0xFFFFFF
                byte1 = sample & 0xFF
                byte2 = (sample >> 8) & 0xFF
                byte3 = (sample >> 16) & 0xFF
                output_bytes.extend([byte1, byte2, byte3])
            wav_file.writeframes(bytes(output_bytes))

def test_audio_api(base_url="http://localhost:8000"):
    """Test the audio encoding API endpoint"""
    print("Testing Audio API Endpoint")
    print("=" * 60)
    
    # Create test audio
    test_file = "test_24bit_audio_api.wav"
    create_test_audio(test_file, sample_width=3)
    print(f"✓ Created 24-bit test audio: {test_file}")
    
    # Test payload
    payload_text = "Hello from 24-bit audio! This is testing the overflow fix. " * 10
    
    try:
        with open(test_file, 'rb') as f:
            files = {'carrier': (test_file, f, 'audio/wav')}
            data = {
                'payload_text': payload_text,
                'bits_per_sample': 2,
                'encryption_key': ''
            }
            
            print(f"\nSending POST request to {base_url}/api/encode/audio")
            print(f"  Payload size: {len(payload_text)} bytes")
            print(f"  Bits per sample: 2")
            
            response = requests.post(f"{base_url}/api/encode/audio", files=files, data=data)
            
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS! Audio encoding worked!")
                print(f"\nResponse data:")
                print(f"  - File ID: {result.get('file_id')}")
                print(f"  - Output: {result.get('output_filename')}")
                print(f"  - Capacity used: {result.get('encode_info', {}).get('capacity_used', 0):.2f}%")
                print(f"  - Sample width: {result.get('encode_info', {}).get('sample_width')} bits")
                print(f"  - SNR: {result.get('metrics', {}).get('snr', 'N/A')}")
                return True
            else:
                print(f"❌ FAILED with status {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {base_url}")
        print(f"Make sure the backend server is running:")
        print(f"  cd backend && python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n✓ Cleaned up test file")

if __name__ == "__main__":
    print("\n⚠️  Make sure backend server is running before this test!")
    print("   Run: cd backend && python main.py\n")
    
    input("Press Enter to start API test (or Ctrl+C to cancel)...")
    
    success = test_audio_api()
    sys.exit(0 if success else 1)