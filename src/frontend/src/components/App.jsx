import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, ExternalLink, Newspaper, Sparkles, Link, TrendingUp, ChevronDown, MessageCircle, BarChart3, Filter, X } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend, ResponsiveContainer } from 'recharts';

const API_URL = 'http://localhost:8000';

const MODELS = [
  { key: 'qwen3', name: 'Qwen3' },
  { key: 'embeddinggemma', name: 'EmbeddingGemma' },
  { key: 'dangvantuan', name: 'dangvantuan' },  
  { key: 'tfidf', name: 'TF-IDF' }, 
  { key: 'ensemble', name: 'Ensemble' },
];

const SENTIMENTS = [
  { key: null, name: 'Tất cả', color: '#6b7280', icon: '📰' },
  { key: 'negative', name: 'Tiêu cực', color: '#ef4444', icon: '😟' },
  { key: 'neutral', name: 'Trung lập', color: '#6b7280', icon: '😐' },
  { key: 'positive', name: 'Tích cực', color: '#22c55e', icon: '😊' },
];

// Performance data for radar chart
const PERFORMANCE_DATA = [
  {
    metric: 'Precision@10',
    'TF-IDF': 0.0729,
    'dangvantuan': 0.1222,
    'Qwen3': 0.0987,
    'EmbeddingGemma': 0.0934,
  },
  {
    metric: 'Recall@10',
    'TF-IDF': 0.3426,
    'dangvantuan': 0.5724,
    'Qwen3': 0.4512,
    'EmbeddingGemma': 0.4326,
  },
  {
    metric: 'Accuracy@10',
    'TF-IDF': 0.4884,
    'dangvantuan': 0.7324,
    'Qwen3': 0.6020,
    'EmbeddingGemma': 0.5868,
  },
  {
    metric: 'MRR@10',
    'TF-IDF': 0.2678,
    'dangvantuan': 0.2412,
    'Qwen3': 0.1971,
    'EmbeddingGemma': 0.1918,
  },
];

const MODEL_COLORS = {
  'TF-IDF': '#ef4444',
  'dangvantuan': '#3b82f6',
  'Qwen3': '#10b981',
  'EmbeddingGemma': '#f59e0b',
};

function BackgroundParticles() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
      <div className="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
      <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000" />
    </div>
  );
}

// Sentiment Badge Component
function SentimentBadge({ sentiment, confidence, size = 'sm' }) {
  const sentimentConfig = SENTIMENTS.find(s => s.key === sentiment) || SENTIMENTS[0];
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-medium ${sizeClasses[size]}`}
      style={{ 
        backgroundColor: `${sentimentConfig.color}15`,
        color: sentimentConfig.color,
        border: `1px solid ${sentimentConfig.color}30`
      }}
    >
      <span>{sentimentConfig.icon}</span>
      <span>{sentimentConfig.name}</span>
      {confidence && (
        <span className="opacity-70">({(confidence * 100).toFixed(0)}%)</span>
      )}
    </span>
  );
}

// Sentiment Filter Selector
function SentimentSelector({ selectedSentiment, onSentimentChange, disabled }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentSentiment = SENTIMENTS.find(s => s.key === selectedSentiment) || SENTIMENTS[0];

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-150 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl border border-gray-200 transition-all duration-200"
        style={{ 
          borderColor: selectedSentiment ? currentSentiment.color + '50' : undefined,
          backgroundColor: selectedSentiment ? currentSentiment.color + '10' : undefined
        }}
      >
        <Filter size={16} className="text-gray-500" />
        <span className="text-sm font-medium" style={{ color: selectedSentiment ? currentSentiment.color : '#374151' }}>
          {currentSentiment.icon} {currentSentiment.name}
        </span>
        {selectedSentiment && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSentimentChange(null);
            }}
            className="ml-1 p-0.5 hover:bg-gray-200 rounded-full transition-colors"
          >
            <X size={12} className="text-gray-500" />
          </button>
        )}
        <ChevronDown size={16} className={`text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden z-50 animate-fadeInUp">
          {SENTIMENTS.map((sentiment) => (
            <button
              key={sentiment.key || 'all'}
              onClick={() => {
                onSentimentChange(sentiment.key);
                setIsOpen(false);
              }}
              className={`w-full px-4 py-3 text-left text-sm hover:bg-gray-50 transition-colors flex items-center justify-between ${
                selectedSentiment === sentiment.key ? 'bg-gray-50' : ''
              }`}
            >
              <span className="flex items-center gap-2">
                <span>{sentiment.icon}</span>
                <span style={{ color: sentiment.key ? sentiment.color : '#374151' }}>{sentiment.name}</span>
              </span>
              {selectedSentiment === sentiment.key && (
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: sentiment.color }} />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Performance Page Component
function PerformancePage() {
  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 relative z-10">
      <div className="max-w-4xl mx-auto">
        {/* Title */}
        <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 rounded-2xl p-6 mb-6 border border-white/50 shadow-lg animate-fadeInUp">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <BarChart3 size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">Model Performance</h2>
              <p className="text-sm text-gray-500">So sánh hiệu suất các mô hình embedding</p>
            </div>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 mb-6 animate-fadeInUp" style={{ animationDelay: '100ms' }}>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">Radar Chart - Model Comparison</h3>
          <div className="h-[450px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={PERFORMANCE_DATA} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis 
                  dataKey="metric" 
                  tick={{ fill: '#374151', fontSize: 12, fontWeight: 500 }}
                />
                <PolarRadiusAxis 
                  angle={90} 
                  domain={[0, 0.8]} 
                  tick={{ fill: '#6b7280', fontSize: 10 }}
                />
                <Radar
                  name="TF-IDF"
                  dataKey="TF-IDF"
                  stroke={MODEL_COLORS['TF-IDF']}
                  fill={MODEL_COLORS['TF-IDF']}
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
                <Radar
                  name="dangvantuan"
                  dataKey="dangvantuan"
                  stroke={MODEL_COLORS['dangvantuan']}
                  fill={MODEL_COLORS['dangvantuan']}
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
                <Radar
                  name="Qwen3"
                  dataKey="Qwen3"
                  stroke={MODEL_COLORS['Qwen3']}
                  fill={MODEL_COLORS['Qwen3']}
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
                <Radar
                  name="EmbeddingGemma"
                  dataKey="EmbeddingGemma"
                  stroke={MODEL_COLORS['EmbeddingGemma']}
                  fill={MODEL_COLORS['EmbeddingGemma']}
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
                <Legend 
                  wrapperStyle={{ paddingTop: '20px' }}
                  iconType="circle"
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Data Table */}
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 animate-fadeInUp" style={{ animationDelay: '200ms' }}>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Chi tiết số liệu</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Metric</th>
                  <th className="text-center py-3 px-4 font-semibold" style={{ color: MODEL_COLORS['TF-IDF'] }}>TF-IDF</th>
                  <th className="text-center py-3 px-4 font-semibold" style={{ color: MODEL_COLORS['dangvantuan'] }}>dangvantuan</th>
                  <th className="text-center py-3 px-4 font-semibold" style={{ color: MODEL_COLORS['Qwen3'] }}>Qwen3</th>
                  <th className="text-center py-3 px-4 font-semibold" style={{ color: MODEL_COLORS['EmbeddingGemma'] }}>EmbeddingGemma</th>
                </tr>
              </thead>
              <tbody>
                {PERFORMANCE_DATA.map((row, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4 font-medium text-gray-800">{row.metric}</td>
                    <td className="text-center py-3 px-4 text-gray-600">{row['TF-IDF'].toFixed(4)}</td>
                    <td className="text-center py-3 px-4 text-gray-600 font-semibold bg-blue-50">{row['dangvantuan'].toFixed(4)}</td>
                    <td className="text-center py-3 px-4 text-gray-600">{row['Qwen3'].toFixed(4)}</td>
                    <td className="text-center py-3 px-4 text-gray-600">{row['EmbeddingGemma'].toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-gray-400 mt-4 text-center">
            * dangvantuan/vietnamese-embedding cho kết quả tốt nhất trên hầu hết các metrics
          </p>
        </div>
      </div>
    </div>
  );
}

function Message({ message, index }) {
  const isUser = message.type === 'user';

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fadeInUp`}
      style={{ animationDelay: `${index * 50}ms` }}
    >
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
            <div className="flex items-center justify-between gap-2 mb-3 pb-2 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <TrendingUp size={16} className="text-green-500" />
                <p className="text-sm font-medium text-gray-700">
                  Tìm thấy {message.results.length} bài báo
                  {message.sentimentFilter && (
                    <span className="text-gray-500"> (lọc từ {message.totalBeforeFilter})</span>
                  )}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {message.sentimentFilter && (
                  <SentimentBadge sentiment={message.sentimentFilter} size="sm" />
                )}
                {message.modelUsed && (
                  <span className="text-xs px-2 py-1 bg-purple-100 text-purple-600 rounded-full font-medium">
                    {message.modelUsed}
                  </span>
                )}
              </div>
            </div>
            <div className="space-y-3">
              {message.results.length === 0 ? (
                <div className="text-center py-4 text-gray-500">
                  <p className="text-sm">Không tìm thấy bài báo phù hợp với bộ lọc sentiment</p>
                </div>
              ) : (
                message.results.map((article, idx) => (
                  <div
                    key={idx}
                    className="group bg-gradient-to-r from-gray-50 to-white rounded-xl p-3 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-300 cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-sm">
                        #{idx + 1}
                      </span>
                      {article.sentiment && (
                        <SentimentBadge 
                          sentiment={article.sentiment} 
                          confidence={article.sentiment_confidence}
                          size="sm"
                        />
                      )}
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
                ))
              )}
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

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center ml-2 flex-shrink-0 shadow-lg">
          <span className="text-white text-xs font-bold">U</span>
        </div>
      )}
    </div>
  );
}

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
      <p className="text-gray-600 text-sm leading-relaxed mb-4">
        Gửi cho tôi URL bài báo từ <span className="font-semibold text-orange-500">VnExpress</span> hoặc{' '}
        <span className="font-semibold text-blue-500">Dân Trí</span>, tôi sẽ tìm các bài báo tương tự cho bạn.
      </p>
      
      {/* Sentiment Filter Info */}
      <div className="bg-white/70 rounded-xl p-3 mb-4 border border-gray-100">
        <p className="text-xs font-medium text-gray-700 mb-2 flex items-center gap-1">
          <Filter size={12} /> Lọc theo cảm xúc bài báo:
        </p>
        <div className="flex flex-wrap gap-2">
          {SENTIMENTS.slice(1).map(s => (
            <span 
              key={s.key}
              className="text-xs px-2 py-1 rounded-full"
              style={{ 
                backgroundColor: s.color + '15',
                color: s.color,
                border: `1px solid ${s.color}30`
              }}
            >
              {s.icon} {s.name}
            </span>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-xs px-3 py-1.5 bg-white rounded-full text-gray-600 border border-gray-200">
          🔹 Qwen3 - Embedding model
        </span>
        <span className="text-xs px-3 py-1.5 bg-white rounded-full text-gray-600 border border-gray-200">
          🔸 EmbeddingGemma - Embedding model
        </span>
        <span className="text-xs px-3 py-1.5 bg-white rounded-full text-gray-600 border border-gray-200">
          🔻 dangvantuan - Embedding model
        </span>
        <span className="text-xs px-3 py-1.5 bg-white rounded-full text-gray-600 border border-gray-200">
          📊 TF-IDF - Sparse model
        </span>
        <span className="text-xs px-3 py-1.5 bg-white rounded-full text-gray-600 border border-gray-200">
          ⚡ Ensemble - Kết hợp cả 4
        </span>
      </div>
    </div>
  );
}

function ModelSelector({ selectedModel, onModelChange, disabled }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentModel = MODELS.find(m => m.key === selectedModel);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-purple-50 to-blue-50 hover:from-purple-100 hover:to-blue-100 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl border border-purple-200 transition-all duration-200"
      >
        <span className="text-sm font-medium text-gray-700">{currentModel?.name}</span>
        <ChevronDown size={16} className={`text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden z-50 animate-fadeInUp">
          {MODELS.map((model) => (
            <button
              key={model.key}
              onClick={() => {
                onModelChange(model.key);
                setIsOpen(false);
              }}
              className={`w-full px-4 py-3 text-left text-sm hover:bg-gradient-to-r hover:from-purple-50 hover:to-blue-50 transition-colors flex items-center justify-between ${
                selectedModel === model.key ? 'bg-gradient-to-r from-purple-50 to-blue-50 text-purple-700 font-medium' : 'text-gray-700'
              }`}
            >
              <span>{model.name}</span>
              {selectedModel === model.key && (
                <span className="w-2 h-2 bg-purple-500 rounded-full" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Chat Page Component
function ChatPage({ 
  messages, 
  input, 
  setInput, 
  isLoading, 
  selectedModel, 
  setSelectedModel,
  selectedSentiment,
  setSelectedSentiment, 
  handleSend, 
  handleKeyDown, 
  messagesEndRef, 
  inputRef 
}) {
  return (
    <>
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

      <div className="relative bg-white/80 backdrop-blur-lg border-t border-white/20 px-4 py-4 z-10">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-3">
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
              disabled={isLoading}
            />
            <SentimentSelector
              selectedSentiment={selectedSentiment}
              onSentimentChange={setSelectedSentiment}
              disabled={isLoading}
            />
            <div className="flex-1 flex items-center gap-3 bg-white rounded-2xl shadow-lg border border-gray-100 p-2 focus-within:ring-2 focus-within:ring-blue-500/50 focus-within:border-blue-300 transition-all duration-300">
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
          </div>
          <p className="text-center text-xs text-gray-400 mt-2">
            Nhấn Enter để gửi • Hỗ trợ VnExpress & Dân Trí • 
            {selectedSentiment ? (
              <span style={{ color: SENTIMENTS.find(s => s.key === selectedSentiment)?.color }}>
                {' '}Đang lọc: {SENTIMENTS.find(s => s.key === selectedSentiment)?.name}
              </span>
            ) : ' Không lọc sentiment'}
          </p>
        </div>
      </div>
    </>
  );
}

function App() {
  const [activePage, setActivePage] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('qwen3');
  const [selectedSentiment, setSelectedSentiment] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const isValidUrl = (text) => {
    return text.includes('vnexpress.net') || text.includes('dantri.com.vn');
  };

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
        body: JSON.stringify({ 
          url, 
          model: selectedModel, 
          top_k: 5,
          sentiment_filter: selectedSentiment 
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Có lỗi xảy ra');
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          type: 'bot',
          results: data.results,
          inputText: data.input_text,
          modelUsed: data.model_used,
          sentimentFilter: data.sentiment_filter,
          totalBeforeFilter: data.total_before_filter,
        },
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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 relative">
      <BackgroundParticles />

      <header className="relative bg-white/80 backdrop-blur-lg border-b border-white/20 px-6 py-4 shadow-sm z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
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

          {/* Tab Navigation */}
          <div className="flex items-center gap-2 bg-gray-100 rounded-xl p-1">
            <button
              onClick={() => setActivePage('chat')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                activePage === 'chat'
                  ? 'bg-white text-blue-600 shadow-md'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <MessageCircle size={16} />
              Chat
            </button>
            <button
              onClick={() => setActivePage('performance')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                activePage === 'performance'
                  ? 'bg-white text-blue-600 shadow-md'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <BarChart3 size={16} />
              Performance
            </button>
          </div>
        </div>
      </header>

      {/* Page Content */}
      {activePage === 'chat' ? (
        <ChatPage
          messages={messages}
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
          selectedSentiment={selectedSentiment}
          setSelectedSentiment={setSelectedSentiment}
          handleSend={handleSend}
          handleKeyDown={handleKeyDown}
          messagesEndRef={messagesEndRef}
          inputRef={inputRef}
        />
      ) : (
        <PerformancePage />
      )}
    </div>
  );
}

export default App;