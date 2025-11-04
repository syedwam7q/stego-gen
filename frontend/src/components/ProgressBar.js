import React from 'react';

function ProgressBar({ progress, status, isActive }) {
  if (!isActive) return null;

  return (
    <div className="progress-container">
      <div className="progress-bar-wrapper">
        <div 
          className="progress-bar" 
          style={{ width: `${progress}%` }}
        >
        </div>
      </div>
      <div className="progress-text">{progress}%</div>
      {status && <div className="progress-status">{status}</div>}
    </div>
  );
}

export default ProgressBar;