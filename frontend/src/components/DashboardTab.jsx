import React, { useState } from 'react';
import { 
  Server, ShieldAlert, Activity, CreditCard, 
  TrendingUp, AlertTriangle, FileText, CheckCircle2, 
  Lock, RefreshCw, ChevronRight, Zap, X, Download, Sparkles, MessageSquare
} from 'lucide-react';
import { 
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer, Cell 
} from 'recharts';

export default function DashboardTab({ t, notify, agency = 'abidjan', onAskAssistant }) {
  const [loadingAction, setLoadingAction] = useState(null);
  const [selectedActionModal, setSelectedActionModal] = useState(null);

  // Dynamic Agency Data Mapping
  const agencyMetrics = {
    abidjan: {
      name: "Agence Abidjan",
      monitoredApis: 14,
      threatCount: 19,
      riskScore: 82,
      riskStatus: "ATTENTION",
      riskBadgeColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
      critical: 2,
      high: 5,
      medium: 8,
      low: 4,
      trendData: [
        { time: '00:00', threats: 12, bookings: 420 },
        { time: '04:00', threats: 8, bookings: 210 },
        { time: '08:00', threats: 15, bookings: 890 },
        { time: '12:00', threats: 24, bookings: 1450 },
        { time: '16:00', threats: 18, bookings: 1210 },
        { time: '20:00', threats: 9, bookings: 780 },
      ]
    },
    paris: {
      name: "Agence Paris",
      monitoredApis: 28,
      threatCount: 6,
      riskScore: 96,
      riskStatus: "OPTIMAL",
      riskBadgeColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
      critical: 0,
      high: 1,
      medium: 2,
      low: 3,
      trendData: [
        { time: '00:00', threats: 2, bookings: 890 },
        { time: '04:00', threats: 1, bookings: 340 },
        { time: '08:00', threats: 4, bookings: 1900 },
        { time: '12:00', threats: 6, bookings: 2800 },
        { time: '16:00', threats: 3, bookings: 2100 },
        { time: '20:00', threats: 2, bookings: 1450 },
      ]
    },
    global: {
      name: "Toutes les Agences (Global)",
      monitoredApis: 42,
      threatCount: 25,
      riskScore: 89,
      riskStatus: "BON",
      riskBadgeColor: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
      critical: 2,
      high: 6,
      medium: 10,
      low: 7,
      trendData: [
        { time: '00:00', threats: 14, bookings: 1310 },
        { time: '04:00', threats: 9, bookings: 550 },
        { time: '08:00', threats: 19, bookings: 2790 },
        { time: '12:00', threats: 30, bookings: 4250 },
        { time: '16:00', threats: 21, bookings: 3310 },
        { time: '20:00', threats: 11, bookings: 2230 },
      ]
    }
  };

  const currentData = agencyMetrics[agency] || agencyMetrics.abidjan;

  const severityData = [
    { name: t.dashboard.charts.severityLabels.critical, count: currentData.critical, color: '#F43F5E' },
    { name: t.dashboard.charts.severityLabels.high, count: currentData.high, color: '#F59E0B' },
    { name: t.dashboard.charts.severityLabels.medium, count: currentData.medium, color: '#06B6D4' },
    { name: t.dashboard.charts.severityLabels.low, count: currentData.low, color: '#10B981' },
  ];

  // Action Details Configuration
  const actionDetails = {
    auditPayment: {
      id: 'auditPayment',
      title: 'Audit des passerelles de paiement PCI-DSS',
      agencyName: currentData.name,
      severity: 'HIGH',
      badgeColor: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      findings: 'Détection d\'une version obsolète de la bibliothèque TLS sur l\'API de paiement Stripe/Visa. Risque potentiel d\'interception de données bancaires.',
      recommendation: 'Activer impérativement TLS 1.3 sur les endpoints de traitement de carte et mettre à jour le SDK de paiement.',
      aiQuery: `Réaliser un diagnostic de sécurité PCI-DSS et TLS 1.3 sur les passerelles de paiement de l'${currentData.name}.`
    },
    verifyAmadeus: {
      id: 'verifyAmadeus',
      title: 'Vérification des accès GDS Amadeus & Sabre',
      agencyName: currentData.name,
      severity: currentData.critical > 0 ? 'CRITICAL' : 'LOW',
      badgeColor: currentData.critical > 0 ? 'text-rose-400 bg-rose-500/10 border-rose-500/30' : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
      findings: currentData.critical > 0 
        ? 'Alerte : 2 jetons API Amadeus expirent sans rotation automatique et 1 session d\'émission PNR provient d\'une IP non autorisée.'
        : 'Statut conforme : Toutes les clés API Amadeus possèdent une rotation 2FA active et 0 session suspecte détectée.',
      recommendation: 'Appliquer immédiatement la rotation obligatoire des jetons PNR et restreindre les sous-réseaux IP autorisés.',
      aiQuery: `Quelles sont les failles récentes sur Amadeus Web Services et comment sécuriser les jetons PNR pour ${currentData.name} ?`
    },
    scanEndpoints: {
      id: 'scanEndpoints',
      title: 'Scan RCE des Webhooks de Réservation',
      agencyName: currentData.name,
      severity: 'MEDIUM',
      badgeColor: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
      findings: 'Les webhooks de synchronisation des billets d\'avion acceptent des chaînes JSON non assainies. Risque potentiel de Remote Code Execution (RCE).',
      recommendation: 'Implémenter la validation stricte des payloads JSON entrants avec Pydantic et désactiver l\'évaluation dynamique de code.',
      aiQuery: `Comment protéger les webhooks de réservation contre les vulnérabilités RCE et l'injection de payload pour ${currentData.name} ?`
    },
    generateReport: {
      id: 'generateReport',
      title: 'Rapport d\'Audit de Sécurité PDF',
      agencyName: currentData.name,
      severity: 'INFO',
      badgeColor: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
      findings: `Génération automatique du rapport certifié TECHPULSE-AI pour ${currentData.name}. Contient l'analyse des ${currentData.monitoredApis} APIs et le détail des ${currentData.threatCount} incidents.`,
      recommendation: 'Téléchargez le document d\'audit officiel ou transmettez-le à votre responsable de conformité.',
      aiQuery: `Générer un bilan complet de sécurité pour ${currentData.name}.`
    }
  };

  const handleAction = (actionKey) => {
    setLoadingAction(actionKey);
    setTimeout(() => {
      setLoadingAction(null);
      if (actionKey === 'generateReport') {
        downloadAuditReport();
        notify("Rapport d'audit téléchargé avec succès ! 📄");
      } else {
        setSelectedActionModal(actionDetails[actionKey]);
      }
    }, 800);
  };

  const downloadAuditReport = () => {
    const reportContent = `===============================================================
TECHPULSE-AI — RAPPORT D'AUDIT CYBER ET CONFORMITÉ GDS
===============================================================
Agence : ${currentData.name}
Date de l'audit : ${new Date().toLocaleDateString('fr-FR')} à ${new Date().toLocaleTimeString('fr-FR')}
Statut de Sécurité : ${currentData.riskStatus} (Score : ${currentData.riskScore}/100)

---------------------------------------------------------------
1. MÉTRIQUES ET INDICATEURS CLÉS (KPI)
---------------------------------------------------------------
- APIs & Endpoints Surveillés : ${currentData.monitoredApis}
- Incidents / Menaces Détectés : ${currentData.threatCount}
- Niveau de Menace Critique : ${currentData.critical}
- Niveau de Menace Élevée : ${currentData.high}
- Niveau de Menace Moyenne : ${currentData.medium}
- Niveau de Menace Faible : ${currentData.low}

---------------------------------------------------------------
2. SYNTHÈSE DES RECOMMANDATIONS ACTIONNABLES
---------------------------------------------------------------
[ACTION 1] Passerelles de Paiement (PCI-DSS)
- Détection : TLS obsolète sur les flux de paiement.
- Recommandation : Activer impérativement TLS 1.3 sur les endpoints.

[ACTION 2] Système GDS Amadeus & Sabre
- Détection : ${currentData.critical > 0 ? 'Jetons API à renouveler d\'urgence' : 'Accès conformes et sécurisés'}.
- Recommandation : Appliquer la rotation automatique des jetons PNR.

[ACTION 3] Webhooks de Réservation (Protection RCE)
- Détection : Risque potentiel d'injection JSON.
- Recommandation : Valider les payloads avec Pydantic.

---------------------------------------------------------------
Certifié par le moteur d'Intelligence Cyber TECHPULSE-AI (RAG + DistilBERT)
===============================================================`;

    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Audit_Cyber_TECHPULSE_${agency.toUpperCase()}_${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Modal d'Action Dynamique */}
      {selectedActionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="glass-panel max-w-xl w-full p-6 rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl relative space-y-4">
            <button 
              onClick={() => setSelectedActionModal(null)}
              className="absolute top-4 right-4 p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-3">
              <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400">
                <Zap className="w-6 h-6" />
              </div>
              <div>
                <span className={`inline-block px-2.5 py-0.5 text-xs font-bold rounded-full border ${selectedActionModal.badgeColor} mb-1`}>
                  {selectedActionModal.severity}
                </span>
                <h3 className="text-lg font-bold text-white">{selectedActionModal.title}</h3>
                <p className="text-xs text-slate-400">{selectedActionModal.agencyName}</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
              <div className="font-semibold text-slate-300 flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Diagnostic & Faits Détectés :</span>
              </div>
              <p className="text-slate-400 leading-relaxed pl-5.5">{selectedActionModal.findings}</p>
            </div>

            <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-900/40 space-y-2 text-xs">
              <div className="font-semibold text-cyan-300 flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                <span>Recommandation Prioritaire :</span>
              </div>
              <p className="text-slate-300 leading-relaxed pl-5.5">{selectedActionModal.recommendation}</p>
            </div>

            <div className="pt-2 flex flex-col sm:flex-row gap-3">
              <button 
                onClick={() => {
                  const query = selectedActionModal.aiQuery;
                  setSelectedActionModal(null);
                  if (onAskAssistant) onAskAssistant(query);
                }}
                className="flex-1 py-2.5 px-4 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition flex items-center justify-center space-x-2"
              >
                <Sparkles className="w-4 h-4 text-cyan-200" />
                <span>Demander des détails à l'Assistant IA</span>
              </button>

              <button 
                onClick={() => {
                  downloadAuditReport();
                  notify("Rapport téléchargé ! 📄");
                }}
                className="py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition flex items-center justify-center space-x-2"
              >
                <Download className="w-4 h-4 text-slate-400" />
                <span>Télécharger Rapport</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab Header Banner with Agency Indicator */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-cyan-950/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">{t.dashboard.title}</h2>
          <p className="text-sm text-slate-400 mt-1">{t.dashboard.subtitle}</p>
        </div>
        <div className="flex items-center space-x-2 self-start md:self-auto">
          <span className="text-xs text-slate-400 font-semibold">Vue Filtre :</span>
          <span className={`px-3 py-1.5 rounded-xl text-xs font-extrabold border ${currentData.riskBadgeColor}`}>
            {currentData.name}
          </span>
        </div>
      </div>

      {/* 4 Executive KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Monitored APIs */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/30 transition group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t.dashboard.kpis.monitoredApis}</span>
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 group-hover:scale-110 transition">
              <Server className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-white">{currentData.monitoredApis}</span>
            <span className="text-xs text-cyan-400 font-semibold ml-2">Actifs</span>
          </div>
        </div>

        {/* KPI 2: Active Threats */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-rose-500/30 transition group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t.dashboard.kpis.activeThreats}</span>
            <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 group-hover:scale-110 transition">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-white">{currentData.threatCount}</span>
            <span className="text-xs text-rose-400 font-semibold ml-2">{currentData.critical} critiques</span>
          </div>
        </div>

        {/* KPI 3: Security Score */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-emerald-500/30 transition group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t.dashboard.kpis.securityScore}</span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:scale-110 transition">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-white">{currentData.riskScore}%</span>
            <span className={`text-xs font-semibold ml-2 px-2 py-0.5 rounded-full border ${currentData.riskBadgeColor}`}>
              {currentData.riskStatus}
            </span>
          </div>
        </div>

        {/* KPI 4: Protected Transactions */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-amber-500/30 transition group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t.dashboard.kpis.protectedTx}</span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 group-hover:scale-110 transition">
              <CreditCard className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-white">99.98%</span>
            <span className="text-xs text-amber-400 font-semibold ml-2">PCI-DSS OK</span>
          </div>
        </div>
      </div>

      {/* Two Analytical Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart 1: Threat Trend vs Transactions (2 cols) */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-cyan-400" />
                <span>{t.dashboard.charts.trendTitle}</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">{currentData.name}</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={currentData.trendData}>
                <defs>
                  <linearGradient id="colorThreats" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#F43F5E" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorBookings" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '0.75rem', color: '#F8FAFC' }}
                />
                <Area type="monotone" dataKey="threats" stroke="#F43F5E" fillOpacity={1} fill="url(#colorThreats)" name="Menaces" />
                <Area type="monotone" dataKey="bookings" stroke="#06B6D4" fillOpacity={1} fill="url(#colorBookings)" name="Réservations" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Severity Distribution Bar Chart (1 col) */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <span>{t.dashboard.charts.severityTitle}</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">{currentData.name}</p>

            <div className="h-52 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
                  <XAxis type="number" stroke="#64748B" fontSize={12} />
                  <YAxis type="category" dataKey="name" stroke="#94A3B8" fontSize={11} width={75} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '0.75rem', color: '#F8FAFC' }}
                  />
                  <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Action & Recommendations Cards */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <span>{t.dashboard.quickActions.title}</span>
          </h3>
          <span className="text-xs text-cyan-400 font-semibold">Interactif & Dynamique</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Action 1 */}
          <div 
            onClick={() => handleAction('auditPayment')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <CreditCard className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition" />
                <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition" />
              </div>
              <h4 className="font-bold text-sm text-white">{t.dashboard.quickActions.auditPayment}</h4>
              <p className="text-xs text-slate-400 mt-1">{t.dashboard.quickActions.auditPaymentDesc}</p>
            </div>
            <button className="mt-4 w-full py-2 rounded-lg bg-cyan-950/60 border border-cyan-800/40 group-hover:bg-cyan-600 text-xs font-semibold text-cyan-200 group-hover:text-white transition flex items-center justify-center space-x-1.5">
              <span>{loadingAction === 'auditPayment' ? 'Analyse en cours...' : 'Lancer l\'audit PCI-DSS'}</span>
            </button>
          </div>

          {/* Action 2 */}
          <div 
            onClick={() => handleAction('verifyAmadeus')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-emerald-500/40 cursor-pointer transition flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <Lock className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition" />
                <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition" />
              </div>
              <h4 className="font-bold text-sm text-white">{t.dashboard.quickActions.verifyAmadeus}</h4>
              <p className="text-xs text-slate-400 mt-1">{t.dashboard.quickActions.verifyAmadeusDesc}</p>
            </div>
            <button className="mt-4 w-full py-2 rounded-lg bg-emerald-950/60 border border-emerald-800/40 group-hover:bg-emerald-600 text-xs font-semibold text-emerald-200 group-hover:text-white transition flex items-center justify-center space-x-1.5">
              <span>{loadingAction === 'verifyAmadeus' ? 'Vérification...' : 'Vérifier Accès Amadeus'}</span>
            </button>
          </div>

          {/* Action 3 */}
          <div 
            onClick={() => handleAction('scanEndpoints')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-amber-500/40 cursor-pointer transition flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <RefreshCw className="w-5 h-5 text-amber-400 group-hover:scale-110 transition" />
                <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-amber-400 transition" />
              </div>
              <h4 className="font-bold text-sm text-white">{t.dashboard.quickActions.scanEndpoints}</h4>
              <p className="text-xs text-slate-400 mt-1">{t.dashboard.quickActions.scanEndpointsDesc}</p>
            </div>
            <button className="mt-4 w-full py-2 rounded-lg bg-amber-950/60 border border-amber-800/40 group-hover:bg-amber-600 text-xs font-semibold text-amber-200 group-hover:text-white transition flex items-center justify-center space-x-1.5">
              <span>{loadingAction === 'scanEndpoints' ? 'Scan RCE...' : 'Scanner Webhooks'}</span>
            </button>
          </div>

          {/* Action 4 */}
          <div 
            onClick={() => handleAction('generateReport')}
            className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition flex flex-col justify-between group"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <FileText className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition" />
                <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition" />
              </div>
              <h4 className="font-bold text-sm text-white">{t.dashboard.quickActions.generateReport}</h4>
              <p className="text-xs text-slate-400 mt-1">{t.dashboard.quickActions.generateReportDesc}</p>
            </div>
            <button className="mt-4 w-full py-2 rounded-lg bg-cyan-950/60 border border-cyan-800/40 group-hover:bg-cyan-600 text-xs font-semibold text-cyan-200 group-hover:text-white transition flex items-center justify-center space-x-1.5">
              <span>{loadingAction === 'generateReport' ? 'Génération...' : 'Exporter Rapport (.TXT/.PDF)'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
