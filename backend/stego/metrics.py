import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import math
import os
import wave
import cv2


def calculate_psnr(original_path: str, stego_path: str) -> float:
    if not os.path.exists(original_path):
        raise FileNotFoundError(f"Original image not found: {original_path}")
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego image not found: {stego_path}")
    
    try:
        original = Image.open(original_path).convert('RGB')
        stego = Image.open(stego_path).convert('RGB')
    except Exception as e:
        raise ValueError(f"Failed to open images: {str(e)}")
    
    if original.size != stego.size:
        raise ValueError(
            f"Image dimensions don't match. Original: {original.size}, Stego: {stego.size}"
        )
    
    original_array = np.array(original).astype(np.float64)
    stego_array = np.array(stego).astype(np.float64)
    
    mse = np.mean((original_array - stego_array) ** 2)
    
    if mse == 0:
        return 100.0
    
    if mse < 0:
        raise ValueError(f"Invalid MSE value: {mse}")
    
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    
    return round(psnr, 2)


def calculate_ssim(original_path: str, stego_path: str) -> float:
    if not os.path.exists(original_path):
        raise FileNotFoundError(f"Original image not found: {original_path}")
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego image not found: {stego_path}")
    
    try:
        original = Image.open(original_path).convert('RGB')
        stego = Image.open(stego_path).convert('RGB')
    except Exception as e:
        raise ValueError(f"Failed to open images: {str(e)}")
    
    if original.size != stego.size:
        raise ValueError(
            f"Image dimensions don't match. Original: {original.size}, Stego: {stego.size}"
        )
    
    original_array = np.array(original)
    stego_array = np.array(stego)
    
    try:
        ssim_value = ssim(original_array, stego_array, channel_axis=2, data_range=255)
    except Exception as e:
        raise ValueError(f"SSIM calculation failed: {str(e)}")
    
    return round(float(ssim_value), 4)


def calculate_mse(original_path: str, stego_path: str) -> float:
    if not os.path.exists(original_path) or not os.path.exists(stego_path):
        raise FileNotFoundError("One or both images not found")
    
    original = Image.open(original_path).convert('RGB')
    stego = Image.open(stego_path).convert('RGB')
    
    if original.size != stego.size:
        raise ValueError("Image dimensions don't match")
    
    original_array = np.array(original).astype(np.float64)
    stego_array = np.array(stego).astype(np.float64)
    
    mse = np.mean((original_array - stego_array) ** 2)
    return round(float(mse), 4)


def assess_quality(psnr: float, ssim: float) -> dict:
    if psnr >= 40:
        psnr_quality = "Excellent"
        psnr_desc = "Virtually invisible to human eye"
    elif psnr >= 30:
        psnr_quality = "Good"
        psnr_desc = "Minor differences, generally imperceptible"
    elif psnr >= 20:
        psnr_quality = "Fair"
        psnr_desc = "Noticeable differences under scrutiny"
    else:
        psnr_quality = "Poor"
        psnr_desc = "Significant visible differences"
    
    if ssim >= 0.95:
        ssim_quality = "Excellent"
        ssim_desc = "Structural similarity nearly perfect"
    elif ssim >= 0.90:
        ssim_quality = "Good"
        ssim_desc = "Minor structural differences"
    elif ssim >= 0.80:
        ssim_quality = "Fair"
        ssim_desc = "Noticeable structural changes"
    else:
        ssim_quality = "Poor"
        ssim_desc = "Significant structural degradation"
    
    return {
        'psnr_quality': psnr_quality,
        'psnr_description': psnr_desc,
        'ssim_quality': ssim_quality,
        'ssim_description': ssim_desc
    }


def calculate_metrics(original_path: str, stego_path: str) -> dict:
    try:
        psnr = calculate_psnr(original_path, stego_path)
        ssim_val = calculate_ssim(original_path, stego_path)
        mse = calculate_mse(original_path, stego_path)
        
        quality = assess_quality(psnr, ssim_val)
        
        return {
            'psnr': psnr,
            'ssim': ssim_val,
            'mse': mse,
            'psnr_quality': quality['psnr_quality'],
            'psnr_description': quality['psnr_description'],
            'ssim_quality': quality['ssim_quality'],
            'ssim_description': quality['ssim_description']
        }
    except Exception as e:
        raise RuntimeError(f"Metrics calculation failed: {str(e)}")


def calculate_audio_snr(original_path: str, stego_path: str) -> float:
    if not os.path.exists(original_path):
        raise FileNotFoundError(f"Original audio not found: {original_path}")
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego audio not found: {stego_path}")
    
    try:
        with wave.open(original_path, 'rb') as original_wav:
            original_params = original_wav.getparams()
            original_data = original_wav.readframes(original_params.nframes)
        
        with wave.open(stego_path, 'rb') as stego_wav:
            stego_params = stego_wav.getparams()
            stego_data = stego_wav.readframes(stego_params.nframes)
    except Exception as e:
        raise ValueError(f"Failed to open audio files: {str(e)}")
    
    if original_params.sampwidth != stego_params.sampwidth:
        raise ValueError("Audio sample widths don't match")
    
    if original_params.sampwidth == 1:
        original_samples = np.frombuffer(original_data, dtype=np.uint8).astype(np.float64)
        stego_samples = np.frombuffer(stego_data, dtype=np.uint8).astype(np.float64)
    elif original_params.sampwidth == 2:
        original_samples = np.frombuffer(original_data, dtype=np.int16).astype(np.float64)
        stego_samples = np.frombuffer(stego_data, dtype=np.int16).astype(np.float64)
    else:
        raise ValueError(f"Unsupported sample width: {original_params.sampwidth}")
    
    min_len = min(len(original_samples), len(stego_samples))
    original_samples = original_samples[:min_len]
    stego_samples = stego_samples[:min_len]
    
    signal_power = np.mean(original_samples ** 2)
    noise = stego_samples - original_samples
    noise_power = np.mean(noise ** 2)
    
    if noise_power == 0:
        return 100.0
    
    if signal_power == 0:
        return 0.0
    
    snr = 10 * math.log10(signal_power / noise_power)
    return round(snr, 2)


def calculate_audio_metrics(original_path: str, stego_path: str) -> dict:
    try:
        snr = calculate_audio_snr(original_path, stego_path)
        
        if snr >= 40:
            quality = "Excellent"
            description = "Virtually inaudible changes"
        elif snr >= 30:
            quality = "Good"
            description = "Minor differences, generally imperceptible"
        elif snr >= 20:
            quality = "Fair"
            description = "Noticeable differences under scrutiny"
        else:
            quality = "Poor"
            description = "Significant audible differences"
        
        return {
            'snr': snr,
            'quality': quality,
            'description': description
        }
    except Exception as e:
        raise RuntimeError(f"Audio metrics calculation failed: {str(e)}")


def calculate_video_psnr(original_path: str, stego_path: str, max_frames: int = 100) -> float:
    if not os.path.exists(original_path):
        raise FileNotFoundError(f"Original video not found: {original_path}")
    if not os.path.exists(stego_path):
        raise FileNotFoundError(f"Stego video not found: {stego_path}")
    
    try:
        original_cap = cv2.VideoCapture(original_path)
        stego_cap = cv2.VideoCapture(stego_path)
        
        if not original_cap.isOpened() or not stego_cap.isOpened():
            raise ValueError("Failed to open video files")
        
        total_mse = 0
        frame_count = 0
        frames_to_check = max_frames
        
        while frame_count < frames_to_check:
            ret1, original_frame = original_cap.read()
            ret2, stego_frame = stego_cap.read()
            
            if not ret1 or not ret2:
                break
            
            if original_frame.shape != stego_frame.shape:
                raise ValueError("Video frame dimensions don't match")
            
            original_array = original_frame.astype(np.float64)
            stego_array = stego_frame.astype(np.float64)
            
            mse = np.mean((original_array - stego_array) ** 2)
            total_mse += mse
            frame_count += 1
        
        original_cap.release()
        stego_cap.release()
        
        if frame_count == 0:
            raise ValueError("No frames to compare")
        
        avg_mse = total_mse / frame_count
        
        if avg_mse == 0:
            return 100.0
        
        max_pixel = 255.0
        psnr = 20 * math.log10(max_pixel / math.sqrt(avg_mse))
        
        return round(psnr, 2)
        
    except Exception as e:
        if 'original_cap' in locals():
            original_cap.release()
        if 'stego_cap' in locals():
            stego_cap.release()
        raise ValueError(f"Video metrics calculation failed: {str(e)}")


def calculate_video_metrics(original_path: str, stego_path: str, max_frames: int = 100) -> dict:
    try:
        psnr = calculate_video_psnr(original_path, stego_path, max_frames)
        
        if psnr >= 40:
            quality = "Excellent"
            description = "Virtually invisible changes"
        elif psnr >= 30:
            quality = "Good"
            description = "Minor differences, generally imperceptible"
        elif psnr >= 20:
            quality = "Fair"
            description = "Noticeable differences under scrutiny"
        else:
            quality = "Poor"
            description = "Significant visible differences"
        
        return {
            'psnr': psnr,
            'quality': quality,
            'description': description
        }
    except Exception as e:
        raise RuntimeError(f"Video metrics calculation failed: {str(e)}")
