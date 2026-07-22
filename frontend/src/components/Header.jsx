import React from 'react';
import { ShieldCheck, Languages, Building2, CheckCircle2, ChevronDown } from 'lucide-react';

export default function Header({ lang, setLang, agency, setAgency, t }) {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
      {/* Brand & Logo */}
      <div className="flex items-center space-x-3">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 text-white shadow-lg glow-cyan">
          <ShieldCheck className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
          </span>
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold tracking-tight text-white">{t.brandTitle}</h1>
            <span className="px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              V2.4 SaaS
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium hidden sm:block">{t.brandSubtitle}</p>
        </div>
      </div>

      {/* Center & Right Controls */}
      <div className="flex items-center flex-wrap space-x-3 ml-auto">
        {/* Agency Selector */}
        <div className="relative group">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-xs text-slate-300 hover:border-slate-600 transition cursor-pointer">
            <Building2 className="w-4 h-4 text-cyan-400" />
            <span className="font-medium hidden md:inline">{t.agencyLabel}:</span>
            <select
              value={agency}
              onChange={(e) => setAgency(e.target.value)}
              className="bg-transparent text-slate-200 font-semibold focus:outline-none cursor-pointer pr-1"
            >
              <option value="abidjan" className="bg-slate-900 text-slate-200">{t.agencies.abidjan}</option>
              <option value="paris" className="bg-slate-900 text-slate-200">{t.agencies.paris}</option>
              <option value="global" className="bg-slate-900 text-slate-200">{t.agencies.global}</option>
            </select>
          </div>
        </div>

        {/* Global Security Risk Status Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold shadow-sm">
          <CheckCircle2 className="w-4 h-4" />
          <span>{t.statusProtected}</span>
        </div>

        {/* Language Switcher (FR / EN) */}
        <button
          onClick={() => setLang(lang === 'fr' ? 'en' : 'fr')}
          title={t.switchLanguage}
          className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-500 hover:to-cyan-600 text-white text-xs font-bold shadow-md transition transform active:scale-95"
        >
          <Languages className="w-4 h-4" />
          <span>{t.languageBtn}</span>
        </button>
      </div>
    </header>
  );
}
