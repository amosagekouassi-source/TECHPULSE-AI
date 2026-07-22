import React, { useState } from 'react';
import { Settings, Cpu, Bell, Key, Save, CheckCircle2 } from 'lucide-react';

export default function SettingsTab({ t, notify }) {
  const [provider, setProvider] = useState('gemini');
  const [threshold, setThreshold] = useState('highAndCritical');

  const handleSave = (e) => {
    e.preventDefault();
    notify(t.settings.saveSuccess);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
          <Settings className="w-6 h-6 text-cyan-400" />
          <span>{t.settings.title}</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">{t.settings.subtitle}</p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* LLM Provider Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <span>{t.settings.llmProviderTitle}</span>
          </h3>

          <div className="space-y-3">
            <label className="flex items-center space-x-3 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition">
              <input
                type="radio"
                name="provider"
                value="gemini"
                checked={provider === 'gemini'}
                onChange={(e) => setProvider(e.target.value)}
                className="text-cyan-500 focus:ring-cyan-500"
              />
              <div className="text-sm text-slate-200 font-semibold">{t.settings.llmProviders.gemini}</div>
            </label>

            <label className="flex items-center space-x-3 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition">
              <input
                type="radio"
                name="provider"
                value="openai"
                checked={provider === 'openai'}
                onChange={(e) => setProvider(e.target.value)}
                className="text-cyan-500 focus:ring-cyan-500"
              />
              <div className="text-sm text-slate-200 font-semibold">{t.settings.llmProviders.openai}</div>
            </label>

            <label className="flex items-center space-x-3 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition">
              <input
                type="radio"
                name="provider"
                value="offline"
                checked={provider === 'offline'}
                onChange={(e) => setProvider(e.target.value)}
                className="text-cyan-500 focus:ring-cyan-500"
              />
              <div className="text-sm text-slate-200 font-semibold">{t.settings.llmProviders.offline}</div>
            </label>
          </div>
        </div>

        {/* Alert Threshold Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Bell className="w-5 h-5 text-amber-400" />
            <span>{t.settings.alertThresholdsTitle}</span>
          </h3>

          <select
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="criticalOnly">{t.settings.criticalOnly}</option>
            <option value="highAndCritical">{t.settings.highAndCritical}</option>
            <option value="allAlerts">{t.settings.allAlerts}</option>
          </select>
        </div>

        {/* Key Status */}
        <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-800/50 flex items-center space-x-3 text-xs text-cyan-300">
          <Key className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>{t.settings.apiKeyStatus}</span>
        </div>

        {/* Save Button */}
        <button
          type="submit"
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 hover:to-cyan-500 text-white text-sm font-bold shadow-lg shadow-cyan-950/60 flex items-center space-x-2 transition"
        >
          <Save className="w-4 h-4" />
          <span>{t.settings.saveBtn}</span>
        </button>
      </form>
    </div>
  );
}
