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

  // Handle prompt sending
  const handleSend = (textToSend) => {
    const query = textToSend || inputValue;
    if (!query.trim() || isProcessing) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textToSend) setInputValue('');
    setIsProcessing(true);

    // Simulate RAG Pipeline process & response synthesis
    setTimeout(() => {
      let intent = 'GENERAL_QUESTION';
      let severity = null;
      let cves = [];
      let modules = { faiss: true, distilbert: false, llm: true };
      let answerText = '';

      const queryLower = query.toLowerCase();

      const greetings = ['bonjour', 'salut', 'hello', 'hi', 'coucou', 'bonsoir', 'hey'];
      const isGreeting = greetings.some(g => queryLower.includes(g));

      if (isGreeting && !queryLower.includes('cve') && !queryLower.includes('rce')) {
        intent = 'GENERAL_QUESTION';
        cves = [];
        modules = { faiss: false, distilbert: false, llm: true };
        answerText = lang === 'fr'
          ? "Bonjour ! Je suis **TECHPULSE-AI**, votre assistant virtuel en cybersécurité pour le secteur du voyage.\n\nComment puis-je vous aider aujourd'hui ? (ex: *sécurisation des API GDS Amadeus*, *analyse d'alerte*, *bonnes pratiques PCI-DSS*)"
          : "Hello! I am **TECHPULSE-AI**, your virtual cybersecurity assistant for the travel industry.\n\nHow can I assist you today? (e.g., *securing Amadeus GDS APIs*, *threat analysis*, *PCI-DSS best practices*)";
      } else if (queryLower.includes('cve') || queryLower.includes('qu\'est-ce') || queryLower.includes('what is')) {
        intent = 'GENERAL_QUESTION';
        cves = [];
        modules = { faiss: false, distilbert: false, llm: true };
        answerText = lang === 'fr'
          ? "Une **CVE** (*Common Vulnerabilities and Exposures*) est un identifiant universel attribué aux vulnérabilités connues.\n\nDans le secteur du voyage, les CVE vous permettent d'identifier si vos serveurs de réservation, API GDS ou passerelles de paiement présentent des failles identifiées par la communauté mondiale de cybersécurité."
          : "A **CVE** (*Common Vulnerabilities and Exposures*) is a standardized identifier assigned to publicly disclosed cybersecurity vulnerabilities.\n\nIn the travel industry, tracking CVEs helps IT teams ensure booking engines, GDS connectors, and payment gateways are patched before exploit vectors emerge.";
      } else if (queryLower.includes('amadeus') || queryLower.includes('gds') || queryLower.includes('sécuriser') || queryLower.includes('secure')) {
        intent = 'CYBER_QUESTION';
        cves = ['CVE-2025-0168'];
        modules.distilbert = true;
        severity = 'HIGH';
        answerText = lang === 'fr'
          ? "Pour sécuriser les intégrations **GDS Amadeus & Sabre** de votre agence de voyage :\n\n1. **Authentification & Muting Token** : Mettez en place des jetons OAuth 2.0 à durée de vie courte (15 min).\n2. **Mutual TLS (mTLS)** : Exigez des certificats bi-directionnels pour toute requête de réservation.\n3. **Rate Limiting Stricte** : Limitez le volume de requêtes par minute pour prévenir l'aspiration massive de tarifs ou d'inventaires de vols.\n4. **Audit Log Centralisé** : Surveillez les anomalies sur l'API billetterie."
          : "To secure your travel agency's **Amadeus & Sabre GDS** integrations:\n\n1. **Authentication & Token Expiry**: Implement OAuth 2.0 tokens with short TTLs (15 min).\n2. **Mutual TLS (mTLS)**: Enforce bi-directional certificates for booking webhooks.\n3. **Strict Rate Limiting**: Limit API requests per minute to prevent tariff scraping.\n4. **Centralized Audit Logging**: Monitor anomalies on ticket issuance APIs.";
      } else if (queryLower.includes('rce') || queryLower.includes('critique') || queryLower.includes('vulnerability') || queryLower.includes('serveur')) {
        intent = 'THREAT_ANALYSIS';
        cves = ['CVE-2025-1429', 'CVE-2026-0041'];
        modules.distilbert = true;
        severity = 'CRITICAL';
        answerText = lang === 'fr'
          ? "🚨 **Alerte d'Analyse de Menace RCE Détectée**\n\nUne vulnérabilité d'exécution de code à distance (RCE) sur un serveur de réservation présente un risque direct de prise de contrôle du système et d'exfiltration des données voyageurs (PNR, passeports).\n\n**Plan d'Action Immédiat :**\n- **Isolation Réseau** : Placez le serveur impacté derrière un WAF strict en mode blocage.\n- **Révocation des Identifiants** : Réinitialisez immédiatement les API Keys connectées au GDS.\n- **Atténuation RAG** : Consulter la directive de sécurité référencée dans la CVE-2025-1429."
          : "🚨 **RCE Threat Analysis Alert Detected**\n\nA Remote Code Execution (RCE) flaw on a booking server poses a severe threat of system compromise and passenger record (PNR) leakage.\n\n**Immediate Action Plan:**\n- **Network Isolation**: Place the affected host behind a WAF in strict blocking mode.\n- **Credential Revocation**: Immediately rotate API keys connected to GDS systems.\n- **Patching**: Apply emergency security updates as specified in CVE-2025-1429.";
      } else {
        intent = 'CYBER_QUESTION';
        cves = [];
        modules = { faiss: true, distilbert: false, llm: true };
        answerText = lang === 'fr'
          ? `J'ai bien reçu votre demande concernant *"${query}"*.\n\nDans le secteur du tourisme et des agences de voyage, il est essentiel de protéger les données sensibles des voyageurs (passeports, coordonnées bancaires) et de surveiller l'intégrité des webhooks de réservation.`
          : `I have received your request regarding *"${query}"*.\n\nIn the tourism and travel agency sector, securing passenger data and monitoring booking webhook endpoints is essential.`;
      }

      const botMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: answerText,
        intent,
        severity,
        cves,
        modules,
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsProcessing(false);
    }, 1000);
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
                  {msg.cves && msg.cves.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <span className="text-slate-400">{t.assistant.cveSourcesLabel}</span>
                      {msg.cves.map((cve) => (
                        <span
                          key={cve}
                          className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-700/50 font-mono font-bold flex items-center space-x-1 cursor-pointer hover:bg-cyan-900 transition"
                        >
                          <span>{cve}</span>
                          <ExternalLink className="w-3 h-3" />
                        </span>
                      ))}
                    </div>
                  )}
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
