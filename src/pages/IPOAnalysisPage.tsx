import { useState } from 'react';
import { Search, SlidersHorizontal, TrendingUp, BarChart3 } from 'lucide-react';
import { ipoStocks } from '../data/ipoData';
import type { IPOStock } from '../data/ipoData';
import IPOCard from '../components/IPOCard';
import Badge from '../components/Badge';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';
import { slugify } from '../seo/config';

function makeSlug(s: IPOStock): string {
  return `${slugify(s.company)}-${s.id}`;
}

export default function IPOAnalysisPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredStocks = ipoStocks.filter((stock) => {
    const matchesSearch = stock.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      stock.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
      stock.sector.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || stock.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <>
      <PageSeo
        meta={ROUTES.ipoAnalysis}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'IPO Analysis', path: '/ipo-analysis' },
        ]}
      />
      <div className="space-y-6">
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'IPO Analysis' }]} />
        <div className="border-b border-surface-300/60 pb-6">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="default" size="md">IPO Intelligence</Badge>
          </div>
          <h1 className="text-2xl font-bold text-surface-white mt-3 tracking-tight">
            Upcoming IPO Analysis
          </h1>
          <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">
            AI-powered analysis of upcoming IPOs with company overviews, financial snapshots,
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
              onChange={(e) => setSearchQuery(e.target.value)}
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
                onClick={() => setStatusFilter(status)}
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
          {filteredStocks.map((stock, i) => (
            <div key={stock.id} className="animate-fade-in" style={{ animationDelay: `${i * 60}ms` }}>
              <IPOCard stock={stock} slug={makeSlug(stock)} />
            </div>
          ))}
        </div>

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

