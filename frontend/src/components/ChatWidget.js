import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';

/**
 * ChatWidget — Floating RAG chatbot panel.
 * Renders a toggleable chat icon in the bottom-right corner.
 * Sends messages to POST /api/chat with current city/week context.
 */
export default function ChatWidget({ currentCity, currentWeek }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hi! I'm **SatIntel AI**. Ask me about environmental data, city analytics, pollution, temperature, vegetation, or anything about the platform. 🛰️",
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom on new message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    // Add user message
    const userMsg = { role: 'user', text: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await sendChatMessage(trimmed, currentCity, currentWeek);
      const data = res.data;
      const botMsg = {
        role: 'assistant',
        text: data.reply || "I couldn't generate a response. Please try again.",
        sources: data.sources || [],
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: '⚠️ Sorry, I encountered an error. Please make sure the backend is running and try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Simple markdown-ish bold rendering
  const renderText = (text) => {
    if (!text) return '';
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i}>{part.slice(2, -2)}</strong>
        );
      }
      // Handle bullet points
      if (part.includes('\n')) {
        return part.split('\n').map((line, j) => (
          <React.Fragment key={`${i}-${j}`}>
            {j > 0 && <br />}
            {line.startsWith('- ') || line.startsWith('• ') ? (
              <span style={{ display: 'block', paddingLeft: 12 }}>
                {'→ ' + line.slice(2)}
              </span>
            ) : (
              line
            )}
          </React.Fragment>
        ));
      }
      return part;
    });
  };

  // Quick suggestion chips
  const suggestions = [
    "What's the current temperature?",
    "How is air quality today?",
    "Show vegetation health",
    "Explain soil moisture",
  ];

  const handleSuggestion = (text) => {
    setInput(text);
    // Auto-send
    const userMsg = { role: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    sendChatMessage(text, currentCity, currentWeek)
      .then((res) => {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            text: res.data.reply,
            sources: res.data.sources || [],
          },
        ]);
      })
      .catch(() => {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', text: '⚠️ Error getting response.' },
        ]);
      })
      .finally(() => {
        setIsLoading(false);
        setInput('');
      });
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button
        className={`chat-fab ${isOpen ? 'chat-fab-active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Ask SatIntel AI"
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="chat-panel">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-left">
              <span className="chat-header-icon">🛰️</span>
              <div>
                <div className="chat-header-title">SatIntel AI</div>
                <div className="chat-header-subtitle">
                  Powered by Gemini • {currentCity}
                </div>
              </div>
            </div>
            <div className="chat-header-badge">RAG</div>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`chat-message ${
                  msg.role === 'user' ? 'chat-message-user' : 'chat-message-bot'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="chat-avatar">🤖</div>
                )}
                <div
                  className={`chat-bubble ${
                    msg.role === 'user'
                      ? 'chat-bubble-user'
                      : 'chat-bubble-bot'
                  }`}
                >
                  <div className="chat-bubble-text">
                    {renderText(msg.text)}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="chat-sources">
                      <span className="chat-sources-label">Sources:</span>
                      {msg.sources.map((s, i) => (
                        <span key={i} className="chat-source-chip">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="chat-avatar chat-avatar-user">👤</div>
                )}
              </div>
            ))}

            {/* Typing indicator */}
            {isLoading && (
              <div className="chat-message chat-message-bot">
                <div className="chat-avatar">🤖</div>
                <div className="chat-bubble chat-bubble-bot">
                  <div className="chat-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            {/* Suggestions (only show if few messages) */}
            {messages.length <= 2 && !isLoading && (
              <div className="chat-suggestions">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    className="chat-suggestion-chip"
                    onClick={() => handleSuggestion(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input-container">
            <input
              ref={inputRef}
              className="chat-input"
              type="text"
              placeholder="Ask about environmental data..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
            <button
              className="chat-send-btn"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}
