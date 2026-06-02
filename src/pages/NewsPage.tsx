import { useState } from 'react';
import { Search, SlidersHorizontal, Newspaper, TrendingUp, TrendingDown, Minus, Brain, Clock, Zap, ListChecks, CalendarDays, type LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { newsArticles, type NewsArticle } from '../data/newsData';
import Badge from '../components/Badge';
import { ROUTES } from '../seo/routes';
import { getArticleSlug } from '../components/ArticleReader';
import Breadcrumbs from '../components/Breadcrumbs';
import PageSeo from '../components/PageSeo';

const CATEGORY_FILTERS = [
  { id: 'all', label: 'Top Stories' },
  { id: 'crypto', label: 'Crypto' },
  { id: 'ipo', label: 'IPO' },
  { id: 'stocks', label: 'Stocks' },
  { id: 'india', label: 'India' },
] as const;

type CategoryFilter = typeof CATEGORY_FILTERS[number]['id'];

const sentimentConfig: Record<string, { variant: 'success' | 'danger' | 'info'; icon: LucideIcon; label: string }> = {
  bullish: { variant: 'success', icon: TrendingUp, label: 'Bullish' },
  bearish: { variant: 'danger', icon: TrendingDown, label: 'Bearish' },
  neutral: { variant: 'info', icon: Minus, label: 'Neutral' },
};

const impactConfig: Record<string, 'danger' | 'warning' | 'info'> = {
  high: 'danger',
  medium: 'warning',
  low: 'info',
};

function ArticleCard({ article, index, i }: { article: NewsArticle; index: number; i: number }) {
  const slug = getArticleSlug(article);
  const heroImage = article.images?.[0];
  const sentiment = sentimentConfig[article.sentiment] || sentimentConfig.neutral;
  const SentimentIcon = sentiment.icon;
  return (
    <Link
      to={`/news/${slug}`}
      className={`block bg-surface-100 border border-surface-300/60 rounded-xl overflow-hidden hover:border-surface-500 transition-all duration-200 animate-fade-in ${
        index === 0 ? 'lg:col-span-2' : ''
      }`}
      style={{ animationDelay: `${i * 60}ms` }}
    >
      {heroImage?.url && (
        <div className="relative w-full h-56 sm:h-72 overflow-hidden">
          <img
            src={heroImage.url}
            alt={heroImage.alt || article.headline}
            width={1400}
            height={788}
            loading={index === 0 ? 'eager' : 'lazy'}
            decoding="async"
            fetchPriority={index === 0 ? 'high' : 'auto'}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-surface-100 via-surface-100/10 to-transparent" />
          {heroImage.attribution && (
            <span className="absolute bottom-2 right-3 text-[10px] text-surface-700 bg-surface-100/80 px-2 py-0.5 rounded">
              {heroImage.attribution}
            </span>
          )}
        </div>
      )}

      <div className="p-5">
        <div className="flex flex-wrap items-center gap-1.5 mb-2.5">
          <Badge variant={sentiment.variant} size="sm">
            <SentimentIcon className="w-3 h-3" />
            {sentiment.label}
          </Badge>
          <Badge variant={impactConfig[article.impact] || 'info'} size="sm">
            {article.impact || 'medium'} impact
          </Badge>
          <span className="text-[11px] text-surface-600 font-medium ml-1">{article.category}</span>
          {article.publishedAt && (
            <span className="text-[11px] text-surface-500 inline-flex items-center gap-1">
              <CalendarDays className="w-3 h-3" />
              {new Date(article.publishedAt).toLocaleDateString()}
            </span>
          )}
        </div>

        <h2 className={`font-bold text-surface-white leading-snug mb-1.5 ${index === 0 ? 'text-[22px]' : 'text-[17px]'}`}>
          {article.headline}
        </h2>
        {article.subheadline && (
          <p className="text-[13px] text-surface-700 mb-3 leading-relaxed">{article.subheadline}</p>
        )}

        {article.keyHighlights && article.keyHighlights.length > 0 && (
          <div className="grid grid-cols-2 gap-2 mb-4">
            {article.keyHighlights.slice(0, 4).map((h, hi) => (
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
            {(article.relatedCoins || []).map((c) => (
              <span key={c} className="text-[11px] px-1.5 py-0.5 rounded bg-surface-200 text-surface-800 font-mono border border-surface-300/40">{c}</span>
            ))}
            {(article.relatedStocks || []).map((s) => (
              <span key={s} className="text-[11px] px-1.5 py-0.5 rounded bg-surface-200 text-surface-800 font-mono border border-surface-300/40">{s}</span>
            ))}
          </div>
          <span className="flex items-center gap-1.5 text-[12px] text-surface-700 group-hover:text-brand-light transition-colors font-medium">
            <Brain className="w-3.5 h-3.5" />
            Read Full Article
          </span>
        </div>
      </div>
    </Link>
  );
}

export default function NewsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('all');
  const [sentimentFilter, setSentimentFilter] = useState<string>('all');

  const articles = newsArticles;

  const filtered = articles.filter((news) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = !q || [
      news.headline,
      news.subheadline,
      news.category,
      news.primaryKeyword,
      ...(news.secondaryKeywords || []),
      ...(news.relatedCoins || []),
      ...(news.relatedStocks || []),
    ].join(' ').toLowerCase().includes(q);
    const matchesCategory = categoryFilter === 'all' || news.category === categoryFilter;
    const matchesSentiment = sentimentFilter === 'all' || news.sentiment === sentimentFilter;
    return matchesSearch && matchesCategory && matchesSentiment;
  });

  return (
    <>
      <PageSeo
        meta={ROUTES.news}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'News', path: '/news' },
        ]}
      />
      <div className="space-y-6">
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'News' }]} />
        <div className="border-b border-surface-300/60 pb-6">
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-brand-muted border border-brand-border text-[11px] font-semibold text-brand-light uppercase tracking-wider">News Intelligence</span>
          </div>
          <h1 className="text-2xl font-bold text-surface-white mt-3 tracking-tight">Crypto, IPO & Stock Market News</h1>
          <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">
            Premium market coverage for crypto, IPOs, Indian equities, and global stocks with AI-assisted analysis, source attribution, and investor-focused context.
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
              aria-label="Search news"
            />
          </div>
          <div className="flex items-center gap-1.5">
            <SlidersHorizontal className="w-3.5 h-3.5 text-surface-600 mr-1" />
            {['all', 'bullish', 'bearish', 'neutral'].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setSentimentFilter(s)}
                className={`px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all ${
                  sentimentFilter === s ? 'bg-surface-300 text-surface-white' : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'
                }`}
                aria-pressed={sentimentFilter === s}
              >
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-1.5 overflow-x-auto pb-1" role="tablist" aria-label="News categories">
          {CATEGORY_FILTERS.map((filter) => (
            <button
              key={filter.id}
              type="button"
              role="tab"
              aria-selected={categoryFilter === filter.id}
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

        {filtered.length === 0 ? (
          <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
            <p className="text-surface-600 text-[14px]">No stories match your criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filtered.map((article, i) => (
              <ArticleCard key={article.id} article={article} index={i} i={i} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
