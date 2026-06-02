import { useState } from 'react';
import { Activity, TrendingUp, Coins, Newspaper, Menu, X, Info, Mail, FileText, Shield, Cookie } from 'lucide-react';

export type Tab = 'home' | 'ipo' | 'crypto-airdrops' | 'crypto-news' | 'about' | 'contact' | 'privacy' | 'terms' | 'cookies';

interface HeaderProps {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
}

export default function Header({ activeTab, onTabChange }: HeaderProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const mainTabs = [
    { id: 'ipo' as Tab, label: 'IPO Analysis', icon: TrendingUp },
    { id: 'crypto-airdrops' as Tab, label: 'Airdrops', icon: Coins },
    { id: 'crypto-news' as Tab, label: 'News', icon: Newspaper },
  ];

  const pageTabs = [
    { id: 'about' as Tab, label: 'About', icon: Info },
    { id: 'contact' as Tab, label: 'Contact', icon: Mail },
    { id: 'privacy' as Tab, label: 'Privacy', icon: Shield },
    { id: 'terms' as Tab, label: 'Terms', icon: FileText },
    { id: 'cookies' as Tab, label: 'Cookies', icon: Cookie },
  ];

  const isPage = activeTab in { about: 1, contact: 1, privacy: 1, terms: 1, cookies: 1 };

  return (
    <header className="sticky top-0 z-50 bg-surface-0/80 backdrop-blur-xl border-b border-surface-300/60">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">
          <button
            onClick={() => onTabChange('home')}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity group"
          >
            <div className="w-7 h-7 rounded-md bg-brand flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-[15px] font-semibold text-surface-white tracking-tight">
                PulseTrends
              </span>
              <span className="hidden sm:inline text-[11px] text-surface-600 font-medium">
                IPO & Crypto Intelligence
              </span>
            </div>
          </button>

          <nav className="hidden md:flex items-center gap-0.5">
            {mainTabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[13px] font-medium transition-all duration-150 ${
                  activeTab === tab.id
                    ? 'bg-surface-300 text-surface-white'
                    : 'text-surface-700 hover:text-surface-900 hover:bg-surface-200'
                }`}
              >
                <tab.icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            ))}
            <div className="w-px h-4 bg-surface-400 mx-1.5" />
            {pageTabs.slice(0, 3).map(tab => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all ${
                  isPage && activeTab === tab.id
                    ? 'text-surface-white'
                    : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <span className="hidden md:relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-60" />
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-success" />
            </span>
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-1.5 text-surface-700 hover:text-surface-white rounded-md hover:bg-surface-300 transition-colors"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <div className="md:hidden pb-3 pt-1 border-t border-surface-300/60 animate-fade-in">
            <p className="px-3 py-1.5 text-[11px] text-surface-600 uppercase tracking-wider font-medium">Sections</p>
            {mainTabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => { onTabChange(tab.id); setMobileOpen(false); }}
                className={`flex items-center gap-2.5 w-full px-3 py-2.5 rounded-md text-[13px] font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-surface-300 text-surface-white'
                    : 'text-surface-700 hover:text-surface-white'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
            <p className="px-3 py-1.5 mt-2 text-[11px] text-surface-600 uppercase tracking-wider font-medium">Pages</p>
            {pageTabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => { onTabChange(tab.id); setMobileOpen(false); }}
                className={`flex items-center gap-2.5 w-full px-3 py-2.5 rounded-md text-[13px] font-medium transition-all ${
                  isPage && activeTab === tab.id
                    ? 'bg-surface-300 text-surface-white'
                    : 'text-surface-700 hover:text-surface-white'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </header>
  );
}
