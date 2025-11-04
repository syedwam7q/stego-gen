import React, { useState, useRef } from 'react';
import axios from 'axios';
import ProgressBar from './ProgressBar';

const API_BASE = 'http://localhost:8000';

function Steganalysis() {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  
  const fileInputRef = useRef(null);

  const handleFileChange = (file) => {
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }
    
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`File too large: ${(file.size / 1024 / 1024).toFixed(2)}MB. Maximum: 50MB`);
      return;
    }
    
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setResults(null);
    setError(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileChange(file);
  };

  const handleAnalyze = async () => {
    if (!imageFile) {
      setError('Please select an image to analyze');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setProgress(0);
    setProgressStatus('Running steganalysis tests...');

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 200);

    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await axios.post(`${API_BASE}/api/ai/steganalysis`, formData);
      clearInterval(progressInterval);
      setProgress(100);
      setProgressStatus('Analysis complete!');
      setTimeout(() => {
        setResults(response.data.results);
        setProgress(0);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      setProgress(0);
      const errorMsg = err.response?.data?.detail || err.message || 'Analysis failed';
      setError(errorMsg);
      console.error('Steganalysis error:', err);
    } finally {
      setTimeout(() => {
        setAnalyzing(false);
        setProgressStatus('');
      }, 500);
    }
  };

  const getSuspicionColor = (level) => {
    switch(level) {
      case 'high': return '#ff4444';
      case 'medium': return '#ffaa00';
      case 'low': return '#00cc66';
      default: return '#888';
    }
  };

  const getScoreColor = (score) => {
    if (score < 30) return '#00cc66';
    if (score < 50) return '#88cc00';
    if (score < 70) return '#ffaa00';
    return '#ff4444';
  };

  return (
    <div className="steganalysis-page">
      {error && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="card" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
          🔍 AI Steganalysis
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Detect hidden data in images using advanced AI-powered statistical analysis
        </p>

        {/* File Upload */}
        <div className="form-group">
          <label className="form-label">Image to Analyze</label>
          <div
            className={`file-input ${imageFile ? 'has-file' : ''} ${dragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={(e) => handleFileChange(e.target.files[0])}
              style={{ display: 'none' }}
            />
            <div className="file-icon">
              {imageFile ? '✅' : '🖼️'}
            </div>
            <p>{imageFile ? imageFile.name : 'Click or drag image file here'}</p>
            {imageFile && <div className="file-size">{(imageFile.size / 1024).toFixed(2)} KB</div>}
          </div>
          {imagePreview && (
            <img src={imagePreview} alt="Preview" className="preview-image" style={{ marginTop: '1rem' }} />
          )}
        </div>

        {/* Analyze Button */}
        <button 
          className="btn btn-primary"
          onClick={handleAnalyze}
          disabled={!imageFile || analyzing}
          style={{ marginTop: '1rem', width: '100%' }}
        >
          {analyzing ? 'Analyzing...' : '🔬 Run Steganalysis'}
        </button>

        {/* Progress Bar */}
        {analyzing && (
          <ProgressBar 
            progress={progress} 
            status={progressStatus}
            style={{ marginTop: '1rem' }}
          />
        )}
      </div>

      {/* Results */}
      {results && (
        <>
          {/* Overall Score */}
          <div className="card" style={{ marginBottom: '2rem', borderLeft: `4px solid ${getScoreColor(results.overall_score)}` }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Detection Results</h2>
            
            <div style={{ 
              background: 'var(--bg-tertiary)', 
              padding: '1.5rem', 
              borderRadius: '8px', 
              marginBottom: '1.5rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '3rem', fontWeight: 'bold', color: getScoreColor(results.overall_score) }}>
                {results.overall_score.toFixed(1)}
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Detection Score (0-100)
              </div>
              <div style={{ 
                fontSize: '1.1rem', 
                fontWeight: '600', 
                marginTop: '1rem', 
                color: 'var(--text-primary)' 
              }}>
                {results.likelihood}
              </div>
            </div>

            {/* AI Interpretation */}
            <div style={{ 
              background: 'var(--bg-tertiary)', 
              padding: '1rem', 
              borderRadius: '8px', 
              borderLeft: '3px solid var(--primary)',
              marginBottom: '1.5rem'
            }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                🤖 AI Expert Analysis
              </h3>
              <p style={{ color: 'var(--text-primary)', lineHeight: '1.6', margin: 0 }}>
                {results.ai_interpretation}
              </p>
            </div>

            {/* Recommendations */}
            <div style={{ marginTop: '1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '0.75rem' }}>📋 Recommendations</h3>
              <ul style={{ paddingLeft: '1.5rem', margin: 0 }}>
                {results.recommendations.map((rec, idx) => (
                  <li key={idx} style={{ marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Detailed Tests */}
          <div className="card">
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Detailed Test Results</h2>

            {/* LSB Analysis */}
            {results.tests.lsb_analysis && (
              <div style={{ 
                marginBottom: '1.5rem', 
                padding: '1rem', 
                background: 'var(--bg-tertiary)', 
                borderRadius: '8px',
                borderLeft: `4px solid ${getSuspicionColor(results.tests.lsb_analysis.suspicion_level)}`
              }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  🔬 LSB Pattern Analysis
                  <span style={{ 
                    fontSize: '0.8rem', 
                    padding: '0.2rem 0.6rem', 
                    borderRadius: '12px', 
                    background: getSuspicionColor(results.tests.lsb_analysis.suspicion_level),
                    color: 'white',
                    marginLeft: 'auto'
                  }}>
                    {results.tests.lsb_analysis.suspicion_level.toUpperCase()}
                  </span>
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                  {results.tests.lsb_analysis.explanation}
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div>LSB Entropy: <strong>{results.tests.lsb_analysis.lsb_entropy}</strong></div>
                  <div>Pattern Score: <strong>{results.tests.lsb_analysis.sequential_pattern_score}</strong></div>
                </div>
              </div>
            )}

            {/* Chi-Square Test */}
            {results.tests.chi_square_test && (
              <div style={{ 
                marginBottom: '1.5rem', 
                padding: '1rem', 
                background: 'var(--bg-tertiary)', 
                borderRadius: '8px',
                borderLeft: `4px solid ${getSuspicionColor(results.tests.chi_square_test.suspicion_level)}`
              }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  📊 Chi-Square Statistical Test
                  <span style={{ 
                    fontSize: '0.8rem', 
                    padding: '0.2rem 0.6rem', 
                    borderRadius: '12px', 
                    background: getSuspicionColor(results.tests.chi_square_test.suspicion_level),
                    color: 'white',
                    marginLeft: 'auto'
                  }}>
                    {results.tests.chi_square_test.suspicion_level.toUpperCase()}
                  </span>
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                  {results.tests.chi_square_test.explanation}
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div>Chi-Square: <strong>{results.tests.chi_square_test.chi_square_statistic}</strong></div>
                  <div>P-Value: <strong>{results.tests.chi_square_test.p_value}</strong></div>
                </div>
              </div>
            )}

            {/* Histogram Analysis */}
            {results.tests.histogram_analysis && (
              <div style={{ 
                marginBottom: '1.5rem', 
                padding: '1rem', 
                background: 'var(--bg-tertiary)', 
                borderRadius: '8px',
                borderLeft: `4px solid ${getSuspicionColor(results.tests.histogram_analysis.suspicion_level)}`
              }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  📈 Histogram Analysis
                  <span style={{ 
                    fontSize: '0.8rem', 
                    padding: '0.2rem 0.6rem', 
                    borderRadius: '12px', 
                    background: getSuspicionColor(results.tests.histogram_analysis.suspicion_level),
                    color: 'white',
                    marginLeft: 'auto'
                  }}>
                    {results.tests.histogram_analysis.suspicion_level.toUpperCase()}
                  </span>
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                  {results.tests.histogram_analysis.explanation}
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div>Anomaly Ratio: <strong>{results.tests.histogram_analysis.pair_anomaly_ratio}</strong></div>
                  <div>Anomalous Pairs: <strong>{results.tests.histogram_analysis.anomalous_pairs}</strong></div>
                </div>
              </div>
            )}

            {/* RS Analysis */}
            {results.tests.rs_analysis && (
              <div style={{ 
                marginBottom: '1.5rem', 
                padding: '1rem', 
                background: 'var(--bg-tertiary)', 
                borderRadius: '8px',
                borderLeft: `4px solid ${getSuspicionColor(results.tests.rs_analysis.suspicion_level)}`
              }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  🔍 RS Steganalysis
                  <span style={{ 
                    fontSize: '0.8rem', 
                    padding: '0.2rem 0.6rem', 
                    borderRadius: '12px', 
                    background: getSuspicionColor(results.tests.rs_analysis.suspicion_level),
                    color: 'white',
                    marginLeft: 'auto'
                  }}>
                    {results.tests.rs_analysis.suspicion_level.toUpperCase()}
                  </span>
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                  {results.tests.rs_analysis.explanation}
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div>RS Ratio: <strong>{results.tests.rs_analysis.rs_ratio}</strong></div>
                  <div>Est. Embedding: <strong>{results.tests.rs_analysis.estimated_embedding_percentage.toFixed(1)}%</strong></div>
                </div>
              </div>
            )}

            {/* Visual Analysis */}
            {results.tests.visual_analysis && (
              <div style={{ 
                marginBottom: '1.5rem', 
                padding: '1rem', 
                background: 'var(--bg-tertiary)', 
                borderRadius: '8px',
                borderLeft: `4px solid ${getSuspicionColor(results.tests.visual_analysis.suspicion_level)}`
              }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  👁️ Visual LSB Plane Analysis
                  <span style={{ 
                    fontSize: '0.8rem', 
                    padding: '0.2rem 0.6rem', 
                    borderRadius: '12px', 
                    background: getSuspicionColor(results.tests.visual_analysis.suspicion_level),
                    color: 'white',
                    marginLeft: 'auto'
                  }}>
                    {results.tests.visual_analysis.suspicion_level.toUpperCase()}
                  </span>
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                  {results.tests.visual_analysis.explanation}
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div>LSB Variance: <strong>{results.tests.visual_analysis.lsb_plane_variance.toFixed(0)}</strong></div>
                  <div>R: <strong>{results.tests.visual_analysis.channel_variances[0].toFixed(0)}</strong></div>
                  <div>G: <strong>{results.tests.visual_analysis.channel_variances[1].toFixed(0)}</strong></div>
                  <div>B: <strong>{results.tests.visual_analysis.channel_variances[2].toFixed(0)}</strong></div>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {!results && !analyzing && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', background: 'var(--bg-tertiary)' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🕵️</div>
          <h3 style={{ color: 'var(--text-secondary)', fontWeight: 'normal' }}>
            Upload an image to detect potential steganography
          </h3>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
            Our AI-powered analysis uses multiple statistical tests to identify hidden data
          </p>
        </div>
      )}
    </div>
  );
}

export default Steganalysis;