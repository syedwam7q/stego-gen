import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import './AlgorithmComparison.css';

const ALGORITHMS = [
  { id: 'lsb', name: 'LSB', icon: '📷', description: 'Least Significant Bit' },
  { id: 'dct', name: 'DCT', icon: '🔍', description: 'Discrete Cosine Transform' },
  { id: 'dwt', name: 'DWT', icon: '🌊', description: 'Discrete Wavelet Transform' },
  { id: 'audio', name: 'Audio', icon: '🎵', description: 'Audio Steganography' },
  { id: 'video', name: 'Video', icon: '🎬', description: 'Video Steganography' }
];

function AlgorithmComparison() {
  const [algo1, setAlgo1] = useState('lsb');
  const [algo2, setAlgo2] = useState('dct');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // File upload recommendation state
  const [uploadedFile, setUploadedFile] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handleCompare = async () => {
    if (algo1 === algo2) {
      setError('Please select two different algorithms');
      return;
    }

    setLoading(true);
    setError(null);
    setComparison(null);

    try {
      const formData = new FormData();
      formData.append('algorithm1', algo1);
      formData.append('algorithm2', algo2);

      const response = await axios.post(`${API_BASE_URL}/api/ai/compare-algorithms`, formData);
      setComparison(response.data.comparison);
    } catch (err) {
      console.error('Comparison error:', err);
      // Fallback to client-side comparison
      setComparison(getFallbackComparison(algo1, algo2));
    } finally {
      setLoading(false);
    }
  };

  const getFallbackComparison = (a1, a2) => {
    // This shouldn't be needed anymore since backend has improved fallback
    return {
      capacity: {
        winner: a1.toUpperCase(),
        explanation: 'Backend comparison unavailable',
        score1: 50,
        score2: 50
      },
      security: {
        winner: a2.toUpperCase(),
        explanation: 'Backend comparison unavailable',
        score1: 50,
        score2: 50
      },
      robustness: {
        winner: a1.toUpperCase(),
        explanation: 'Backend comparison unavailable',
        score1: 50,
        score2: 50
      },
      complexity: {
        winner: a2.toUpperCase(),
        explanation: 'Backend comparison unavailable',
        score1: 50,
        score2: 50
      },
      use_cases: {
        [a1]: getUseCase(a1),
        [a2]: getUseCase(a2)
      },
      recommendation: `Choose based on your specific needs. Both algorithms have unique strengths.`
    };
  };

  const getUseCase = (algo) => {
    const useCases = {
      lsb: 'Large payloads, lossless formats, quick processing',
      dct: 'Web sharing, JPEG images, compression resistance',
      dwt: 'High security requirements, quality preservation',
      audio: 'Audio-based communication, WAV files',
      video: 'Massive capacity needs, video content'
    };
    return useCases[algo] || 'General purpose steganography';
  };

  const getAlgorithmInfo = (algoId) => {
    return ALGORITHMS.find(a => a.id === algoId) || ALGORITHMS[0];
  };

  const handleFileUpload = (file) => {
    if (!file) return;
    
    const fileType = file.type;
    if (!fileType.startsWith('image/') && !fileType.startsWith('audio/') && !fileType.startsWith('video/')) {
      setError('Please upload an image, audio, or video file');
      return;
    }
    
    setUploadedFile(file);
    setError(null);
    setRecommendation(null);
  };

  const handleAnalyzeFile = async () => {
    if (!uploadedFile) {
      setError('Please upload a file first');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('carrier', uploadedFile);
      formData.append('payload_text', 'sample_text_for_analysis');
      formData.append('goal', 'max_invisibility');

      const response = await axios.post(`${API_BASE_URL}/api/analyze`, formData);
      
      // Build recommendation from analysis
      const analysis = response.data;
      const recommendedAlgo = analysis.recommendation?.algorithm || 'LSB';
      const fileType = uploadedFile.type.startsWith('audio/') ? 'audio' : 
                       uploadedFile.type.startsWith('video/') ? 'video' : 'image';
      
      let algoSuggestions = [];
      if (fileType === 'image') {
        if (analysis.image_stats?.texture_score > 100) {
          algoSuggestions = [
            { algo: 'LSB', score: 95, reason: 'High texture makes LSB very effective and secure' },
            { algo: 'DWT', score: 85, reason: 'Excellent for high-security needs with good texture' },
            { algo: 'DCT', score: 75, reason: 'Good if image will be compressed later' }
          ];
        } else {
          algoSuggestions = [
            { algo: 'DWT', score: 90, reason: 'Best imperceptibility for smooth images' },
            { algo: 'DCT', score: 85, reason: 'Resistant to compression and processing' },
            { algo: 'LSB', score: 70, reason: 'Use 1-2 bits per channel for safety' }
          ];
        }
      } else if (fileType === 'audio') {
        algoSuggestions = [
          { algo: 'Audio LSB', score: 95, reason: 'Optimized for WAV audio files' },
          { algo: 'Video', score: 50, reason: 'Not applicable for audio files' }
        ];
      } else if (fileType === 'video') {
        algoSuggestions = [
          { algo: 'Video LSB', score: 95, reason: 'Massive capacity across frames' },
          { algo: 'Audio', score: 60, reason: 'Could extract audio track if needed' }
        ];
      }

      setRecommendation({
        fileType,
        fileSize: uploadedFile.size,
        fileName: uploadedFile.name,
        suggestions: algoSuggestions,
        imageStats: analysis.image_stats,
        aiRecommendation: analysis.recommendation
      });
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to analyze file. Please try again.');
    } finally {
      setAnalyzing(false);
    }
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
    if (file) handleFileUpload(file);
  };

  const getFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="algorithm-comparison-page">
      <div className="page-header">
        <h1 className="gradient-text">⚖️ Algorithm Comparison</h1>
        <p className="page-subtitle">
          Compare steganography algorithms side-by-side with AI insights
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* File Upload for Algorithm Recommendation */}
      <div className="card" style={{ background: 'linear-gradient(135deg, rgba(91, 110, 219, 0.05), rgba(139, 92, 246, 0.05))' }}>
        <h2 className="section-title">📤 Upload File for Smart Recommendation</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          Upload your carrier file and let AI analyze which algorithm works best for your specific file
        </p>

        <div
          className={`file-input ${uploadedFile ? 'has-file' : ''} ${dragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-upload-input').click()}
          style={{ marginBottom: '1rem' }}
        >
          <input
            id="file-upload-input"
            type="file"
            accept="image/*,audio/*,video/*"
            onChange={(e) => handleFileUpload(e.target.files[0])}
            style={{ display: 'none' }}
          />
          <div className="file-icon">
            {uploadedFile ? '✅' : '📁'}
          </div>
          <p>{uploadedFile ? uploadedFile.name : 'Click or drag your file here (image, audio, or video)'}</p>
          {uploadedFile && <div className="file-size">{getFileSize(uploadedFile.size)}</div>}
        </div>

        <button
          className="btn btn-primary"
          onClick={handleAnalyzeFile}
          disabled={!uploadedFile || analyzing}
          style={{ width: '100%', marginBottom: '1rem' }}
        >
          {analyzing ? '🔍 Analyzing...' : '🤖 Get AI Recommendation'}
        </button>

        {recommendation && (
          <div className="recommendation-results" style={{
            background: 'var(--bg-primary)',
            padding: '1.5rem',
            borderRadius: '12px',
            border: '2px solid var(--accent-primary)',
            marginTop: '1rem'
          }}>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              🎯 AI-Powered Algorithm Recommendations
            </h3>
            
            <div style={{ display: 'grid', gap: '1rem' }}>
              {recommendation.suggestions.map((suggestion, idx) => (
                <div key={idx} style={{
                  background: 'var(--bg-secondary)',
                  padding: '1rem',
                  borderRadius: '8px',
                  border: `2px solid ${idx === 0 ? 'var(--accent-success)' : 'var(--border-light'}`
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>
                      {idx === 0 && '🏆 '}{suggestion.algo}
                    </strong>
                    <span style={{
                      background: idx === 0 ? 'var(--accent-success)' : 'var(--accent-primary)',
                      color: 'white',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '12px',
                      fontSize: '0.85rem',
                      fontWeight: '600'
                    }}>
                      {suggestion.score}% Match
                    </span>
                  </div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
                    {suggestion.reason}
                  </p>
                </div>
              ))}
            </div>

            {recommendation.imageStats && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '0.5rem' }}>
                  📊 File Analysis:
                </strong>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.5rem', fontSize: '0.9rem' }}>
                  {recommendation.imageStats.texture_score && (
                    <div>
                      <span style={{ color: 'var(--text-tertiary)' }}>Texture: </span>
                      <strong style={{ color: 'var(--text-primary)' }}>{recommendation.imageStats.texture_score.toFixed(2)}</strong>
                    </div>
                  )}
                  {recommendation.imageStats.entropy && (
                    <div>
                      <span style={{ color: 'var(--text-tertiary)' }}>Entropy: </span>
                      <strong style={{ color: 'var(--text-primary)' }}>{recommendation.imageStats.entropy.toFixed(2)}</strong>
                    </div>
                  )}
                  {recommendation.imageStats.variance && (
                    <div>
                      <span style={{ color: 'var(--text-tertiary)' }}>Variance: </span>
                      <strong style={{ color: 'var(--text-primary)' }}>{recommendation.imageStats.variance.toFixed(2)}</strong>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Algorithm Selection */}
      <div className="card">
        <h2 className="section-title">Select Algorithms to Compare</h2>
        
        <div className="algorithm-selector-grid">
          <div className="algorithm-selector">
            <label className="form-label">First Algorithm</label>
            <div className="algorithm-options">
              {ALGORITHMS.map(algo => (
                <div
                  key={algo.id}
                  className={`algorithm-option ${algo1 === algo.id ? 'selected' : ''}`}
                  onClick={() => setAlgo1(algo.id)}
                >
                  <div className="algorithm-option-icon">{algo.icon}</div>
                  <div className="algorithm-option-name">{algo.name}</div>
                  <div className="algorithm-option-desc">{algo.description}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="vs-divider">
            <div className="vs-circle">VS</div>
          </div>

          <div className="algorithm-selector">
            <label className="form-label">Second Algorithm</label>
            <div className="algorithm-options">
              {ALGORITHMS.map(algo => (
                <div
                  key={algo.id}
                  className={`algorithm-option ${algo2 === algo.id ? 'selected' : ''}`}
                  onClick={() => setAlgo2(algo.id)}
                >
                  <div className="algorithm-option-icon">{algo.icon}</div>
                  <div className="algorithm-option-name">{algo.name}</div>
                  <div className="algorithm-option-desc">{algo.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <button
          className="btn btn-primary btn-large"
          onClick={handleCompare}
          disabled={loading || algo1 === algo2}
          style={{ marginTop: '2rem' }}
        >
          {loading ? '⏳ Comparing...' : '🔍 Compare Algorithms'}
        </button>
      </div>

      {/* Comparison Results */}
      {comparison && (
        <>
          {/* Head-to-Head Comparison */}
          <div className="card comparison-results">
            <h2 className="section-title">🏆 Head-to-Head Comparison</h2>
            
            <div className="comparison-grid">
              {['capacity', 'security', 'robustness', 'complexity'].map(category => (
                <div key={category} className="comparison-category">
                  <div className="comparison-category-header">
                    <h3>{category.charAt(0).toUpperCase() + category.slice(1)}</h3>
                  </div>
                  
                  <div className="comparison-winner">
                    <div className="winner-badge">
                      🏆 Winner: {comparison[category].winner}
                    </div>
                    <p className="winner-explanation">
                      {comparison[category].explanation}
                    </p>
                  </div>

                  <div className="comparison-bars">
                    <div className={`comparison-bar ${comparison[category].winner === getAlgorithmInfo(algo1).name.toUpperCase() ? 'winner' : ''}`}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                        <span>{getAlgorithmInfo(algo1).name}</span>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
                          {comparison[category].score1 || 0}%
                        </span>
                      </div>
                      <div className="bar-fill" style={{ width: `${comparison[category].score1 || 70}%` }} />
                    </div>
                    <div className={`comparison-bar ${comparison[category].winner === getAlgorithmInfo(algo2).name.toUpperCase() ? 'winner' : ''}`}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                        <span>{getAlgorithmInfo(algo2).name}</span>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-tertiary)' }}>
                          {comparison[category].score2 || 0}%
                        </span>
                      </div>
                      <div className="bar-fill" style={{ width: `${comparison[category].score2 || 70}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Use Cases */}
          <div className="card">
            <h2 className="section-title">💡 Best Use Cases</h2>
            <div className="use-cases-grid">
              <div className="use-case-card">
                <div className="use-case-header">
                  <span className="use-case-icon">{getAlgorithmInfo(algo1).icon}</span>
                  <h3>{getAlgorithmInfo(algo1).name}</h3>
                </div>
                <p>{comparison.use_cases[algo1]}</p>
              </div>

              <div className="use-case-card">
                <div className="use-case-header">
                  <span className="use-case-icon">{getAlgorithmInfo(algo2).icon}</span>
                  <h3>{getAlgorithmInfo(algo2).name}</h3>
                </div>
                <p>{comparison.use_cases[algo2]}</p>
              </div>
            </div>
          </div>

          {/* AI Recommendation */}
          <div className="card ai-recommendation">
            <h2 className="section-title">🤖 AI Recommendation</h2>
            <div className="ai-recommendation-content">
              <div className="recommendation-icon">💡</div>
              <p>{comparison.recommendation}</p>
            </div>
          </div>
        </>
      )}

      {/* Algorithm Details Reference */}
      <div className="card">
        <h2 className="section-title">📚 Algorithm Details Reference</h2>
        <div className="algorithm-details-grid">
          {ALGORITHMS.map(algo => (
            <div key={algo.id} className="algorithm-detail-card">
              <div className="algorithm-detail-icon">{algo.icon}</div>
              <h3>{algo.name}</h3>
              <p className="algorithm-detail-desc">{algo.description}</p>
              <div className="algorithm-detail-tags">
                {algo.id === 'lsb' && (
                  <>
                    <span className="tag">High Capacity</span>
                    <span className="tag">Fast</span>
                    <span className="tag">Simple</span>
                  </>
                )}
                {algo.id === 'dct' && (
                  <>
                    <span className="tag">Robust</span>
                    <span className="tag">JPEG Safe</span>
                    <span className="tag">Medium Capacity</span>
                  </>
                )}
                {algo.id === 'dwt' && (
                  <>
                    <span className="tag">High Security</span>
                    <span className="tag">Quality</span>
                    <span className="tag">Complex</span>
                  </>
                )}
                {algo.id === 'audio' && (
                  <>
                    <span className="tag">Inaudible</span>
                    <span className="tag">WAV</span>
                    <span className="tag">Large Files</span>
                  </>
                )}
                {algo.id === 'video' && (
                  <>
                    <span className="tag">Massive Capacity</span>
                    <span className="tag">Multi-Format</span>
                    <span className="tag">Complex</span>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AlgorithmComparison;