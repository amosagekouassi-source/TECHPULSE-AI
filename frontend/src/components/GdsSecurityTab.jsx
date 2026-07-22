import React, { useState } from 'react';
import { Globe, Server, Lock, AlertCircle, CheckCircle2, ShieldAlert, RefreshCw } from 'lucide-react';

export default function GdsSecurityTab({ t, notify }) {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => {
      setRefreshing(false);
      notify("Connecteurs GDS réinitialisés et ré-analysés.");
    }, 1000);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Globe className="w-6 h-6 text-cyan-400" />
            <span>{t.gdsSecurity.title}</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">{t.gdsSecurity.subtitle}</p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-bold text-slate-200 transition"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Rafraîchir les flux</span>
        </button>
      </div>

      {/* Systems Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/90 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-4 px-6 font-semibold">{t.gdsSecurity.tableHeaders.system}</th>
                <th className="py-4 px-6 font-semibold">{t.gdsSecurity.tableHeaders.type}</th>
                <th className="py-4 px-6 font-semibold">{t.gdsSecurity.tableHeaders.status}</th>
                <th className="py-4 px-6 font-semibold">{t.gdsSecurity.tableHeaders.latency}</th>
                <th className="py-4 px-6 font-semibold">{t.gdsSecurity.tableHeaders.tls}</th>
                <th className="py-4 px-6 font-semibold">{t.gdsSecurity.tableHeaders.anomaly}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {t.gdsSecurity.systems.map((sys, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition">
                  <td className="py-4 px-6 font-bold text-white flex items-center space-x-3">
                    <Server className="w-4 h-4 text-cyan-400 shrink-0" />
                    <span>{sys.name}</span>
                  </td>
                  <td className="py-4 px-6 text-slate-400 font-medium">{sys.type}</td>
                  <td className="py-4 px-6">
                    <span className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                      sys.status === 'Protégé' || sys.status === 'Protected'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    }`}>
                      {sys.status === 'Protégé' || sys.status === 'Protected' ? (
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      ) : (
                        <AlertCircle className="w-3.5 h-3.5" />
                      )}
                      <span>{sys.status}</span>
                    </span>
                  </td>
                  <td className="py-4 px-6 font-mono text-cyan-400 font-semibold">{sys.latency}</td>
                  <td className="py-4 px-6 text-slate-300 font-mono text-xs">{sys.tls}</td>
                  <td className="py-4 px-6">
                    {sys.anomaly === 'Aucune' || sys.anomaly === 'None' ? (
                      <span className="text-slate-500 text-xs">{sys.anomaly}</span>
                    ) : (
                      <span className="text-amber-400 text-xs font-semibold flex items-center space-x-1">
                        <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                        <span>{sys.anomaly}</span>
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
