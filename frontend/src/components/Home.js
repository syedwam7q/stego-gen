import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="home-page">
      {/* Hero Section */}
      <div className={`hero-section ${isVisible ? 'visible' : ''}`}>
        <div className="hero-content">
          <div className="hero-logo-container float">
            <img src="/logo/logo.png" alt="StegoGen Logo" className="hero-logo" />
          </div>
          <h1 className="hero-title">
            <span className="gradient-text">StegoGen</span>
          </h1>
          <p className="hero-subtitle">
            AI-Powered Steganography Platform
          </p>
          <p className="hero-description">
            Hide your secrets in plain sight with military-grade encryption and AI-optimized embedding
          </p>
          <div className="hero-buttons">
            <Link to="/encode" className="btn btn-primary btn-large">
              🔒 Start Encoding
            </Link>
            <Link to="/decode" className="btn btn-secondary btn-large">
              🔓 Decode Message
            </Link>
          </div>
          
          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat-value">5</div>
              <div className="hero-stat-label">Algorithms</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">AES-256</div>
              <div className="hero-stat-label">Encryption</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">AI</div>
              <div className="hero-stat-label">Powered</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="card features-section">
        <h2 className="section-title">
          <span className="gradient-text">🚀 Advanced Features</span>
        </h2>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎨</div>
            <h3>Multiple Algorithms</h3>
            <p>Choose from LSB, DCT, DWT, Audio, and Video steganography techniques tailored to your needs</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI Optimization</h3>
            <p>Powered by Grok AI to analyze carriers and recommend optimal parameters for maximum invisibility</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🔐</div>
            <h3>Military-Grade Security</h3>
            <p>AES-256 encryption ensures your hidden data remains secure even if discovered</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Quality Metrics</h3>
            <p>Real-time PSNR and SSIM calculations to measure imperceptibility of embedded data</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📁</div>
            <h3>Binary File Support</h3>
            <p>Hide any file type - images, documents, archives - not just text messages</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Lightning Fast</h3>
            <p>Optimized algorithms with progress tracking for efficient encoding and decoding</p>
          </div>
        </div>
      </div>

      {/* Algorithms Section */}
      <div className="card algorithms-section">
        <h2 className="section-title">
          <span className="gradient-text">🔬 Steganography Algorithms</span>
        </h2>
        
        <div className="algorithms-showcase">
          <div className="algorithm-showcase-card algo-lsb">
            <div className="algo-header">
              <span className="algo-icon">📷</span>
              <h3>LSB (Least Significant Bit)</h3>
            </div>
            <div className="algo-badge">Spatial Domain</div>
            <p className="algo-description">
              Classic steganography technique that modifies the least significant bits of image pixels. 
              Perfect for natural images with textures and high capacity requirements.
            </p>
            <div className="algo-specs">
              <span className="algo-spec">✓ High Capacity</span>
              <span className="algo-spec">✓ Fast Processing</span>
              <span className="algo-spec">✓ Easy to Use</span>
            </div>
          </div>

          <div className="algorithm-showcase-card algo-dct">
            <div className="algo-header">
              <span className="algo-icon">🔍</span>
              <h3>DCT (Discrete Cosine Transform)</h3>
            </div>
            <div className="algo-badge">Frequency Domain</div>
            <p className="algo-description">
              Embeds data in frequency coefficients, making it resistant to JPEG compression and 
              various image processing operations.
            </p>
            <div className="algo-specs">
              <span className="algo-spec">✓ Compression Resistant</span>
              <span className="algo-spec">✓ Robust</span>
              <span className="algo-spec">✓ Secure</span>
            </div>
          </div>

          <div className="algorithm-showcase-card algo-dwt">
            <div className="algo-header">
              <span className="algo-icon">🌊</span>
              <h3>DWT (Discrete Wavelet Transform)</h3>
            </div>
            <div className="algo-badge">Wavelet Domain</div>
            <p className="algo-description">
              Advanced wavelet-based embedding with excellent imperceptibility and robustness 
              against various attacks and transformations.
            </p>
            <div className="algo-specs">
              <span className="algo-spec">✓ Imperceptible</span>
              <span className="algo-spec">✓ Attack Resistant</span>
              <span className="algo-spec">✓ High Quality</span>
            </div>
          </div>

          <div className="algorithm-showcase-card algo-audio">
            <div className="algo-header">
              <span className="algo-icon">🎵</span>
              <h3>Audio Steganography</h3>
            </div>
            <div className="algo-badge">Audio Domain</div>
            <p className="algo-description">
              Hide data within WAV audio files using inaudible modifications to audio samples. 
              Perfect for audio-based secret communication.
            </p>
            <div className="algo-specs">
              <span className="algo-spec">✓ Inaudible</span>
              <span className="algo-spec">✓ WAV Support</span>
              <span className="algo-spec">✓ Large Capacity</span>
            </div>
          </div>

          <div className="algorithm-showcase-card algo-video">
            <div className="algo-header">
              <span className="algo-icon">🎬</span>
              <h3>Video Steganography</h3>
            </div>
            <div className="algo-badge">Video Domain</div>
            <p className="algo-description">
              Embed data across multiple video frames with auto-parameter detection. 
              Supports MP4, AVI, MOV, and MKV formats.
            </p>
            <div className="algo-specs">
              <span className="algo-spec">✓ Massive Capacity</span>
              <span className="algo-spec">✓ Multi-Format</span>
              <span className="algo-spec">✓ Auto-Detect</span>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="card how-it-works-section">
        <h2 className="section-title">
          <span className="gradient-text">⚙️ How It Works</span>
        </h2>
        
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Upload Carrier</h3>
              <p>Upload your carrier file (image, audio, or video) that will hold the hidden data</p>
            </div>
          </div>

          <div className="step-connector"></div>

          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>AI Analysis</h3>
              <p>Our AI analyzes the carrier and recommends optimal hiding parameters</p>
            </div>
          </div>

          <div className="step-connector"></div>

          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Add Secret</h3>
              <p>Input your secret message or upload a file, optionally encrypt with AES-256</p>
            </div>
          </div>

          <div className="step-connector"></div>

          <div className="step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>Encode & Download</h3>
              <p>Watch the progress bar as your data is embedded, then download the stego file</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="card cta-section">
        <h2 className="cta-title">Ready to Hide Your Secrets?</h2>
        <p className="cta-description">
          Join the secure communication revolution with AI-powered steganography
        </p>
        <div className="cta-buttons">
          <Link to="/encode" className="btn btn-primary btn-large pulse">
            🚀 Get Started Now
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;