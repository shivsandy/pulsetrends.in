import { useState, useEffect } from 'react';
import type { LucideIcon } from 'lucide-react';
import { Search, SlidersHorizontal, Newspaper, TrendingUp, TrendingDown, Minus, Brain, ChevronDown, Clock, Zap, ExternalLink, RefreshCw, Lightbulb, AlertTriangle, Target, BarChart3, Quote, ListChecks, ArrowLeft, CalendarDays } from 'lucide-react';
import Badge from './Badge';
import { newsArticles } from '../data/newsData';

interface FinancialMetrics {
  tableCaption: string;
  headers: string[];
  rows: string[][];
}

interface AiAnalysis {
  bullCase: string;
  bearCase: string;
  neutralCase: string;
  probabilityWeightedOutlook: string;
  potentialCatalysts: string[];
  keyRisks: string[];
}

interface ArticleImage {
  url: string;
  alt: string;
  attribution: string;
  title?: string;
  caption?: string;
  category?: string;
  sourceUrl?: string;
  source?: string;
  photoId?: string;
}

interface NewsArticle {
  id: string;
  headline: string;
  subheadline: string;
  keyHighlights: string[];
  executiveSummary: string;
  marketBackground: string;
  detailedAnalysis: string;
  financialMetrics: FinancialMetrics | null;
  expertInsights: string;
  risks: string[];
  opportunities: string[];
  outlook: string;
  conclusion: string;
  sourcesReferenced: string[];
  aiAnalysis: AiAnalysis | null;
  images: ArticleImage[];
  ipoDetails?: {
    companyOverview?: string;
    ipoSize?: string;
    valuation?: string;
    offerPrice?: string;
    subscriptionStatus?: string;
    greyMarketPremium?: string;
  };
  cryptoDetails?: {
    tokenOverview?: string;
    marketCap?: string;
    tradingVolume?: string;
    priceMovement?: string;
  };
  category: string;
  sentiment: string;
  impact: string;
  relatedCoins: string[];
  relatedStocks: string[];
  primaryKeyword: string;
  secondaryKeywords: string[];
  metaDescription: string;
  publishedAt: string;
}

const FALLBACK_NEWS: NewsArticle[] = [
  {
    id: 'fallback-1',
    headline: 'Bitcoin Surges Past $70K as Institutional Demand Accelerates',
    subheadline: 'Record ETF inflows and favorable macro conditions drive BTC to new highs above $70,000.',
    keyHighlights: ['Bitcoin breaks $70K for first time in 2026', 'Spot BTC ETFs report $2B+ weekly inflows', 'Pension funds and sovereign wealth funds accumulating', 'Options market sees increased $80K strike hedging'],
    executiveSummary: 'Bitcoin has surged past the $70,000 mark driven by accelerating institutional adoption and favorable macroeconomic conditions. Spot Bitcoin ETFs are seeing record inflows of over $2 billion weekly.',
    marketBackground: 'The cryptocurrency market has been consolidating since the start of 2026, with Bitcoin trading in a $55K-$65K range before this breakout.',
    detailedAnalysis: 'Multiple catalysts converged to drive this breakout. Institutional adoption continues to accelerate with pension funds and sovereign wealth funds allocating to Bitcoin ETFs approved in major jurisdictions.',
    financialMetrics: { tableCaption: 'Bitcoin Key Metrics', headers: ['Metric', 'Value', 'Change'], rows: [['Price', '$70,284', '+12.5%'], ['Market Cap', '$1.38T', '+12.3%'], ['24h Volume', '$52.8B', '+45%'], ['Open Interest', '$28.5B', '+18%']] },
    expertInsights: 'The Options market now shows increased hedging activity at the $80,000 strike price, suggesting traders anticipate further upside according to market analysts.',
    risks: ['Regulatory crackdown in major economies', 'Macroeconomic headwinds from inflation', 'Potential profit-taking at resistance levels'],
    opportunities: ['Continued institutional adoption', 'Global regulatory clarity improving', 'Growing use cases in DeFi and payments'],
    outlook: 'Analysts project Bitcoin could test $80K-$100K by year-end if institutional inflows continue at current pace.',
    conclusion: 'Bitcoin\'s breakout above $70K represents a significant milestone, driven by genuine institutional demand rather than retail speculation.',
    sourcesReferenced: ['Yahoo Finance - Bitcoin Markets', 'CoinDesk - Institutional Crypto Report'],
    aiAnalysis: {
      bullCase: 'Continued institutional adoption drives sustained demand. Pension funds and sovereign wealth funds represent a massive untapped market.',
      bearCase: 'Profit-taking at resistance levels could trigger a correction. Regulatory uncertainty in some jurisdictions remains a risk.',
      neutralCase: 'Bitcoin may consolidate in a $65K-$80K range as the market digests recent gains.',
      probabilityWeightedOutlook: '60% probability of continued uptrend toward $80K, 25% consolidation, 15% correction',
      potentialCatalysts: ['More sovereign wealth fund allocations', 'Fed rate decisions', 'Global regulatory frameworks'],
      keyRisks: ['Regulatory reversal', 'Macroeconomic downturn', 'Security incidents'],
    },
    images: [{ url: '', alt: '', attribution: '' }],
    category: 'crypto', sentiment: 'bullish', impact: 'high',
    relatedCoins: ['BTC'], relatedStocks: [],
    primaryKeyword: 'Bitcoin price $70K', secondaryKeywords: ['BTC rally', 'Bitcoin ETF inflows'],
    metaDescription: 'Bitcoin breaks $70K as institutional demand accelerates with record ETF inflows and favorable macro conditions.',
    publishedAt: new Date().toISOString(),
  },
  {
    id: 'fallback-2',
    headline: 'Ethereum Layer 2 Activity Hits All-Time High as Gas Fees Drop 90%',
    subheadline: 'Dencun upgrade drives L2 transactions past 15M daily with fees below $0.01.',
    keyHighlights: ['Ethereum L2 daily transactions surpass 15 million', 'Dencun upgrade reduces fees by 90%', 'Arbitrum leads with 40% market share', 'New use cases emerging in microtransactions and gaming'],
    executiveSummary: 'Ethereum Layer 2 networks have reached a new milestone, processing more transactions than ever before as users flock to scaling solutions.',
    marketBackground: 'Ethereum has faced scalability challenges since its inception, with high gas fees during peak usage periods.',
    detailedAnalysis: 'Total L2 transactions surpassed 15 million per day, representing over 80% of all Ethereum ecosystem activity. The Dencun upgrade has been instrumental.',
    financialMetrics: { tableCaption: 'L2 Network Comparison', headers: ['Network', 'Market Share', 'Avg Fee'], rows: [['Arbitrum', '40%', '<$0.01'], ['Base', '25%', '<$0.01'], ['Optimism', '20%', '<$0.01'], ['zkSync', '10%', '<$0.02']] },
    expertInsights: 'Industry experts suggest L2s will ultimately handle the vast majority of transactions, with L1 reserved for settlement.',
    risks: ['L2 fragmentation across different standards', 'Centralization concerns in sequencer design'],
    opportunities: ['Institutional adoption through L2 rails', 'New DeFi and gaming primitives unlocked by low fees'],
    outlook: 'L2 activity expected to continue growing as more applications migrate.',
    conclusion: 'The Dencun upgrade has proven transformative for Ethereum, enabling a new wave of applications.',
    sourcesReferenced: ['CoinDesk - L2 Report', 'L2Beat - Network Data'],
    aiAnalysis: {
      bullCase: 'L2s unlock new application categories impossible at high fee levels, driving exponential transaction growth.',
      bearCase: 'L2 fragmentation and liquidity dispersion could limit network effects.',
      neutralCase: 'Ethereum ecosystem continues scaling steadily with L2s handling increasing transaction volume.',
      probabilityWeightedOutlook: '75% continued growth, 15% consolidation, 10% disruption from competing L1s',
      potentialCatalysts: ['Major enterprise adoption on L2s', 'Cross-L2 interoperability solutions'],
      keyRisks: ['Competition from alternative L1s', 'L2 security vulnerabilities'],
    },
    images: [{ url: '', alt: '', attribution: '' }],
    category: 'crypto', sentiment: 'bullish', impact: 'medium',
    relatedCoins: ['ETH', 'ARB', 'OP'], relatedStocks: [],
    primaryKeyword: 'Ethereum L2 scaling', secondaryKeywords: ['Layer 2 transactions', 'Dencun upgrade'],
    metaDescription: 'Ethereum L2 activity hits all-time high with 15M daily transactions as Dencun upgrade drives fees below $0.01.',
    publishedAt: new Date().toISOString(),
  },
  {
    id: 'fallback-3',
    headline: 'SEC Approves First Spot Ethereum ETF, Market Reacts Positively',
    subheadline: 'Watershed approval signals shifting regulatory landscape, unlocking institutional capital.',
    keyHighlights: ['SEC approves landmark spot Ethereum ETF', 'ETH rallies 15% on news', 'Estimates suggest $5-10B first-year inflows', 'Multiple issuers expected to launch competing products'],
    executiveSummary: 'The US SEC has approved the first spot Ethereum ETF, marking a watershed moment for the cryptocurrency industry.',
    marketBackground: 'The approval follows months of deliberation and signals a shifting regulatory landscape.',
    detailedAnalysis: 'Industry experts expect this to unlock significant institutional capital, with estimates suggesting inflows could reach $5-10B in the first year.',
    financialMetrics: { tableCaption: 'Spot ETF Market Potential', headers: ['Metric', 'Estimate'], rows: [['Year 1 Inflows', '$5-10B'], ['Fee Range', '0.15-0.50%'], ['AUM Year 3', '$25-50B']] },
    expertInsights: 'Multiple issuers are expected to launch competing products, driving fee compression and increased accessibility.',
    risks: ['Lower-than-expected demand', 'Regulatory challenges in other jurisdictions'],
    opportunities: ['Billion-dollar institutional capital unlocked', 'ETH price appreciation from demand'],
    outlook: 'Long-term bullish for Ethereum as institutional barriers fall.',
    conclusion: 'The approval represents regulatory validation of Ethereum as a legitimate asset class.',
    sourcesReferenced: ['SEC Official Release', 'Bloomberg - ETF Analysis'],
    aiAnalysis: {
      bullCase: 'Institutional capital floodgates open, driving sustained ETH demand and price appreciation similar to BTC ETF impact.',
      bearCase: 'GBTC-style outflows could offset new inflows initially, creating selling pressure.',
      neutralCase: 'Gradual accumulation by institutions over 12-18 months as allocations are approved.',
      probabilityWeightedOutlook: '65% bullish momentum, 20% neutral consolidation, 15% sell-the-news',
      potentialCatalysts: ['Staking yield inclusion in ETFs', 'Global peer jurisdictions following SEC lead'],
      keyRisks: ['Macroeconomic downturn reducing risk appetite', 'Concentration risk'],
    },
    images: [{ url: '', alt: '', attribution: '' }],
    category: 'crypto', sentiment: 'bullish', impact: 'high',
    relatedCoins: ['ETH'], relatedStocks: [],
    primaryKeyword: 'Ethereum ETF approval', secondaryKeywords: ['SEC spot ETH ETF', 'Ethereum institutional adoption'],
    metaDescription: 'SEC approves first spot Ethereum ETF, unlocking institutional capital and driving 15% ETH price rally.',
    publishedAt: new Date().toISOString(),
  },
];

type AiTab = 'bull' | 'bear' | 'neutral';
type CategoryFilter = 'all' | 'crypto' | 'ipo' | 'stocks' | 'india';

const NEWS_API_BASE = import.meta.env.VITE_NEWS_API_URL ||
  (import.meta.env.DEV ? 'http://localhost:5000' : '');

const CATEGORY_FILTERS: { id: CategoryFilter; label: string }[] = [
  { id: 'all', label: 'Top Stories' },
  { id: 'crypto', label: 'Crypto' },
  { id: 'ipo', label: 'IPO' },
  { id: 'stocks', label: 'Stocks' },
  { id: 'india', label: 'India' },
];

const FALLBACK_IMAGES: Record<string, ArticleImage[]> = {
  crypto: [
    {
      url: 'https://images.unsplash.com/photo-1640161704729-cbe966a08476?auto=format&fit=crop&w=1400&q=80',
      alt: 'Bitcoin and cryptocurrency market data on digital trading screens',
      title: 'Bitcoin and cryptocurrency market data',
      caption: 'Cryptocurrency market data on digital trading screens',
      attribution: 'Photo by Avi Waxman on Unsplash',
      category: 'crypto',
    },
    {
      url: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=1400&q=80',
      alt: 'Bitcoin and Ethereum physical coins with blockchain visualization',
      title: 'Bitcoin Ethereum physical coins',
      caption: 'Bitcoin and Ethereum physical coins',
      attribution: 'Photo by Dmitry Demidko on Unsplash',
      category: 'crypto',
    },
    {
      url: 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&w=1400&q=80',
      alt: 'Ethereum cryptocurrency coin close-up with golden lighting',
      title: 'Ethereum cryptocurrency coin',
      caption: 'Ethereum cryptocurrency coin',
      attribution: 'Photo on Unsplash',
      category: 'crypto',
    },
    {
      url: 'https://images.unsplash.com/photo-1518544801976-3e159e50e5bb?auto=format&fit=crop&w=1400&q=80',
      alt: 'DeFi and decentralized finance blockchain network visualization',
      title: 'DeFi blockchain network',
      caption: 'DeFi blockchain network visualization',
      attribution: 'Photo on Unsplash',
      category: 'crypto',
    },
  ],
  ipo: [
    {
      url: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?auto=format&fit=crop&w=1400&q=80',
      alt: 'IPO prospectus and financial documents on a desk',
      title: 'IPO prospectus and financial documents',
      caption: 'IPO prospectus and financial documents',
      attribution: 'Photo on Unsplash',
      category: 'ipo',
    },
    {
      url: 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1400&q=80',
      alt: 'Stock market trading floor with screens and analyst workstations',
      title: 'Stock market trading floor',
      caption: 'Stock market trading floor',
      attribution: 'Photo on Unsplash',
      category: 'ipo',
    },
    {
      url: 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1400&q=80',
      alt: 'Initial public offering bell ringing ceremony on the trading floor',
      title: 'IPO bell ringing ceremony',
      caption: 'IPO bell ringing ceremony',
      attribution: 'Photo on Unsplash',
      category: 'ipo',
    },
  ],
  india: [
    {
      url: 'https://images.unsplash.com/photo-1605651531144-51381895e23d?auto=format&fit=crop&w=1400&q=80',
      alt: 'Mumbai cityscape with financial district skyline',
      title: 'Mumbai financial district skyline',
      caption: 'Mumbai financial district skyline',
      attribution: 'Photo by Photo by Sudipta Mondal on Unsplash',
      category: 'india',
    },
    {
      url: 'https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?auto=format&fit=crop&w=1400&q=80',
      alt: 'Bombay Stock Exchange building exterior in Dalal Street, Mumbai',
      title: 'Bombay Stock Exchange Dalal Street',
      caption: 'BSE Dalal Street, Mumbai',
      attribution: 'Photo on Unsplash',
      category: 'india',
    },
    {
      url: 'https://images.unsplash.com/photo-1568871391916-72e64a36a93d?auto=format&fit=crop&w=1400&q=80',
      alt: 'Indian rupee currency notes and financial documents',
      title: 'Indian rupee currency notes',
      caption: 'Indian rupee currency notes',
      attribution: 'Photo on Unsplash',
      category: 'india',
    },
    {
      url: 'https://images.unsplash.com/photo-1604594849809-dfedbc827105?auto=format&fit=crop&w=1400&q=80',
      alt: 'Indian stock market trading display with Sensex and Nifty tickers',
      title: 'Sensex and Nifty market display',
      caption: 'Sensex and Nifty market display',
      attribution: 'Photo on Unsplash',
      category: 'india',
    },
  ],
  stocks: [
    {
      url: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1400&q=80',
      alt: 'Stock market trading charts on a multi-screen trading desk',
      title: 'Stock market trading charts',
      caption: 'Stock market trading charts',
      attribution: 'Photo on Unsplash',
      category: 'stocks',
    },
    {
      url: 'https://images.unsplash.com/photo-1543286386-713bdd548da4?auto=format&fit=crop&w=1400&q=80',
      alt: 'Bull and bear market trend charts for global equity investing',
      title: 'Bull and bear market trend charts',
      caption: 'Bull and bear market trend charts',
      attribution: 'Photo on Unsplash',
      category: 'stocks',
    },
    {
      url: 'https://images.unsplash.com/photo-1559523182-a284c3fb7cff?auto=format&fit=crop&w=1400&q=80',
      alt: 'Wall Street financial district skyscrapers in lower Manhattan',
      title: 'Wall Street financial district',
      caption: 'Wall Street financial district',
      attribution: 'Photo on Unsplash',
      category: 'stocks',
    },
  ],
};

const KEYWORD_FALLBACK_HINTS: Array<{ match: RegExp; category: keyof typeof FALLBACK_IMAGES }> = [
  { match: /\b(bitcoin|btc)\b/i, category: 'crypto' },
  { match: /\b(ethereum|eth|ether)\b/i, category: 'crypto' },
  { match: /\b(defi|decentralized|blockchain|altcoin|web3|stablecoin|nft)\b/i, category: 'crypto' },
  { match: /\b(nifty|sensex|nse|bse|mumbai|indian|rupee|rbi|sebi)\b/i, category: 'india' },
  { match: /\b(ipo|listing|drhp|prospectus|grey market|gmp|anchor investor|book building)\b/i, category: 'ipo' },
  { match: /\b(nasdaq|s&p|dow|jones|wall street|earnings|dividend|equity)\b/i, category: 'stocks' },
];

function detectImageCategory(article: NewsArticle): keyof typeof FALLBACK_IMAGES {
  const text = `${article.headline} ${article.subheadline || ''} ${article.primaryKeyword || ''} ${(article.category || '')}`.toLowerCase();
  for (const hint of KEYWORD_FALLBACK_HINTS) {
    if (hint.match.test(text)) return hint.category;
  }
  const cat = (article.category || '').toLowerCase();
  if (cat.includes('crypto')) return 'crypto';
  if (cat.includes('ipo')) return 'ipo';
  if (cat.includes('india')) return 'india';
  return 'stocks';
}

function fallbackImageFor(article: NewsArticle, index: number = 0): ArticleImage {
  const category = detectImageCategory(article);
  const set = FALLBACK_IMAGES[category] || FALLBACK_IMAGES.stocks;
  const pick = set[Math.abs(index) % set.length];
  const keyword = (article.primaryKeyword || article.headline || '').trim();
  return {
    ...pick,
    alt: pick.alt + (keyword ? ` - ${keyword}` : ''),
    title: keyword ? `${pick.title} - ${keyword}` : pick.title,
  };
}

function getHeroImage(article: NewsArticle, index: number = 0): ArticleImage {
  const image = article.images?.find((img) => img.url);
  if (image) return image;
  return fallbackImageFor(article, index);
}

function getReadingTime(article: NewsArticle) {
  const text = [
    article.executiveSummary,
    article.marketBackground,
    article.detailedAnalysis,
    article.expertInsights,
    article.outlook,
    article.conclusion,
  ].join(' ');
  return Math.max(3, Math.ceil(text.split(/\s+/).filter(Boolean).length / 220));
}

function ArticleReader({
  article,
  relatedArticles,
  aiTab,
  onAiTabChange,
  onBack,
  onSelectArticle,
}: {
  article: NewsArticle;
  relatedArticles: NewsArticle[];
  aiTab: AiTab;
  onAiTabChange: (tab: AiTab) => void;
  onBack: () => void;
  onSelectArticle: (article: NewsArticle) => void;
}) {
  const heroImage = getHeroImage(article);
  const ai = article.aiAnalysis;
  const financialMetrics = article.financialMetrics;

  return (
    <article className="animate-fade-in">
      <button
        onClick={onBack}
        className="mb-4 inline-flex items-center gap-2 text-[13px] text-surface-700 hover:text-surface-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to news
      </button>

      <div className="overflow-hidden rounded-xl border border-surface-300/60 bg-surface-100">
        <div className="relative h-72 sm:h-[420px] overflow-hidden">
          <img src={heroImage.url} alt={heroImage.alt || article.headline} className="h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-surface-100 via-surface-100/30 to-transparent" />
          {heroImage.attribution && (
            <span className="absolute bottom-3 right-3 rounded bg-surface-100/85 px-2 py-0.5 text-[10px] text-surface-700">
              {heroImage.attribution}
            </span>
          )}
        </div>

        <div className="px-5 pb-7 pt-5 sm:px-8">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <Badge variant="default" size="sm">{article.category || 'markets'}</Badge>
            <Badge variant={article.impact === 'high' ? 'danger' : article.impact === 'medium' ? 'warning' : 'info'} size="sm">
              {article.impact || 'medium'} impact
            </Badge>
            <span className="inline-flex items-center gap-1 text-[12px] text-surface-600">
              <CalendarDays className="h-3.5 w-3.5" />
              {article.publishedAt ? new Date(article.publishedAt).toLocaleDateString() : 'Latest'}
            </span>
            <span className="text-[12px] text-surface-600">{getReadingTime(article)} min read</span>
          </div>

          <h1 className="max-w-4xl text-3xl font-bold leading-tight tracking-tight text-surface-white sm:text-[42px]">
            {article.headline}
          </h1>
          {article.subheadline && (
            <p className="mt-3 max-w-3xl text-[16px] leading-relaxed text-surface-700">
              {article.subheadline}
            </p>
          )}

          {(article.relatedCoins?.length > 0 || article.relatedStocks?.length > 0) && (
            <div className="mt-4 flex flex-wrap items-center gap-1.5">
              <span className="mr-1 text-[11px] uppercase tracking-wider text-surface-600">Related</span>
              {[...(article.relatedCoins || []), ...(article.relatedStocks || [])].map((item) => (
                <span key={item} className="rounded border border-surface-300/60 bg-surface-200 px-2 py-0.5 font-mono text-[11px] text-surface-800">
                  {item}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div className="space-y-6">
          {article.keyHighlights?.length > 0 && (
            <section className="rounded-lg border border-surface-300/50 bg-surface-100 p-5">
              <h2 className="mb-3 text-[15px] font-bold text-surface-white">Key Takeaways</h2>
              <div className="grid gap-2 sm:grid-cols-2">
                {article.keyHighlights.slice(0, 6).map((item, index) => (
                  <div key={index} className="flex items-start gap-2 rounded-md bg-surface-200/45 p-3">
                    <ListChecks className="mt-0.5 h-4 w-4 shrink-0 text-brand-light" />
                    <p className="text-[13px] leading-relaxed text-surface-800">{item}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="space-y-5 rounded-lg border border-surface-300/50 bg-surface-100 p-5 sm:p-6">
            {article.executiveSummary && (
              <div>
                <h2 className="mb-2 text-xl font-bold text-surface-white">Summary</h2>
                <p className="text-[15px] leading-8 text-surface-800">{article.executiveSummary}</p>
              </div>
            )}
            {article.marketBackground && (
              <div>
                <h2 className="mb-2 text-xl font-bold text-surface-white">Market Context</h2>
                <p className="text-[15px] leading-8 text-surface-800">{article.marketBackground}</p>
              </div>
            )}
            {article.detailedAnalysis && (
              <div>
                <h2 className="mb-2 text-xl font-bold text-surface-white">Analysis</h2>
                <p className="text-[15px] leading-8 text-surface-800">{article.detailedAnalysis}</p>
              </div>
            )}
            {article.expertInsights && (
              <div className="rounded-lg border-l-3 border-brand bg-surface-200/35 p-4">
                <Quote className="mb-2 h-4 w-4 text-brand-light" />
                <p className="text-[14px] italic leading-7 text-surface-800">{article.expertInsights}</p>
              </div>
            )}
          </section>

          {financialMetrics && financialMetrics.headers.length > 0 && (
            <section className="rounded-lg border border-surface-300/50 bg-surface-100 p-5">
              <h2 className="mb-3 flex items-center gap-2 text-xl font-bold text-surface-white">
                <BarChart3 className="h-5 w-5 text-brand-light" />
                {financialMetrics.tableCaption || 'Market Metrics'}
              </h2>
              <div className="overflow-x-auto rounded-lg border border-surface-300/40">
                <table className="w-full text-[13px]">
                  <thead>
                    <tr className="bg-surface-200/70">
                      {financialMetrics.headers.map((header) => (
                        <th key={header} className="border-b border-surface-300/40 px-3 py-2 text-left font-semibold text-surface-900">{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {financialMetrics.rows.map((row, rowIndex) => (
                      <tr key={rowIndex} className="border-b border-surface-300/20 last:border-0">
                        {row.map((cell, cellIndex) => (
                          <td key={cellIndex} className="px-3 py-2 text-surface-800">{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <section className="grid gap-4 sm:grid-cols-2">
            {article.risks?.length > 0 && (
              <div className="rounded-lg border border-danger-border/40 bg-danger-muted/30 p-4">
                <h2 className="mb-2 flex items-center gap-2 text-[15px] font-bold text-danger">
                  <AlertTriangle className="h-4 w-4" />
                  Risks
                </h2>
                <ul className="space-y-2">
                  {article.risks.map((risk, index) => (
                    <li key={index} className="text-[13px] leading-relaxed text-surface-800">{risk}</li>
                  ))}
                </ul>
              </div>
            )}
            {article.opportunities?.length > 0 && (
              <div className="rounded-lg border border-success-border/40 bg-success-muted/30 p-4">
                <h2 className="mb-2 flex items-center gap-2 text-[15px] font-bold text-success">
                  <Lightbulb className="h-4 w-4" />
                  Opportunities
                </h2>
                <ul className="space-y-2">
                  {article.opportunities.map((item, index) => (
                    <li key={index} className="text-[13px] leading-relaxed text-surface-800">{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          {ai && (
            <section className="rounded-lg border border-surface-300/50 bg-surface-100 p-5">
              <h2 className="mb-3 flex items-center gap-2 text-xl font-bold text-surface-white">
                <Target className="h-5 w-5 text-brand-light" />
                Investment Lens
              </h2>
              <div className="mb-3 flex gap-1">
                {(['bull', 'bear', 'neutral'] as AiTab[]).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => onAiTabChange(tab)}
                    className={`rounded-md px-3 py-1.5 text-[12px] font-medium capitalize transition-all ${
                      aiTab === tab
                        ? tab === 'bull' ? 'bg-success text-white' : tab === 'bear' ? 'bg-danger text-white' : 'bg-surface-400 text-white'
                        : 'bg-surface-200 text-surface-600 hover:text-surface-800'
                    }`}
                  >
                    {tab === 'bull' ? 'Bull Case' : tab === 'bear' ? 'Bear Case' : 'Neutral'}
                  </button>
                ))}
              </div>
              <p className="text-[14px] leading-7 text-surface-800">
                {aiTab === 'bull' ? ai.bullCase : aiTab === 'bear' ? ai.bearCase : ai.neutralCase}
              </p>
              {ai.probabilityWeightedOutlook && (
                <p className="mt-3 border-t border-surface-300/40 pt-3 text-[13px] text-surface-700">
                  <span className="font-semibold text-surface-900">Outlook:</span> {ai.probabilityWeightedOutlook}
                </p>
              )}
            </section>
          )}

          {(article.outlook || article.conclusion) && (
            <section className="rounded-lg border border-surface-300/50 bg-surface-100 p-5">
              {article.outlook && <p className="mb-4 text-[15px] leading-8 text-surface-800">{article.outlook}</p>}
              {article.conclusion && <p className="text-[15px] leading-8 text-surface-800">{article.conclusion}</p>}
            </section>
          )}

          {article.sourcesReferenced?.length > 0 && (
            <section className="border-t border-surface-300/50 pt-4">
              <h2 className="mb-2 text-[13px] font-semibold uppercase tracking-wider text-surface-600">Sources Referenced</h2>
              <ul className="space-y-1">
                {article.sourcesReferenced.map((source, index) => (
                  <li key={index} className="flex items-start gap-1.5 text-[12px] text-surface-600">
                    <ExternalLink className="mt-0.5 h-3 w-3 shrink-0" />
                    {source}
                  </li>
                ))}
              </ul>
              <p className="mt-4 text-[11px] italic leading-relaxed text-surface-500">
                This PulseTrends story is AI-assisted and based on cited source material. It is informational content, not financial advice.
              </p>
            </section>
          )}
        </div>

        <aside className="space-y-3">
          <h2 className="text-[13px] font-semibold uppercase tracking-wider text-surface-600">More Stories</h2>
          {relatedArticles.slice(0, 4).map((item) => {
            const image = getHeroImage(item);
            return (
              <button
                key={item.id}
                onClick={() => onSelectArticle(item)}
                className="group flex w-full gap-3 rounded-lg border border-surface-300/50 bg-surface-100 p-2 text-left transition-colors hover:border-surface-500"
              >
                <img src={image.url} alt={image.alt || item.headline} className="h-16 w-20 shrink-0 rounded-md object-cover" loading="lazy" />
                <div>
                  <p className="text-[11px] uppercase tracking-wider text-surface-600">{item.category || 'markets'}</p>
                  <p className="line-clamp-3 text-[12px] font-semibold leading-snug text-surface-900 group-hover:text-brand-light">{item.headline}</p>
                </div>
              </button>
            );
          })}
        </aside>
      </div>
    </article>
  );
}

export default function CryptoNewsSection() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('all');
  const [sentimentFilter, setSentimentFilter] = useState<string>('all');
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);
  const [aiTab, setAiTab] = useState<AiTab>('bull');

  const fetchNews = async () => {
    try {
      setLoading(true);
      setError('');
      if (NEWS_API_BASE) {
        const resp = await fetch(`${NEWS_API_BASE}/api/news`);
        if (resp.ok) {
          const data = await resp.json();
          if (data && data.length > 0) {
            setArticles(data);
            return;
          }
        }
      }
      if (newsArticles.length > 0) {
        setArticles(newsArticles);
        return;
      }
      setArticles(FALLBACK_NEWS);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load news');
      setArticles(newsArticles.length > 0 ? newsArticles : FALLBACK_NEWS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchNews(); }, []);

  const filteredNews = articles.filter((news) => {
    const q = searchQuery.toLowerCase();
    const searchableText = [
      news.headline,
      news.subheadline,
      news.category,
      news.primaryKeyword,
      ...(news.secondaryKeywords || []),
      ...(news.relatedCoins || []),
      ...(news.relatedStocks || []),
    ].join(' ').toLowerCase();
    const matchesSearch = news.headline.toLowerCase().includes(q) ||
      searchableText.includes(q) ||
      (news.category || '').toLowerCase().includes(q) ||
      (news.relatedCoins || []).some(c => c.toLowerCase().includes(q)) ||
      (news.relatedStocks || []).some(s => s.toLowerCase().includes(q));
    const matchesCategory = categoryFilter === 'all' ||
      (categoryFilter === 'india'
        ? /india|indian|nse|bse|nifty|sensex|rbi|gmp/.test(searchableText)
        : (news.category || '').toLowerCase() === categoryFilter || searchableText.includes(categoryFilter));
    const matchesSentiment = sentimentFilter === 'all' || news.sentiment === sentimentFilter;
    return matchesSearch && matchesCategory && matchesSentiment;
  });

  const sentimentConfig: Record<string, { icon: LucideIcon; variant: 'success' | 'danger' | 'outline'; label: string }> = {
    bullish: { icon: TrendingUp, variant: 'success', label: 'Bullish' },
    bearish: { icon: TrendingDown, variant: 'danger', label: 'Bearish' },
    neutral: { icon: Minus, variant: 'outline', label: 'Neutral' },
  };

  const impactConfig: Record<string, 'danger' | 'warning' | 'info'> = {
    high: 'danger',
    medium: 'warning',
    low: 'info',
  };

  if (selectedArticle) {
    return (
      <ArticleReader
        article={selectedArticle}
        relatedArticles={articles.filter((article) => article.id !== selectedArticle.id)}
        aiTab={aiTab}
        onAiTabChange={setAiTab}
        onBack={() => setSelectedArticle(null)}
        onSelectArticle={(article) => {
          setSelectedArticle(article);
          setAiTab('bull');
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-surface-300/60 pb-6">
        <Badge variant="default" size="md">News Intelligence</Badge>
        <h2 className="text-2xl font-bold text-surface-white mt-3 tracking-tight">
          Crypto, IPO & Stock Market News
        </h2>
        <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">
          Premium market coverage for crypto, IPOs, Indian equities, and global stocks with
          AI-assisted analysis, source attribution, and investor-focused context.
        </p>
        <div className="flex items-center gap-5 mt-4">
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">Live</span> Feed</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">AI</span> Powered</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Newspaper className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">{articles.length}</span> Stories</span>
          </div>
          <button
            onClick={() => { fetchNews(); setAiTab('bull'); }}
            disabled={loading}
            className="ml-auto flex items-center gap-1 text-[12px] text-surface-600 hover:text-surface-white transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-600" />
          <input
            type="text"
            placeholder="Search crypto, IPOs, stocks, Nifty, Sensex..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-200 border border-surface-300 rounded-lg text-[13px] text-surface-white placeholder-surface-600 focus:outline-none focus:border-surface-500 transition-colors"
          />
        </div>
        <div className="flex items-center gap-1.5">
          <SlidersHorizontal className="w-3.5 h-3.5 text-surface-600 mr-1" />
          {['all', 'bullish', 'bearish', 'neutral'].map((s) => (
            <button key={s} onClick={() => setSentimentFilter(s)}
              className={`px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all ${sentimentFilter === s ? 'bg-surface-300 text-surface-white' : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'}`}>
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {CATEGORY_FILTERS.map((filter) => (
          <button
            key={filter.id}
            onClick={() => setCategoryFilter(filter.id)}
            className={`shrink-0 px-3 py-1.5 rounded-md text-[12px] font-medium transition-all ${
              categoryFilter === filter.id
                ? 'bg-brand-muted text-brand-light border border-brand-border'
                : 'bg-surface-100 border border-surface-300/50 text-surface-700 hover:text-surface-white hover:border-surface-500'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {loading && articles.length === 0 && (
        <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
          <RefreshCw className="w-6 h-6 text-surface-600 mx-auto mb-3 animate-spin" />
          <p className="text-surface-600 text-[14px]">Loading news...</p>
        </div>
      )}

      {error && articles.length === 0 && (
        <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
          <p className="text-surface-600 text-[14px]">Unable to connect to news API</p>
          <p className="text-surface-500 text-[12px] mt-1">Make sure the news API server is running on port 5000</p>
          <button onClick={() => { fetchNews(); setAiTab('bull'); }} className="mt-3 px-4 py-1.5 rounded-md text-[12px] font-medium text-white bg-brand hover:bg-brand-light transition-colors">Retry</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredNews.map((news, i) => {
          const sentiment = sentimentConfig[news.sentiment] || sentimentConfig.neutral;
          const SentimentIcon = sentiment.icon;
          const isExpanded = false;
          const ai = news.aiAnalysis;
          const heroImage = getHeroImage(news, i);
          const sectionImages = news.images?.slice(1) || [];

          return (
            <div key={news.id} className={`bg-surface-100 border border-surface-300/60 rounded-xl overflow-hidden hover:border-surface-500 transition-all duration-200 animate-fade-in ${
              i === 0 ? 'lg:col-span-2' : ''
            }`}
              style={{ animationDelay: `${i * 60}ms` }}>

              {heroImage?.url && (
                <div className="relative w-full h-56 sm:h-72 overflow-hidden">
                  <img src={heroImage.url} alt={heroImage.alt || news.headline} className="w-full h-full object-cover" loading="lazy" />
                  <div className="absolute inset-0 bg-gradient-to-t from-surface-100 via-surface-100/10 to-transparent" />
                  {heroImage.attribution && (
                    <span className="absolute bottom-2 right-3 text-[10px] text-surface-700 bg-surface-100/80 px-2 py-0.5 rounded">{heroImage.attribution}</span>
                  )}
                </div>
              )}

              <div className="p-5">
                <div className="flex flex-wrap items-center gap-1.5 mb-2.5">
                  <Badge variant={sentiment.variant} size="sm"><SentimentIcon className="w-3 h-3" />{sentiment.label}</Badge>
                  <Badge variant={impactConfig[news.impact] || 'info'} size="sm">{news.impact || 'medium'} impact</Badge>
                  <span className="text-[11px] text-surface-600 font-medium ml-1">{news.category}</span>
                  {news.publishedAt && <span className="text-[11px] text-surface-500">{new Date(news.publishedAt).toLocaleDateString()}</span>}
                </div>

                <h2 className={`font-bold text-surface-white leading-snug mb-1.5 ${i === 0 ? 'text-[22px]' : 'text-[17px]'}`}>{news.headline}</h2>
                {news.subheadline && <p className="text-[13px] text-surface-700 mb-3 leading-relaxed">{news.subheadline}</p>}

                {news.keyHighlights && news.keyHighlights.length > 0 && (
                  <div className="grid grid-cols-2 gap-2 mb-4">
                    {news.keyHighlights.slice(0, 4).map((h, hi) => (
                      <div key={hi} className="flex items-start gap-2 bg-surface-200/40 border border-surface-300/30 rounded-lg px-3 py-2">
                        <ListChecks className="w-3.5 h-3.5 text-brand-light mt-0.5 shrink-0" />
                        <span className="text-[12px] text-surface-800 leading-snug">{h}</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] text-surface-600 mr-1">Related</span>
                    {(news.relatedCoins || []).map((c) => (
                      <span key={c} className="text-[11px] px-1.5 py-0.5 rounded bg-surface-200 text-surface-800 font-mono border border-surface-300/40">{c}</span>
                    ))}
                    {(news.relatedStocks || []).map((s) => (
                      <span key={s} className="text-[11px] px-1.5 py-0.5 rounded bg-surface-200 text-surface-800 font-mono border border-surface-300/40">{s}</span>
                    ))}
                  </div>
                  <button onClick={() => { setSelectedArticle(news); setAiTab('bull'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                    className="flex items-center gap-1.5 text-[12px] text-surface-700 hover:text-brand-light transition-colors font-medium">
                    <Brain className="w-3.5 h-3.5" />
                    Read Full Article
                    <ChevronDown className="w-3 h-3" />
                  </button>
                </div>
              </div>

              {isExpanded && (
                <div className="px-5 pb-6 animate-fade-in space-y-5">
                  {/* Executive Summary */}
                  {news.executiveSummary && (
                    <div className="bg-surface-200/40 border border-surface-300/40 rounded-lg p-4">
                      <h4 className="text-[14px] font-bold text-surface-white mb-2">Executive Summary</h4>
                      <p className="text-[13px] text-surface-800 leading-relaxed">{news.executiveSummary}</p>
                    </div>
                  )}

                  {/* Market Background */}
                  {news.marketBackground && (
                    <div>
                      <h4 className="text-[14px] font-bold text-surface-white mb-2">Market Background</h4>
                      <p className="text-[13px] text-surface-800 leading-relaxed">{news.marketBackground}</p>
                    </div>
                  )}

                  {/* Detailed Analysis */}
                  {news.detailedAnalysis && (
                    <div>
                      <h4 className="text-[14px] font-bold text-surface-white mb-2">Detailed Analysis</h4>
                      <p className="text-[13px] text-surface-800 leading-relaxed">{news.detailedAnalysis}</p>
                    </div>
                  )}

                  {/* Inline images */}
                  {sectionImages.map((img, si) => img.url && (
                    <div key={si} className="rounded-lg overflow-hidden">
                      <img src={img.url} alt={img.alt || ''} className="w-full h-48 object-cover rounded-lg" loading="lazy" />
                      {img.attribution && <p className="text-[10px] text-surface-600 mt-1">{img.attribution}</p>}
                    </div>
                  ))}

                  {/* IPO Details */}
                  {news.ipoDetails && (
                    <div className="bg-surface-200/30 border border-surface-300/40 rounded-lg p-4">
                      <h4 className="text-[14px] font-bold text-surface-white mb-3">IPO Details</h4>
                      <div className="grid grid-cols-2 gap-3 text-[12px]">
                        {news.ipoDetails.companyOverview && <div className="col-span-2"><span className="text-surface-600 font-medium">Company:</span> <span className="text-surface-800">{news.ipoDetails.companyOverview}</span></div>}
                        {news.ipoDetails.ipoSize && <div><span className="text-surface-600 font-medium">IPO Size:</span> <span className="text-surface-800">{news.ipoDetails.ipoSize}</span></div>}
                        {news.ipoDetails.valuation && <div><span className="text-surface-600 font-medium">Valuation:</span> <span className="text-surface-800">{news.ipoDetails.valuation}</span></div>}
                        {news.ipoDetails.offerPrice && <div><span className="text-surface-600 font-medium">Offer Price:</span> <span className="text-surface-800">{news.ipoDetails.offerPrice}</span></div>}
                        {news.ipoDetails.subscriptionStatus && <div><span className="text-surface-600 font-medium">Subscription:</span> <span className="text-surface-800">{news.ipoDetails.subscriptionStatus}</span></div>}
                        {news.ipoDetails.greyMarketPremium && <div><span className="text-surface-600 font-medium">GMP:</span> <span className="text-surface-800">{news.ipoDetails.greyMarketPremium}</span></div>}
                      </div>
                    </div>
                  )}

                  {/* Crypto Details */}
                  {news.cryptoDetails && (
                    <div className="bg-surface-200/30 border border-surface-300/40 rounded-lg p-4">
                      <h4 className="text-[14px] font-bold text-surface-white mb-3">Crypto Analysis</h4>
                      <div className="grid grid-cols-2 gap-3 text-[12px]">
                        {news.cryptoDetails.tokenOverview && <div className="col-span-2"><span className="text-surface-600 font-medium">Token:</span> <span className="text-surface-800">{news.cryptoDetails.tokenOverview}</span></div>}
                        {news.cryptoDetails.marketCap && <div><span className="text-surface-600 font-medium">Market Cap:</span> <span className="text-surface-800">{news.cryptoDetails.marketCap}</span></div>}
                        {news.cryptoDetails.tradingVolume && <div><span className="text-surface-600 font-medium">Volume:</span> <span className="text-surface-800">{news.cryptoDetails.tradingVolume}</span></div>}
                        {news.cryptoDetails.priceMovement && <div className="col-span-2"><span className="text-surface-600 font-medium">Price Movement:</span> <span className="text-surface-800">{news.cryptoDetails.priceMovement}</span></div>}
                      </div>
                    </div>
                  )}

                  {/* Financial Metrics Table */}
                  {news.financialMetrics && news.financialMetrics.headers && news.financialMetrics.headers.length > 0 && (
                    <div>
                      <h4 className="text-[14px] font-bold text-surface-white mb-2">
                        <BarChart3 className="w-4 h-4 inline mr-1.5 text-brand-light" />
                        {news.financialMetrics.tableCaption || 'Financial Metrics'}
                      </h4>
                      <div className="overflow-x-auto rounded-lg border border-surface-300/40">
                        <table className="w-full text-[12px]">
                          <thead>
                            <tr className="bg-surface-200/70">
                              {news.financialMetrics.headers.map((h, hi) => (
                                <th key={hi} className="text-left px-3 py-2 font-semibold text-surface-900 border-b border-surface-300/40">{h}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {news.financialMetrics.rows.map((row, ri) => (
                              <tr key={ri} className="border-b border-surface-300/20 last:border-0 hover:bg-surface-200/30">
                                {row.map((cell, ci) => (
                                  <td key={ci} className="px-3 py-2 text-surface-800">{cell}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Expert Insights */}
                  {news.expertInsights && (
                    <div className="bg-surface-200/30 border-l-3 border-brand rounded-lg p-4">
                      <div className="flex items-start gap-2">
                        <Quote className="w-4 h-4 text-brand-light mt-0.5 shrink-0" />
                        <p className="text-[13px] text-surface-800 italic leading-relaxed">{news.expertInsights}</p>
                      </div>
                    </div>
                  )}

                  {/* Risks & Opportunities */}
                  <div className="grid grid-cols-2 gap-4">
                    {news.risks && news.risks.length > 0 && (
                      <div className="bg-danger-muted/30 border border-danger-border/40 rounded-lg p-4">
                        <h4 className="text-[13px] font-bold text-danger mb-2 flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5" /> Risks
                        </h4>
                        <ul className="space-y-1">
                          {news.risks.map((r, ri) => (
                            <li key={ri} className="text-[12px] text-surface-800 flex items-start gap-1.5">
                              <span className="text-danger mt-0.5">•</span> {r}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {news.opportunities && news.opportunities.length > 0 && (
                      <div className="bg-success-muted/30 border border-success-border/40 rounded-lg p-4">
                        <h4 className="text-[13px] font-bold text-success mb-2 flex items-center gap-1.5">
                          <Lightbulb className="w-3.5 h-3.5" /> Opportunities
                        </h4>
                        <ul className="space-y-1">
                          {news.opportunities.map((o, oi) => (
                            <li key={oi} className="text-[12px] text-surface-800 flex items-start gap-1.5">
                              <span className="text-success mt-0.5">•</span> {o}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* AI Analysis */}
                  {ai && (
                    <div className="bg-surface-200/50 border border-surface-300/40 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <Brain className="w-4 h-4 text-brand-light" />
                        <h4 className="text-[14px] font-bold text-surface-white">AI Analysis</h4>
                      </div>
                      <div className="flex gap-1 mb-3">
                        {(['bull', 'bear', 'neutral'] as AiTab[]).map((tab) => (
                          <button key={tab} onClick={() => setAiTab(tab)}
                            className={`px-3 py-1.5 rounded-md text-[12px] font-medium transition-all capitalize ${
                              aiTab === tab
                                ? tab === 'bull' ? 'bg-success text-white' : tab === 'bear' ? 'bg-danger text-white' : 'bg-surface-400 text-white'
                                : 'bg-surface-200 text-surface-600 hover:text-surface-800'
                            }`}>
                            {tab === 'bull' ? 'Bull Case' : tab === 'bear' ? 'Bear Case' : 'Neutral'}
                          </button>
                        ))}
                      </div>
                      <p className="text-[13px] text-surface-800 leading-relaxed">
                        {aiTab === 'bull' ? ai.bullCase : aiTab === 'bear' ? ai.bearCase : ai.neutralCase}
                      </p>
                      {aiTab === 'bull' && ai.potentialCatalysts.length > 0 && (
                        <div className="mt-3">
                          <span className="text-[12px] font-semibold text-surface-900 mb-1 block">Potential Catalysts:</span>
                          <div className="flex flex-wrap gap-1">
                            {ai.potentialCatalysts.map((c, ci) => (
                              <span key={ci} className="text-[10px] px-1.5 py-0.5 rounded bg-success-muted border border-success-border text-success">{c}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {aiTab === 'bear' && ai.keyRisks.length > 0 && (
                        <div className="mt-3">
                          <span className="text-[12px] font-semibold text-surface-900 mb-1 block">Key Risks:</span>
                          <div className="flex flex-wrap gap-1">
                            {ai.keyRisks.map((r, ri) => (
                              <span key={ri} className="text-[10px] px-1.5 py-0.5 rounded bg-danger-muted border border-danger-border text-danger">{r}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {ai.probabilityWeightedOutlook && (
                        <div className="mt-3 pt-3 border-t border-surface-300/30">
                          <div className="flex items-center gap-1.5">
                            <Target className="w-3.5 h-3.5 text-brand-light" />
                            <span className="text-[12px] font-semibold text-surface-900">Probability-Weighted Outlook:</span>
                            <span className="text-[12px] text-surface-800">{ai.probabilityWeightedOutlook}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Outlook & Conclusion */}
                  {news.outlook && (
                    <div>
                      <h4 className="text-[14px] font-bold text-surface-white mb-2">Outlook</h4>
                      <p className="text-[13px] text-surface-800 leading-relaxed">{news.outlook}</p>
                    </div>
                  )}
                  {news.conclusion && (
                    <div className="bg-surface-200/30 border border-surface-300/40 rounded-lg p-4">
                      <h4 className="text-[13px] font-bold text-surface-white mb-1.5">Conclusion</h4>
                      <p className="text-[13px] text-surface-800 leading-relaxed">{news.conclusion}</p>
                    </div>
                  )}

                  {/* Sources */}
                  {news.sourcesReferenced && news.sourcesReferenced.length > 0 && (
                    <div className="border-t border-surface-300/30 pt-3">
                      <h4 className="text-[12px] font-semibold text-surface-600 mb-1.5">Sources Referenced</h4>
                      <ul className="space-y-0.5">
                        {news.sourcesReferenced.map((src, si) => (
                          <li key={si} className="text-[11px] text-surface-600 flex items-start gap-1">
                            <ExternalLink className="w-3 h-3 mt-0.5 shrink-0" />
                            {src}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <p className="text-[10px] text-surface-500 italic">This article was AI-generated based on scraped source material. Facts are sourced from referenced publications. Analysis and opinions are AI-generated and should not be considered financial advice.</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {!loading && filteredNews.length === 0 && (
        <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
          <Newspaper className="w-10 h-10 text-surface-500 mx-auto mb-3" />
          <p className="text-surface-600 text-[14px]">No news articles match your criteria</p>
          <p className="text-surface-500 text-[12px] mt-1">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
}
