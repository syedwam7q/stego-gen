import React, { useState, useRef } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import './CapacityCalculator.css';

function CapacityCalculator() {
  const [mode, setMode] = useState('manual'); // 'manual' or 'file'
  const [carrierFile, setCarrierFile] = useState(null);
  const [carrierPreview, setCarrierPreview] = useState(null);
  
  // Manual inputs
  const [width, setWidth] = useState(1920);
  const [height, setHeight] = useState(1080);
  const [bitsPerChannel, setBitsPerChannel] = useState(1);
  const [algorithm, setAlgorithm] = useState('lsb');
  
  // Results
  const [capacityResults, setCapacityResults] = useState(null);
  const [aiRecommendation, setAiRecommendation] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef(null);

  const calculateCapacity = () => {
    let capacityBytes = 0;
    let capacityBits = 0;

    if (algorithm === 'lsb' || algorithm === 'dct' || algorithm === 'dwt') {
      const totalPixels = width * height;
      capacityBits = totalPixels * 3 * bitsPerChannel; // RGB channels
      capacityBytes = Math.floor(capacityBits / 8);
    } else if (algorithm === 'audio') {
      // Assuming 44.1kHz, stereo, 16-bit, 1 minute
      const sampleRate = 44100;
      const duration = 60; // seconds
      const channels = 2;
      const bitsPerSample = bitsPerChannel;
      capacityBits = sampleRate * duration * channels * bitsPerSample;
      capacityBytes = Math.floor(capacityBits / 8);
    }

    // Account for overhead (metadata, etc.)
    const usableCapacity = Math.floor(capacityBytes * 0.95); // 5% overhead

    setCapacityResults({
      totalBits: capacityBits,
      totalBytes: capacityBytes,
      usableBytes: usableCapacity,
      examples: {
        text: Math.floor(usableCapacity * 0.9), // ~90% for text
        image: usableCapacity < 1024 * 10 ? 'Too small' : 'Small images possible',
        document: usableCapacity > 1024 * 50 ? 'Possible' : 'Limited'
      }
    });

    generateAIRecommendation(usableCapacity);
  };

  const generateAIRecommendation = (capacity) => {
    let recommendation = {
      capacity: formatBytes(capacity),
      suggestions: [],
      warnings: [],
      bestUse: ''
    };

    if (bitsPerChannel === 1) {
      recommendation.suggestions.push('✅ Lowest detection risk - ideal for sensitive data');
      recommendation.suggestions.push('✅ Best for smaller payloads (text messages, keys)');
      recommendation.bestUse = 'Highly secure communications with small payload';
    } else if (bitsPerChannel === 2) {
      recommendation.suggestions.push('⚖️ Balanced capacity and security');
      recommendation.suggestions.push('✅ Good for medium-sized data (documents, small images)');
      recommendation.bestUse = 'General purpose steganography';
    } else if (bitsPerChannel >= 3) {
      recommendation.suggestions.push('📦 Maximum capacity for large files');
      recommendation.warnings.push('⚠️ Higher detection risk - use carefully');
      recommendation.warnings.push('⚠️ More visible artifacts possible');
      recommendation.bestUse = 'Large file storage in trusted environments';
    }

    if (algorithm === 'dct') {
      recommendation.suggestions.push('🛡️ DCT: Resistant to JPEG compression');
      recommendation.bestUse += ' (web/social media sharing)';
    } else if (algorithm === 'dwt') {
      recommendation.suggestions.push('⭐ DWT: Superior imperceptibility');
      recommendation.bestUse += ' (high-quality requirements)';
    }

    setAiRecommendation(recommendation);
  };

  const handleFileUpload = async (file) => {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    setCarrierFile(file);
    setCarrierPreview(URL.createObjectURL(file));
    setError(null);
    setAnalyzing(true);

    // Get actual dimensions
    const img = new Image();
    img.onload = async () => {
      setWidth(img.width);
      setHeight(img.height);
      
      // Analyze with backend
      try {
        const formData = new FormData();
        formData.append('carrier', file);
        formData.append('payload_text', 'test');
        
        const response = await axios.post(`${API_BASE_URL}/api/analyze`, formData);
        const imageStats = response.data.image_stats;
        
        // Update with real analysis
        setCapacityResults({
          totalBytes: imageStats.max_capacity_bytes,
          usableBytes: Math.floor(imageStats.max_capacity_bytes * 0.95),
          totalPixels: imageStats.width * imageStats.height,
          dimensions: `${imageStats.width} × ${imageStats.height}`,
          imageQuality: {
            entropy: imageStats.entropy.toFixed(2),
            texture: imageStats.texture_score.toFixed(2),
            complexity: imageStats.variance > 1000 ? 'High' : imageStats.variance > 500 ? 'Medium' : 'Low'
          }
        });

        // AI recommendation from backend
        if (response.data.recommendation) {
          const rec = response.data.recommendation;
          setAiRecommendation({
            algorithm: rec.algorithm,
            bitsPerChannel: rec.bits_per_channel,
            detectionRisk: rec.detection_risk,
            explanation: rec.explanation,
            confidence: rec.confidence
          });
        }
      } catch (err) {
        console.error('Analysis error:', err);
        // Fall back to basic calculation
        calculateCapacity();
      } finally {
        setAnalyzing(false);
      }
    };
    img.src = URL.createObjectURL(file);
  };

  const formatBytes = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  return (
    <div className="capacity-calculator-page">
      <div className="page-header">
        <h1 className="gradient-text">📐 Capacity Calculator</h1>
        <p className="page-subtitle">
          Calculate how much data you can hide in your carrier files
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Mode Selection */}
      <div className="card">
        <div className="mode-selector">
          <button
            className={`mode-btn ${mode === 'manual' ? 'active' : ''}`}
            onClick={() => setMode('manual')}
          >
            📊 Manual Input
          </button>
          <button
            className={`mode-btn ${mode === 'file' ? 'active' : ''}`}
            onClick={() => setMode('file')}
          >
            📁 Upload File
          </button>
        </div>

        {mode === 'manual' ? (
          <>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Algorithm</label>
                <select
                  className="form-control"
                  value={algorithm}
                  onChange={(e) => setAlgorithm(e.target.value)}
                >
                  <option value="lsb">LSB (Image)</option>
                  <option value="dct">DCT (Image)</option>
                  <option value="dwt">DWT (Image)</option>
                  <option value="audio">Audio WAV</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Bits Per Channel</label>
                <select
                  className="form-control"
                  value={bitsPerChannel}
                  onChange={(e) => setBitsPerChannel(parseInt(e.target.value))}
                >
                  <option value="1">1 bit (Most Secure)</option>
                  <option value="2">2 bits (Balanced)</option>
                  <option value="3">3 bits</option>
                  <option value="4">4 bits (Max Capacity)</option>
                </select>
              </div>

              {algorithm !== 'audio' && (
                <>
                  <div className="form-group">
                    <label className="form-label">Width (pixels)</label>
                    <input
                      type="number"
                      className="form-control"
                      value={width}
                      onChange={(e) => setWidth(parseInt(e.target.value) || 0)}
                      min="1"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Height (pixels)</label>
                    <input
                      type="number"
                      className="form-control"
                      value={height}
                      onChange={(e) => setHeight(parseInt(e.target.value) || 0)}
                      min="1"
                    />
                  </div>
                </>
              )}
            </div>

            <button
              className="btn btn-primary btn-large"
              onClick={calculateCapacity}
              style={{ marginTop: '1.5rem' }}
            >
              🔢 Calculate Capacity
            </button>
          </>
        ) : (
          <div className="file-upload-section">
            <div
              className="file-input large-file-input"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => handleFileUpload(e.target.files[0])}
                style={{ display: 'none' }}
              />
              <div className="file-icon-large">
                {carrierPreview ? '✅' : '🖼️'}
              </div>
              <div className="file-text">
                {carrierFile ? carrierFile.name : 'Click to upload carrier image'}
              </div>
              {carrierFile && (
                <div className="file-size">
                  {formatBytes(carrierFile.size)}
                </div>
              )}
            </div>

            {carrierPreview && (
              <div className="image-preview">
                <img src={carrierPreview} alt="Carrier preview" />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Results */}
      {capacityResults && (
        <>
          <div className="card results-card">
            <h2 className="section-title">📊 Capacity Results</h2>
            
            <div className="capacity-stats-grid">
              <div className="capacity-stat">
                <div className="capacity-stat-icon">📦</div>
                <div className="capacity-stat-content">
                  <div className="capacity-stat-label">Total Capacity</div>
                  <div className="capacity-stat-value">
                    {formatBytes(capacityResults.usableBytes)}
                  </div>
                  <div className="capacity-stat-meta">
                    {formatNumber(capacityResults.totalBits)} bits
                  </div>
                </div>
              </div>

              {capacityResults.dimensions && (
                <div className="capacity-stat">
                  <div className="capacity-stat-icon">🖼️</div>
                  <div className="capacity-stat-content">
                    <div className="capacity-stat-label">Dimensions</div>
                    <div className="capacity-stat-value">
                      {capacityResults.dimensions}
                    </div>
                    <div className="capacity-stat-meta">
                      {formatNumber(capacityResults.totalPixels)} pixels
                    </div>
                  </div>
                </div>
              )}

              <div className="capacity-stat">
                <div className="capacity-stat-icon">📝</div>
                <div className="capacity-stat-content">
                  <div className="capacity-stat-label">Text Capacity</div>
                  <div className="capacity-stat-value">
                    ~{formatNumber(capacityResults.usableBytes)} chars
                  </div>
                  <div className="capacity-stat-meta">
                    ~{Math.floor(capacityResults.usableBytes / 500)} pages
                  </div>
                </div>
              </div>
            </div>

            {capacityResults.imageQuality && (
              <div className="image-quality-section">
                <h3>Image Quality Analysis</h3>
                <div className="quality-metrics">
                  <div className="quality-metric">
                    <span className="quality-label">Entropy:</span>
                    <span className="quality-value">{capacityResults.imageQuality.entropy}</span>
                  </div>
                  <div className="quality-metric">
                    <span className="quality-label">Texture Score:</span>
                    <span className="quality-value">{capacityResults.imageQuality.texture}</span>
                  </div>
                  <div className="quality-metric">
                    <span className="quality-label">Complexity:</span>
                    <span className="quality-value">{capacityResults.imageQuality.complexity}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* AI Recommendations */}
          {aiRecommendation && (
            <div className="card ai-recommendation-card">
              <h2 className="section-title">🤖 AI Recommendations</h2>
              
              {aiRecommendation.explanation && (
                <div className="ai-explanation">
                  <p>{aiRecommendation.explanation}</p>
                  {aiRecommendation.confidence && (
                    <div className="confidence-badge">
                      Confidence: {aiRecommendation.confidence}%
                    </div>
                  )}
                </div>
              )}

              {aiRecommendation.algorithm && (
                <div className="recommendation-highlight">
                  <strong>Recommended:</strong> {aiRecommendation.algorithm.toUpperCase()} 
                  with {aiRecommendation.bitsPerChannel} bits/channel
                  <span className={`risk-badge risk-${aiRecommendation.detectionRisk}`}>
                    {aiRecommendation.detectionRisk} risk
                  </span>
                </div>
              )}

              {aiRecommendation.bestUse && (
                <div className="best-use">
                  <strong>💡 Best Use Case:</strong> {aiRecommendation.bestUse}
                </div>
              )}

              {aiRecommendation.suggestions && aiRecommendation.suggestions.length > 0 && (
                <div className="suggestions-list">
                  {aiRecommendation.suggestions.map((suggestion, idx) => (
                    <div key={idx} className="suggestion-item">
                      {suggestion}
                    </div>
                  ))}
                </div>
              )}

              {aiRecommendation.warnings && aiRecommendation.warnings.length > 0 && (
                <div className="warnings-list">
                  {aiRecommendation.warnings.map((warning, idx) => (
                    <div key={idx} className="warning-item">
                      {warning}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {analyzing && (
        <div className="card analyzing-card">
          <div className="analyzing-content">
            <div className="spinner"></div>
            <p>Analyzing image with AI...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default CapacityCalculator;