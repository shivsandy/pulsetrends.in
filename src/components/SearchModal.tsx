import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, TrendingUp, Coins, Newspaper, ArrowRight } from 'lucide-react';
import Fuse from 'fuse.js';
import type { IFuseOptions } from 'fuse.js';
import { ipoStocks } from '../data/ipoData';
import { newsArticles } from '../data/newsData';
import { cryptoProjects } from '../data/cryptoData';
import { slugify } from '../seo/config';
import { trackSearch } from '../lib/analytics';

interface SearchResult {
  type: 'ipo' | 'news' | 'airdrop';
  title: string;
  description: string;
  url: string;
  metadata?: string;
}

const fuseOptions: IFuseOptions<SearchResult> = {
  keys: [
    { name: 'title', weight: 2 },
    { name: 'description', weight: 1 },
    { name: 'metadata', weight: 0.5 },
  ],
  threshold: 0.4,
  minMatchCharLength: 2,
};

function buildSearchIndex(): SearchResult[] {
  const results: SearchResult[] = [];

  for (const stock of ipoStocks) {
    const stockSlug = `${slugify(stock.company)}-${stock.id}`;
    results.push({
      type: 'ipo',
      title: `${stock.company} (${stock.ticker})`,
      description: stock.description || `${stock.company} IPO analysis`,
      url: `/ipo-analysis/${stockSlug}`,
      metadata: [stock.sector, stock.status, stock.listingExchange].filter(Boolean).join(' · '),
    });
  }

  for (const article of newsArticles) {
    const articleSlug = `${slugify(article.headline)}-${article.id}`;
    results.push({
      type: 'news',
      title: article.headline,
      description: article.subheadline || article.metaDescription || article.executiveSummary || '',
      url: `/news/${articleSlug}`,
      metadata: [article.category, article.sentiment, article.publishedAt ? new Date(article.publishedAt).toLocaleDateString() : ''].filter(Boolean).join(' · '),
    });
  }

  const airdrops = cryptoProjects.filter((p) => p.category === 'airdrop');
  for (const project of airdrops) {
    const projectSlug = `${slugify(project.name)}-${project.id}`;
    results.push({
      type: 'airdrop',
      title: `${project.name} (${project.ticker})`,
      description: project.description || `${project.name} airdrop`,
      url: `/airdrops/${projectSlug}`,
      metadata: [project.chain, project.status].filter(Boolean).join(' · '),
    });
  }

  return results;
}

export default function SearchModal({ onClose }: { onClose: () => void }) {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const fuseRef = useRef<Fuse<SearchResult> | null>(null);

  useEffect(() => {
    const index = buildSearchIndex();
    fuseRef.current = new Fuse(index, fuseOptions);
  }, []);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (!fuseRef.current || !query.trim()) {
      setResults([]);
      setSelectedIndex(-1);
      return;
    }
    const res = fuseRef.current.search(query.trim());
    setResults(res.map((r) => r.item).slice(0, 12));
    setSelectedIndex(-1);
  }, [query]);

  const handleSelect = useCallback((url: string) => {
    if (query.trim()) trackSearch(query.trim());
    onClose();
    navigate(url);
  }, [navigate, onClose, query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && selectedIndex >= 0 && results[selectedIndex]) {
      handleSelect(results[selectedIndex].url);
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  useEffect(() => {
    if (selectedIndex >= 0 && listRef.current) {
      const items = listRef.current.querySelectorAll('[data-result-index]');
      if (items[selectedIndex]) {
        items[selectedIndex].scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  const typeIcon = (type: string) => {
    switch (type) {
      case 'ipo': return <TrendingUp className="w-3.5 h-3.5 text-brand-light" />;
      case 'news': return <Newspaper className="w-3.5 h-3.5 text-info" />;
      case 'airdrop': return <Coins className="w-3.5 h-3.5 text-warning" />;
      default: return <ArrowRight className="w-3.5 h-3.5 text-surface-600" />;
    }
  };

  const typeLabel = (type: string) => {
    switch (type) {
      case 'ipo': return 'IPO';
      case 'news': return 'News';
      case 'airdrop': return 'Airdrop';
      default: return '';
    }
  };

  return (
    <div
      className="fixed inset-0 z-[70] flex items-start justify-center pt-[10vh] sm:pt-[15vh] bg-black/60 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      role="dialog"
      aria-modal="true"
      aria-label="Search IPOs, News, and Airdrops"
    >
      <div className="w-full max-w-xl mx-4 bg-surface-100 border border-surface-300/60 rounded-xl shadow-2xl overflow-hidden animate-fade-in">
        <div className="flex items-center gap-3 px-4 py-3 border-b border-surface-300/60">
          <Search className="w-4 h-4 text-surface-600 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search IPOs, news, airdrops..."
            className="flex-1 bg-transparent text-[14px] text-surface-white placeholder-surface-600 focus:outline-none"
            aria-label="Search query"
          />
          <kbd className="hidden sm:inline-flex px-1.5 py-0.5 text-[10px] font-mono text-surface-600 bg-surface-200 border border-surface-300/60 rounded">
            ESC
          </kbd>
        </div>

        {query.trim() && results.length === 0 && (
          <div className="px-4 py-10 text-center">
            <p className="text-[13px] text-surface-600">No results for &quot;{query}&quot;</p>
            <p className="text-[11px] text-surface-500 mt-1">Try a different search term</p>
          </div>
        )}

        {results.length > 0 && (
          <div ref={listRef} className="max-h-[60vh] overflow-y-auto" role="listbox">
            {results.map((result, i) => (
              <button
                key={`${result.type}-${result.url}`}
                data-result-index={i}
                role="option"
                aria-selected={selectedIndex === i}
                onClick={() => handleSelect(result.url)}
                onMouseEnter={() => setSelectedIndex(i)}
                className={`w-full flex items-start gap-3 px-4 py-3 text-left transition-colors border-b border-surface-300/30 last:border-0 ${
                  selectedIndex === i ? 'bg-surface-200' : 'hover:bg-surface-200/50'
                }`}
              >
                <div className="w-7 h-7 rounded-md bg-surface-200 border border-surface-300/60 flex items-center justify-center shrink-0 mt-0.5">
                  {typeIcon(result.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[13px] font-semibold text-surface-white truncate">
                      {result.title}
                    </span>
                    <span className="text-[10px] uppercase tracking-wider text-surface-600 font-medium shrink-0">
                      {typeLabel(result.type)}
                    </span>
                  </div>
                  <p className="text-[12px] text-surface-700 mt-0.5 line-clamp-1">{result.description}</p>
                  {result.metadata && (
                    <p className="text-[10px] text-surface-600 mt-0.5">{result.metadata}</p>
                  )}
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-surface-600 shrink-0 mt-1.5" />
              </button>
            ))}
          </div>
        )}

        <div className="px-4 py-2 border-t border-surface-300/60 flex items-center gap-4 text-[10px] text-surface-600">
          <span><kbd className="px-1 py-0.5 bg-surface-200 border border-surface-300/60 rounded font-mono">↑↓</kbd> Navigate</span>
          <span><kbd className="px-1 py-0.5 bg-surface-200 border border-surface-300/60 rounded font-mono">↵</kbd> Open</span>
          <span><kbd className="px-1 py-0.5 bg-surface-200 border border-surface-300/60 rounded font-mono">Esc</kbd> Close</span>
        </div>
      </div>
    </div>
  );
}
