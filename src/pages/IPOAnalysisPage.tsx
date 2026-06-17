import { useState, useMemo } from 'react';
import { Search, SlidersHorizontal, TrendingUp, BarChart3, ChevronLeft, ChevronRight } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { ipoStocks } from '../data/ipoData';
import type { IPOStock } from '../data/ipoData';
import IPOCard from '../components/IPOCard';
import Badge from '../components/Badge';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';
import { slugify } from '../seo/config';

const POSTS_PER_PAGE = 20;

function makeSlug(s: IPOStock): string {
  return `${slugify(s.company)}-${s.id}`;
}

function Pagination({
  currentPage,
  totalPages,
  onPageChange,
}: {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}) {
  if (totalPages <= 1) return null;

  const getPageNumbers = () => {
    const pages: (number | 'ellipsis')[] = [];
    const siblings = 1;
    const start = Math.max(2, currentPage - siblings);
    const end = Math.min(totalPages - 1, currentPage + siblings);
    pages.push(1);
    if (start > 2) pages.push('ellipsis');
    for (let i = start; i <= end; i++) pages.push(i);
    if (end < totalPages - 1) pages.push('ellipsis');
    if (totalPages > 1) pages.push(totalPages);
    return pages;
  };

  const pageNumbers = getPageNumbers();

  return (
    <nav className="flex items-center justify-center gap-1.5 pt-4" aria-label="IPO pagination">
      <button
        type="button"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-[12px] font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed enabled:hover:bg-surface-200 enabled:hover:text-surface-white text-surface-700 border border-surface-300/50 bg-surface-100"
        aria-label="Previous page"
      >
        <ChevronLeft className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Previous</span>
      </button>
      <div className="flex items-center gap-1">
        {pageNumbers.map((page, idx) =>
          page === 'ellipsis' ? (
            <span key={`ellipsis-${idx}`} className="px-2 py-1.5 text-[12px] text-surface-600 select-none" aria-hidden="true">...</span>
          ) : (
            <button
              key={page}
              type="button"
              onClick={() => onPageChange(page)}
              disabled={page === currentPage}
              className={`min-w-[36px] px-2.5 py-1.5 rounded-lg text-[12px] font-medium transition-all ${
                page === currentPage
                  ? 'bg-brand-muted text-brand-light border border-brand-border cursor-default'
                  : 'text-surface-700 hover:text-surface-white hover:bg-surface-200 border border-surface-300/50 bg-surface-100'
              }`}
              aria-label={`Page ${page}`}
              aria-current={page === currentPage ? 'page' : undefined}
            >
              {page}
            </button>
          )
        )}
      </div>
      <button
        type="button"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-[12px] font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed enabled:hover:bg-surface-200 enabled:hover:text-surface-white text-surface-700 border border-surface-300/50 bg-surface-100"
        aria-label="Next page"
      >
        <span className="hidden sm:inline">Next</span>
        <ChevronRight className="w-3.5 h-3.5" />
      </button>
    </nav>
  );
}

export default function IPOAnalysisPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const pageParam = searchParams.get('page');
  const parsed = pageParam ? parseInt(pageParam, 10) : 1;
  const currentPage = Number.isNaN(parsed) || parsed < 1 ? 1 : parsed;

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredStocks = useMemo(() => {
    return ipoStocks.filter((stock) => {
      const matchesSearch = stock.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
        stock.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
        stock.sector.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter === 'all' || stock.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [searchQuery, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredStocks.length / POSTS_PER_PAGE));
  const safePage = Math.min(currentPage, totalPages);
  const pageStart = (safePage - 1) * POSTS_PER_PAGE;
  const paginatedStocks = filteredStocks.slice(pageStart, pageStart + POSTS_PER_PAGE);

  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return;
    setSearchParams(page === 1 ? {} : { page: String(page) });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    handlePageChange(1);
  };

  const handleStatusChange = (status: string) => {
    setStatusFilter(status);
    handlePageChange(1);
  };

  return (
    <>
      <PageSeo
        meta={{
          ...ROUTES.ipoAnalysis,
          ...(safePage > 1
            ? {
                title: `IPO Analysis - Page ${safePage} | PulseTrends`,
                description: `IPO analysis page ${safePage} — AI-powered analysis of upcoming and recent IPOs with financial snapshots, scoring, and market data.`,
              }
            : {}),
        }}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'IPO Analysis', path: '/ipo-analysis' },
          ...(safePage > 1 ? [{ name: `Page ${safePage}`, path: `/ipo-analysis?page=${safePage}` }] : []),
        ]}
      />
      <div className="space-y-6">
        <Breadcrumbs items={[
          { name: 'Home', path: '/' },
          { name: 'IPO Analysis' },
          ...(safePage > 1 ? [{ name: `Page ${safePage}` }] : []),
        ]} />
        <div className="border-b border-surface-300/60 pb-6">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="default" size="md">IPO Intelligence</Badge>
          </div>
          <h1 className="text-2xl font-bold text-surface-white mt-3 tracking-tight">
            IPO Analysis
          </h1>
          <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">
            AI-powered analysis of upcoming and recent IPOs with company overviews, financial snapshots,
            strengths, risks, and proprietary scoring across multiple dimensions.
          </p>
          <div className="flex items-center gap-5 mt-4">
            <div className="flex items-center gap-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-surface-600" />
              <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">{ipoStocks.length}</span> IPOs Tracked</span>
            </div>
            <div className="flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-surface-600" />
              <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">Real-time</span> Scoring</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-600" />
            <input
              type="text"
              placeholder="Search by name, ticker, or sector..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full pl-9 pr-4 py-2 bg-surface-200 border border-surface-300 rounded-lg text-[13px] text-surface-white placeholder-surface-600 focus:outline-none focus:border-surface-500 transition-colors"
              aria-label="Search IPOs"
            />
          </div>
          <div className="flex items-center gap-1.5">
            <SlidersHorizontal className="w-3.5 h-3.5 text-surface-600 mr-1" />
            {['all', 'upcoming', 'open', 'subscribed', 'listed'].map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => handleStatusChange(status)}
                className={`px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all ${
                  statusFilter === status
                    ? 'bg-surface-300 text-surface-white'
                    : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'
                }`}
                aria-pressed={statusFilter === status}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {paginatedStocks.map((stock, i) => (
            <div key={stock.id} className="animate-fade-in" style={{ animationDelay: `${i * 60}ms` }}>
              <IPOCard stock={stock} slug={makeSlug(stock)} />
            </div>
          ))}
        </div>

        {filteredStocks.length > POSTS_PER_PAGE && (
          <Pagination
            currentPage={safePage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        )}

        {filteredStocks.length === 0 && (
          <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
            <p className="text-surface-600 text-[14px]">No IPOs match your criteria</p>
            <p className="text-surface-500 text-[12px] mt-1">Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </>
  );
}

