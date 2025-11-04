"""
AI-Powered Steganalysis Module - Detect and analyze potential steganography in images
"""
import numpy as np
from PIL import Image
import cv2
from typing import Dict, List, Tuple
import os
import requests
import json
from scipy import stats


class SteganographyDetector:
    """
    Advanced steganalysis tool to detect hidden data in images
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"
    
    def analyze_for_steganography(self, image_path: str) -> Dict:
        """
        Comprehensive analysis to detect potential steganography
        Returns detailed report with multiple detection methods
        """
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img.convert('RGB'))
        
        # Run multiple detection tests
        lsb_analysis = self._analyze_lsb_patterns(img_array)
        histogram_analysis = self._analyze_histogram(img_array)
        chi_square_test = self._chi_square_attack(img_array)
        rs_analysis = self._rs_steganalysis(img_array)
        visual_analysis = self._visual_attack(img_array)
        statistical_analysis = self._statistical_analysis(img_array)
        
        # Aggregate results
        detection_score = self._calculate_detection_score({
            'lsb': lsb_analysis,
            'histogram': histogram_analysis,
            'chi_square': chi_square_test,
            'rs': rs_analysis,
            'visual': visual_analysis,
            'statistical': statistical_analysis
        })
        
        # Generate AI-powered interpretation
        ai_interpretation = self._get_ai_interpretation({
            'lsb_analysis': lsb_analysis,
            'histogram_analysis': histogram_analysis,
            'chi_square_test': chi_square_test,
            'rs_analysis': rs_analysis,
            'detection_score': detection_score
        })
        
        return {
            'overall_score': detection_score,
            'likelihood': self._score_to_likelihood(detection_score),
            'tests': {
                'lsb_analysis': lsb_analysis,
                'histogram_analysis': histogram_analysis,
                'chi_square_test': chi_square_test,
                'rs_analysis': rs_analysis,
                'visual_analysis': visual_analysis,
                'statistical_analysis': statistical_analysis
            },
            'ai_interpretation': ai_interpretation,
            'recommendations': self._generate_recommendations(detection_score, {
                'lsb': lsb_analysis,
                'chi_square': chi_square_test
            })
        }
    
    def _analyze_lsb_patterns(self, img_array: np.ndarray) -> Dict:
        """Analyze LSB bit patterns for anomalies"""
        
        # Extract LSBs
        lsb_plane = img_array & 1
        
        # Calculate randomness of LSB plane
        lsb_entropy = self._calculate_entropy(lsb_plane.flatten())
        
        # Check for sequential patterns
        sequential_score = self._check_sequential_patterns(lsb_plane)
        
        # LSB should be highly random (entropy close to 1.0 in binary)
        # Modified data tends to have entropy closer to 0.9-1.0
        natural_entropy = 0.7  # Natural images typically have lower LSB entropy
        
        suspicion = "low"
        if lsb_entropy > 0.95:
            suspicion = "high"
        elif lsb_entropy > 0.85:
            suspicion = "medium"
        
        return {
            'lsb_entropy': round(float(lsb_entropy), 4),
            'sequential_pattern_score': round(float(sequential_score), 4),
            'suspicion_level': suspicion,
            'passed': suspicion == "low",
            'explanation': f"LSB entropy of {lsb_entropy:.3f} {'suggests possible' if lsb_entropy > 0.85 else 'indicates likely no'} hidden data"
        }
    
    def _analyze_histogram(self, img_array: np.ndarray) -> Dict:
        """Analyze histogram for LSB embedding artifacts"""
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Calculate histogram
        hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
        
        # Check for pairs of values anomaly (LSB artifact)
        pair_anomalies = 0
        for i in range(0, 255, 2):
            diff = abs(int(hist[i]) - int(hist[i + 1]))
            expected_diff = (hist[i] + hist[i + 1]) * 0.3  # 30% threshold
            if diff < expected_diff:
                pair_anomalies += 1
        
        pair_anomaly_ratio = pair_anomalies / 128.0
        
        suspicion = "low"
        if pair_anomaly_ratio > 0.7:
            suspicion = "high"
        elif pair_anomaly_ratio > 0.5:
            suspicion = "medium"
        
        return {
            'pair_anomaly_ratio': round(float(pair_anomaly_ratio), 4),
            'anomalous_pairs': int(pair_anomalies),
            'suspicion_level': suspicion,
            'passed': suspicion == "low",
            'explanation': f"Histogram shows {pair_anomalies} anomalous value pairs, {'indicating' if suspicion != 'low' else 'not indicating'} LSB tampering"
        }
    
    def _chi_square_attack(self, img_array: np.ndarray) -> Dict:
        """Chi-square statistical attack to detect LSB embedding"""
        
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY).flatten()
        
        # Count frequencies of each value
        observed = np.bincount(gray, minlength=256)
        
        # For LSB embedding, pairs (2k, 2k+1) should have similar frequencies
        chi_square_values = []
        for i in range(0, 254, 2):
            # Expected frequency if LSB is random
            expected = (observed[i] + observed[i + 1]) / 2.0
            if expected > 0:
                chi_sq = ((observed[i] - expected) ** 2 + (observed[i + 1] - expected) ** 2) / expected
                chi_square_values.append(chi_sq)
        
        avg_chi_square = np.mean(chi_square_values) if chi_square_values else 0
        
        # Higher chi-square suggests embedding
        suspicion = "low"
        if avg_chi_square > 3.0:
            suspicion = "high"
        elif avg_chi_square > 1.5:
            suspicion = "medium"
        
        # Calculate p-value
        p_value = 1.0 - stats.chi2.cdf(avg_chi_square, df=1)
        
        return {
            'chi_square_statistic': round(float(avg_chi_square), 4),
            'p_value': round(float(p_value), 4),
            'suspicion_level': suspicion,
            'passed': suspicion == "low",
            'explanation': f"Chi-square test statistic of {avg_chi_square:.3f} (p={p_value:.4f}) {'suggests' if suspicion != 'low' else 'does not suggest'} embedded data"
        }
    
    def _rs_steganalysis(self, img_array: np.ndarray) -> Dict:
        """RS Steganalysis - detects LSB embedding length"""
        
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        h, w = gray.shape
        
        # Sample random blocks
        block_size = 8
        num_blocks = min(100, (h // block_size) * (w // block_size))
        
        r_counts = []
        s_counts = []
        
        for _ in range(num_blocks):
            y = np.random.randint(0, h - block_size)
            x = np.random.randint(0, w - block_size)
            block = gray[y:y+block_size, x:x+block_size].flatten()
            
            # Calculate discrimination function (simplified)
            diffs = np.abs(np.diff(block.astype(int)))
            r_counts.append(np.sum(diffs > 1))
            s_counts.append(np.sum(diffs <= 1))
        
        r_mean = np.mean(r_counts)
        s_mean = np.mean(s_counts)
        
        # In clean images, R ≈ S. In stego images, R > S
        rs_ratio = r_mean / (s_mean + 1e-6)
        
        suspicion = "low"
        estimated_percentage = 0
        
        if rs_ratio > 1.3:
            suspicion = "high"
            estimated_percentage = min(100, (rs_ratio - 1.0) * 50)
        elif rs_ratio > 1.15:
            suspicion = "medium"
            estimated_percentage = (rs_ratio - 1.0) * 30
        
        return {
            'rs_ratio': round(float(rs_ratio), 4),
            'r_mean': round(float(r_mean), 2),
            's_mean': round(float(s_mean), 2),
            'estimated_embedding_percentage': round(float(estimated_percentage), 2),
            'suspicion_level': suspicion,
            'passed': suspicion == "low",
            'explanation': f"RS analysis ratio of {rs_ratio:.3f} estimates ~{estimated_percentage:.1f}% embedding capacity used"
        }
    
    def _visual_attack(self, img_array: np.ndarray) -> Dict:
        """Visual analysis - extract and analyze LSB planes"""
        
        # Extract each LSB plane
        lsb_planes = []
        for channel in range(3):
            lsb = (img_array[:, :, channel] & 1) * 255
            lsb_planes.append(lsb)
        
        # Analyze variance and patterns in LSB planes
        variances = [np.var(plane) for plane in lsb_planes]
        avg_variance = np.mean(variances)
        
        # Natural images have low LSB plane variance (~5000-8000)
        # Embedded data increases variance (~8000-12000)
        
        suspicion = "low"
        if avg_variance > 9000:
            suspicion = "high"
        elif avg_variance > 7500:
            suspicion = "medium"
        
        return {
            'lsb_plane_variance': round(float(avg_variance), 2),
            'channel_variances': [round(float(v), 2) for v in variances],
            'suspicion_level': suspicion,
            'passed': suspicion == "low",
            'explanation': f"LSB plane variance of {avg_variance:.0f} {'indicates' if suspicion != 'low' else 'appears normal for'} the image content"
        }
    
    def _statistical_analysis(self, img_array: np.ndarray) -> Dict:
        """General statistical analysis"""
        
        # Calculate various statistical properties
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Kurtosis (measure of "tailedness")
        kurtosis = float(stats.kurtosis(gray.flatten()))
        
        # Skewness
        skewness = float(stats.skew(gray.flatten()))
        
        # Standard deviation
        std_dev = float(np.std(gray))
        
        return {
            'kurtosis': round(kurtosis, 4),
            'skewness': round(skewness, 4),
            'std_deviation': round(std_dev, 2),
            'explanation': "Statistical properties of pixel distribution"
        }
    
    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy"""
        hist, _ = np.histogram(data, bins=256, range=(0, 256))
        hist = hist / hist.sum()
        hist = hist[hist > 0]
        return float(-np.sum(hist * np.log2(hist)))
    
    def _check_sequential_patterns(self, lsb_plane: np.ndarray) -> float:
        """Check for sequential patterns in LSB plane"""
        flat = lsb_plane.flatten()
        # Check runs of same values
        runs = np.diff(np.where(np.diff(flat) != 0)[0])
        if len(runs) > 0:
            avg_run = np.mean(runs)
            # Natural images: avg run ~2-3, embedded data: ~5-10
            return float(min(avg_run / 10.0, 1.0))
        return 0.0
    
    def _calculate_detection_score(self, results: Dict) -> float:
        """Calculate overall detection score (0-100)"""
        
        score = 0.0
        weights = {
            'lsb': 0.25,
            'histogram': 0.15,
            'chi_square': 0.30,
            'rs': 0.20,
            'visual': 0.10
        }
        
        for test, weight in weights.items():
            if test in results:
                suspicion = results[test].get('suspicion_level', 'low')
                if suspicion == 'high':
                    score += weight * 100
                elif suspicion == 'medium':
                    score += weight * 60
                elif suspicion == 'low':
                    score += weight * 20
        
        return round(score, 2)
    
    def _score_to_likelihood(self, score: float) -> str:
        """Convert score to likelihood description"""
        if score < 30:
            return "Very Unlikely - No significant signs of steganography detected"
        elif score < 50:
            return "Unlikely - Minor anomalies, but could be natural image characteristics"
        elif score < 70:
            return "Possible - Several indicators suggest potential hidden data"
        elif score < 85:
            return "Likely - Strong evidence of steganographic embedding"
        else:
            return "Very Likely - Multiple tests confirm probable steganography"
    
    def _get_ai_interpretation(self, analysis_results: Dict) -> str:
        """Get AI-powered interpretation of results"""
        
        if not self.api_key:
            return self._fallback_interpretation(analysis_results)
        
        prompt = f"""You are a forensic steganalysis expert. Analyze these test results and provide a clear, professional interpretation.

STEGANALYSIS RESULTS:
{json.dumps(analysis_results, indent=2)}

Provide a 3-4 sentence expert interpretation that:
1. Summarizes the findings in plain language
2. Explains what the tests reveal
3. States the confidence level of detection
4. Mentions any caveats or limitations

Be professional, clear, and avoid over-claiming certainty."""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "messages": [
                        {"role": "system", "content": "You are a forensic steganalysis expert providing professional analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    "model": "grok-beta",
                    "temperature": 0.3,
                    "max_tokens": 400
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"AI interpretation error: {e}")
        
        return self._fallback_interpretation(analysis_results)
    
    def _fallback_interpretation(self, analysis_results: Dict) -> str:
        """Fallback interpretation when AI unavailable"""
        
        score = analysis_results.get('detection_score', 0)
        
        if score < 30:
            return "The image passes most steganalysis tests with minimal anomalies. Statistical properties appear consistent with natural image characteristics. It is unlikely that significant steganographic content is present, though sophisticated techniques could potentially evade detection."
        elif score < 50:
            return "Some minor statistical anomalies detected, but these could result from normal image processing or compression. While certain tests show slight deviations from expected values, there is insufficient evidence to confidently assert steganographic content is present."
        elif score < 70:
            return "Multiple tests indicate potential steganographic embedding. LSB patterns and statistical measures show characteristics common in images with hidden data. However, these signatures could also result from heavy image processing or certain natural textures. Further investigation recommended."
        else:
            return "Strong evidence of steganography detected across multiple independent tests. Chi-square analysis, LSB patterns, and RS steganalysis all indicate probable data embedding. The statistical signatures are consistent with LSB or similar spatial domain steganography techniques. Confidence level is high that this image contains hidden information."
    
    def _generate_recommendations(self, score: float, test_results: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if score > 70:
            recommendations.append("🔍 High likelihood of steganography - consider this image suspicious")
            recommendations.append("🔬 Extract LSB planes and analyze for hidden patterns")
            recommendations.append("📊 Try decoding with common steganography tools (LSB extraction, 1-4 bits)")
        elif score > 50:
            recommendations.append("⚠️ Moderate suspicion - further analysis recommended")
            recommendations.append("🔧 Apply advanced steganalysis techniques")
            recommendations.append("📷 Compare with original source if available")
        else:
            recommendations.append("✅ Image appears clean - low probability of steganography")
            recommendations.append("💡 Minor anomalies may be due to compression or processing")
        
        # Specific recommendations based on tests
        if test_results.get('lsb', {}).get('suspicion_level') == 'high':
            recommendations.append("🎯 LSB plane shows high entropy - likely LSB steganography")
        
        if test_results.get('chi_square', {}).get('suspicion_level') == 'high':
            recommendations.append("📈 Chi-square test failed - statistical embedding detected")
        
        recommendations.append("ℹ️ Note: Sophisticated steganography may evade these detection methods")
        
        return recommendations


# Singleton instance
_detector_instance = None

def get_detector() -> SteganographyDetector:
    """Get or create SteganographyDetector singleton"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SteganographyDetector()
    return _detector_instance