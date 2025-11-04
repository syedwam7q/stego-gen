import numpy as np
from PIL import Image
import cv2
from scipy.stats import entropy
import os


def analyze_image(image_path: str) -> dict:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Failed to open image: {str(e)}")
    
    original_format = img.format
    original_mode = img.mode
    
    if img.width < 10 or img.height < 10:
        raise ValueError(
            f"Image too small: {img.width}x{img.height}. "
            "Minimum recommended size: 100x100 pixels"
        )
    
    if img.width * img.height < 10000:
        print(f"Warning: Small image ({img.width}x{img.height}). Limited capacity for hiding data.")
    
    if img.mode not in ['RGB', 'RGBA', 'L']:
        try:
            img = img.convert('RGB')
        except Exception as e:
            raise ValueError(f"Failed to convert image to RGB: {str(e)}")
    elif img.mode == 'RGBA':
        img = img.convert('RGB')
    elif img.mode == 'L':
        img = img.convert('RGB')
    
    try:
        img_array = np.array(img)
    except Exception as e:
        raise ValueError(f"Failed to convert image to array: {str(e)}")
    
    if len(img_array.shape) != 3:
        raise ValueError(f"Invalid image dimensions: {img_array.shape}")
    
    height, width, channels = img_array.shape
    
    if channels != 3:
        raise ValueError(f"Image must have 3 color channels (RGB), got {channels}")
    
    try:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    except Exception as e:
        raise ValueError(f"Failed to convert to grayscale: {str(e)}")
    
    hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
    hist_sum = hist.sum()
    if hist_sum > 0:
        hist = hist / hist_sum
    img_entropy = entropy(hist + 1e-10, base=2)
    
    variance = np.var(gray)
    
    try:
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size if edges.size > 0 else 0.0
    except Exception as e:
        print(f"Warning: Edge detection failed: {e}")
        edge_density = 0.0
    
    texture_score = variance * edge_density
    
    try:
        noise_level = estimate_noise(gray)
    except Exception as e:
        print(f"Warning: Noise estimation failed: {e}")
        noise_level = 0.0
    
    uniformity = calculate_uniformity(gray)
    smoothness = calculate_smoothness(gray)
    
    max_capacity_1bit = (width * height * 3) // 8
    max_capacity_2bit = (width * height * 3 * 2) // 8
    max_capacity_4bit = (width * height * 3 * 4) // 8
    
    suitability = assess_suitability(img_entropy, variance, edge_density, noise_level)
    
    return {
        'width': width,
        'height': height,
        'format': original_format or 'Unknown',
        'original_mode': original_mode,
        'entropy': round(float(img_entropy), 2),
        'variance': round(float(variance), 2),
        'edge_density': round(float(edge_density), 4),
        'texture_score': round(float(texture_score), 2),
        'noise_level': round(float(noise_level), 2),
        'uniformity': round(float(uniformity), 4),
        'smoothness': round(float(smoothness), 4),
        'total_pixels': width * height,
        'max_capacity_bytes': max_capacity_1bit,
        'capacity_at_1bit': max_capacity_1bit,
        'capacity_at_2bit': max_capacity_2bit,
        'capacity_at_4bit': max_capacity_4bit,
        'suitability': suitability
    }


def estimate_noise(gray_img: np.ndarray) -> float:
    if gray_img.size == 0:
        return 0.0
    
    laplacian = cv2.Laplacian(gray_img, cv2.CV_64F)
    noise = np.std(laplacian)
    
    return float(noise)


def calculate_uniformity(gray_img: np.ndarray) -> float:
    if gray_img.size == 0:
        return 0.0
    
    hist, _ = np.histogram(gray_img.flatten(), bins=256, range=(0, 256))
    hist = hist / hist.sum() if hist.sum() > 0 else hist
    
    uniformity = np.sum(hist ** 2)
    return float(uniformity)


def calculate_smoothness(gray_img: np.ndarray) -> float:
    if gray_img.size == 0:
        return 0.0
    
    variance = np.var(gray_img)
    smoothness = 1 - (1 / (1 + variance))
    return float(smoothness)


def assess_suitability(entropy: float, variance: float, edge_density: float, noise: float) -> str:
    score = 0
    
    if entropy > 6.5:
        score += 2
    elif entropy > 5.5:
        score += 1
    
    if variance > 1000:
        score += 2
    elif variance > 500:
        score += 1
    
    if edge_density > 0.1:
        score += 2
    elif edge_density > 0.05:
        score += 1
    
    if noise > 10:
        score += 1
    
    if score >= 6:
        return "Excellent - High texture, complex image ideal for steganography"
    elif score >= 4:
        return "Good - Sufficient complexity for hiding data"
    elif score >= 2:
        return "Moderate - Low texture, data may be more detectable"
    else:
        return "Poor - Very smooth image, embedding will be more visible"
