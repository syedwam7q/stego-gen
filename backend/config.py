import os
from typing import Dict, Any


ALGORITHM_PROFILES = {
    'stealth': {
        'name': 'Maximum Stealth',
        'description': 'Minimal detectability, lower capacity',
        'lsb': {'bits_per_channel': 1},
        'dct': {'strength': 5.0},
        'dwt': {'strength': 0.05, 'wavelet': 'haar'},
        'audio': {'bits_per_sample': 1},
        'video': {'bits_per_channel': 1, 'frame_skip': 2}
    },
    'balanced': {
        'name': 'Balanced',
        'description': 'Good balance between capacity and stealth',
        'lsb': {'bits_per_channel': 2},
        'dct': {'strength': 10.0},
        'dwt': {'strength': 0.1, 'wavelet': 'haar'},
        'audio': {'bits_per_sample': 2},
        'video': {'bits_per_channel': 2, 'frame_skip': 1}
    },
    'capacity': {
        'name': 'Maximum Capacity',
        'description': 'Higher capacity, more detectable',
        'lsb': {'bits_per_channel': 4},
        'dct': {'strength': 20.0},
        'dwt': {'strength': 0.2, 'wavelet': 'db1'},
        'audio': {'bits_per_sample': 4},
        'video': {'bits_per_channel': 4, 'frame_skip': 1}
    }
}


SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
SUPPORTED_AUDIO_FORMATS = ['.wav']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']

MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
MAX_PAYLOAD_SIZE_MB = int(os.getenv('MAX_PAYLOAD_SIZE_MB', '10'))

UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'outputs')

GROK_API_KEY = os.getenv('GROK_API_KEY', '')


def get_profile(profile_name: str) -> Dict[str, Any]:
    if profile_name not in ALGORITHM_PROFILES:
        raise ValueError(f"Unknown profile: {profile_name}. Available: {', '.join(ALGORITHM_PROFILES.keys())}")
    
    return ALGORITHM_PROFILES[profile_name]


def get_algorithm_params(profile_name: str, algorithm: str) -> Dict[str, Any]:
    profile = get_profile(profile_name)
    
    if algorithm not in profile:
        raise ValueError(f"Algorithm {algorithm} not found in profile {profile_name}")
    
    return profile[algorithm]


def is_supported_format(filename: str, file_type: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    
    if file_type == 'image':
        return ext in SUPPORTED_IMAGE_FORMATS
    elif file_type == 'audio':
        return ext in SUPPORTED_AUDIO_FORMATS
    elif file_type == 'video':
        return ext in SUPPORTED_VIDEO_FORMATS
    
    return False
