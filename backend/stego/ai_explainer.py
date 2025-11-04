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
        """Fallback algorithm comparison with detailed analysis"""
        
        # Normalize algorithm names
        algo1 = algo1.upper()
        algo2 = algo2.upper()
        
        # Detailed comparison data
        algo_profiles = {
            "LSB": {
                "capacity_score": 100,
                "security_score": 60,
                "robustness_score": 50,
                "complexity_score": 90
            },
            "DCT": {
                "capacity_score": 65,
                "security_score": 80,
                "robustness_score": 90,
                "complexity_score": 60
            },
            "DWT": {
                "capacity_score": 70,
                "security_score": 85,
                "robustness_score": 85,
                "complexity_score": 50
            },
            "AUDIO": {
                "capacity_score": 95,
                "security_score": 70,
                "robustness_score": 65,
                "complexity_score": 75
            },
            "VIDEO": {
                "capacity_score": 100,
                "security_score": 75,
                "robustness_score": 70,
                "complexity_score": 55
            }
        }
        
        profile1 = algo_profiles.get(algo1, algo_profiles["LSB"])
        profile2 = algo_profiles.get(algo2, algo_profiles["LSB"])
        
        # Build dynamic comparison based on scores
        capacity_winner = algo1 if profile1["capacity_score"] > profile2["capacity_score"] else algo2
        if abs(profile1["capacity_score"] - profile2["capacity_score"]) < 5:
            capacity_winner = "Similar"
            
        security_winner = algo1 if profile1["security_score"] > profile2["security_score"] else algo2
        robustness_winner = algo1 if profile1["robustness_score"] > profile2["robustness_score"] else algo2
        complexity_winner = algo1 if profile1["complexity_score"] > profile2["complexity_score"] else algo2
        
        # Use case descriptions
        use_case_map = {
            "LSB": "Best for large payloads in lossless images (PNG, BMP). Fast and simple spatial domain technique.",
            "DCT": "Ideal for JPEG images and web sharing. Resistant to compression and lossy transformations.",
            "DWT": "Professional-grade wavelet embedding. Excellent imperceptibility and robustness for high-security needs.",
            "AUDIO": "Perfect for audio-based covert communication in WAV files. Large capacity with inaudible modifications.",
            "VIDEO": "Massive capacity across multiple frames. Supports MP4, AVI, MOV, and MKV formats."
        }
        
        # Build recommendation string
        if capacity_winner == algo1 and security_winner == algo2:
            recommendation = f"Choose {algo1} for higher capacity needs or {algo2} for better security and robustness."
        elif capacity_winner == algo2 and security_winner == algo1:
            recommendation = f"Choose {algo1} for better security or {algo2} for higher capacity."
        elif profile1["security_score"] > profile2["security_score"]:
            recommendation = f"{algo1} offers better overall security and imperceptibility. {algo2} may be simpler or have higher capacity."
        else:
            recommendation = f"{algo2} provides superior security features. {algo1} might be better for capacity or ease of use."
        
        return {
            "capacity": {
                "winner": capacity_winner,
                "explanation": f"{capacity_winner} provides superior embedding capacity. Score: {profile1['capacity_score']} vs {profile2['capacity_score']}",
                "score1": profile1["capacity_score"],
                "score2": profile2["capacity_score"]
            },
            "security": {
                "winner": security_winner,
                "explanation": f"{security_winner} offers better resistance to steganalysis attacks. Score: {profile1['security_score']} vs {profile2['security_score']}",
                "score1": profile1["security_score"],
                "score2": profile2["security_score"]
            },
            "robustness": {
                "winner": robustness_winner,
                "explanation": f"{robustness_winner} is more resistant to image processing and compression. Score: {profile1['robustness_score']} vs {profile2['robustness_score']}",
                "score1": profile1["robustness_score"],
                "score2": profile2["robustness_score"]
            },
            "complexity": {
                "winner": complexity_winner,
                "explanation": f"{complexity_winner} is simpler to implement and faster to execute. Score: {profile1['complexity_score']} vs {profile2['complexity_score']}",
                "score1": profile1["complexity_score"],
                "score2": profile2["complexity_score"]
            },
            "use_cases": {
                algo1: use_case_map.get(algo1, "General purpose steganography"),
                algo2: use_case_map.get(algo2, "General purpose steganography")
            },
            "recommendation": recommendation
        }


# Singleton instance
_explainer_instance = None

def get_explainer() -> AIExplainer:
    """Get or create AIExplainer singleton instance"""
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = AIExplainer()
    return _explainer_instance