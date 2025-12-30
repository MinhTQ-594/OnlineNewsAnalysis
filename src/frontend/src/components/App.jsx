import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, ExternalLink, Newspaper, Sparkles, Link, TrendingUp } from 'lucide-react';

const API_URL = 'http://localhost:8000';

// Animated background particles
function BackgroundParticles() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
      <div className="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
      <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000" />
    </div>
  );
}

// Message component
function Message({ message, index }) {
  const isUser = message.type === 'user';

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fadeInUp`}
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {/* Bot avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-2 flex-shrink-0 shadow-lg">
          <Sparkles size={14} className="text-white" />
        </div>
      )}

      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-md transition-all duration-300 hover:shadow-lg ${
          isUser
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-sm'
            : 'bg-white text-gray-800 rounded-bl-sm border border-gray-100'
        }`}
      >
        {message.type === 'bot' && message.results ? (
          <div className="min-w-[320px]">
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-100">
              <TrendingUp size={16} className="text-green-500" />
              <p className="text-sm font-medium text-gray-700">
                Tìm thấy {message.results.length} bài báo liên quan
              </p>
            </div>
            <div className="space-y-3">
              {message.results.map((article, idx) => (
                <div
                  key={idx}
                  className="group bg-gradient-to-r from-gray-50 to-white rounded-xl p-3 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-300 cursor-pointer"
                >
                  <div className="flex items-center mb-2">
                      <span className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-sm">
                        #{idx + 1}
                      </span>
                  </div>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm break-all hover:underline flex items-start gap-1.5 group-hover:text-blue-700 transition-colors"
                  >
                    <ExternalLink size={14} className="mt-0.5 flex-shrink-0 opacity-50 group-hover:opacity-100 transition-opacity" />
                    <span className="line-clamp-2">{article.url}</span>
                  </a>
                  <p className="text-gray-500 text-xs mt-2 line-clamp-2 leading-relaxed">
                    {article.text.substring(0, 120)}...
                  </p>
                </div>
              ))}
            </div>
          </div>
        ) : message.type === 'bot' && message.error ? (
          <div className="flex items-center gap-2 text-red-500">
            <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center">
              <span className="text-xs">!</span>
            </div>
            <span>{message.error}</span>
          </div>
        ) : (
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center ml-2 flex-shrink-0 shadow-lg">
          <span className="text-white text-xs font-bold">U</span>
        </div>
      )}
    </div>
  );
}

// Typing indicator
function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4 animate-fadeInUp">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-2 shadow-lg">
        <Sparkles size={14} className="text-white" />
      </div>
      <div className="bg-white rounded-2xl rounded-bl-sm px-5 py-4 shadow-md border border-gray-100">
        <div className="flex space-x-1.5">
          <div className="w-2.5 h-2.5 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-bounce [animation-delay:0ms]" />
          <div className="w-2.5 h-2.5 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-bounce [animation-delay:150ms]" />
          <div className="w-2.5 h-2.5 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  );
}

// Welcome card
function WelcomeCard() {
  return (
    <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 rounded-2xl p-6 mb-6 border border-white/50 shadow-lg animate-fadeInUp">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
          <Newspaper size={24} className="text-white" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-gray-800">Chào mừng bạn! 👋</h2>
          <p className="text-sm text-gray-500">Trợ lý tìm kiếm bài báo thông minh</p>
        </div>
      </div>
      <p className="text-gray-600 text-sm leading-relaxed">
        Gửi cho tôi URL bài báo từ <span className="font-semibold text-orange-500">VnExpress</span> hoặc{' '}
        <span className="font-semibold text-blue-500">Dân Trí</span>, tôi sẽ tìm các bài báo tương tự cho bạn.
      </p>
    </div>
  );
}

// Main App
function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Validate URL
  const isValidUrl = (text) => {
    return text.includes('vnexpress.net') || text.includes('dantri.com.vn');
  };

  // Send message
  const handleSend = async () => {
    const url = input.trim();
    if (!url || isLoading) return;

    setMessages((prev) => [...prev, { type: 'user', content: url }]);
    setInput('');
    setIsLoading(true);

    if (!isValidUrl(url)) {
      setMessages((prev) => [
        ...prev,
        { type: 'bot', error: 'Vui lòng nhập URL từ VnExpress hoặc Dân Trí.' },
      ]);
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, top_k: 5 }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Có lỗi xảy ra');
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { type: 'bot', results: data.results, inputText: data.input_text },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { type: 'bot', error: error.message || 'Không thể kết nối đến server' },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  // Enter key
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 relative">
      <BackgroundParticles />

      {/* Header */}
      <header className="relative bg-white/80 backdrop-blur-lg border-b border-white/20 px-6 py-4 shadow-sm z-10">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-11 h-11 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-purple-500/25 animate-pulse">
              <Newspaper size={22} />
            </div>
            <div className="ml-3">
              <h1 className="text-xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
                News Article Finder
              </h1>
              <p className="text-sm text-gray-500 flex items-center gap-1">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                Sẵn sàng tìm kiếm
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-xs text-gray-500">
            <span className="px-2 py-1 bg-orange-100 text-orange-600 rounded-md font-medium">VnExpress</span>
            <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded-md font-medium">Dân Trí</span>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 relative z-10">
        <div className="max-w-3xl mx-auto">
          {messages.length === 0 && <WelcomeCard />}
          {messages.map((msg, index) => (
            <Message key={index} message={msg} index={index} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="relative bg-white/80 backdrop-blur-lg border-t border-white/20 px-4 py-4 z-10">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-3 bg-white rounded-2xl shadow-lg border border-gray-100 p-2 focus-within:ring-2 focus-within:ring-blue-500/50 focus-within:border-blue-300 transition-all duration-300">
            <div className="pl-2">
              <Link size={20} className="text-gray-400" />
            </div>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Dán URL bài báo vào đây..."
              className="flex-1 py-2 bg-transparent focus:outline-none text-gray-700 placeholder-gray-400"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-all duration-300 shadow-md hover:shadow-lg hover:scale-105 disabled:hover:scale-100 disabled:shadow-none"
            >
              {isLoading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
          <p className="text-center text-xs text-gray-400 mt-2">
            Nhấn Enter để gửi • Hỗ trợ VnExpress & Dân Trí
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;