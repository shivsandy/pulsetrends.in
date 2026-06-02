import { useState } from 'react';
import { Search, SlidersHorizontal, Coins, Gift, Sparkles, Brain, TrendingUp, TrendingDown } from 'lucide-react';
import { cryptoProjects } from '../data/cryptoData';
import type { CryptoProject } from '../data/cryptoData';
import Badge from './Badge';

export default function CryptoAirdropSection() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filtered = cryptoProjects.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.chain.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || p.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div className="border-b border-surface-300/60 pb-6">
        <Badge variant="default" size="md">Crypto Intelligence</Badge>
        <h2 className="text-2xl font-bold text-surface-white mt-3 tracking-tight">
          Crypto Projects & Airdrops
        </h2>
        <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">
          AI-powered analysis of top cryptocurrencies, DeFi protocols, and airdrop opportunities.
        </p>
        <div className="flex items-center gap-5 mt-4">
          <div className="flex items-center gap-1.5">
            <Gift className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">{cryptoProjects.filter(p => p.status === 'active').length}</span> Active</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Coins className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">{cryptoProjects.length}</span> Total Tracked</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">AI</span> Scored</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-600" />
          <input
            type="text"
            placeholder="Search by name, ticker, chain..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-surface-200 border border-surface-300 rounded-lg text-[13px] text-surface-white placeholder-surface-600 focus:outline-none focus:border-surface-500 transition-colors"
          />
        </div>
        <div className="flex items-center gap-1.5">
          <SlidersHorizontal className="w-3.5 h-3.5 text-surface-600 mr-1" />
          {['all', 'active', 'upcoming', 'ended'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all ${
                statusFilter === status
                  ? 'bg-surface-300 text-surface-white'
                  : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filtered.map((project, i) => (
          <CryptoProjectCard key={project.id} project={project} index={i} />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
          <p className="text-surface-600 text-[14px]">No projects match your criteria</p>
          <p className="text-surface-500 text-[12px] mt-1">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
}

function CryptoProjectCard({ project, index }: { project: CryptoProject; index: number }) {
  const analysis = project.aiAnalysis;
  const sentiment = analysis?.sentiment || 'neutral';
  const sentimentColor =
    sentiment === 'bullish' ? 'text-success' :
    sentiment === 'bearish' ? 'text-danger' : 'text-surface-700';

  return (
    <div className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 hover:border-surface-500 transition-all duration-200 animate-fade-in group"
      style={{ animationDelay: `${index * 80}ms` }}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center">
            <Coins className="w-5 h-5 text-surface-700" />
          </div>
          <div>
            <h3 className="font-semibold text-surface-white text-[15px] leading-tight group-hover:text-brand-light transition-colors">{project.name}</h3>
            <p className="text-[12px] text-surface-600 mt-0.5 font-mono">{project.ticker} / {project.chain}</p>
          </div>
        </div>
        <Badge variant={project.status === 'active' ? 'success' : project.status === 'upcoming' ? 'warning' : 'outline'} size="sm">{project.status}</Badge>
      </div>

      <div className="flex items-center gap-2 mb-2 text-[12px]">
        <Badge variant="info" size="sm">{project.category}</Badge>
        {project.price && <span className="text-surface-700 font-mono">{project.price}</span>}
        {project.marketCap && <span className="text-surface-600">MCap: {project.marketCap}</span>}
      </div>

      <p className="text-[13px] text-surface-700 mb-3 line-clamp-2 leading-relaxed">{project.description}</p>

      {analysis && (
        <div className="bg-surface-200/50 border border-surface-300/40 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1.5">
            <Brain className="w-3.5 h-3.5 text-brand-light" />
            <span className="text-[12px] font-semibold text-surface-900">AI Analysis</span>
            <div className="flex items-center gap-1 ml-auto">
              {sentiment === 'bullish' ? <TrendingUp className="w-3 h-3 text-success" /> :
               sentiment === 'bearish' ? <TrendingDown className="w-3 h-3 text-danger" /> : null}
              <span className={`text-[12px] font-semibold ${sentimentColor}`}>
                {analysis.convictionScore}/100
              </span>
            </div>
          </div>
          <p className="text-[12px] text-surface-700 leading-relaxed line-clamp-3">{analysis.summary}</p>
          {analysis.keyDrivers.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {analysis.keyDrivers.slice(0, 3).map((d, i) => (
                <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-success-muted border border-success-border text-success">{d.slice(0, 40)}</span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="flex items-center justify-between pt-3 mt-3 border-t border-surface-300/40">
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] text-surface-600">Vol: {project.volume24h || '—'}</span>
        </div>
        <span className="text-[12px] text-surface-700 group-hover:text-brand-light transition-colors font-medium">
          {analysis?.verdict ? `Verdict: ${analysis.verdict.slice(0, 60)}...` : 'No AI verdict'}
        </span>
      </div>
    </div>
  );
}
