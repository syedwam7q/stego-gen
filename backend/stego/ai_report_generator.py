"""
AI-Powered Report Generator - Creates comprehensive technical reports for steganography operations
"""
import os
import json
from datetime import datetime
from typing import Dict, Optional
import requests
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class ReportGenerator:
    """
    Generates professional technical reports for encode/decode operations
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.api_url = "https://api.x.ai/v1/chat/completions"
    
    def generate_encode_report(
        self,
        operation_data: Dict,
        output_path: str,
        include_images: bool = True
    ) -> str:
        """
        Generate comprehensive encode operation report
        
        Args:
            operation_data: Dictionary containing:
                - algorithm: Algorithm used
                - carrier_info: Carrier file information
                - image_stats: Image analysis statistics
                - recommendation: AI recommendation details
                - encode_result: Encoding results
                - metrics: Quality metrics (PSNR, SSIM, MSE)
                - settings: User settings
            output_path: Path to save the PDF report
            include_images: Whether to include image previews
        
        Returns:
            Path to generated PDF file
        """
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#5b6edb'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#5b6edb'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("Steganography Operation Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Operation Summary
        story.append(Paragraph("Operation Summary", heading_style))
        summary_data = [
            ['Operation Type', 'Encode (Hide Data)'],
            ['Algorithm', operation_data.get('algorithm', 'N/A').upper()],
            ['Timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Status', '✓ Successful' if operation_data.get('success') else '✗ Failed']
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Image Analysis
        if 'image_stats' in operation_data:
            story.append(Paragraph("Carrier Image Analysis", heading_style))
            stats = operation_data['image_stats']
            
            analysis_data = [
                ['Dimension', f"{stats.get('width')}x{stats.get('height')} pixels"],
                ['Format', stats.get('format', 'N/A')],
                ['Total Pixels', f"{stats.get('total_pixels', 0):,}"],
                ['Entropy', f"{stats.get('entropy', 0):.2f} bits (image complexity)"],
                ['Variance', f"{stats.get('variance', 0):.2f} (pixel variation)"],
                ['Texture Score', f"{stats.get('texture_score', 0):.2f}"],
                ['Edge Density', f"{stats.get('edge_density', 0):.4f}"],
                ['Noise Level', f"{stats.get('noise_level', 0):.2f}"],
                ['Suitability', stats.get('suitability', 'N/A')]
            ]
            
            analysis_table = Table(analysis_data, colWidths=[2*inch, 4*inch])
            analysis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(analysis_table)
            story.append(Spacer(1, 0.3*inch))
        
        # AI Recommendation
        if 'recommendation' in operation_data:
            story.append(Paragraph("AI Recommendation & Strategy", heading_style))
            rec = operation_data['recommendation']
            
            rec_data = [
                ['Recommended Algorithm', rec.get('algorithm', 'N/A')],
                ['Bits per Channel', str(rec.get('bits_per_channel', 'N/A'))],
                ['Detection Risk', rec.get('detection_risk', 'N/A').upper()],
                ['Confidence Score', f"{rec.get('confidence', 0):.0%}"],
                ['Embedding Region', rec.get('region_hint', 'N/A')]
            ]
            
            rec_table = Table(rec_data, colWidths=[2*inch, 4*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(rec_table)
            story.append(Spacer(1, 0.15*inch))
            
            # AI Explanation
            explanation = rec.get('explanation', 'No explanation available')
            story.append(Paragraph("<b>AI Reasoning:</b>", styles['Normal']))
            story.append(Paragraph(explanation, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Quality Metrics
        if 'metrics' in operation_data:
            story.append(Paragraph("Quality Metrics & Imperceptibility", heading_style))
            metrics = operation_data['metrics']
            
            # Get AI interpretation of metrics
            metrics_interpretation = self._get_metrics_interpretation(metrics)
            
            metrics_data = [
                ['PSNR (Peak Signal-to-Noise Ratio)', f"{metrics.get('psnr', 0):.2f} dB"],
                ['SSIM (Structural Similarity)', f"{metrics.get('ssim', 0):.4f}"],
                ['MSE (Mean Squared Error)', f"{metrics.get('mse', 0):.4f}"]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 0.15*inch))
            
            story.append(Paragraph("<b>Interpretation:</b>", styles['Normal']))
            story.append(Paragraph(metrics_interpretation, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Capacity Analysis
        if 'image_stats' in operation_data:
            story.append(Paragraph("Capacity Analysis", heading_style))
            stats = operation_data['image_stats']
            payload_size = operation_data.get('payload_size', 0)
            
            capacity_data = [
                ['Payload Size', f"{payload_size:,} bytes ({payload_size/1024:.2f} KB)"],
                ['Capacity @ 1 bit/ch', f"{stats.get('capacity_at_1bit', 0):,} bytes"],
                ['Capacity @ 2 bits/ch', f"{stats.get('capacity_at_2bit', 0):,} bytes"],
                ['Capacity @ 4 bits/ch', f"{stats.get('capacity_at_4bit', 0):,} bytes"],
                ['Utilization', f"{(payload_size/stats.get('capacity_at_1bit', 1)*100):.1f}% @ 1 bit/ch"]
            ]
            
            capacity_table = Table(capacity_data, colWidths=[2.5*inch, 3.5*inch])
            capacity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(capacity_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Security Considerations
        story.append(Paragraph("Security Analysis & Recommendations", heading_style))
        security_advice = self._generate_security_advice(operation_data)
        story.append(Paragraph(security_advice, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Technical Details
        story.append(Paragraph("Technical Implementation Details", heading_style))
        settings = operation_data.get('settings', {})
        
        tech_details = []
        tech_details.append(f"<b>Algorithm:</b> {operation_data.get('algorithm', 'N/A').upper()}")
        tech_details.append(f"<b>Embedding Method:</b> {self._get_algorithm_description(operation_data.get('algorithm'))}")
        
        if settings.get('encryption_key'):
            tech_details.append(f"<b>Encryption:</b> AES-256 with random IV")
        else:
            tech_details.append(f"<b>Encryption:</b> None (plaintext embedding)")
        
        tech_details.append(f"<b>Bits per Channel:</b> {settings.get('bits_per_channel', 'N/A')}")
        
        for detail in tech_details:
            story.append(Paragraph(detail, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("_" * 80, styles['Normal']))
        story.append(Paragraph(
            "This report was generated by StegoGen AI-Powered Steganography Platform",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _get_metrics_interpretation(self, metrics: Dict) -> str:
        """Get AI interpretation of quality metrics"""
        
        if not self.api_key:
            return self._fallback_metrics_interpretation(metrics)
        
        prompt = f"""Interpret these steganography quality metrics for a technical report:

PSNR: {metrics.get('psnr', 0):.2f} dB
SSIM: {metrics.get('ssim', 0):.4f}
MSE: {metrics.get('mse', 0):.4f}

Provide a 2-3 sentence professional interpretation explaining:
1. What these values indicate about invisibility
2. Whether the embedding is detectable
3. Overall quality assessment

Use clear, technical language suitable for a formal report."""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "model": "grok-beta",
                    "temperature": 0.2,
                    "max_tokens": 250
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Metrics interpretation error: {e}")
        
        return self._fallback_metrics_interpretation(metrics)
    
    def _fallback_metrics_interpretation(self, metrics: Dict) -> str:
        """Fallback metrics interpretation"""
        
        psnr = metrics.get('psnr', 0)
        ssim = metrics.get('ssim', 0)
        
        if psnr > 40 and ssim > 0.95:
            quality = "excellent"
            detection = "highly unlikely"
        elif psnr > 35 and ssim > 0.90:
            quality = "good"
            detection = "unlikely without specialized tools"
        elif psnr > 30:
            quality = "acceptable"
            detection = "possible with statistical analysis"
        else:
            quality = "poor"
            detection = "likely"
        
        return f"The quality metrics indicate {quality} imperceptibility with PSNR of {psnr:.2f}dB and SSIM of {ssim:.4f}. Visual detection is {detection}. These values suggest that the embedded data {'is well-hidden and' if quality in ['excellent', 'good'] else 'may be'} suitable for transmission through standard channels without immediate suspicion."
    
    def _generate_security_advice(self, operation_data: Dict) -> str:
        """Generate security recommendations"""
        
        if not self.api_key:
            return self._fallback_security_advice(operation_data)
        
        metrics = operation_data.get('metrics', {})
        recommendation = operation_data.get('recommendation', {})
        encrypted = operation_data.get('settings', {}).get('encryption_key') is not None
        
        prompt = f"""Provide security recommendations for this steganography operation:

Algorithm: {operation_data.get('algorithm')}
Detection Risk: {recommendation.get('detection_risk', 'unknown')}
PSNR: {metrics.get('psnr', 0):.2f}
Encrypted: {encrypted}

Write 3-4 sentences of security advice covering:
1. Detection risks
2. Best practices for secure transmission
3. Platforms to avoid
4. Additional security measures

Make it professional and actionable."""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "model": "grok-beta",
                    "temperature": 0.3,
                    "max_tokens": 300
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
        except:
            pass
        
        return self._fallback_security_advice(operation_data)
    
    def _fallback_security_advice(self, operation_data: Dict) -> str:
        """Fallback security advice"""
        
        encrypted = operation_data.get('settings', {}).get('encryption_key') is not None
        detection_risk = operation_data.get('recommendation', {}).get('detection_risk', 'medium')
        
        advice = f"This steganographic image has {detection_risk} detection risk. "
        
        if encrypted:
            advice += "The payload is encrypted, adding a crucial layer of security even if the steganography is detected. "
        else:
            advice += "WARNING: The payload is not encrypted. If detected, the hidden data can be easily read. Always use encryption for sensitive data. "
        
        advice += "Avoid uploading to social media platforms that apply aggressive compression (Instagram, Facebook), as this may destroy or expose the hidden data. "
        advice += "For maximum security, transmit through lossless channels (direct file transfer, email, cloud storage with original quality preserved) and use strong encryption keys."
        
        return advice
    
    def _get_algorithm_description(self, algorithm: str) -> str:
        """Get description of algorithm"""
        
        descriptions = {
            'lsb': 'Least Significant Bit modification in spatial domain',
            'dct': 'Discrete Cosine Transform coefficient modification',
            'dwt': 'Discrete Wavelet Transform coefficient embedding',
            'audio': 'LSB embedding in audio samples',
            'video': 'Frame-by-frame LSB embedding in video'
        }
        
        return descriptions.get(algorithm, 'Unknown algorithm')


# Singleton
_report_generator = None

def get_report_generator() -> ReportGenerator:
    """Get or create ReportGenerator singleton"""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator