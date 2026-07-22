import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import DashboardTab from './components/DashboardTab';
import ChatbotTab from './components/ChatbotTab';
import GdsSecurityTab from './components/GdsSecurityTab';
import SettingsTab from './components/SettingsTab';
import { translations } from './i18n/translations';
import { CheckCircle2 } from 'lucide-react';

export default function App() {
  const [lang, setLang] = useState('fr');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [agency, setAgency] = useState('abidjan');
  const [toastMessage, setToastMessage] = useState(null);

  const t = translations[lang] || translations.fr;

  const notify = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col font-sans">
      {/* Toast Notification Banner */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center space-x-2 px-4 py-3 rounded-xl bg-cyan-950 border border-cyan-500 text-cyan-300 text-xs font-bold shadow-2xl shadow-cyan-950 animate-bounce">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Header */}
      <Header
        lang={lang}
        setLang={setLang}
        agency={agency}
        setAgency={setAgency}
        t={t}
      />

      {/* Main Body Layout */}
      <div className="flex-1 flex flex-col lg:flex-row p-4 lg:p-6 gap-6 max-w-7xl w-full mx-auto">
        {/* Navigation Sidebar */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} t={t} />

        {/* Main Content Workspace Area */}
        <main className="flex-1 min-w-0">
          {activeTab === 'dashboard' && <DashboardTab t={t} notify={notify} />}
          {activeTab === 'assistant' && <ChatbotTab t={t} lang={lang} />}
          {activeTab === 'gdsSecurity' && <GdsSecurityTab t={t} notify={notify} />}
          {activeTab === 'settings' && <SettingsTab t={t} notify={notify} />}
        </main>
      </div>
    </div>
  );
}
