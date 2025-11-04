import React, { useState, useRef } from 'react';
import axios from 'axios';
import ProgressBar from './ProgressBar';

const API_BASE = 'http://localhost:8000';

const formatError = (error) => {
  if (typeof error === 'string') {
    return error;
  }
  if (Array.isArray(error)) {
    return error.map(err => {
      if (typeof err === 'object' && err !== null) {
        return err.msg || JSON.stringify(err);
      }
      return String(err);
    }).join(', ');
  }
  if (typeof error === 'object' && error !== null) {
    return error.msg || error.message || JSON.stringify(error);
  }
  return String(error);
};

const getFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

function Encode() {
  const [algorithm, setAlgorithm] = useState('lsb');
  const [carrierFile, setCarrierFile] = useState(null);
  const [carrierPreview, setCarrierPreview] = useState(null);
  const [payloadText, setPayloadText] = useState('');
  const [payloadFile, setPayloadFile] = useState(null);
  const [encryptionKey, setEncryptionKey] = useState('');
  const [bitsPerChannel, setBitsPerChannel] = useState(1);
  const [strength, setStrength] = useState(10);
  const [usePayloadFile, setUsePayloadFile] = useState(false);
  
  const [analyzing, setAnalyzing] = useState(false);
  const [encoding, setEncoding] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  
  const [analysis, setAnalysis] = useState(null);
  const [encodeResult, setEncodeResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  
  const carrierInputRef = useRef(null);
  const payloadInputRef = useRef(null);

  const getAcceptedFileTypes = () => {
    switch (algorithm) {
      case 'audio':
        return { types: ['audio/wav', 'audio/wave', 'audio/x-wav'], label: 'WAV audio files' };
      case 'video':
        return { types: ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'], label: 'MP4, AVI, MOV, MKV video files' };
      case 'lsb':
      case 'dct':
      case 'dwt':
      default:
        return { types: ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff'], label: 'PNG, JPG, BMP, or TIFF images' };
    }
  };

  const handleFileChange = (file) => {
    if (!file) return;
    
    const accepted = getAcceptedFileTypes();
    if (!accepted.types.includes(file.type)) {
      setError(`Invalid file type. Please use ${accepted.label}`);
      return;
    }
    
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`File too large: ${getFileSize(file.size)}. Maximum: 50MB`);
      return;
    }
    
    if (file.size === 0) {
      setError('File is empty');
      return;
    }
    
    setCarrierFile(file);
    if (algorithm === 'audio') {
      setCarrierPreview(null);
    } else if (algorithm === 'video') {
      setCarrierPreview(null);
    } else {
      setCarrierPreview(URL.createObjectURL(file));
    }
    setAnalysis(null);
    setEncodeResult(null);
    setError(null);
  };

  const handlePayloadFileChange = (file) => {
    if (!file) return;
    
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`Payload file too large: ${getFileSize(file.size)}. Maximum: 5MB`);
      return;
    }
    setPayloadFile(file);
    setPayloadText('');
    setError(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleCarrierDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileChange(file);
  };

  const handlePayloadDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handlePayloadFileChange(file);
  };

  const handleAnalyze = async () => {
    if (!carrierFile || !payloadText) {
      setError('Please select a carrier image and enter payload text');
      return;
    }
    
    if (payloadText.length > 10 * 1024 * 1024) {
      setError('Payload text too large. Maximum: 10MB');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setProgress(0);
    setProgressStatus('Analyzing carrier with AI...');

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 150);

    const formData = new FormData();
    formData.append('carrier', carrierFile);
    formData.append('payload_text', payloadText);
    formData.append('goal', 'max_invisibility');

    try {
      const response = await axios.post(`${API_BASE}/api/analyze`, formData);
      clearInterval(progressInterval);
      setProgress(100);
      setProgressStatus('Analysis complete!');
      setTimeout(() => {
        setAnalysis(response.data);
        setProgress(0);
      }, 500);
      const recommendedBits = response.data.recommendation.bits_per_channel;
      if (Number.isInteger(recommendedBits) && recommendedBits >= 1 && recommendedBits <= 4) {
        setBitsPerChannel(recommendedBits);
      }
    } catch (err) {
      clearInterval(progressInterval);
      setProgress(0);
      const errorMsg = formatError(err.response?.data?.detail || err.message || 'Analysis failed');
      setError(errorMsg);
      console.error('Analysis error:', err);
    } finally {
      setTimeout(() => {
        setAnalyzing(false);
        setProgressStatus('');
      }, 500);
    }
  };

  const handleEncode = async () => {
    if (!carrierFile) {
      setError('Please select a carrier file');
      return;
    }
    
    if (algorithm === 'lsb' && !payloadText && !payloadFile) {
      setError('Please enter payload text or select a payload file');
      return;
    }
    
    if (algorithm !== 'lsb' && !payloadText) {
      setError('Please enter payload text');
      return;
    }
    
    if (payloadText && payloadText.length > 10 * 1024 * 1024) {
      setError('Payload text too large. Maximum: 10MB');
      return;
    }
    
    if (encryptionKey && encryptionKey.length < 8) {
      setError('Encryption key too weak. Use at least 8 characters');
      return;
    }

    setEncoding(true);
    setError(null);
    setProgress(0);
    setProgressStatus('Preparing to encode...');

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 300);

    const formData = new FormData();
    const endpoints = {
      lsb: '/api/encode',
      dct: '/api/encode/dct',
      dwt: '/api/encode/dwt',
      audio: '/api/encode/audio',
      video: '/api/encode/video'
    };

    formData.append('carrier', carrierFile);

    if (payloadFile && algorithm === 'lsb') {
      formData.append('payload_file', payloadFile);
    } else {
      formData.append('payload_text', payloadText);
    }

    if (algorithm === 'lsb') {
      if (!Number.isInteger(bitsPerChannel) || bitsPerChannel < 1 || bitsPerChannel > 4) {
        setError('Bits per channel must be between 1 and 4');
        setEncoding(false);
        return;
      }
      formData.append('bits_per_channel', bitsPerChannel);
    } else if (algorithm === 'dct' || algorithm === 'dwt') {
      formData.append('strength', strength);
    } else if (algorithm === 'video') {
      formData.append('bits_per_channel', bitsPerChannel);
      formData.append('frame_skip', 1);
    } else if (algorithm === 'audio') {
      formData.append('bits_per_sample', 2);
    }
    
    if (encryptionKey) {
      formData.append('encryption_key', encryptionKey);
    }

    if (analysis?.file_id) {
      formData.append('file_id', analysis.file_id);
    }

    try {
      setProgressStatus('Embedding secret data...');
      const response = await axios.post(`${API_BASE}${endpoints[algorithm]}`, formData);
      clearInterval(progressInterval);
      setProgress(100);
      setProgressStatus('Encoding complete!');
      setTimeout(() => {
        setEncodeResult(response.data);
        setProgress(0);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      setProgress(0);
      const errorMsg = formatError(err.response?.data?.detail || err.message || 'Encoding failed');
      setError(errorMsg);
      console.error('Encoding error:', err);
    } finally {
      setTimeout(() => {
        setEncoding(false);
        setProgressStatus('');
      }, 500);
    }
  };

  const handleDownload = () => {
    if (encodeResult?.download_url) {
      window.open(`${API_BASE}${encodeResult.download_url}`, '_blank');
    }
  };

  return (
    <div className="encode-page">
      {error && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="card" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Encode Message</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Hide your secrets using advanced steganography algorithms
        </p>

        {/* Algorithm Selection */}
        <div className="form-group">
          <label className="form-label">Algorithm</label>
          <select 
            className="form-control" 
            value={algorithm} 
            onChange={(e) => {
              setAlgorithm(e.target.value);
              setCarrierFile(null);
              setCarrierPreview(null);
              setPayloadFile(null);
              setEncodeResult(null);
              setError(null);
            }}
          >
            <option value="lsb">LSB (Least Significant Bit) - Images</option>
            <option value="dct">DCT (Discrete Cosine Transform) - Images</option>
            <option value="dwt">DWT (Discrete Wavelet Transform) - Images</option>
            <option value="audio">Audio LSB - WAV Files</option>
            <option value="video">Video LSB - MP4/AVI/MOV/MKV</option>
          </select>
          <small style={{ color: 'var(--text-tertiary)', marginTop: '0.5rem', display: 'block' }}>
            {algorithm === 'lsb' && '✓ Classic spatial domain steganography with adjustable bits per channel'}
            {algorithm === 'dct' && '✓ Frequency domain embedding, resistant to compression'}
            {algorithm === 'dwt' && '✓ Wavelet domain embedding, excellent imperceptibility'}
            {algorithm === 'audio' && '✓ Hide data in audio samples using LSB technique'}
            {algorithm === 'video' && '✓ Hide data across video frames using LSB technique'}
          </small>
        </div>

        {/* Carrier File Upload */}
        <div className="form-group">
          <label className="form-label">
            {algorithm === 'audio' ? 'Carrier Audio File' : algorithm === 'video' ? 'Carrier Video File' : 'Carrier Image'}
          </label>
          <div
            className={`file-input ${carrierFile ? 'has-file' : ''} ${dragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleCarrierDrop}
            onClick={() => carrierInputRef.current?.click()}
          >
            <input
              ref={carrierInputRef}
              type="file"
              accept={algorithm === 'audio' ? 'audio/wav' : algorithm === 'video' ? 'video/*' : 'image/*'}
              onChange={(e) => handleFileChange(e.target.files[0])}
              style={{ display: 'none' }}
            />
            <div className="file-icon">
              {carrierFile ? '✅' : algorithm === 'audio' ? '🔊' : algorithm === 'video' ? '🎥' : '🖼️'}
            </div>
            <p>{carrierFile ? carrierFile.name : `Click or drag ${algorithm === 'audio' ? 'audio' : algorithm === 'video' ? 'video' : 'image'} file here`}</p>
            {carrierFile && <div className="file-size">{getFileSize(carrierFile.size)}</div>}
          </div>
          {carrierPreview && (
            <img src={carrierPreview} alt="Carrier preview" className="preview-image" style={{ marginTop: '1rem' }} />
          )}
        </div>

        {/* Payload Input */}
        <div className="form-group">
          <label className="form-label">Secret Payload</label>
          
          {algorithm === 'lsb' && (
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', fontSize: '0.95rem' }}>
                <input 
                  type="radio" 
                  checked={!usePayloadFile} 
                  onChange={() => {
                    setUsePayloadFile(false);
                    setPayloadFile(null);
                  }}
                  style={{ marginRight: '0.5rem', cursor: 'pointer' }}
                />
                Text Message
              </label>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', fontSize: '0.95rem' }}>
                <input 
                  type="radio" 
                  checked={usePayloadFile} 
                  onChange={() => setUsePayloadFile(true)}
                  style={{ marginRight: '0.5rem', cursor: 'pointer' }}
                />
                File Upload
              </label>
            </div>
          )}

          {!usePayloadFile || algorithm !== 'lsb' ? (
            <>
              <textarea
                className="form-control"
                rows="4"
                placeholder="Enter your secret message here..."
                value={payloadText}
                onChange={(e) => setPayloadText(e.target.value)}
              />
              <small style={{ color: 'var(--text-tertiary)', marginTop: '0.5rem', display: 'block' }}>
                {payloadText.length} characters • {getFileSize(new Blob([payloadText]).size)}
              </small>
            </>
          ) : (
            <>
              <div
                className={`file-input ${payloadFile ? 'has-file' : ''}`}
                onClick={() => payloadInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handlePayloadDrop}
              >
                <input
                  ref={payloadInputRef}
                  type="file"
                  onChange={(e) => handlePayloadFileChange(e.target.files[0])}
                  style={{ display: 'none' }}
                />
                <div className="file-icon">{payloadFile ? '✅' : '📄'}</div>
                <p>{payloadFile ? payloadFile.name : 'Click or drag file here'}</p>
                {payloadFile && <div className="file-size">{getFileSize(payloadFile.size)}</div>}
              </div>
            </>
          )}
        </div>

        {/* Algorithm Parameters */}
        {algorithm === 'lsb' && (
          <div className="form-group">
            <label className="form-label">
              Bits per Channel <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{bitsPerChannel}</span>
            </label>
            <input
              type="range"
              min="1"
              max="4"
              value={bitsPerChannel}
              onChange={(e) => setBitsPerChannel(parseInt(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', height: '6px' }}
            />
            <small style={{ color: 'var(--text-tertiary)', display: 'block', marginTop: '0.5rem' }}>
              Higher = more capacity but lower quality. Recommended: 1-2
            </small>
          </div>
        )}

        {algorithm === 'dct' && (
          <div className="form-group">
            <label className="form-label">
              Embedding Strength <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{strength}</span>
            </label>
            <input
              type="range"
              min="1"
              max="100"
              value={strength}
              onChange={(e) => setStrength(parseInt(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', height: '6px' }}
            />
            <small style={{ color: 'var(--text-tertiary)', display: 'block', marginTop: '0.5rem' }}>
              Recommended: 10-15 for good balance
            </small>
          </div>
        )}
        
        {algorithm === 'dwt' && (
          <div className="form-group">
            <label className="form-label">
              Embedding Strength <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>{strength.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min="0.01"
              max="10"
              step="0.01"
              value={strength}
              onChange={(e) => setStrength(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', height: '6px' }}
            />
            <small style={{ color: 'var(--text-tertiary)', display: 'block', marginTop: '0.5rem' }}>
              Recommended: 0.1-1 for good balance
            </small>
          </div>
        )}

        {/* Encryption */}
        <div className="form-group">
          <label className="form-label">Encryption Key (Optional)</label>
          <input
            type="password"
            className="form-control"
            placeholder="Leave empty for no encryption"
            value={encryptionKey}
            onChange={(e) => setEncryptionKey(e.target.value)}
          />
          <small style={{ color: 'var(--text-tertiary)' }}>
            {encryptionKey.length > 0 ? `✓ ${encryptionKey.length} characters` : 'Use a strong key for AES-256 encryption'}
          </small>
        </div>

        {/* Progress */}
        <ProgressBar progress={progress} status={progressStatus} isActive={analyzing || encoding} />

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          {(algorithm === 'lsb' || algorithm === 'dct' || algorithm === 'dwt') && (
            <button
              className="btn btn-secondary"
              onClick={handleAnalyze}
              disabled={analyzing || encoding || !carrierFile || !payloadText}
            >
              {analyzing ? '🤖 Analyzing...' : '🤖 Analyze with AI'}
            </button>
          )}
          <button
            className="btn btn-primary"
            onClick={handleEncode}
            disabled={encoding || analyzing || !carrierFile || (algorithm === 'lsb' ? (!payloadText && !payloadFile) : !payloadText)}
            style={{ flex: 1, minWidth: '150px' }}
          >
            {encoding ? '🔒 Encoding...' : '🔒 Encode Now'}
          </button>
        </div>
      </div>

      {/* AI Analysis Results */}
      {analysis && (
        <div className="card" style={{ marginBottom: '2rem', backgroundColor: 'rgba(102, 126, 234, 0.05)' }}>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '1.5rem', color: 'var(--accent-primary)' }}>🤖 AI Analysis Results</h2>
          
          <div className="alert alert-info">
            <strong>{analysis.recommendation.source}:</strong> {analysis.recommendation.explanation}
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Algorithm</div>
              <div className="stat-value">{analysis.recommendation.algorithm}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Bits per Channel</div>
              <div className="stat-value">{analysis.recommendation.bits_per_channel}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Confidence</div>
              <div className="stat-value">{(analysis.recommendation.confidence * 100).toFixed(0)}%</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Image Entropy</div>
              <div className="stat-value">{analysis.image_stats.entropy?.toFixed(2) || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Encode Results */}
      {encodeResult && (
        <div className="card" style={{ backgroundColor: 'rgba(67, 233, 123, 0.05)' }}>
          <div className="alert alert-success">
            ✓ Message successfully encoded!
          </div>

          <div className="stats-grid" style={{ marginBottom: '2rem', marginTop: '1rem' }}>
            {encodeResult.metrics?.psnr !== undefined && (
              <div className="stat-card">
                <div className="stat-label">PSNR</div>
                <div className="stat-value">{encodeResult.metrics.psnr} dB</div>
              </div>
            )}
            {encodeResult.metrics?.ssim !== undefined && (
              <div className="stat-card">
                <div className="stat-label">SSIM</div>
                <div className="stat-value">{encodeResult.metrics.ssim}</div>
              </div>
            )}
            {encodeResult.encode_info?.capacity_used !== undefined && (
              <div className="stat-card">
                <div className="stat-label">Capacity Used</div>
                <div className="stat-value">{encodeResult.encode_info.capacity_used.toFixed(2)}%</div>
              </div>
            )}
            {encodeResult.encode_info?.payload_size !== undefined && (
              <div className="stat-card">
                <div className="stat-label">Payload Size</div>
                <div className="stat-value">{getFileSize(encodeResult.encode_info.payload_size)}</div>
              </div>
            )}
          </div>

          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <button className="btn btn-success btn-lg" onClick={handleDownload} style={{ width: '100%', maxWidth: '300px' }}>
              📥 Download {algorithm === 'audio' ? 'Audio' : algorithm === 'video' ? 'Video' : 'Image'}
            </button>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px', borderLeft: '4px solid var(--accent-warning)' }}>
            <strong>💡 Important:</strong> Save these settings for decoding:
            <ul style={{ marginTop: '0.75rem', marginLeft: '1.5rem', fontSize: '0.95rem' }}>
              <li>Algorithm: <code style={{ background: 'var(--bg-tertiary)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>{algorithm.toUpperCase()}</code></li>
              {algorithm === 'lsb' && encodeResult.encode_info?.bits_per_channel && (
                <li>Bits per channel: <code style={{ background: 'var(--bg-tertiary)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>{encodeResult.encode_info.bits_per_channel}</code></li>
              )}
              {(algorithm === 'dct' || algorithm === 'dwt') && (
                <li>Strength: <code style={{ background: 'var(--bg-tertiary)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>{strength}</code></li>
              )}
              {encryptionKey && <li>Encryption: <code style={{ background: 'var(--bg-tertiary)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>✓ Required</code></li>}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default Encode;