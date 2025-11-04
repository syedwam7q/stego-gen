import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './AIChat.css';

const API_BASE = 'http://localhost:8000';

function AIChat({ context = null, isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "👋 Hi! I'm your AI steganography assistant. Ask me anything about:\n\n• Algorithm differences (LSB, DCT, DWT)\n• Security and detection risks\n• Quality metrics (PSNR, SSIM)\n• Best practices for hiding data\n\nWhat would you like to know?"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickQuestions = [
    "What's the difference between LSB and DCT?",
    "How can I improve security?",
    "What is PSNR and why does it matter?",
    "Which algorithm should I use?",
    "How to avoid detection on social media?"
  ];

  const handleSend = async (question = null) => {
    const messageText = question || input.trim();
    if (!messageText) return;

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: messageText }]);
    setInput('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('question', messageText);
      
      if (context) {
        formData.append('context', JSON.stringify(context));
      }

      const response = await axios.post(`${API_BASE}/api/ai/chat`, formData);
      
      // Add AI response
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response 
      }]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Sorry, I'm having trouble responding right now. Please try again." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="ai-chat-overlay" onClick={onClose}>
      <div className="ai-chat-container" onClick={(e) => e.stopPropagation()}>
        <div className="ai-chat-header">
          <div>
            <h3>🤖 AI Assistant</h3>
            <p>Steganography Expert</p>
          </div>
          <button className="ai-chat-close" onClick={onClose}>✕</button>
        </div>

        <div className="ai-chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`ai-chat-message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="ai-chat-message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {messages.length <= 1 && (
          <div className="quick-questions">
            <p>Quick questions:</p>
            {quickQuestions.map((q, idx) => (
              <button 
                key={idx} 
                className="quick-question-btn"
                onClick={() => handleSend(q)}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        <div className="ai-chat-input">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about steganography..."
            rows="2"
            disabled={loading}
          />
          <button 
            className="send-btn"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>

        <div className="ai-chat-footer">
          <small>💡 Tip: Ask specific questions for better answers</small>
        </div>
      </div>
    </div>
  );
}

export default AIChat;