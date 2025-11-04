"""
AI Explainer Module - Provides contextual AI explanations and learning assistance
"""
import requests
import json
import os
from typing import Dict, Optional, List


class AIExplainer:
    """
    Provides AI-powered explanations and learning assistance for steganography concepts
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.model = "grok-beta"
        self.conversation_history: List[Dict] = []
    
    def explain_algorithm_choice(self, algorithm: str, image_stats: dict, recommendation: dict) -> str:
        """Explain why a specific algorithm was recommended"""
        
        if not self.api_key:
            return self._fallback_algorithm_explanation(algorithm, image_stats, recommendation)
        
        prompt = f"""You are a steganography expert teaching a user about algorithm selection.

SELECTED ALGORITHM: {algorithm}
IMAGE CHARACTERISTICS:
- Dimensions: {image_stats.get('width')}x{image_stats.get('height')}
- Entropy: {image_stats.get('entropy')} (complexity)
- Texture Score: {image_stats.get('texture_score')}
- Variance: {image_stats.get('variance')}
- Edge Density: {image_stats.get('edge_density')}

AI RECOMMENDATION:
- Bits per channel: {recommendation.get('bits_per_channel')}
- Detection Risk: {recommendation.get('detection_risk')}
- Confidence: {recommendation.get('confidence')}

Explain in 2-3 sentences why this algorithm and these settings are optimal for this image. 
Make it educational and easy to understand for someone learning steganography.
Focus on the relationship between image characteristics and algorithm choice."""

        try:
            response = self._call_grok_api(prompt, temperature=0.3)
            return response.strip()
        except Exception as e:
            print(f"AI Explainer error: {e}")
            return self._fallback_algorithm_explanation(algorithm, image_stats, recommendation)
    
    def explain_security_risk(self, metrics: dict, algorithm: str, settings: dict) -> Dict:
        """Provide detailed security risk analysis and mitigation suggestions"""
        
        if not self.api_key:
            return self._fallback_security_analysis(metrics, algorithm, settings)
        
        prompt = f"""You are a security expert analyzing steganography risks.

ALGORITHM: {algorithm}
SETTINGS: {json.dumps(settings)}
QUALITY METRICS:
- PSNR: {metrics.get('psnr', 'N/A')} dB (higher = less visible changes)
- SSIM: {metrics.get('ssim', 'N/A')} (closer to 1.0 = more similar)
- MSE: {metrics.get('mse', 'N/A')} (lower = fewer changes)

Provide a JSON response with:
{{
  "risk_level": "low/medium/high/critical",
  "detection_probability": "percentage estimate",
  "vulnerabilities": ["list of 3-4 specific vulnerabilities"],
  "mitigation_steps": ["list of 3-4 actionable recommendations"],
  "platforms_analysis": {{
    "social_media": "risk assessment for Instagram/Facebook/Twitter",
    "email": "risk assessment for email attachments",
    "cloud_storage": "risk assessment for cloud services"
  }},
  "summary": "2-3 sentence overall assessment"
}}

Be specific and practical. Consider statistical attacks, visual inspection, and platform-specific compression."""

        try:
            response = self._call_grok_api(prompt, temperature=0.2)
            # Parse JSON response
            content = response.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"AI Security Analysis error: {e}")
            return self._fallback_security_analysis(metrics, algorithm, settings)
    
    def chat_response(self, user_question: str, context: Optional[Dict] = None) -> str:
        """
        Respond to user questions about steganography with context awareness
        """
        
        if not self.api_key:
            return self._fallback_chat_response(user_question)
        
        system_prompt = """You are an expert steganography assistant helping users understand data hiding techniques.
        
Your role:
- Explain steganography concepts clearly and concisely
- Answer technical questions about algorithms (LSB, DCT, DWT)
- Provide security and privacy advice
- Help users understand metrics (PSNR, SSIM, MSE)
- Suggest best practices for secure steganography

Keep responses:
- Clear and educational (2-4 sentences)
- Practical and actionable
- Friendly but professional
- Technically accurate"""

        # Build context-aware prompt
        context_info = ""
        if context:
            if 'current_algorithm' in context:
                context_info += f"\nUser is currently using: {context['current_algorithm']}"
            if 'image_stats' in context:
                context_info += f"\nCurrent image stats: {json.dumps(context['image_stats'], indent=2)}"
            if 'last_operation' in context:
                context_info += f"\nLast operation: {context['last_operation']}"
        
        user_prompt = f"{context_info}\n\nUser question: {user_question}"
        
        try:
            return self._call_grok_api(user_prompt, system_prompt=system_prompt, temperature=0.4)
        except Exception as e:
            print(f"AI Chat error: {e}")
            return self._fallback_chat_response(user_question)
    
    def generate_comparison(self, algorithm1: str, algorithm2: str) -> Dict:
        """Compare two steganography algorithms"""
        
        if not self.api_key:
            return self._fallback_comparison(algorithm1, algorithm2)
        
        prompt = f"""Compare these steganography algorithms for a user deciding which to use:

ALGORITHM 1: {algorithm1}
ALGORITHM 2: {algorithm2}

Provide JSON response:
{{
  "capacity": {{"winner": "algorithm name", "explanation": "why"}},
  "security": {{"winner": "algorithm name", "explanation": "why"}},
  "robustness": {{"winner": "algorithm name", "explanation": "why"}},
  "complexity": {{"winner": "algorithm name", "explanation": "why"}},
  "use_cases": {{
    "{algorithm1}": "best use cases",
    "{algorithm2}": "best use cases"
  }},
  "recommendation": "which to choose and when"
}}"""

        try:
            response = self._call_grok_api(prompt, temperature=0.3)
            content = response.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            return json.loads(content.strip())
        except Exception as e:
            print(f"AI Comparison error: {e}")
            return self._fallback_comparison(algorithm1, algorithm2)
    
    def _call_grok_api(self, user_prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3) -> str:
        """Make API call to Grok"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        
        response = requests.post(
            self.api_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            json={
                "messages": messages,
                "model": self.model,
                "temperature": temperature,
                "max_tokens": 800
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"API returned status {response.status_code}")
    
    # Fallback methods when API is unavailable
    
    def _fallback_algorithm_explanation(self, algorithm: str, image_stats: dict, recommendation: dict) -> str:
        """Fallback explanation when AI is unavailable"""
        
        texture = image_stats.get('texture_score', 0)
        entropy = image_stats.get('entropy', 0)
        bits = recommendation.get('bits_per_channel', 1)
        
        if algorithm == "LSB":
            if texture > 100:
                return f"LSB with {bits} bits/channel is recommended because your image has high texture (score: {texture}), which effectively hides bit-level changes. The complex patterns mask the embedded data from visual and statistical detection."
            else:
                return f"LSB with {bits} bits/channel is used. Note: Your image has lower texture (score: {texture}), so using fewer bits per channel maintains better invisibility despite the smooth regions."
        elif algorithm == "DCT":
            return "DCT embeds data in frequency coefficients, making it resistant to JPEG compression. It's ideal for images that may be compressed or shared online."
        elif algorithm == "DWT":
            return "DWT uses wavelet transforms for embedding, providing excellent imperceptibility and robustness. It's particularly effective for images with diverse frequency content."
        
        return f"The {algorithm} algorithm is suitable for your use case based on the image characteristics and payload requirements."
    
    def _fallback_security_analysis(self, metrics: dict, algorithm: str, settings: dict) -> Dict:
        """Fallback security analysis"""
        
        psnr = metrics.get('psnr', 0)
        ssim = metrics.get('ssim', 0)
        bits = settings.get('bits_per_channel', 1)
        
        # Assess risk based on metrics
        if psnr > 40 and ssim > 0.95:
            risk = "low"
            detection_prob = "5-15%"
        elif psnr > 35 and ssim > 0.90:
            risk = "medium"
            detection_prob = "20-35%"
        elif psnr > 30:
            risk = "high"
            detection_prob = "40-60%"
        else:
            risk = "critical"
            detection_prob = "70-90%"
        
        return {
            "risk_level": risk,
            "detection_probability": detection_prob,
            "vulnerabilities": [
                f"Statistical analysis may detect {bits}-bit embedding patterns",
                "Chi-square attacks can identify LSB anomalies",
                "Visual inspection may reveal artifacts if image is zoomed",
                "Histogram analysis might show unusual bit distribution"
            ],
            "mitigation_steps": [
                "Use encryption to randomize payload before embedding",
                "Choose images with high texture and complexity",
                "Reduce bits per channel for higher security",
                "Avoid sharing on platforms that apply compression"
            ],
            "platforms_analysis": {
                "social_media": "High risk - platforms compress images, may expose or destroy hidden data",
                "email": "Medium risk - generally safe but some email clients may process images",
                "cloud_storage": "Low-Medium risk - direct downloads preserve data, but avoid auto-optimization features"
            },
            "summary": f"With PSNR of {psnr:.2f}dB and SSIM of {ssim:.3f}, your steganography has {risk} detection risk. The embedded data is {'reasonably' if risk in ['low', 'medium'] else 'potentially'} secure against casual inspection but may be vulnerable to dedicated steganalysis."
        }
    
    def _fallback_chat_response(self, question: str) -> str:
        """Fallback chat response"""
        
        q_lower = question.lower()
        
        if "lsb" in q_lower:
            return "LSB (Least Significant Bit) steganography replaces the least significant bits of pixel values with your secret data. It's simple and effective for images with good texture. Higher bits per channel = more capacity but more detectable."
        elif "dct" in q_lower:
            return "DCT (Discrete Cosine Transform) embeds data in frequency domain, similar to JPEG compression. It's resistant to compression and ideal for images shared online, though it has lower capacity than LSB."
        elif "dwt" in q_lower:
            return "DWT (Discrete Wavelet Transform) uses wavelet decomposition for embedding. It offers excellent invisibility and robustness, making it suitable for high-security applications where detection must be minimal."
        elif "psnr" in q_lower or "ssim" in q_lower:
            return "PSNR (Peak Signal-to-Noise Ratio) and SSIM (Structural Similarity Index) measure image quality after embedding. Higher PSNR (>40dB) and SSIM (>0.95) mean better invisibility. These metrics help assess detection risk."
        elif "security" in q_lower or "safe" in q_lower or "detect" in q_lower:
            return "For maximum security: use encryption, choose high-texture images, minimize bits per channel, and avoid platforms that compress images. Statistical analysis is the main detection method, so randomizing your payload with encryption is crucial."
        elif "capacity" in q_lower:
            return "Capacity depends on carrier size and bits per channel. For images: capacity = width × height × 3 channels × bits_per_channel ÷ 8 bytes. Trade-off: higher capacity = higher detection risk."
        else:
            return "I'm here to help you understand steganography! Ask me about algorithms (LSB, DCT, DWT), security concerns, quality metrics (PSNR, SSIM), or best practices for hiding data securely."
    
    def _fallback_comparison(self, algo1: str, algo2: str) -> Dict:
        """Fallback algorithm comparison"""
        
        comparisons = {
            ("LSB", "DCT"): {
                "capacity": {"winner": "LSB", "explanation": "LSB can embed more data with adjustable bits per channel"},
                "security": {"winner": "DCT", "explanation": "DCT is more resistant to statistical attacks"},
                "robustness": {"winner": "DCT", "explanation": "DCT survives JPEG compression better"},
                "complexity": {"winner": "LSB", "explanation": "LSB is simpler to implement and faster"},
                "use_cases": {
                    "LSB": "Large payloads, lossless formats, personal use",
                    "DCT": "Compressed images, web sharing, compression resistance needed"
                },
                "recommendation": "Use LSB for maximum capacity with lossless formats. Use DCT when image may be compressed or shared online."
            },
            ("LSB", "DWT"): {
                "capacity": {"winner": "LSB", "explanation": "LSB offers higher capacity"},
                "security": {"winner": "DWT", "explanation": "DWT provides better imperceptibility"},
                "robustness": {"winner": "DWT", "explanation": "DWT is more robust to modifications"},
                "complexity": {"winner": "LSB", "explanation": "LSB is much simpler"},
                "use_cases": {
                    "LSB": "Quick embedding, large payloads, personal files",
                    "DWT": "High-security needs, professional applications"
                },
                "recommendation": "Use LSB for everyday use and large data. Use DWT when security and invisibility are paramount."
            },
            ("DCT", "DWT"): {
                "capacity": {"winner": "Similar", "explanation": "Both have moderate capacity"},
                "security": {"winner": "DWT", "explanation": "DWT generally offers better imperceptibility"},
                "robustness": {"winner": "DCT", "explanation": "DCT better handles JPEG-specific operations"},
                "complexity": {"winner": "DCT", "explanation": "DCT is slightly less complex"},
                "use_cases": {
                    "DCT": "JPEG images, web distribution",
                    "DWT": "Professional steganography, research, high-security"
                },
                "recommendation": "Use DCT for JPEG and web images. Use DWT for maximum security with PNG/lossless formats."
            }
        }
        
        key = (algo1, algo2)
        if key not in comparisons:
            key = (algo2, algo1)
        
        return comparisons.get(key, {
            "capacity": {"winner": "Depends", "explanation": "Varies by implementation"},
            "security": {"winner": "Depends", "explanation": "Varies by settings"},
            "robustness": {"winner": "Depends", "explanation": "Varies by use case"},
            "complexity": {"winner": "Depends", "explanation": "Both have trade-offs"},
            "use_cases": {algo1: "Various", algo2: "Various"},
            "recommendation": "Choose based on your specific requirements and image type."
        })


# Singleton instance
_explainer_instance = None

def get_explainer() -> AIExplainer:
    """Get or create AIExplainer singleton instance"""
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = AIExplainer()
    return _explainer_instance