import { useState, useEffect } from 'react';
import { Search, SlidersHorizontal, Newspaper, TrendingUp, TrendingDown, Minus, Brain, ChevronDown, ChevronUp, Clock, Zap, ExternalLink, RefreshCw } from 'lucide-react';
import Badge from './Badge';

interface NewsArticle {
  id: string;
  title: string;
  content: string;
  summary: string;
  category: string;
  sentiment: string;
  impact: string;
  relatedCoins: string[];
  relatedStocks: string[];
  image: string;
  imageAlt: string;
  imageAttribution: string;
  metaDescription: string;
  publishedAt: string;
}

export default function CryptoNewsSection() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState<string>('all');
  const [expandedNews, setExpandedNews] = useState<string | null>(null);

  const fetchNews = async () => {
    try {
      setLoading(true);
      setError('');
      const resp = await fetch('http://localhost:5000/api/news');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setArticles(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load news');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchNews(); }, []);

  const filteredNews = articles.filter((news) => {
    const matchesSearch = news.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (news.category || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (news.relatedCoins || []).some(c => c.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesSentiment = sentimentFilter === 'all' || news.sentiment === sentimentFilter;
    return matchesSearch && matchesSentiment;
  });

  const sentimentConfig: Record<string, { icon: any; variant: 'success' | 'danger' | 'outline'; label: string }> = {
    bullish: { icon: TrendingUp, variant: 'success', label: 'Bullish' },
    bearish: { icon: TrendingDown, variant: 'danger', label: 'Bearish' },
    neutral: { icon: Minus, variant: 'outline', label: 'Neutral' },
  };

  const impactConfig: Record<string, 'danger' | 'warning' | 'info'> = {
    high: 'danger',
    medium: 'warning',
    low: 'info',
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-surface-300/60 pb-6">
        <Badge variant="default" size="md">News Intelligence</Badge>
        <h2 className="text-2xl font-bold text-surface-white mt-3 tracking-tight">
          Crypto News & AI Analysis
        </h2>
        <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">
          Stay ahead with AI-analyzed crypto news. Every story includes sentiment analysis,
          impact assessment, and actionable market insights.
        </p>
        <div className="flex items-center gap-5 mt-4">
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">Live</span> Feed</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">AI</span> Generated</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Newspaper className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">{articles.length}</span> Stories</span>
          </div>
          <button
            onClick={fetchNews}
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
            placeholder="Search by title, category, or coin..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-200 border border-surface-300 rounded-lg text-[13px] text-surface-white placeholder-surface-600 focus:outline-none focus:border-surface-500 transition-colors"
          />
        </div>
        <div className="flex items-center gap-1.5">
          <SlidersHorizontal className="w-3.5 h-3.5 text-surface-600 mr-1" />
          {['all', 'bullish', 'bearish', 'neutral'].map((sentiment) => (
            <button
              key={sentiment}
              onClick={() => setSentimentFilter(sentiment)}
              className={`px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all ${
                sentimentFilter === sentiment
                  ? 'bg-surface-300 text-surface-white'
                  : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'
              }`}
            >
              {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {loading && articles.length === 0 && (
        <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
          <RefreshCw className="w-6 h-6 text-surface-600 mx-auto mb-3 animate-spin" />
          <p className="text-surface-600 text-[14px]">Generating AI news articles...</p>
          <p className="text-surface-500 text-[12px] mt-1">This may take a few minutes on first start</p>
        </div>
      )}

      {error && articles.length === 0 && (
        <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
          <p className="text-surface-600 text-[14px]">Unable to connect to news API</p>
          <p className="text-surface-500 text-[12px] mt-1">Make sure the news API server is running on port 5000</p>
          <button onClick={fetchNews} className="mt-3 px-4 py-1.5 rounded-md text-[12px] font-medium text-white bg-brand hover:bg-brand-light transition-colors">
            Retry
          </button>
        </div>
      )}

      {!loading && !error && articles.length === 0 && (
        <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
          <p className="text-surface-600 text-[14px]">No news articles available yet</p>
          <p className="text-surface-500 text-[12px] mt-1">Articles will be generated automatically</p>
        </div>
      )}

      <div className="space-y-3">
        {filteredNews.map((news, i) => {
          const sentiment = sentimentConfig[news.sentiment] || sentimentConfig.neutral;
          const SentimentIcon = sentiment.icon;
          const isExpanded = expandedNews === news.id;

          return (
            <div
              key={news.id}
              className="bg-surface-100 border border-surface-300/60 rounded-xl overflow-hidden hover:border-surface-500 transition-all duration-200 animate-fade-in"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="p-5">
                <div className="flex flex-wrap items-center gap-1.5 mb-2.5">
                  <Badge variant={sentiment.variant} size="sm">
                    <SentimentIcon className="w-3 h-3" />
                    {sentiment.label}
                  </Badge>
                  <Badge variant={impactConfig[news.impact] || 'info'} size="sm">
                    {news.impact || 'medium'} impact
                  </Badge>
                  <span className="text-[11px] text-surface-600 font-medium ml-1">{news.category}</span>
                  {news.publishedAt && <span className="text-[11px] text-surface-500">{new Date(news.publishedAt).toLocaleDateString()}</span>}
                </div>

                <h3 className="font-semibold text-surface-white text-[15px] leading-snug mb-2">{news.title}</h3>

                <p className="text-[13px] text-surface-700 mb-3 leading-relaxed">{news.metaDescription || news.content?.slice(0, 200)}</p>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] text-surface-600 mr-1">Related</span>
                    {(news.relatedCoins || []).map((coin) => (
                      <span key={coin} className="text-[11px] px-1.5 py-0.5 rounded bg-surface-200 text-surface-800 font-mono border border-surface-300/40">
                        {coin}
                      </span>
                    ))}
                    {(news.relatedStocks || []).map((stock) => (
                      <span key={stock} className="text-[11px] px-1.5 py-0.5 rounded bg-surface-200 text-surface-800 font-mono border border-surface-300/40">
                        {stock}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={() => setExpandedNews(isExpanded ? null : news.id)}
                    className="flex items-center gap-1.5 text-[12px] text-surface-700 hover:text-brand-light transition-colors font-medium"
                  >
                    <Brain className="w-3.5 h-3.5" />
                    {isExpanded ? 'Hide Article' : 'Read Full Article'}
                    {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>
                </div>

                {news.image && (
                  <div className="mt-3 text-[11px] text-surface-600">
                    <img src={news.image} alt={news.imageAlt || news.title} className="w-full h-48 object-cover rounded-lg" loading="lazy" />
                    <p className="mt-1">{news.imageAttribution}</p>
                  </div>
                )}
              </div>

              {isExpanded && (
                <div className="px-5 pb-5 animate-fade-in">
                  <div className="bg-surface-200/50 border border-surface-300 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2.5">
                      <Brain className="w-4 h-4 text-brand-light" />
                      <h4 className="font-semibold text-[13px] text-surface-white">Full AI-Generated Article</h4>
                    </div>
                    <div className="prose prose-invert max-w-none text-[13px] text-surface-800 leading-relaxed space-y-3"
                      dangerouslySetInnerHTML={{ __html: renderMarkdown(news.content || '') }}
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function renderMarkdown(text: string): string {
  let html = text
    .replace(/^### (.*$)/gm, '<h3 class="text-[15px] font-semibold text-surface-white mt-4 mb-2">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="text-[17px] font-bold text-surface-white mt-5 mb-2">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-[19px] font-bold text-surface-white mt-5 mb-2">$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^- (.*$)/gm, '<li class="text-[13px] text-surface-800 ml-4 list-disc">$1</li>')
    .replace(/\n\n/g, '</p><p class="text-[13px] text-surface-800 leading-relaxed">')
    .replace(/\n/g, '<br/>');
  html = '<p class="text-[13px] text-surface-800 leading-relaxed">' + html + '</p>';
  return html;
}
