import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getHistory, getHistoryStats } from '../utils/history';
import { getAllPresets } from '../utils/presets';
import './Dashboard.css';

function Dashboard() {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [presets, setPresets] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setHistory(getHistory().slice(0, 5)); // Last 5 operations
    setStats(getHistoryStats());
    setPresets(getAllPresets());
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1 className="gradient-text">📊 Dashboard</h1>
        <p className="dashboard-subtitle">Your steganography operations at a glance</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-value">{stats?.total || 0}</div>
            <div className="stat-label">Total Operations</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <div className="stat-value">{formatBytes(stats?.totalDataHidden || 0)}</div>
            <div className="stat-label">Data Hidden</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{stats?.avgQuality.psnr || 0} dB</div>
            <div className="stat-label">Avg PSNR</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <div className="stat-value">{stats?.avgQuality.ssim || 0}</div>
            <div className="stat-label">Avg SSIM</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="section-title">⚡ Quick Actions</h2>
        <div className="quick-actions-grid">
          <Link to="/encode" className="quick-action-card">
            <div className="quick-action-icon">🔒</div>
            <h3>Encode</h3>
            <p>Hide secret data in carrier files</p>
          </Link>

          <Link to="/decode" className="quick-action-card">
            <div className="quick-action-icon">🔓</div>
            <h3>Decode</h3>
            <p>Extract hidden data from stego files</p>
          </Link>

          <Link to="/steganalysis" className="quick-action-card">
            <div className="quick-action-icon">🔍</div>
            <h3>Steganalysis</h3>
            <p>Detect hidden data in images</p>
          </Link>

          <Link to="/compare" className="quick-action-card">
            <div className="quick-action-icon">⚖️</div>
            <h3>Compare</h3>
            <p>Compare algorithms side-by-side</p>
          </Link>

          <Link to="/capacity" className="quick-action-card">
            <div className="quick-action-icon">📐</div>
            <h3>Calculator</h3>
            <p>Calculate hiding capacity</p>
          </Link>

          <Link to="/batch" className="quick-action-card">
            <div className="quick-action-icon">📁</div>
            <h3>Batch Process</h3>
            <p>Process multiple files at once</p>
          </Link>
        </div>
      </div>

      {/* Recent Activity & Presets */}
      <div className="dashboard-grid">
        {/* Recent History */}
        <div className="card">
          <div className="card-header-row">
            <h2 className="section-title">🕐 Recent Activity</h2>
            <Link to="/history" className="btn btn-secondary btn-sm">View All</Link>
          </div>
          
          {history.length === 0 ? (
            <div className="empty-state">
              <p>No operations yet. Start by encoding or decoding a file!</p>
            </div>
          ) : (
            <div className="history-list">
              {history.map(entry => (
                <div key={entry.id} className="history-item">
                  <div className="history-icon">
                    {entry.type === 'encode' && '🔒'}
                    {entry.type === 'decode' && '🔓'}
                    {entry.type === 'analyze' && '🔍'}
                  </div>
                  <div className="history-content">
                    <div className="history-title">
                      {entry.algorithm?.toUpperCase() || 'N/A'} {entry.type}
                    </div>
                    <div className="history-meta">
                      {formatDate(entry.timestamp)}
                      {entry.payloadSize && ` • ${formatBytes(entry.payloadSize)}`}
                    </div>
                  </div>
                  {entry.metrics && (
                    <div className="history-metrics">
                      <span className="metric-badge">PSNR: {entry.metrics.psnr?.toFixed(1)}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Favorite Presets */}
        <div className="card">
          <div className="card-header-row">
            <h2 className="section-title">⭐ Presets</h2>
            <Link to="/presets" className="btn btn-secondary btn-sm">Manage</Link>
          </div>
          
          <div className="presets-list">
            {presets.slice(0, 5).map(preset => (
              <div key={preset.id} className="preset-item">
                <div className="preset-icon">{preset.icon || '⚙️'}</div>
                <div className="preset-content">
                  <div className="preset-name">{preset.name}</div>
                  <div className="preset-description">{preset.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Algorithm Usage */}
      {stats && stats.total > 0 && (
        <div className="card">
          <h2 className="section-title">📈 Algorithm Usage</h2>
          <div className="algorithm-stats">
            {Object.entries(stats.byAlgorithm).map(([algo, count]) => {
              const percentage = ((count / stats.total) * 100).toFixed(1);
              return (
                <div key={algo} className="algorithm-stat-item">
                  <div className="algorithm-stat-header">
                    <span className="algorithm-stat-name">{algo.toUpperCase()}</span>
                    <span className="algorithm-stat-value">{count} ({percentage}%)</span>
                  </div>
                  <div className="algorithm-stat-bar">
                    <div 
                      className="algorithm-stat-fill"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* AI Recommendations */}
      <div className="card ai-recommendations">
        <h2 className="section-title">🤖 AI Recommendations</h2>
        <div className="ai-tips-grid">
          <div className="ai-tip-card">
            <div className="ai-tip-icon">💡</div>
            <h3>Improve Security</h3>
            <p>Always use encryption with strong keys to protect your hidden data even if discovered.</p>
          </div>
          <div className="ai-tip-card">
            <div className="ai-tip-icon">🎨</div>
            <h3>Choose High-Texture Images</h3>
            <p>Images with complex patterns and textures hide data better than smooth gradients.</p>
          </div>
          <div className="ai-tip-card">
            <div className="ai-tip-icon">📊</div>
            <h3>Monitor PSNR & SSIM</h3>
            <p>Keep PSNR above 40dB and SSIM above 0.95 for minimal detection risk.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;