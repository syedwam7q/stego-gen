import requests
import json
import os
import time
from typing import Dict, Optional


def get_grok_recommendation(image_stats: dict, payload_size: int, goal: str = "max_invisibility") -> dict:
    api_key = os.getenv("GROK_API_KEY")
    
    if not api_key or api_key.strip() == "":
        print("Info: No Grok API key found. Using fallback algorithm-based recommendation.")
        return get_fallback_recommendation(image_stats, payload_size)
    
    suitability_info = image_stats.get('suitability', 'Unknown')
    capacity_1bit = image_stats.get('capacity_at_1bit', image_stats.get('max_capacity_bytes', 0))
    capacity_2bit = image_stats.get('capacity_at_2bit', capacity_1bit * 2)
    capacity_4bit = image_stats.get('capacity_at_4bit', capacity_1bit * 4)
    
    capacity_ratio_1bit = (payload_size / capacity_1bit * 100) if capacity_1bit > 0 else 0
    capacity_ratio_2bit = (payload_size / capacity_2bit * 100) if capacity_2bit > 0 else 0
    
    prompt = f"""You are an expert in steganography and image analysis. Analyze the following image statistics and recommend the optimal LSB embedding parameters.

IMAGE ANALYSIS:
- Dimensions: {image_stats['width']}x{image_stats['height']} pixels
- Format: {image_stats['format']}
- Total Pixels: {image_stats.get('total_pixels', 'N/A')}

QUALITY METRICS:
- Entropy: {image_stats['entropy']} bits (higher = more random/complex)
- Variance: {image_stats['variance']} (pixel variation level)
- Edge Density: {image_stats['edge_density']} (texture richness)
- Texture Score: {image_stats['texture_score']} (combined complexity)
- Noise Level: {image_stats['noise_level']}
- Suitability: {suitability_info}

CAPACITY ANALYSIS:
- Payload Size: {payload_size} bytes ({payload_size / 1024:.2f} KB)
- Capacity at 1 bit/channel: {capacity_1bit} bytes ({capacity_ratio_1bit:.1f}% used)
- Capacity at 2 bits/channel: {capacity_2bit} bytes ({capacity_ratio_2bit:.1f}% used)
- Capacity at 4 bits/channel: {capacity_4bit} bytes

USER GOAL: {goal}

Based on this analysis, recommend the optimal embedding strategy. Consider:
1. Higher bits_per_channel = more capacity but more detectable
2. Complex/noisy images can hide more bits per channel
3. Smooth images need lower bits_per_channel for invisibility
4. Balance capacity needs with detection risk

Respond with ONLY valid JSON (no markdown, no extra text):
{{
  "algorithm": "LSB",
  "bits_per_channel": 1,
  "region_hint": "description of where to embed",
  "explanation": "detailed reasoning for this recommendation",
  "confidence": 0.85,
  "detection_risk": "low/medium/high"
}}"""

    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a steganography and image processing expert. Respond ONLY with valid JSON, no markdown formatting."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-beta",
                    "temperature": 0.2,
                    "max_tokens": 500
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' not in result or len(result['choices']) == 0:
                    print(f"Warning: Unexpected API response structure")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return get_fallback_recommendation(image_stats, payload_size)
                
                content = result['choices'][0]['message']['content']
                
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                elif content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                try:
                    recommendation = json.loads(content)
                except json.JSONDecodeError as je:
                    print(f"Warning: Failed to parse AI response as JSON: {je}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return get_fallback_recommendation(image_stats, payload_size)
                
                bits_per_channel = recommendation.get('bits_per_channel', 1)
                if not isinstance(bits_per_channel, int):
                    try:
                        bits_per_channel = int(bits_per_channel)
                    except:
                        bits_per_channel = 1
                bits_per_channel = min(max(bits_per_channel, 1), 4)
                
                return {
                    'algorithm': recommendation.get('algorithm', 'LSB'),
                    'bits_per_channel': bits_per_channel,
                    'region_hint': recommendation.get('region_hint', 'distributed embedding'),
                    'explanation': recommendation.get('explanation', 'AI-generated recommendation'),
                    'confidence': min(max(float(recommendation.get('confidence', 0.8)), 0.0), 1.0),
                    'detection_risk': recommendation.get('detection_risk', 'unknown'),
                    'source': 'grok'
                }
            elif response.status_code == 401:
                print(f"Error: Invalid Grok API key. Using fallback recommendation.")
                return get_fallback_recommendation(image_stats, payload_size)
            elif response.status_code == 429:
                print(f"Warning: Rate limited by API. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            else:
                print(f"Warning: API returned status {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
            
            return get_fallback_recommendation(image_stats, payload_size)
                
        except requests.exceptions.Timeout:
            print(f"Warning: API request timed out. Attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
        except requests.exceptions.RequestException as e:
            print(f"Warning: API request failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
        except Exception as e:
            print(f"Error in Grok API call: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
    
    return get_fallback_recommendation(image_stats, payload_size)


def get_fallback_recommendation(image_stats: dict, payload_size: int) -> dict:
    max_capacity = image_stats.get('max_capacity_bytes', 1)
    if max_capacity == 0:
        max_capacity = 1
    
    capacity_ratio = payload_size / max_capacity
    
    texture_score = image_stats.get('texture_score', 0)
    entropy = image_stats.get('entropy', 0)
    variance = image_stats.get('variance', 0)
    edge_density = image_stats.get('edge_density', 0)
    
    complexity_score = (
        (entropy / 8.0) * 0.3 +
        (min(variance / 2000, 1.0)) * 0.3 +
        (min(edge_density / 0.2, 1.0)) * 0.2 +
        (min(texture_score / 200, 1.0)) * 0.2
    )
    
    if capacity_ratio > 0.9:
        bits_per_channel = 4
        detection_risk = "high"
        explanation = "Very high capacity needed (>90%). Using 4 bits per channel. Warning: This is highly detectable."
    elif capacity_ratio > 0.75:
        bits_per_channel = 3
        detection_risk = "medium-high"
        explanation = "High capacity needed (75-90%). Using 3 bits per channel for sufficient space."
    elif capacity_ratio > 0.5:
        bits_per_channel = 2
        detection_risk = "medium"
        explanation = "Moderate capacity needed (50-75%). Using 2 bits per channel for balance."
    elif capacity_ratio > 0.25:
        if complexity_score < 0.3:
            bits_per_channel = 1
            detection_risk = "low"
            explanation = "Low image complexity detected. Using 1 bit per channel for maximum invisibility despite moderate capacity needs."
        else:
            bits_per_channel = 2
            detection_risk = "low-medium"
            explanation = "Moderate capacity with good image complexity. Using 2 bits per channel."
    else:
        bits_per_channel = 1
        detection_risk = "low"
        explanation = "Low capacity needed (<25%). Using 1 bit per channel for maximum invisibility and security."
    
    if complexity_score > 0.7:
        if texture_score > 100:
            region_hint = "Excellent image complexity. Embed throughout entire image - changes will be imperceptible."
        else:
            region_hint = "High complexity image. Distributed embedding recommended across all regions."
    elif complexity_score > 0.4:
        region_hint = "Moderate texture. Focus on textured regions and edges. Avoid large uniform areas."
    elif complexity_score > 0.2:
        region_hint = "Low texture image. Concentrate on edges and any textured regions. Avoid smooth areas."
    else:
        region_hint = "Very smooth image. Embedding will be challenging. Seek textured regions if any, or consider using a different carrier image."
    
    confidence = 0.6 + (complexity_score * 0.2)
    
    return {
        'algorithm': 'LSB',
        'bits_per_channel': bits_per_channel,
        'region_hint': region_hint,
        'explanation': explanation,
        'confidence': round(confidence, 2),
        'detection_risk': detection_risk,
        'source': 'fallback',
        'complexity_score': round(complexity_score, 2)
    }
