import { useState } from 'react';
import Header from './components/Header';
import type { Tab } from './components/Header';
import Ticker from './components/Ticker';
import CookieConsent from './components/CookieConsent';
import IPOSection from './components/IPOSection';
import CryptoAirdropSection from './components/CryptoAirdropSection';
import CryptoNewsSection from './components/CryptoNewsSection';
import AboutPage from './components/AboutPage';
import ContactPage from './components/ContactPage';
import PrivacyPage from './components/PrivacyPage';
import TermsPage from './components/TermsPage';
import CookiesPage from './components/CookiesPage';
import Badge from './components/Badge';
import { TrendingUp, Coins, Newspaper, Brain, BarChart3, ArrowRight, Activity, Layers, Sparkles, Shield } from 'lucide-react';
import { ipoStocks } from './data/ipoData';

function HeroLanding({ onNavigate }: { onNavigate: (tab: Tab) => void }) {
  return (
    <div className="space-y-10">
      <div className="border-b border-surface-300/60 pb-10">
        <Badge variant="default" size="md">Premium Signal Desk</Badge>
        <h1 className="text-3xl sm:text-4xl lg:text-[44px] font-bold text-surface-white mt-4 tracking-tight leading-[1.15]">
          Intelligence for IPOs, crypto airdrops,<br className="hidden sm:block" /> and market-moving news.
        </h1>
        <p className="text-[15px] text-surface-700 mt-3 max-w-2xl leading-relaxed">
          PulseTrends turns chaotic market signals into clear, AI-analyzed briefs. Faster decisions, 
          cleaner insights, and deeper analysis for investors who want signal over noise.
        </p>

        <div className="flex flex-wrap items-center gap-6 mt-6">
          <div className="flex items-center gap-2">
            <span className="text-[12px] text-surface-600 uppercase tracking-wider font-medium">IPOs Tracked</span>
            <span className="text-[14px] font-bold text-surface-white">{ipoStocks.length}+</span>
          </div>
          <div className="w-px h-4 bg-surface-400" />
          <div className="flex items-center gap-2">
            <span className="text-[12px] text-surface-600 uppercase tracking-wider font-medium">Engine</span>
            <span className="text-[14px] font-bold text-surface-white">AI Analysis</span>
          </div>
          <div className="w-px h-4 bg-surface-400" />
          <div className="flex items-center gap-2">
            <span className="text-[12px] text-surface-600 uppercase tracking-wider font-medium">Coverage</span>
            <div className="flex items-center gap-1.5">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-60"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-success"></span>
              </span>
              <span className="text-[14px] font-bold text-surface-white">Live</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            tab: 'ipo' as Tab,
            icon: TrendingUp,
            badge: 'IPO Analysis',
            title: 'Upcoming IPO Intelligence',
            description: 'Deep-dive analysis with company overviews, financials, AI scoring, and risk assessment for every upcoming IPO.',
            metrics: [
              { label: 'Scoring Dimensions', value: '6' },
              { label: 'Coverage', value: 'Global' },
            ],
          },
          {
            tab: 'crypto-airdrops' as Tab,
            icon: Coins,
            badge: 'Airdrop Radar',
            title: 'Crypto Airdrop Tracker',
            description: 'Eligibility guides, estimated values, farming strategies, and AI conviction scores for active and upcoming airdrops.',
            metrics: [
              { label: 'Chains', value: 'Multi' },
              { label: 'Est. Values', value: 'Live' },
            ],
          },
          {
            tab: 'crypto-news' as Tab,
            icon: Newspaper,
            badge: 'News Desk',
            title: 'AI-Analyzed Crypto News',
            description: 'Market-moving stories with sentiment analysis, impact scoring, and actionable trading insights from AI.',
            metrics: [
              { label: 'Sentiment', value: 'AI' },
              { label: 'Sources', value: '6+' },
            ],
          },
        ].map((feature) => (
          <button
            key={feature.tab}
            onClick={() => onNavigate(feature.tab)}
            className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 text-left hover:border-surface-500 transition-all duration-200 group"
          >
            <div className="flex items-center justify-between mb-3">
              <Badge variant="outline" size="sm">{feature.badge}</Badge>
              <feature.icon className="w-4 h-4 text-surface-600" />
            </div>
            <h3 className="text-[16px] font-semibold text-surface-white mb-1.5 tracking-tight group-hover:text-brand-light transition-colors">
              {feature.title}
            </h3>
            <p className="text-[13px] text-surface-700 leading-relaxed mb-4">
              {feature.description}
            </p>
            <div className="flex items-center gap-4 mb-3">
              {feature.metrics.map((m) => (
                <div key={m.label}>
                  <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">{m.label}</span>
                  <p className="text-[13px] font-semibold text-surface-white">{m.value}</p>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-1 text-[12px] font-medium text-surface-700 group-hover:text-brand-light transition-colors pt-3 border-t border-surface-300/40">
              Read Full Briefs
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </button>
        ))}
      </div>

      <div className="border border-surface-300/60 rounded-xl bg-surface-100">
        <div className="p-6 border-b border-surface-300/40">
          <Badge variant="outline" size="sm">Methodology</Badge>
          <h2 className="text-xl font-bold text-surface-white mt-3 tracking-tight">
            A calmer interface, stronger hierarchy, and clearer signals.
          </h2>
          <p className="text-[13px] text-surface-700 mt-1.5">
            Every analysis follows a structured pipeline from data collection to actionable insights.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-surface-300/40">
          {[
            { step: '01', title: 'Data Aggregation', desc: 'Financial filings, on-chain data, market feeds, and social signals collected in real-time.', icon: Layers },
            { step: '02', title: 'AI Processing', desc: 'Proprietary models analyze 24+ risk metrics, patterns, and market dynamics to generate scores.', icon: Brain },
            { step: '03', title: 'Signal Output', desc: 'Clear verdicts, detailed reports, and confidence-weighted recommendations you can act on.', icon: Sparkles },
          ].map((item) => (
            <div key={item.step} className="p-6">
              <div className="flex items-center gap-2.5 mb-2">
                <span className="text-[11px] font-bold text-surface-500 font-mono">{item.step}</span>
                <item.icon className="w-4 h-4 text-surface-600" />
              </div>
              <h3 className="font-semibold text-[14px] text-surface-white mb-1">{item.title}</h3>
              <p className="text-[13px] text-surface-700 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { icon: BarChart3, label: 'IPOs Analyzed', value: `${ipoStocks.length}+` },
          { icon: Shield, label: 'Risk Metrics', value: '24+' },
          { icon: Brain, label: 'AI Models', value: '25+' },
          { icon: Activity, label: 'Uptime', value: '99.9%' },
        ].map((stat) => (
          <div key={stat.label} className="bg-surface-100 border border-surface-300/60 rounded-lg p-4 text-center">
            <stat.icon className="w-4 h-4 text-surface-600 mx-auto mb-2" />
            <p className="text-lg font-bold text-surface-white">{stat.value}</p>
            <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium">{stat.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

const pageComponents: Record<string, React.ComponentType> = {
  about: AboutPage,
  contact: ContactPage,
  privacy: PrivacyPage,
  terms: TermsPage,
  cookies: CookiesPage,
};

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('home');

  const handleNavigate = (tab: Tab) => {
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderMain = () => {
    if (activeTab in pageComponents) {
      const Page = pageComponents[activeTab];
      return <Page />;
    }
    switch (activeTab) {
      case 'home': return <HeroLanding onNavigate={handleNavigate} />;
      case 'ipo': return <IPOSection />;
      case 'crypto-airdrops': return <CryptoAirdropSection />;
      case 'crypto-news': return <CryptoNewsSection />;
      default: return <HeroLanding onNavigate={handleNavigate} />;
    }
  };

  const footerLinks = [
    { id: 'about' as Tab, label: 'About' },
    { id: 'contact' as Tab, label: 'Contact' },
    { id: 'privacy' as Tab, label: 'Privacy' },
    { id: 'terms' as Tab, label: 'Terms' },
    { id: 'cookies' as Tab, label: 'Cookies' },
  ];

  return (
    <div className="min-h-screen bg-surface-0 flex flex-col">
      <Header activeTab={activeTab} onTabChange={handleNavigate} />
      {activeTab !== 'home' && <Ticker />}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex-1">
        {renderMain()}
      </main>

      <footer className="border-t border-surface-300/60 mt-8 bg-surface-50">
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
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-2">Sections</p>
              <div className="flex flex-col gap-1.5">
                <button onClick={() => handleNavigate('ipo')} className="text-[13px] text-surface-700 hover:text-surface-white transition-colors text-left">IPO Analysis</button>
                <button onClick={() => handleNavigate('crypto-airdrops')} className="text-[13px] text-surface-700 hover:text-surface-white transition-colors text-left">Airdrops</button>
                <button onClick={() => handleNavigate('crypto-news')} className="text-[13px] text-surface-700 hover:text-surface-white transition-colors text-left">News</button>
              </div>
            </div>
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-2">Pages</p>
              <div className="flex flex-col gap-1.5">
                {footerLinks.map(link => (
                  <button
                    key={link.id}
                    onClick={() => handleNavigate(link.id)}
                    className="text-[13px] text-surface-700 hover:text-surface-white transition-colors text-left"
                  >
                    {link.label}
                  </button>
                ))}
              </div>
            </div>
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

      <CookieConsent />
    </div>
  );
}


