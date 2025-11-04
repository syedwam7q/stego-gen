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

function Decode() {
  const [algorithm, setAlgorithm] = useState('lsb');
  const [stegoFile, setStegoFile] = useState(null);
  const [stegoPreview, setStegoPreview] = useState(null);
  const [decryptionKey, setDecryptionKey] = useState('');
  const [bitsPerChannel, setBitsPerChannel] = useState(1);
  const [strength, setStrength] = useState(10);
  
  const [decoding, setDecoding] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressStatus, setProgressStatus] = useState('');
  const [decodeResult, setDecodeResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const stegoInputRef = useRef(null);

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
        return { types: ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff'], label: 'PNG images (JPG may corrupt data)' };
    }
  };

  const handleFileChange = (file) => {
    if (!file) return;
    
    const accepted = getAcceptedFileTypes();
    if (!accepted.types.includes(file.type)) {
      setError(`Invalid file type. Please use ${accepted.label}`);
      return;
    }
    
    if ((algorithm === 'lsb' || algorithm === 'dct' || algorithm === 'dwt') && (file.type === 'image/jpeg' || file.type === 'image/jpg')) {
      setError('⚠️ JPEG format may have corrupted the hidden data. PNG format is recommended.');
    }
    
    const maxSize = algorithm === 'video' ? 500 * 1024 * 1024 : 100 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`File too large: ${getFileSize(file.size)}. Maximum: ${maxSize / (1024 * 1024)}MB`);
      return;
    }
    
    if (file.size === 0) {
      setError('File is empty');
      return;
    }
    
    setStegoFile(file);
    if (algorithm === 'audio') {
      setStegoPreview(null);
    } else if (algorithm === 'video') {
      setStegoPreview(null);
    } else {
      setStegoPreview(URL.createObjectURL(file));
    }
    setDecodeResult(null);
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

  const handleDecode = async () => {
    if (!stegoFile) {
      setError('Please select a stego file');
      return;
    }
    
    if (algorithm === 'lsb' && (!Number.isInteger(bitsPerChannel) || bitsPerChannel < 1 || bitsPerChannel > 4)) {
      setError('Bits per channel must be between 1 and 4');
      return;
    }
    
    if (decryptionKey && decryptionKey.length < 8) {
      setError('Decryption key too short. Must be at least 8 characters');
      return;
    }

    setDecoding(true);
    setError(null);
    setProgress(0);
    setProgressStatus('Preparing to decode...');

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 200);

    const formData = new FormData();
    const endpoints = {
      lsb: '/api/decode',
      dct: '/api/decode/dct',
      dwt: '/api/decode/dwt',
      audio: '/api/decode/audio',
      video: '/api/decode/video'
    };

    if (algorithm === 'audio') {
      formData.append('stego_audio', stegoFile);
    } else if (algorithm === 'video') {
      formData.append('stego_video', stegoFile);
    } else {
      formData.append('stego_image', stegoFile);
    }

    if (algorithm === 'lsb') {
      formData.append('bits_per_channel', bitsPerChannel);
    } else if (algorithm === 'dct' || algorithm === 'dwt') {
      formData.append('strength', strength);
    } else if (algorithm === 'video') {
      formData.append('bits_per_channel', bitsPerChannel);
      formData.append('frame_skip', 1);
    }
    
    if (decryptionKey) {
      formData.append('decryption_key', decryptionKey);
    }

    try {
      setProgressStatus('Extracting hidden data...');
      const response = await axios.post(`${API_BASE}${endpoints[algorithm]}`, formData);
      clearInterval(progressInterval);
      setProgress(100);
      setProgressStatus('Decoding complete!');
      setTimeout(() => {
        setDecodeResult(response.data);
        setProgress(0);
      }, 500);
    } catch (err) {
      clearInterval(progressInterval);
      setProgress(0);
      const errorMsg = formatError(err.response?.data?.detail || err.message || 'Decoding failed. Check your settings and key.');
      setError(errorMsg);
      console.error('Decoding error:', err);
    } finally {
      setTimeout(() => {
        setDecoding(false);
        setProgressStatus('');
      }, 500);
    }
  };

  const handleCopyToClipboard = () => {
    if (decodeResult?.payload) {
      navigator.clipboard.writeText(decodeResult.payload).then(() => {
        alert('✓ Message copied to clipboard!');
      }).catch(() => {
        alert('Failed to copy');
      });
    }
  };

  return (
    <div className="decode-page">
      {error && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="card" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Decode Message</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Extract hidden messages from stego files using the correct algorithm and parameters
        </p>

        {/* Algorithm Selection */}
        <div className="form-group">
          <label className="form-label">Algorithm</label>
          <select 
            className="form-control" 
            value={algorithm} 
            onChange={(e) => {
              setAlgorithm(e.target.value);
              setStegoFile(null);
              setStegoPreview(null);
              setDecodeResult(null);
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
            ✓ Select the same algorithm that was used for encoding
          </small>
        </div>

        {/* Stego File Upload */}
        <div className="form-group">
          <label className="form-label">
            {algorithm === 'audio' ? 'Stego Audio File' : algorithm === 'video' ? 'Stego Video File' : 'Stego Image'}
          </label>
          <div
            className={`file-input ${stegoFile ? 'has-file' : ''} ${dragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => stegoInputRef.current?.click()}
          >
            <input
              ref={stegoInputRef}
              type="file"
              accept={algorithm === 'audio' ? 'audio/wav' : algorithm === 'video' ? 'video/*' : 'image/*'}
              onChange={(e) => handleFileChange(e.target.files[0])}
              style={{ display: 'none' }}
            />
            <div className="file-icon">
              {stegoFile ? '✅' : algorithm === 'audio' ? '🔊' : algorithm === 'video' ? '🎥' : '🖼️'}
            </div>
            <p>{stegoFile ? stegoFile.name : `Click or drag stego ${algorithm === 'audio' ? 'audio' : algorithm === 'video' ? 'video' : 'image'} file here`}</p>
            {stegoFile && <div className="file-size">{getFileSize(stegoFile.size)}</div>}
          </div>
          {stegoPreview && (
            <img src={stegoPreview} alt="Stego preview" className="preview-image" style={{ marginTop: '1rem' }} />
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
              Must match the value used during encoding (default: 1)
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
              Must match the value used during encoding
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
              Must match the value used during encoding
            </small>
          </div>
        )}

        {/* Decryption Key */}
        <div className="form-group">
          <label className="form-label">Decryption Key (if encrypted)</label>
          <input
            type="password"
            className="form-control"
            placeholder="Leave empty if message was not encrypted"
            value={decryptionKey}
            onChange={(e) => setDecryptionKey(e.target.value)}
          />
          <small style={{ color: 'var(--text-tertiary)' }}>
            {decryptionKey.length > 0 ? `✓ ${decryptionKey.length} characters` : 'Leave empty if message was not encrypted'}
          </small>
        </div>

        {/* Progress */}
        <ProgressBar progress={progress} status={progressStatus} isActive={decoding} />

        {/* Decode Button */}
        <div style={{ marginBottom: '1.5rem' }}>
          <button
            className="btn btn-primary btn-lg"
            onClick={handleDecode}
            disabled={decoding || !stegoFile}
            style={{ width: '100%' }}
          >
            {decoding ? '🔓 Decoding...' : '🔓 Decode Message'}
          </button>
        </div>
      </div>

      {/* Decode Results */}
      {decodeResult && (
        <div className="card" style={{ marginBottom: '2rem', backgroundColor: 'rgba(67, 233, 123, 0.05)' }}>
          <div className="alert alert-success">
            ✓ {decodeResult.is_binary ? 'Binary file successfully decoded!' : 'Message successfully decoded!'}
          </div>

          <div className="stats-grid" style={{ marginBottom: '2rem', marginTop: '1rem' }}>
            <div className="stat-card">
              <div className="stat-label">Payload Size</div>
              <div className="stat-value">{getFileSize(decodeResult.payload_size)}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Encryption</div>
              <div className="stat-value">{decodeResult.was_encrypted ? '🔒 Yes' : '🔓 No'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Type</div>
              <div className="stat-value">{decodeResult.is_binary ? '📄 Binary' : '📝 Text'}</div>
            </div>
            {!decodeResult.is_binary && (
              <div className="stat-card">
                <div className="stat-label">Characters</div>
                <div className="stat-value">{decodeResult.payload.length}</div>
              </div>
            )}
          </div>

          {decodeResult.is_binary ? (
            <div className="form-group" style={{ marginTop: '1.5rem' }}>
              <label className="form-label">Binary Payload (Hex)</label>
              <textarea
                className="form-control"
                rows="6"
                value={decodeResult.payload_base64 || 'Binary data'}
                readOnly
                style={{ fontFamily: 'monospace', backgroundColor: 'var(--bg-secondary)', fontSize: '0.85rem' }}
              />
              <small style={{ color: 'var(--text-tertiary)', marginTop: '0.5rem', display: 'block' }}>
                Binary files should be saved and opened with appropriate software
              </small>
            </div>
          ) : (
            <div className="form-group" style={{ marginTop: '1.5rem' }}>
              <label className="form-label">Decoded Message</label>
              <textarea
                className="form-control"
                rows="8"
                value={decodeResult.payload}
                readOnly
                style={{ fontFamily: 'monospace', backgroundColor: 'var(--bg-secondary)' }}
              />
              <button 
                className="btn btn-secondary btn-sm" 
                onClick={handleCopyToClipboard}
                style={{ marginTop: '1rem' }}
              >
                📋 Copy to Clipboard
              </button>
            </div>
          )}
        </div>
      )}

      {/* Help Card */}
      <div className="card">
        <h2 style={{ fontSize: '1.3rem', marginBottom: '1.5rem', color: 'var(--text-primary)' }}>💡 Decoding Tips</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
          <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'var(--bg-secondary)' }}>
            <strong style={{ color: 'var(--accent-primary)' }}>✓ Algorithm</strong>
            <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Use the exact same algorithm from encoding</p>
          </div>
          
          {algorithm === 'lsb' && (
            <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'var(--bg-secondary)' }}>
              <strong style={{ color: 'var(--accent-primary)' }}>✓ Bits per Channel</strong>
              <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Must match the encoding value</p>
            </div>
          )}
          
          {(algorithm === 'dct' || algorithm === 'dwt') && (
            <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'var(--bg-secondary)' }}>
              <strong style={{ color: 'var(--accent-primary)' }}>✓ Strength</strong>
              <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Must match the encoding value</p>
            </div>
          )}
          
          <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'var(--bg-secondary)' }}>
            <strong style={{ color: 'var(--accent-primary)' }}>🔐 Encryption Key</strong>
            <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Exact key if message was encrypted</p>
          </div>
          
          {(algorithm === 'lsb' || algorithm === 'dct' || algorithm === 'dwt') && (
            <>
              <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'var(--bg-secondary)' }}>
                <strong style={{ color: 'var(--accent-primary)' }}>📁 PNG Format</strong>
                <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Use PNG, not JPEG or compressed formats</p>
              </div>
              
              <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'var(--bg-secondary)' }}>
                <strong style={{ color: 'var(--accent-primary)' }}>⚠️ Unmodified Files</strong>
                <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Compression or editing corrupts data</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Decode;