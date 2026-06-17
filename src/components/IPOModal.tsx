import { useEffect, useRef } from 'react';
import { X, Building2, Calendar, Brain, AlertTriangle, CheckCircle2, Lightbulb, FileText, Cpu, Leaf, FlaskConical, Landmark, Sprout, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { IPOStock } from '../data/ipoData';
import { getDateDisplay } from '../utils/ipoDisplay';
import ScoreRing from './ScoreRing';
import Badge from './Badge';

interface IPOModalProps {
  stock: IPOStock;
  slug: string;
  onClose: () => void;
}

const sectorIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'Technology / Semiconductors': Cpu,
  'Renewable Energy': Leaf,
  'Healthcare / Biotech': FlaskConical,
  'Fintech / Digital Banking': Landmark,
  'AgriTech': Sprout,
};

function scoreColor(score: number): string {
  if (score >= 80) return '#22c55e';
  if (score >= 65) return '#eab308';
  if (score >= 50) return '#f97316';
  return '#ef4444';
}

function ScoreCard({ label, score }: { label: string; score: number }) {
  const color = scoreColor(score);
  return (
    <div className="flex items-center justify-between p-3 bg-surface-50 border border-surface-300/40 rounded-lg">
      <span className="text-[12px] text-surface-600">{label}</span>
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
        <span className="text-[15px] font-bold text-surface-white">{score}/100</span>
      </div>
    </div>
  );
}

export default function IPOModal({ stock, slug, onClose }: IPOModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);
  const SectorIcon = sectorIcons[stock.sector] || Building2;

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEsc);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === overlayRef.current) onClose();
  };

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/70 backdrop-blur-sm py-8 px-4 animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-label={`IPO details for ${stock.company}`}
    >
      <div className="relative w-full max-w-3xl bg-surface-100 border border-surface-300/60 rounded-2xl shadow-2xl animate-slide-up">
        {/* Close button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 z-10 w-8 h-8 flex items-center justify-center rounded-full bg-surface-200 border border-surface-300/60 text-surface-600 hover:text-surface-white hover:bg-surface-300 transition-all"
          aria-label="Close modal"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="p-6">
          {/* HEADER */}
          <div className="flex items-start gap-4 mb-6">
            <div className="w-14 h-14 rounded-xl bg-surface-200 border border-surface-300 flex items-center justify-center shrink-0">
              <SectorIcon className="w-7 h-7 text-surface-700" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Badge variant={stock.status === 'open' ? 'success' : stock.status === 'upcoming' ? 'warning' : 'info'} size="sm">
                  {stock.status}
                </Badge>
                <span className="text-[11px] text-surface-600 font-mono">{stock.ticker}</span>
              </div>
              <h2 className="text-xl font-bold text-surface-white leading-tight">{stock.company}</h2>
              <p className="text-[13px] text-surface-600 mt-1">{stock.sector} · {stock.listingExchange}</p>
            </div>
            <div className="flex flex-col items-center shrink-0">
              <ScoreRing score={stock.aiScores.overall} size={56} strokeWidth={4} showLabel />
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mt-1">AI Score</p>
            </div>
          </div>

          {/* QUICK INFO GRID */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Price Band</p>
              <p className="text-[14px] font-semibold text-surface-white mt-1">{stock.priceRange || 'TBA'}</p>
            </div>
            <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Lot Size</p>
              <p className="text-[14px] font-semibold text-surface-white mt-1">{stock.lotSize || 'TBA'}</p>
            </div>
            <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Issue Size</p>
              <p className="text-[14px] font-semibold text-surface-white mt-1">{stock.issueSize || 'TBA'}</p>
            </div>
            <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">
                {stock.status === 'listed' ? 'Listing' : 'Expected'} Date
              </p>
              <p className="text-[14px] font-semibold text-surface-white mt-1 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 shrink-0" /> {getDateDisplay(stock)}
              </p>
            </div>
          </div>

          {/* DESCRIPTION */}
          {stock.description && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-surface-white mb-2">Company Overview</h3>
              <p className="text-[13px] text-surface-700 leading-relaxed">{stock.description}</p>
            </div>
          )}

          {/* FINANCIAL HIGHLIGHTS */}
          {(stock.revenueGrowth || stock.profitMargin || stock.peRatio) && (
            <div className="flex items-center gap-5 mb-6 text-[12px] bg-surface-50 border border-surface-300/40 rounded-lg p-4">
              {stock.revenueGrowth && (
                <div>
                  <span className="text-surface-600">Growth</span>
                  <p className={`font-semibold ${stock.revenueGrowth.startsWith('+') ? 'text-success' : 'text-danger'}`}>
                    {stock.revenueGrowth}
                  </p>
                </div>
              )}
              {stock.profitMargin && (
                <>
                  <div className="w-px h-5 bg-surface-300" />
                  <div>
                    <span className="text-surface-600">Margin</span>
                    <p className={`font-semibold ${parseFloat(stock.profitMargin) > 0 ? 'text-success' : 'text-danger'}`}>
                      {stock.profitMargin}
                    </p>
                  </div>
                </>
              )}
              {stock.peRatio && (
                <>
                  <div className="w-px h-5 bg-surface-300" />
                  <div>
                    <span className="text-surface-600">P/E</span>
                    <p className="font-semibold text-surface-900">{stock.peRatio}</p>
                  </div>
                </>
              )}
            </div>
          )}

          {/* AI SCORES */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-surface-white mb-3 flex items-center gap-2">
              <Brain className="w-4 h-4 text-brand-light" /> AI Score Breakdown
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {Object.entries(stock.aiScores).map(([key, value]) => (
                <ScoreCard key={key} label={key.replace(/([A-Z])/g, ' $1')} score={value} />
              ))}
            </div>
          </div>

          {/* EXECUTIVE SUMMARY */}
          {stock.executiveSummary && stock.executiveSummary.length > 20 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-surface-white mb-2 flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" /> Executive Summary
              </h3>
              <div className="text-[13px] text-surface-700 leading-relaxed whitespace-pre-line bg-surface-50 border border-surface-300/40 rounded-lg p-4">
                {stock.executiveSummary}
              </div>
            </div>
          )}

          {/* VERDICT */}
          {stock.aiVerdict && stock.aiVerdict.length > 10 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-surface-white mb-2 flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-yellow-400" /> AI Verdict
              </h3>
              <div className="text-[13px] text-surface-700 leading-relaxed bg-surface-50 border border-surface-300/40 rounded-lg p-4">
                {stock.aiVerdict}
              </div>
            </div>
          )}

          {/* RED FLAGS & CATALYSTS */}
          {(stock.redFlags && stock.redFlags.length > 0) || (stock.positiveCatalysts && stock.positiveCatalysts.length > 0) ? (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-surface-white mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-surface-700" /> Flags & Catalysts
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {stock.positiveCatalysts && stock.positiveCatalysts.length > 0 && (
                  <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                    <p className="text-[11px] font-semibold text-green-400 mb-2 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Positive Catalysts
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {stock.positiveCatalysts.map((c, i) => (
                        <span key={i} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-medium bg-green-900/30 text-green-400 border border-green-800/50">
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {stock.redFlags && stock.redFlags.length > 0 && (
                  <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                    <p className="text-[11px] font-semibold text-red-400 mb-2 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" /> Red Flags
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {stock.redFlags.map((f, i) => (
                        <span key={i} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-medium bg-red-900/30 text-red-400 border border-red-800/50">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : null}

          {/* LINK TO FULL PAGE */}
          <div className="pt-4 border-t border-surface-300/40 flex items-center justify-between">
            <Link
              to={`/ipo-analysis/${slug}`}
              className="inline-flex items-center gap-1.5 text-[12px] font-medium text-brand hover:text-brand-light transition-colors"
            >
              View Full Analysis
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
            <p className="text-[11px] text-surface-500">
              {stock.source && `Source: ${stock.source}`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
