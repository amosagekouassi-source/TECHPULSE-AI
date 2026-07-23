import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, Sparkles, Bot, User, ShieldCheck, 
  Cpu, Database, Layers, ExternalLink, HelpCircle, 
  RefreshCw, CheckCircle2, AlertTriangle
} from 'lucide-react';

export default function ChatbotTab({ t, lang }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: t.assistant.initialGreeting,
      intent: 'GENERAL_QUESTION',
      severity: null,
      cves: [],
      modules: { faiss: false, distilbert: false, llm: true },
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isProcessing]);

  const handleSend = async (text) => {
    const query = text || inputValue;
    if (!query.trim()) return;

    const userMsg = { id: Date.now(), role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    if (!text) setInputValue('');

    // Message temporaire pendant le traitement RAG
    const loadingId = Date.now() + 1;
    setMessages(prev => [...prev, { 
      id: loadingId, 
      role: 'assistant', 
      content: t.assistant.processing, 
      loading: true 
    }]);

    try {
      // Connexion à votre API FastAPI / Python (ex: http://localhost:8000/api/chat)
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query, lang: lang })
      });

      const data = await response.json();

      // Remplacement du message de chargement par la vraie réponse du RAG
      setMessages(prev => prev.map(msg => 
        msg.id === loadingId 
          ? { 
              id: loadingId, 
              role: 'assistant', 
              content: data.response, 
              intent: data.intent, 
              cves: data.cves || [] 
            }
          : msg
      ));
    } catch (error) {
      // Gestion propre en cas de déconnexion du backend
      setMessages(prev => prev.map(msg => 
        msg.id === loadingId 
          ? { 
              id: loadingId, 
              role: 'assistant', 
              content: "⚠️ Connexion au serveur RAG interrompue. Veuillez vérifier le backend Python.", 
              intent: "ERROR" 
            }
          : msg
      ));
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] glass-panel rounded-2xl border border-slate-800 overflow-hidden">
      {/* Top Header of Chat */}
      <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-emerald-500 text-white shadow-md">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base flex items-center space-x-2">
              <span>{t.assistant.title}</span>
              <span className="px-2 py-0.5 text-[10px] font-extrabold uppercase rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                RAG Active
              </span>
            </h3>
            <p className="text-xs text-slate-400">{t.assistant.subtitle}</p>
          </div>
        </div>

        <button 
          onClick={() => setMessages([messages[0]])}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
          title="Réinitialiser la conversation"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start space-x-3.5 ${
              msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
                msg.role === 'user'
                  ? 'bg-gradient-to-tr from-cyan-600 to-cyan-500 text-white'
                  : 'bg-slate-800 border border-slate-700 text-cyan-400'
              }`}
            >
              {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
            </div>

            {/* Bubble Container */}
            <div className={`max-w-2xl space-y-2 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-cyan-600 text-white font-medium rounded-tr-none shadow-lg'
                    : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-tl-none shadow-md'
                }`}
              >
                <div className="whitespace-pre-line">{msg.content}</div>
              </div>

              {/* Bot Metadata & Badges */}
              {msg.role === 'assistant' && (msg.intent || msg.severity || (msg.cves && msg.cves.length > 0)) && (
                <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
                  {/* Intent Badge */}
                  {msg.intent && (
                    <span className="px-2 py-0.5 rounded-md bg-slate-800 text-cyan-400 border border-slate-700 font-semibold">
                      {t.assistant.intentLabel} {msg.intent}
                    </span>
                  )}

                  {/* Severity Badge */}
                  {msg.severity && (
                    <span className={`px-2 py-0.5 rounded-md font-extrabold uppercase border ${
                      msg.severity === 'CRITICAL' 
                        ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' 
                        : 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                    }`}>
                      {t.assistant.severityLabel} {msg.severity}
                    </span>
                  )}

                  {/* CVE Sources Citation Tags */}
                  {(() => {
                    const validCves = (msg.cves || []).filter(c => /^CVE-\d{4}-\d+/i.test(c));
                    return validCves.length > 0 ? (
                      <div className="flex items-center space-x-1">
                        <span className="text-slate-400">{t.assistant.cveSourcesLabel}</span>
                        {validCves.map((cve) => (
                          <span
                            key={cve}
                            className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-700/50 font-mono font-bold flex items-center space-x-1 cursor-pointer hover:bg-cyan-900 transition"
                          >
                            <span>{cve}</span>
                            <ExternalLink className="w-3 h-3" />
                          </span>
                        ))}
                      </div>
                    ) : null;
                  })()}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="flex items-start space-x-3.5">
            <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 text-cyan-400 flex items-center justify-center shrink-0">
              <Bot className="w-5 h-5 animate-pulse" />
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 text-xs text-cyan-400 font-medium flex items-center space-x-2 rounded-tl-none">
              <Sparkles className="w-4 h-4 animate-spin text-cyan-400" />
              <span>{t.assistant.processing}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Prompt Chips Bar */}
      <div className="px-6 py-3 border-t border-slate-800/80 bg-slate-950/60">
        <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
          {t.assistant.promptChipsTitle}
        </p>
        <div className="flex flex-wrap gap-2">
          {t.assistant.promptChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(chip)}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-cyan-950/80 border border-slate-800 hover:border-cyan-500/40 text-xs text-slate-300 hover:text-cyan-400 font-medium transition active:scale-95 text-left"
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-4 border-t border-slate-800 bg-slate-900/90 flex items-center space-x-3"
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={t.assistant.inputPlaceholder}
          className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || isProcessing}
          className="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 hover:to-cyan-500 disabled:opacity-50 text-white text-sm font-bold shadow-lg shadow-cyan-950 flex items-center space-x-2 transition"
        >
          <span>{t.assistant.sendBtn}</span>
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
