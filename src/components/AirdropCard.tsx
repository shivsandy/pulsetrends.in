import { Clock, Gift, Shield, AlertTriangle, Brain, Link, Hexagon, Layers, Gem, ArrowRight } from 'lucide-react';
import type { CryptoAirdrop } from '../data/cryptoData';
import ScoreRing from './ScoreRing';
import Badge from './Badge';

interface AirdropCardProps {
  airdrop: CryptoAirdrop;
  onClick: () => void;
}

const categoryIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'Infrastructure': Link,
  'Layer 1': Hexagon,
  'Layer 1 / DeFi': Hexagon,
  'Layer 2': Layers,
  'DeFi / Perps': Gem,
};

export default function AirdropCard({ airdrop, onClick }: AirdropCardProps) {
  const statusVariant = airdrop.status === 'active' ? 'success' : airdrop.status === 'upcoming' ? 'warning' : 'outline';
  const riskVariant = airdrop.riskLevel === 'Low' ? 'success' : airdrop.riskLevel === 'Medium' ? 'warning' : 'danger';
  const CategoryIcon = categoryIcons[airdrop.category] || Hexagon;

  return (
    <div
      onClick={onClick}
      className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 cursor-pointer hover:border-surface-500 transition-all duration-200 group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center">
            <CategoryIcon className="w-5 h-5 text-surface-700" />
          </div>
          <div>
            <h3 className="font-semibold text-surface-white text-[15px] leading-tight group-hover:text-brand-light transition-colors">{airdrop.name}</h3>
            <p className="text-[12px] text-surface-600 mt-0.5 font-mono">{airdrop.ticker} / {airdrop.chain}</p>
          </div>
        </div>
        <Badge variant={statusVariant} size="sm">{airdrop.status}</Badge>
      </div>

      <p className="text-[13px] text-surface-700 mb-4 line-clamp-2 leading-relaxed">{airdrop.description}</p>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
        <div className="bg-surface-50 border border-surface-300/40 rounded-md px-3 py-2.5">
          <div className="flex items-center gap-1 mb-1">
            <Gift className="w-3 h-3 text-surface-600" />
            <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Est. Value</span>
          </div>
          <p className="text-[13px] font-semibold text-success">{airdrop.airdropSnapshot.estimatedValue}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-md px-3 py-2.5">
          <div className="flex items-center gap-1 mb-1">
            <Clock className="w-3 h-3 text-surface-600" />
            <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Snapshot</span>
          </div>
          <p className="text-[13px] font-semibold text-surface-white">{airdrop.airdropSnapshot.snapshotDate}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-md px-3 py-2.5">
          <div className="flex items-center gap-1 mb-1">
            {airdrop.riskLevel === 'Low' ? (
              <Shield className="w-3 h-3 text-surface-600" />
            ) : (
              <AlertTriangle className="w-3 h-3 text-surface-600" />
            )}
            <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Risk</span>
          </div>
          <Badge variant={riskVariant} size="sm">{airdrop.riskLevel}</Badge>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-md px-3 py-2.5">
          <div className="flex items-center gap-1 mb-1">
            <Brain className="w-3 h-3 text-surface-600" />
            <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">AI Score</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ScoreRing score={airdrop.aiScores.overall} size={24} strokeWidth={2.5} showLabel={false} />
            <span className="text-[13px] font-semibold text-surface-white">{airdrop.aiScores.overall}/100</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3.5 border-t border-surface-300/40">
        <div className="flex flex-wrap gap-1.5">
          <Badge variant="info" size="sm">{airdrop.airdropType}</Badge>
          <Badge variant="outline" size="sm">{airdrop.airdropSnapshot.totalAllocation}</Badge>
        </div>
        <span className="flex items-center gap-1 text-[12px] text-surface-700 group-hover:text-brand-light transition-colors font-medium">
          Full Analysis
          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
        </span>
      </div>
    </div>
  );
}
