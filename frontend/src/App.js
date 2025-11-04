import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import Home from './components/Home';
import Encode from './components/Encode';
import Decode from './components/Decode';
import Steganalysis from './components/Steganalysis';
import Dashboard from './components/Dashboard';
import CapacityCalculator from './components/CapacityCalculator';
import AlgorithmComparison from './components/AlgorithmComparison';
import AIChat from './components/AIChat';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const theme = isDarkMode ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo" onClick={closeMobileMenu}>
              <img src="/logo/logo.png" alt="StegoGen Logo" />
              <span>StegoGen</span>
            </Link>
            
            {/* Mobile Menu Toggle */}
            <button 
              className="mobile-menu-toggle"
              onClick={toggleMobileMenu}
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? '✕' : '☰'}
            </button>

            <ul className={`nav-menu ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
              <li className="nav-item">
                <Link to="/" className="nav-link" onClick={closeMobileMenu}>🏠 Home</Link>
              </li>
              <li className="nav-item">
                <Link to="/dashboard" className="nav-link" onClick={closeMobileMenu}>📊 Dashboard</Link>
              </li>
              <li className="nav-item">
                <Link to="/encode" className="nav-link" onClick={closeMobileMenu}>🔒 Encode</Link>
              </li>
              <li className="nav-item">
                <Link to="/decode" className="nav-link" onClick={closeMobileMenu}>🔓 Decode</Link>
              </li>
              <li className="nav-item">
                <Link to="/steganalysis" className="nav-link" onClick={closeMobileMenu}>🔍 Steganalysis</Link>
              </li>
              <li className="nav-item nav-item-dropdown">
                <span className="nav-link dropdown-trigger">🛠️ Tools</span>
                <ul className="nav-dropdown">
                  <li><Link to="/compare" className="nav-link" onClick={closeMobileMenu}>⚖️ Compare Algorithms</Link></li>
                  <li><Link to="/capacity" className="nav-link" onClick={closeMobileMenu}>📐 Capacity Calculator</Link></li>
                </ul>
              </li>
              <li className="nav-item">
                <button 
                  className="nav-link theme-toggle"
                  onClick={toggleTheme}
                  aria-label="Toggle dark mode"
                >
                  {isDarkMode ? '☀️' : '🌙'}
                </button>
              </li>
            </ul>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/encode" element={<Encode />} />
            <Route path="/decode" element={<Decode />} />
            <Route path="/steganalysis" element={<Steganalysis />} />
            <Route path="/compare" element={<AlgorithmComparison />} />
            <Route path="/capacity" element={<CapacityCalculator />} />
          </Routes>
        </main>

        {/* Floating AI Chat Button */}
        <button 
          className="ai-chat-fab"
          onClick={() => setIsChatOpen(true)}
          aria-label="Open AI Assistant"
          title="Ask AI Assistant"
        >
          🤖
        </button>

        {/* AI Chat Component */}
        <AIChat 
          isOpen={isChatOpen} 
          onClose={() => setIsChatOpen(false)}
        />

        <footer className="footer">
          <p>
          &copy; 2025 StegoGen v2.0 - AI-Powered Steganography Platform |{' '}
          <a href="https://syedwamiq.framer.website" target="_blank" rel="noopener noreferrer">
            Syed Wamiq
          </a>
          </p>
          <p>Secure • Private • Invisible</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
