import React, { useState, useEffect, useRef } from 'react';
import { chatbotApi } from '../../api/chatbotApi';
import { 
  Send, 
  Trash2, 
  Bot, 
  User, 
  ShieldCheck, 
  TrendingUp, 
  ListChecks, 
  Link2,
  Loader2,
  RefreshCw
} from 'lucide-react';

const SafetyChatbot = ({ analysisId }) => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Welcome to the clinical safety copilot terminal. Ask me questions regarding causality claims, seriousness classifications, openFDA reporting totals, chronological clinical events, or regulatory restrictions.',
      suggestedQuestions: [
        'What is the suspect drug in this case?',
        'Explain the causality reasoning',
        'What regulatory restrictions apply here?',
        'Show FDA signal summary metrics'
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  // Scroll to bottom when messages update
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    if (!textToSend) {
      setInput('');
    }

    // Append user query to UI
    setMessages(prev => [...prev, { sender: 'user', text: query }]);
    setLoading(true);

    try {
      const data = await chatbotApi.sendMessage(analysisId, query);
      
      const newMsg = {
        sender: 'bot',
        text: data.response || data.answer?.summary || 'Response parsed successfully.',
        suggestedQuestions: data.suggested_questions || [],
        sources: data.sources || [],
        card: data.answer // holds the structured clinical details
      };

      setMessages(prev => [...prev, newMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: 'Failed to retrieve copilot assessment. Make sure the backend service is running and active.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (loading) return;
    try {
      await chatbotApi.resetSession(analysisId);
      setMessages([
        {
          sender: 'bot',
          text: 'Conversational memory reset. Workspace history has been wiped. Ask me any case specific question.',
          suggestedQuestions: [
            'What is the suspect drug in this case?',
            'Explain the causality reasoning',
            'What regulatory restrictions apply here?',
            'Show FDA signal summary metrics'
          ]
        }
      ]);
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  const renderCardDetails = (card) => {
    if (!card) return null;
    
    // Check if card has any details other than summary
    const hasCausality = card.causality || card.suspect_drug;
    const hasReasoning = card.reasoning && card.reasoning.length > 0;
    const hasEvidence = card.evidence_sources && card.evidence_sources.length > 0;
    const hasChunks = card.retrieved_chunks && card.retrieved_chunks.length > 0;
    
    if (!hasCausality && !hasReasoning && !hasEvidence && !hasChunks) return null;

    return (
      <div className="mt-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 space-y-3.5 text-xs text-slate-750 dark:text-slate-300">
        
        {/* Suspect Drug & Causality */}
        {hasCausality && (
          <div className="space-y-2">
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block">Safety Classification</span>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-white dark:bg-slate-900 border border-slate-150 dark:border-slate-800 p-2 rounded-lg">
                <span className="text-[9px] text-slate-400 block font-bold">Suspect Drug</span>
                <span className="font-extrabold text-slate-800 dark:text-slate-200">{card.suspect_drug || 'N/A'}</span>
              </div>
              <div className="bg-white dark:bg-slate-900 border border-slate-150 dark:border-slate-800 p-2 rounded-lg">
                <span className="text-[9px] text-slate-400 block font-bold">Adverse Event</span>
                <span className="font-extrabold text-slate-850 dark:text-slate-250 truncate block">{card.adverse_effect || 'N/A'}</span>
              </div>
            </div>
            
            {card.causality && (
              <div className="flex items-center justify-between pt-1 text-[11px] font-bold">
                <span className="text-slate-400">Causality Link:</span>
                <span className="text-brand-600 dark:text-brand-400 uppercase font-black">
                  {card.causality.suspected_relationship || card.causality.relationship_strength || 'Possible'}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Reasoning points */}
        {hasReasoning && (
          <div className="space-y-1.5 border-t border-slate-200 dark:border-slate-850 pt-2.5">
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block flex items-center gap-1">
              <ListChecks className="h-3 w-3 text-slate-400" />
              <span>Causality Reasoning</span>
            </span>
            <ul className="list-disc pl-4 space-y-1 text-[11px] font-medium leading-relaxed">
              {card.reasoning.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* FDA Evidence stats */}
        {card.fda_evidence && (
          <div className="space-y-1.5 border-t border-slate-200 dark:border-slate-850 pt-2.5">
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block flex items-center gap-1">
              <TrendingUp className="h-3 w-3 text-slate-400" />
              <span>FDA Evidence Ratios</span>
            </span>
            <div className="grid grid-cols-2 gap-2 text-[10px] font-bold">
              <div className="text-slate-450 dark:text-slate-400">
                Hospitalization Rate: <span className="text-slate-800 dark:text-slate-200">{(card.fda_evidence.hosp_pct * 100).toFixed(1)}%</span>
              </div>
              <div className="text-slate-450 dark:text-slate-400">
                Serious Cases Ratio: <span className="text-slate-800 dark:text-slate-200">{(card.fda_evidence.serious_pct * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        )}

        {/* retrieved Chunks Citations */}
        {hasChunks && (
          <div className="space-y-1.5 border-t border-slate-200 dark:border-slate-850 pt-2.5">
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block flex items-center gap-1">
              <Link2 className="h-3 w-3 text-slate-400" />
              <span>Knowledge Base Citations</span>
            </span>
            <div className="space-y-1.5">
              {card.retrieved_chunks.slice(0, 2).map((chk, idx) => (
                <div key={idx} className="bg-white dark:bg-slate-900 border border-slate-150 dark:border-slate-800 p-2 rounded-lg text-[10px]">
                  <p className="font-semibold text-slate-500 dark:text-slate-400 leading-normal line-clamp-2 italic">
                    "{chk.text || chk.chunk_text}"
                  </p>
                  <div className="mt-1 flex items-center justify-between text-[9px] font-bold text-slate-400">
                    <span className="truncate max-w-[150px]">{chk.source_document || chk.document_name || 'Guideline doc'}</span>
                    <span className="text-brand-500 font-black">Similarity: {(chk.score || chk.similarity || 0.8).toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-slate-900 overflow-hidden">
      {/* Chat Header */}
      <div className="h-14 flex items-center justify-between px-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 select-none">
        <div className="flex items-center gap-2">
          <div className="p-1 bg-brand-100 dark:bg-brand-950/40 text-brand-600 dark:text-brand-400 rounded-lg">
            <Bot className="h-4.5 w-4.5" />
          </div>
          <span className="text-xs font-bold text-slate-850 dark:text-white">
            Clinical Safety Copilot
          </span>
        </div>
        
        <button
          onClick={handleReset}
          className="p-1.5 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-550 hover:text-red-500 dark:hover:text-red-400 rounded-lg transition-colors cursor-pointer"
          title="Reset Conversation Memory"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {/* Message bubble logs */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex gap-3 max-w-[85%] ${
              msg.sender === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
            }`}
          >
            {/* Avatar */}
            <div className={`h-7 w-7 rounded-full flex items-center justify-center shrink-0 border select-none ${
              msg.sender === 'user' 
                ? 'bg-brand-50 dark:bg-brand-950/40 border-brand-200/50 dark:border-brand-850/60 text-brand-600 dark:text-brand-400' 
                : 'bg-slate-100 dark:bg-slate-800 border-slate-200/80 dark:border-slate-750 text-slate-550 dark:text-slate-300'
            }`}>
              {msg.sender === 'user' ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
            </div>

            {/* Bubble */}
            <div className="space-y-2">
              <div className={`p-3 rounded-2xl text-xs font-medium leading-relaxed ${
                msg.sender === 'user' 
                  ? 'bg-brand-600 text-white rounded-tr-none font-semibold' 
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-205 rounded-tl-none border border-slate-200/40 dark:border-slate-750/30'
              }`}>
                <p className="whitespace-pre-wrap">{msg.text}</p>
              </div>

              {/* Structured Card payload details */}
              {msg.card && renderCardDetails(msg.card)}

              {/* Suggestions chips */}
              {msg.suggestedQuestions && msg.suggestedQuestions.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1.5">
                  {msg.suggestedQuestions.map((q, qidx) => (
                    <button
                      key={qidx}
                      onClick={() => handleSend(q)}
                      className="px-2.5 py-1 bg-slate-50 hover:bg-slate-100 dark:bg-slate-950 dark:hover:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[10px] font-bold text-slate-650 dark:text-slate-400 rounded-full transition-all cursor-pointer hover:scale-[1.02]"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 max-w-[80%] mr-auto items-center text-slate-450 dark:text-slate-500">
            <div className="h-7 w-7 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-750 flex items-center justify-center">
              <Loader2 className="h-4.5 w-4.5 animate-spin text-brand-500" />
            </div>
            <span className="text-[10px] font-bold animate-pulse">Safety Copilot is evaluating context...</span>
          </div>
        )}
        <div ref={scrollRef}></div>
      </div>

      {/* Input container */}
      <form 
        onSubmit={(e) => { e.preventDefault(); handleSend(); }} 
        className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex gap-2 select-none"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about hepatotoxicity, RAG references..."
          disabled={loading}
          className="flex-1 px-3.5 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-semibold placeholder-slate-400 focus:outline-none focus:border-brand-500 text-slate-800 dark:text-white"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-2.5 bg-brand-600 hover:bg-brand-700 disabled:bg-slate-250 dark:disabled:bg-slate-850 text-white rounded-xl transition-all cursor-pointer shrink-0 flex items-center justify-center shadow-md shadow-brand-600/15"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
};

export default SafetyChatbot;
