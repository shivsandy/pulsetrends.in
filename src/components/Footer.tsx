import { Link } from 'react-router-dom';
import { Activity, TrendingUp, Coins, Newspaper } from 'lucide-react';

export default function Footer() {
  const sectionLinks = [
    { to: '/ipo-analysis', label: 'IPO Analysis', icon: TrendingUp },
    { to: '/airdrops', label: 'Airdrops', icon: Coins },
    { to: '/news', label: 'News', icon: Newspaper },
  ] as const;
  const pageLinks = [
    { to: '/about', label: 'About' },
    { to: '/contact', label: 'Contact' },
    { to: '/privacy-policy', label: 'Privacy' },
    { to: '/terms', label: 'Terms' },
    { to: '/cookies', label: 'Cookies' },
  ] as const;
  return (
    <footer className="border-t border-surface-300/60 mt-8 bg-surface-50" role="contentinfo">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-5 h-5 rounded bg-brand flex items-center justify-center">
                <Activity className="w-3 h-3 text-white" />
              </div>
              <span className="text-[14px] font-semibold text-surface-800 tracking-tight">PulseTrends</span>
            </div>
            <p className="text-[12px] text-surface-600 leading-relaxed">
              AI-powered intelligence for IPOs, crypto airdrops, and market-moving news.
            </p>
          </div>
          <nav aria-label="Footer sections">
            <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-2">Sections</p>
            <div className="flex flex-col gap-1.5">
              {sectionLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="flex items-center gap-1.5 text-[13px] text-surface-700 hover:text-surface-white transition-colors"
                >
                  <link.icon className="w-3 h-3" />
                  {link.label}
                </Link>
              ))}
            </div>
          </nav>
          <nav aria-label="Footer pages">
            <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-2">Pages</p>
            <div className="flex flex-col gap-1.5">
              {pageLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="text-[13px] text-surface-700 hover:text-surface-white transition-colors"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </nav>
        </div>
        <div className="border-t border-surface-300/40 mt-6 pt-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-[11px] text-surface-500 text-center sm:text-left">
            For informational purposes only. Not financial advice. Always conduct your own research.
          </p>
          <p className="text-[11px] text-surface-500">
            &copy; {new Date().getFullYear()} PulseTrends. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
