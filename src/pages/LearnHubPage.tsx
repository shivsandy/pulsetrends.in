import { Link } from 'react-router-dom';
import { BookOpen, TrendingUp, Coins, Newspaper, ArrowRight, FileText } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { SITE } from '../seo/config';
import { TOPIC_CONFIGS } from './topics/topicsConfig';

const guides = [
  {
    category: 'Crypto Basics',
    icon: Coins,
    items: [
      { slug: 'what-is-cryptocurrency', title: 'What is Cryptocurrency?', desc: 'Complete beginner\'s guide to digital assets, blockchain, and crypto investing.', level: 'Beginner' },
      { slug: 'what-is-bitcoin', title: 'What is Bitcoin (BTC)?', desc: 'Comprehensive guide to the world\'s first cryptocurrency and digital gold.', level: 'Beginner' },
      { slug: 'what-is-ethereum', title: 'What is Ethereum (ETH)?', desc: 'Guide to smart contracts, DeFi, dApps, and the Ethereum ecosystem.', level: 'Beginner' },
    ],
  },
  {
    category: 'IPO & Stock Market',
    icon: TrendingUp,
    items: [
      { slug: 'what-is-ipo', title: 'What is an IPO?', desc: 'Complete guide to Initial Public Offerings, IPO process, and investing.', level: 'Beginner' },
    ],
  },
  {
    category: 'How-To Guides',
    icon: BookOpen,
    items: [
      { slug: 'how-to-buy-cryptocurrency-in-india', title: 'How to Buy Crypto in India', desc: 'Step-by-step guide to buying Bitcoin and crypto on Indian exchanges.', level: 'Beginner' },
      { slug: 'how-to-apply-for-ipo', title: 'How to Apply for an IPO', desc: 'Step-by-step guide to applying for IPOs through ASBA and UPI.', level: 'Beginner' },
    ],
  },
];

export default function LearnHubPage() {
  return (
    <>
      <PageSeo
        meta={{
          path: '/learn',
          title: `Learn — Crypto, IPO & Stock Market Guides | ${SITE.name}`,
          description: `Educational guides and tutorials on cryptocurrency, IPO investing, stock markets, and financial literacy. Learn at ${SITE.name}.`,
          keywords: 'crypto guides, IPO guides, learn crypto, learn investing, financial education, beginner guides',
          ogType: 'website',
        }}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Learn', path: '/learn' },
        ]}
      />

      <div className="max-w-4xl mx-auto animate-fade-in">
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Learn' }]} />

        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-brand-muted border border-brand-border text-[11px] font-semibold text-brand-light uppercase tracking-wider">Educational Hub</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-surface-white tracking-tight mt-2">
          Learn Crypto, IPO & Stock Market Investing
        </h1>
        <p className="text-[15px] text-surface-700 mt-3 max-w-2xl leading-relaxed">
          Educational guides and tutorials designed for Indian investors. From cryptocurrency basics to IPO investing — learn at your own pace.
        </p>

        <div className="mt-8 space-y-8">
          {guides.map((group) => (
            <section key={group.category}>
              <h2 className="text-lg font-bold text-surface-white mb-4 flex items-center gap-2">
                <group.icon className="w-4 h-4 text-brand-light" />
                {group.category}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {group.items.map((item) => {
                  const config = TOPIC_CONFIGS[item.slug];
                  return (
                    <Link
                      key={item.slug}
                      to={`/learn/${item.slug}`}
                      className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 hover:border-surface-500 transition-all duration-200 group block"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <span className="px-2 py-0.5 rounded bg-surface-200 border border-surface-300/40 text-[10px] font-medium text-surface-600 uppercase tracking-wider">
                          {item.level}
                        </span>
                        <ArrowRight className="w-4 h-4 text-surface-600 group-hover:text-brand-light transition-colors" />
                      </div>
                      <h3 className="text-[15px] font-semibold text-surface-white group-hover:text-brand-light transition-colors">
                        {item.title}
                      </h3>
                      <p className="text-[12px] text-surface-700 mt-1 leading-relaxed">{item.desc}</p>
                      {config && (
                        <div className="flex items-center gap-2 mt-3 text-[11px] text-surface-600">
                          <FileText className="w-3 h-3" />
                          <span>{config.sections.length} sections</span>
                          <span>·</span>
                          <span>{config.faqs.length} FAQs</span>
                        </div>
                      )}
                    </Link>
                  );
                })}
              </div>
            </section>
          ))}
        </div>

        <div className="bg-surface-100 border border-surface-300/60 rounded-xl p-6 mt-8">
          <h2 className="text-lg font-bold text-surface-white mb-2">More Learning Resources</h2>
          <p className="text-[13px] text-surface-700 mb-4">
            Dive deeper with our analysis tools and real-time market data.
          </p>
          <div className="flex flex-wrap gap-2">
            <Link to="/ipo-analysis" className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-surface-200 border border-surface-300/60 text-[12px] font-medium text-surface-700 hover:text-surface-white transition-colors">
              <TrendingUp className="w-3.5 h-3.5" /> 1,094+ IPO Analyses
            </Link>
            <Link to="/airdrops" className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-surface-200 border border-surface-300/60 text-[12px] font-medium text-surface-700 hover:text-surface-white transition-colors">
              <Coins className="w-3.5 h-3.5" /> 38 Airdrop Opportunities
            </Link>
            <Link to="/news" className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-surface-200 border border-surface-300/60 text-[12px] font-medium text-surface-700 hover:text-surface-white transition-colors">
              <Newspaper className="w-3.5 h-3.5" /> 21+ Market News Articles
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
