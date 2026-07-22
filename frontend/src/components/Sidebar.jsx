import React from 'react';
import { LayoutDashboard, MessageSquare, Globe, Settings, Cpu, Plane, ShieldAlert } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, t }) {
  const navItems = [
    { id: 'dashboard', label: t.nav.dashboard, icon: LayoutDashboard },
    { id: 'assistant', label: t.nav.assistant, icon: MessageSquare },
    { id: 'gdsSecurity', label: t.nav.gdsSecurity, icon: Globe },
    { id: 'settings', label: t.nav.settings, icon: Settings },
  ];

  return (
    <aside className="w-full lg:w-64 glass-panel border-r border-slate-800/80 p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-6">
        {/* Navigation Category Header */}
        <div className="px-3 pt-2">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Navigation Suite
          </p>
        </div>

        {/* Menu Buttons */}
        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-emerald-500/10 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-950/50'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Operational Clean Footer Status */}
      <div className="mt-8 pt-4 border-t border-slate-800/80 space-y-3">
        <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>{t.systemStatusTitle}</span>
          </div>
          <div className="flex items-center space-x-2 text-[11px] text-emerald-400 font-medium">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>{t.systemStatusOnline}</span>
          </div>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 px-1 font-mono">
          <div className="flex items-center space-x-1">
            <Plane className="w-3.5 h-3.5 text-cyan-400" />
            <span>GDS Amadeus Connect</span>
          </div>
          <span className="text-emerald-400 font-semibold">99.9%</span>
        </div>
      </div>
    </aside>
  );
}
