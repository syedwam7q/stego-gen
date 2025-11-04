// History Management Utility
import { STORAGE_KEYS } from '../config';

export const saveToHistory = (operation) => {
  try {
    const history = getHistory();
    const entry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...operation
    };
    
    const updatedHistory = [entry, ...history].slice(0, 50); // Keep last 50
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(updatedHistory));
    return entry;
  } catch (error) {
    console.error('Failed to save history:', error);
    return null;
  }
};

export const getHistory = () => {
  try {
    const history = localStorage.getItem(STORAGE_KEYS.HISTORY);
    return history ? JSON.parse(history) : [];
  } catch (error) {
    console.error('Failed to load history:', error);
    return [];
  }
};

export const clearHistory = () => {
  try {
    localStorage.removeItem(STORAGE_KEYS.HISTORY);
    return true;
  } catch (error) {
    console.error('Failed to clear history:', error);
    return false;
  }
};

export const deleteHistoryEntry = (id) => {
  try {
    const history = getHistory();
    const updated = history.filter(entry => entry.id !== id);
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(updated));
    return true;
  } catch (error) {
    console.error('Failed to delete history entry:', error);
    return false;
  }
};

export const getHistoryStats = () => {
  const history = getHistory();
  const stats = {
    total: history.length,
    byAlgorithm: {},
    byOperation: { encode: 0, decode: 0, analyze: 0 },
    avgQuality: { psnr: 0, ssim: 0 },
    totalDataHidden: 0
  };

  history.forEach(entry => {
    // Count by algorithm
    if (entry.algorithm) {
      stats.byAlgorithm[entry.algorithm] = (stats.byAlgorithm[entry.algorithm] || 0) + 1;
    }

    // Count by operation type
    if (entry.type) {
      stats.byOperation[entry.type] = (stats.byOperation[entry.type] || 0) + 1;
    }

    // Sum metrics
    if (entry.metrics) {
      stats.avgQuality.psnr += entry.metrics.psnr || 0;
      stats.avgQuality.ssim += entry.metrics.ssim || 0;
    }

    // Sum data size
    if (entry.payloadSize) {
      stats.totalDataHidden += entry.payloadSize;
    }
  });

  // Calculate averages
  if (history.length > 0) {
    stats.avgQuality.psnr = (stats.avgQuality.psnr / history.length).toFixed(2);
    stats.avgQuality.ssim = (stats.avgQuality.ssim / history.length).toFixed(3);
  }

  return stats;
};