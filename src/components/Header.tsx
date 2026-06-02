import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Activity, TrendingUp, Coins, Newspaper, Menu, X, Info, Mail, FileText, Shield, Cookie } from 'lucide-react';

const mainTabs = [
  { to: '/ipo-analysis' as const, label: 'IPO Analysis', icon: TrendingUp },
  { to: '/airdrops' as const, label: 'Airdrops', icon: Coins },
  { to: '/news' as const, label: 'News', icon: Newspaper },
];

const pageTabs = [
  { to: '/about' as const, label: 'About', icon: Info },
  { to: '/contact' as const, label: 'Contact', icon: Mail },
  { to: '/privacy-policy' as const, label: 'Privacy', icon: Shield },
  { to: '/terms' as const, label: 'Terms', icon: FileText },
  { to: '/cookies' as const, label: 'Cookies', icon: Cookie },
];

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-surface-0/80 backdrop-blur-xl border-b border-surface-300/60">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">
          <Link
            to="/"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity group"
            aria-label="PulseTrends home"
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
          </Link>

          <nav className="hidden md:flex items-center gap-0.5" aria-label="Main navigation">
            {mainTabs.map(tab => (
              <NavLink
                key={tab.to}
                to={tab.to}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[13px] font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-surface-300 text-surface-white'
                      : 'text-surface-700 hover:text-surface-900 hover:bg-surface-200'
                  }`
                }
              >
                <tab.icon className="w-3.5 h-3.5" />
                {tab.label}
              </NavLink>
            ))}
            <div className="w-px h-4 bg-surface-400 mx-1.5" />
            {pageTabs.slice(0, 3).map(tab => (
              <NavLink
                key={tab.to}
                to={tab.to}
                className={({ isActive }) =>
                  `px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all ${
                    isActive
                      ? 'text-surface-white'
                      : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'
                  }`
                }
              >
                {tab.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <span className="hidden md:relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-60" />
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-success" />
            </span>
            <button
              type="button"
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-1.5 text-surface-700 hover:text-surface-white rounded-md hover:bg-surface-300 transition-colors"
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileOpen}
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <div className="md:hidden pb-3 pt-1 border-t border-surface-300/60 animate-fade-in">
            <p className="px-3 py-1.5 text-[11px] text-surface-600 uppercase tracking-wider font-medium">Sections</p>
            {mainTabs.map(tab => (
              <NavLink
                key={tab.to}
                to={tab.to}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 w-full px-3 py-2.5 rounded-md text-[13px] font-medium transition-all ${
                    isActive
                      ? 'bg-surface-300 text-surface-white'
                      : 'text-surface-700 hover:text-surface-white'
                  }`
                }
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </NavLink>
            ))}
            <p className="px-3 py-1.5 mt-2 text-[11px] text-surface-600 uppercase tracking-wider font-medium">Pages</p>
            {pageTabs.map(tab => (
              <NavLink
                key={tab.to}
                to={tab.to}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 w-full px-3 py-2.5 rounded-md text-[13px] font-medium transition-all ${
                    isActive
                      ? 'bg-surface-300 text-surface-white'
                      : 'text-surface-700 hover:text-surface-white'
                  }`
                }
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </NavLink>
            ))}
          </div>
        )}
      </div>
    </header>
  );
}
