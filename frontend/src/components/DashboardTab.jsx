import React, { useState } from 'react';
import { 
  Server, ShieldAlert, Activity, CreditCard, 
  TrendingUp, AlertTriangle, FileText, CheckCircle2, 
  Lock, RefreshCw, ChevronRight, Zap
} from 'lucide-react';
import { 
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer, Cell 
} from 'recharts';

export default function DashboardTab({ t, notify }) {
  const [loadingAction, setLoadingAction] = useState(null);

  // Mock Recharts Data
  const trendData = [
    { time: '00:00', threats: 12, bookings: 420 },
    { time: '04:00', threats: 8, bookings: 210 },
    { time: '08:00', threats: 15, bookings: 890 },
    { time: '12:00', threats: 24, bookings: 1450 },
    { time: '16:00', threats: 18, bookings: 1210 },
    { time: '20:00', threats: 9, bookings: 780 },
  ];

  const severityData = [
    { name: t.dashboard.charts.severityLabels.critical, count: 0, color: '#F43F5E' },
    { name: t.dashboard.charts.severityLabels.high, count: 2, color: '#F59E0B' },
    { name: t.dashboard.charts.severityLabels.medium, count: 5, color: '#06B6D4' },
    { name: t.dashboard.charts.severityLabels.low, count: 12, color: '#10B981' },
  ];

  const handleAction = (actionKey) => {
    setLoadingAction(actionKey);
    setTimeout(() => {
      setLoadingAction(null);
      notify(t.dashboard.quickActions.actionSuccess);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      {/* Tab Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-cyan-950/30">
        <h2 className="text-2xl font-bold text-white tracking-tight">{t.dashboard.title}</h2>
        <p className="text-sm text-slate-400 mt-1">{t.dashboard.subtitle}</p>
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
            <span className="text-3xl font-extrabold text-white">14</span>
            <span className="text-xs text-cyan-400 font-semibold ml-2">Active</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{t.dashboard.kpis.monitoredApisSub}</p>
        </div>

        {/* KPI 2: Global Risk Score */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-emerald-500/30 transition group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t.dashboard.kpis.riskScore}</span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:scale-110 transition">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline">
            <span className="text-3xl font-extrabold text-emerald-400">28</span>
            <span className="text-sm font-semibold text-slate-400 ml-1">/100</span>
          </div>
          <p className="text-xs text-emerald-400 font-semibold mt-1">{t.dashboard.kpis.riskScoreSub}</p>
        </div>

        {/* KPI 3: Active Threat Alerts */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-amber-500/30 transition group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t.dashboard.kpis.activeAlerts}</span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 group-hover:scale-110 transition">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-amber-400">2</span>
            <span className="text-xs text-amber-400 font-semibold ml-2">Vigilance</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{t.dashboard.kpis.activeAlertsSub}</p>
        </div>

        {/* KPI 4: Protected Bookings */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/30 transition group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t.dashboard.kpis.protectedBookings}</span>
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 group-hover:scale-110 transition">
              <CreditCard className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-white">18,420</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{t.dashboard.kpis.protectedBookingsSub}</p>
        </div>
      </div>

      {/* Visual Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend Area Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              <span>{t.dashboard.charts.threatTrendsTitle}</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">Live Sync</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorThreats" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#94A3B8' }}
                />
                <Area type="monotone" dataKey="threats" stroke="#06B6D4" strokeWidth={3} fillOpacity={1} fill="url(#colorThreats)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution Bar Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>{t.dashboard.charts.severityDistTitle}</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">DistilBERT Classifier</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="name" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#94A3B8' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Quick Action & Recommendations Cards */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <h3 className="text-base font-bold text-white mb-4 flex items-center space-x-2">
          <Zap className="w-5 h-5 text-amber-400" />
          <span>{t.dashboard.quickActions.title}</span>
        </h3>
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
            <button className="mt-4 w-full py-1.5 rounded-lg bg-slate-800 group-hover:bg-cyan-600 text-xs font-semibold text-slate-200 group-hover:text-white transition">
              {loadingAction === 'auditPayment' ? 'Scan en cours...' : 'Lancer l\'audit'}
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
            <button className="mt-4 w-full py-1.5 rounded-lg bg-slate-800 group-hover:bg-emerald-600 text-xs font-semibold text-slate-200 group-hover:text-white transition">
              {loadingAction === 'verifyAmadeus' ? 'Vérification...' : 'Vérifier GDS'}
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
            <button className="mt-4 w-full py-1.5 rounded-lg bg-slate-800 group-hover:bg-amber-600 text-xs font-semibold text-slate-200 group-hover:text-white transition">
              {loadingAction === 'scanEndpoints' ? 'Analyse RCE...' : 'Scanner webhooks'}
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
            <button className="mt-4 w-full py-1.5 rounded-lg bg-slate-800 group-hover:bg-cyan-600 text-xs font-semibold text-slate-200 group-hover:text-white transition">
              {loadingAction === 'generateReport' ? 'Génération...' : 'Exporter PDF'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
