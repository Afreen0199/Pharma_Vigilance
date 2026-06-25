import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, X, Send, Loader2, Copy, ThumbsUp, ThumbsDown, ChevronDown, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { chatApi } from '../../api/chatApi';

const SUGGESTED_QUESTIONS = [
  "Summarize the main ADRs for this case.",
  "What is the causality assessment?",
  "Are there any FDA boxed warnings?",
  "Explain the seriousness criteria.",
  "What information is missing from this report?",
  "Are there regulatory alerts for this drug?",
];

const ChatbotPanel = ({ analysisId, onToggle }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  useEffect(() => {
    if (onToggle) onToggle(isOpen);
  }, [isOpen, onToggle]);
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState(SUGGESTED_QUESTIONS);
  const [feedback, setFeedback] = useState({});
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  const handleSend = async (text) => {
    const trimmed = text?.trim();
    if (!trimmed) return;

    setMessages(prev => [...prev, { id: Date.now(), text: trimmed, sender: 'user' }]);
    setInput('');
    setIsTyping(true);
    setSuggestions([]);

    try {
      const response = await chatApi.askQuestion(analysisId, trimmed);
      
      // Defensively extract string response
      let answerText = '';
      if (typeof response === 'string') {
        answerText = response;
      } else if (response?.data?.response && typeof response.data.response === 'string') {
        answerText = response.data.response;
      } else if (response?.response && typeof response.response === 'string') {
        answerText = response.response;
      } else if (response?.answer && typeof response.answer === 'string') {
        answerText = response.answer;
      } else if (response?.message && typeof response.message === 'string') {
        answerText = response.message;
      } else {
        answerText = 'Response processed successfully, but no text was returned.';
      }

      // Store remaining payload
      const metadata = typeof response === 'object' ? (response?.data || response) : {};

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: answerText,
        metadata: metadata,
        sender: 'bot'
      }]);

      const newSuggestions = metadata?.suggested_questions || [];
      if (Array.isArray(newSuggestions) && newSuggestions.length > 0) {
        setSuggestions(newSuggestions.slice(0, 4));
      } else {
        setSuggestions([]);
      }
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error connecting to the AI. Please try again.',
        sender: 'bot',
        isError: true,
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFeedback = (msgId, type) => {
    setFeedback(prev => ({ ...prev, [msgId]: type }));
  };

  return (
    <>
      {/* Floating button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 flex items-center gap-2 px-4 py-3 bg-violet-600 hover:bg-violet-700 text-white rounded-2xl shadow-2xl shadow-violet-600/30 transition-all z-50 group"
        >
          <MessageSquare className="h-5 w-5" />
          <span className="text-sm font-bold">AI Copilot</span>
          <span className="absolute -top-1 -right-1 h-3 w-3 bg-emerald-500 rounded-full animate-pulse border-2 border-white dark:border-slate-900"></span>
        </button>
      )}

      {/* Panel */}
      <div
        className={`fixed inset-y-0 right-0 w-[420px] max-w-full bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl transform transition-transform duration-300 ease-in-out z-50 flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800 bg-gradient-to-r from-violet-100 dark:from-violet-900/40 to-slate-50 dark:to-slate-900 shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-violet-600/20 rounded-xl border border-violet-600/30">
              <Bot className="h-5 w-5 text-violet-600 dark:text-violet-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">PV Intelligence Copilot</h3>
              <p className="text-[10px] text-slate-600 dark:text-slate-400 font-medium">Context: <span className="text-violet-600 dark:text-violet-400 font-mono">{analysisId?.substring(0, 12)}...</span></p>
            </div>
          </div>
          <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50 dark:bg-slate-950/50">
          {messages.length === 0 && (
            <div className="text-center pt-8 space-y-3">
              <div className="p-4 bg-violet-600/10 border border-violet-600/20 rounded-2xl">
                <Bot className="h-8 w-8 text-violet-600 dark:text-violet-400 mx-auto mb-2" />
                <p className="text-sm text-slate-800 dark:text-slate-300 font-semibold">AI PharmaVigil Analyst</p>
                <p className="text-xs text-slate-600 dark:text-slate-500 mt-1">I'm ready to answer questions about this case report. Ask me about reactions, causality, FDA signals, or missing information.</p>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} group`}>
              {msg.sender === 'bot' && (
                <div className="h-7 w-7 rounded-full bg-violet-700/30 flex items-center justify-center shrink-0 mr-2 mt-1">
                  <Bot className="h-4 w-4 text-violet-400" />
                </div>
              )}
              <div className={`max-w-[85%] ${msg.sender === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-violet-600 text-white rounded-br-sm'
                    : msg.isError
                    ? 'bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700/40 text-red-600 dark:text-red-300 rounded-bl-sm'
                    : 'bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700/50 text-slate-800 dark:text-slate-200 rounded-bl-sm'
                }`}>
                  {msg.sender === 'bot' ? (
                    <div className="prose prose-slate dark:prose-invert prose-sm max-w-none prose-p:my-1 prose-li:my-0.5 prose-headings:text-slate-800 dark:prose-headings:text-slate-200">
                      <ReactMarkdown>{typeof msg.text === 'string' ? msg.text : ''}</ReactMarkdown>
                      
                      {msg.metadata && Object.keys(msg.metadata).length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-300 dark:border-slate-700/50 space-y-2">
                          {msg.metadata.reasoning && (
                             <div className="text-xs text-slate-700 dark:text-slate-400 bg-slate-200 dark:bg-slate-900/50 p-2 rounded-lg border border-slate-300 dark:border-slate-700/50">
                               <span className="font-bold text-slate-800 dark:text-slate-300 block mb-1">Reasoning</span>
                               {typeof msg.metadata.reasoning === 'string' ? msg.metadata.reasoning : JSON.stringify(msg.metadata.reasoning)}
                             </div>
                          )}
                          {msg.metadata.fda_evidence && (
                             <div className="text-xs text-slate-700 dark:text-slate-400 bg-violet-100 dark:bg-violet-900/10 p-2 rounded-lg border border-violet-300 dark:border-violet-800/30">
                               <span className="font-bold text-violet-700 dark:text-violet-400 block mb-1">FDA Evidence</span>
                               {typeof msg.metadata.fda_evidence === 'string' ? msg.metadata.fda_evidence : JSON.stringify(msg.metadata.fda_evidence)}
                             </div>
                          )}
                          {msg.metadata.sources && Array.isArray(msg.metadata.sources) && msg.metadata.sources.length > 0 && (
                             <div className="text-xs mt-2">
                               <span className="font-bold text-slate-800 dark:text-slate-300 block mb-1">Sources</span>
                               <ul className="list-disc pl-4 text-slate-700 dark:text-slate-400 space-y-1">
                                 {msg.metadata.sources.map((s, i) => (
                                    <li key={i}>{typeof s === 'string' ? s : (s.title || s.source || JSON.stringify(s))}</li>
                                 ))}
                               </ul>
                             </div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    <p>{typeof msg.text === 'string' ? msg.text : ''}</p>
                  )}
                </div>

                {/* Bot message actions */}
                {msg.sender === 'bot' && !msg.isError && (
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity ml-1">
                    <button
                      onClick={() => copyToClipboard(msg.text)}
                      className="flex items-center gap-1 text-[10px] text-slate-500 hover:text-slate-300 transition-colors"
                      title="Copy response"
                    >
                      <Copy className="h-3 w-3" /> Copy
                    </button>
                    <button
                      onClick={() => handleFeedback(msg.id, 'up')}
                      className={`text-[10px] transition-colors ${feedback[msg.id] === 'up' ? 'text-emerald-400' : 'text-slate-500 hover:text-emerald-400'}`}
                    >
                      <ThumbsUp className="h-3 w-3" />
                    </button>
                    <button
                      onClick={() => handleFeedback(msg.id, 'down')}
                      className={`text-[10px] transition-colors ${feedback[msg.id] === 'down' ? 'text-red-400' : 'text-slate-500 hover:text-red-400'}`}
                    >
                      <ThumbsDown className="h-3 w-3" />
                    </button>
                  </div>
                )}
              </div>
              {msg.sender === 'user' && (
                <div className="h-7 w-7 rounded-full bg-violet-600/30 flex items-center justify-center shrink-0 ml-2 mt-1">
                  <User className="h-4 w-4 text-violet-400" />
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="h-7 w-7 rounded-full bg-violet-700/30 flex items-center justify-center shrink-0 mr-2">
                <Bot className="h-4 w-4 text-violet-400" />
              </div>
              <div className="bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700/50 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="h-2 w-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="h-2 w-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="px-4 py-2 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 shrink-0">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-2">Suggested Questions</p>
            <div className="flex flex-wrap gap-1.5">
              {suggestions.slice(0, 4).map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  disabled={isTyping}
                  className="text-[11px] bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white px-2.5 py-1.5 rounded-lg transition-all text-left leading-tight shadow-sm dark:shadow-none"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0">
          <form
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="flex items-center gap-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about this case..."
              disabled={isTyping}
              className="flex-1 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-violet-600/50 focus:ring-1 focus:ring-violet-600/30 transition-all"
            />
            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              className="p-2.5 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-200 dark:disabled:bg-slate-700 disabled:text-slate-400 dark:disabled:text-slate-500 text-white rounded-xl transition-all"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Backdrop on mobile */}
      {isOpen && (
        <div className="fixed inset-0 bg-slate-950/60 z-40 lg:hidden" onClick={() => setIsOpen(false)} />
      )}
    </>
  );
};

export default ChatbotPanel;
