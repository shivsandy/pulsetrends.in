import { Calendar, DollarSign, Building2, ArrowRight, Cpu, Leaf, FlaskConical, Landmark, Sprout } from 'lucide-react';
import type { IPOStock } from '../data/ipoData';
import ScoreRing from './ScoreRing';
import Badge from './Badge';

interface IPOCardProps {
  stock: IPOStock;
  onClick: () => void;
}

const sectorIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'Technology / Semiconductors': Cpu,
  'Renewable Energy': Leaf,
  'Healthcare / Biotech': FlaskConical,
  'Fintech / Digital Banking': Landmark,
  'AgriTech': Sprout,
};

export default function IPOCard({ stock, onClick }: IPOCardProps) {
  const statusVariant = stock.status === 'open' ? 'success' : stock.status === 'upcoming' ? 'warning' : 'info';
  const SectorIcon = sectorIcons[stock.sector] || Building2;

  return (
    <div
      onClick={onClick}
      className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 cursor-pointer hover:border-surface-500 transition-all duration-200 group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center">
            <SectorIcon className="w-5 h-5 text-surface-700" />
          </div>
          <div>
            <h3 className="font-semibold text-surface-white text-[15px] leading-tight group-hover:text-brand-light transition-colors">
              {stock.company}
            </h3>
            <p className="text-[12px] text-surface-600 mt-0.5 font-mono">{stock.ticker}</p>
          </div>
        </div>
        <Badge variant={statusVariant} size="sm">
          {stock.status}
        </Badge>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-2.5 mb-4">
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg px-3 py-2.5">
          <div className="flex items-center gap-1 mb-1">
            <DollarSign className="w-3 h-3 text-surface-600" />
            <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Price</span>
          </div>
          <p className="text-[13px] font-semibold text-surface-white">{stock.priceRange}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg px-3 py-2.5">
          <div className="flex items-center gap-1 mb-1">
            <Building2 className="w-3 h-3 text-surface-600" />
            <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Size</span>
          </div>
          <p className="text-[13px] font-semibold text-surface-white">{stock.issueSize}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg px-3 py-2.5">
          <div className="flex items-center gap-1 mb-1">
            <Calendar className="w-3 h-3 text-surface-600" />
            <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Date</span>
          </div>
          <p className="text-[13px] font-semibold text-surface-white">{stock.expectedDate.split(',')[0]}</p>
        </div>
      </div>

      {/* Financial Strip */}
      <div className="flex items-center gap-5 mb-4 text-[12px]">
        <div>
          <span className="text-surface-600">Growth</span>
          <p className={`font-semibold ${stock.revenueGrowth.startsWith('+') ? 'text-success' : 'text-danger'}`}>
            {stock.revenueGrowth}
          </p>
        </div>
        <div className="w-px h-5 bg-surface-300" />
        <div>
          <span className="text-surface-600">Margin</span>
          <p className={`font-semibold ${parseFloat(stock.profitMargin) > 0 ? 'text-success' : 'text-danger'}`}>
            {stock.profitMargin}
          </p>
        </div>
        <div className="w-px h-5 bg-surface-300" />
        <div>
          <span className="text-surface-600">P/E</span>
          <p className="font-semibold text-surface-900">{stock.peRatio}</p>
        </div>
      </div>

      {/* Footer: AI Score + CTA */}
      <div className="flex items-center justify-between pt-3.5 border-t border-surface-300/40">
        <div className="flex items-center gap-2.5">
          <ScoreRing score={stock.aiScores.overall} size={40} strokeWidth={3.5} showLabel={false} />
          <div>
            <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">AI Score</p>
            <p className="text-[13px] font-semibold text-surface-white">{stock.aiScores.overall}/100</p>
          </div>
        </div>
        <span className="flex items-center gap-1 text-[12px] text-surface-700 group-hover:text-brand-light transition-colors font-medium">
          View Analysis
          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
        </span>
      </div>
    </div>
  );
}
