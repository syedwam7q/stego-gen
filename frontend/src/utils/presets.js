// Presets Management Utility
import { STORAGE_KEYS } from '../config';

export const DEFAULT_PRESETS = [
  {
    id: 'max_security',
    name: 'Maximum Security',
    description: 'Lowest detection risk, minimal capacity',
    algorithm: 'lsb',
    bitsPerChannel: 1,
    encryption: true,
    icon: '🔒'
  },
  {
    id: 'balanced',
    name: 'Balanced',
    description: 'Good balance between capacity and security',
    algorithm: 'lsb',
    bitsPerChannel: 2,
    encryption: true,
    icon: '⚖️'
  },
  {
    id: 'max_capacity',
    name: 'Maximum Capacity',
    description: 'Highest data capacity, higher detection risk',
    algorithm: 'lsb',
    bitsPerChannel: 4,
    encryption: false,
    icon: '📦'
  },
  {
    id: 'robust',
    name: 'Robust (DCT)',
    description: 'Resistant to compression and transformations',
    algorithm: 'dct',
    strength: 15,
    encryption: true,
    icon: '🛡️'
  },
  {
    id: 'high_quality',
    name: 'High Quality (DWT)',
    description: 'Best imperceptibility and quality',
    algorithm: 'dwt',
    strength: 10,
    encryption: true,
    icon: '⭐'
  }
];

export const savePreset = (preset) => {
  try {
    const presets = getUserPresets();
    const newPreset = {
      id: `custom_${Date.now()}`,
      timestamp: new Date().toISOString(),
      custom: true,
      ...preset
    };
    
    const updatedPresets = [...presets, newPreset];
    localStorage.setItem(STORAGE_KEYS.PRESETS, JSON.stringify(updatedPresets));
    return newPreset;
  } catch (error) {
    console.error('Failed to save preset:', error);
    return null;
  }
};

export const getUserPresets = () => {
  try {
    const presets = localStorage.getItem(STORAGE_KEYS.PRESETS);
    return presets ? JSON.parse(presets) : [];
  } catch (error) {
    console.error('Failed to load presets:', error);
    return [];
  }
};

export const getAllPresets = () => {
  return [...DEFAULT_PRESETS, ...getUserPresets()];
};

export const deletePreset = (id) => {
  try {
    const presets = getUserPresets();
    const updated = presets.filter(preset => preset.id !== id);
    localStorage.setItem(STORAGE_KEYS.PRESETS, JSON.stringify(updated));
    return true;
  } catch (error) {
    console.error('Failed to delete preset:', error);
    return false;
  }
};

export const applyPreset = (presetId) => {
  const allPresets = getAllPresets();
  return allPresets.find(p => p.id === presetId) || null;
};