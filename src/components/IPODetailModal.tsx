import { X, Building2, Calendar, TrendingUp, TrendingDown, Shield, AlertTriangle, Brain, ChevronDown, ChevronUp, Cpu, Leaf, FlaskConical, Landmark, Sprout, Sparkles } from 'lucide-react';
import type { IPOStock } from '../data/ipoData';
import ScoreRing from './ScoreRing';

import { useState } from 'react';

interface IPODetailModalProps {
  stock: IPOStock;
  onClose: () => void;
}

const sectorIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'Technology / Semiconductors': Cpu,
  'Renewable Energy': Leaf,
  'Healthcare / Biotech': FlaskConical,
  'Fintech / Digital Banking': Landmark,
  'AgriTech': Sprout,
};

function getRiskSeverity(indicator: string) {
  if (indicator.includes('🔴')) {
    return {
      label: 'High',
      className: 'bg-danger-muted text-danger border-danger-border',
    };
  }

  if (indicator.includes('🟢')) {
    return {
      label: 'Low',
      className: 'bg-success-muted text-success border-success-border',
    };
  }

  return {
    label: 'Medium',
    className: 'bg-warning-muted text-warning border-warning-border',
  };
}

export default function IPODetailModal({ stock, onClose }: IPODetailModalProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>('overview');
  const SectorIcon = sectorIcons[stock.sector] || Building2;

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const sections = [
    { id: 'overview', title: 'Company Overview', icon: Building2 },
    { id: 'details', title: 'IPO Details', icon: Calendar },
    { id: 'financials', title: 'Financial Snapshot', icon: TrendingUp },
    { id: 'strengths', title: 'Strengths', icon: Shield },
    { id: 'risks', title: 'Risks', icon: AlertTriangle },
    { id: 'ai', title: 'AI Analysis & Scores', icon: Brain },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-6 overflow-y-auto" onClick={onClose}>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-2xl bg-surface-100 border border-surface-300 rounded-xl shadow-2xl shadow-black/40 animate-slide-up mb-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 bg-surface-100/95 backdrop-blur-lg rounded-t-xl border-b border-surface-300/60 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center">
              <SectorIcon className="w-5 h-5 text-surface-700" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-surface-white leading-tight">{stock.company}</h2>
              <p className="text-[12px] text-surface-600 font-mono">{stock.ticker} / {stock.sector}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-md hover:bg-surface-300 transition-colors text-surface-600 hover:text-surface-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* AI Verdict Banner */}
        <div className="mx-6 mt-4 mb-2 px-4 py-3 rounded-lg bg-brand-muted border border-brand-border flex items-center gap-3">
          <Sparkles className="w-4 h-4 text-brand-light flex-shrink-0" />
          <div>
            <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">AI Verdict</span>
            <p className="text-[14px] font-semibold text-brand-light">{stock.aiVerdict}</p>
          </div>
        </div>

        {/* Sections */}
        <div className="p-4 space-y-1.5">
          {sections.map(({ id, title, icon: Icon }) => (
            <div key={id} className="rounded-lg border border-surface-300/40 overflow-hidden bg-surface-50">
              <button
                onClick={() => toggleSection(id)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-200/50 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4 text-surface-600" />
                  <span className="font-medium text-[13px] text-surface-900">{title}</span>
                </div>
                {expandedSection === id ? (
                  <ChevronUp className="w-4 h-4 text-surface-600" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-surface-600" />
                )}
              </button>

              {expandedSection === id && (
                <div className="px-4 pb-4 animate-fade-in">
                  {id === 'overview' && (
                    <div className="space-y-3">
                      <p className="text-[13px] text-surface-800 leading-relaxed">{stock.description}</p>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {[
                          { label: 'Founded', value: stock.founded },
                          { label: 'CEO', value: stock.ceo },
                          { label: 'HQ', value: stock.headquarters },
                          { label: 'Employees', value: stock.employees },
                        ].map((item) => (
                          <div key={item.label} className="bg-surface-100 border border-surface-300/40 rounded-md p-2.5">
                            <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mb-0.5">{item.label}</p>
                            <p className="text-[12px] font-medium text-surface-white">{item.value}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {id === 'details' && (
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        {[
                          { label: 'IPO Date', value: stock.expectedDate },
                          { label: 'Price Band', value: stock.priceRange },
                          { label: 'Lot Size', value: `${stock.lotSize} shares` },
                          { label: 'Issue Size', value: stock.issueSize },
                          { label: 'Exchange', value: stock.listingExchange },
                          { label: 'Issue Type', value: stock.ipoType },
                          { label: 'Registrar', value: stock.registrar },
                          { label: 'Status', value: stock.status.toUpperCase() },
                        ].map((item) => (
                          <div key={item.label} className="bg-surface-100 border border-surface-300/40 rounded-md p-2.5">
                            <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mb-0.5">{item.label}</p>
                            <p className="text-[12px] font-medium text-surface-white">{item.value}</p>
                          </div>
                        ))}
                      </div>
                      {stock.subscriptionStatus && (
                        <div className="bg-surface-100 border border-surface-300/40 rounded-md p-3">
                          <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mb-2.5">Subscription Status</p>
                          <div className="grid grid-cols-4 gap-2">
                            {(() => {
                              const sub = typeof stock.subscriptionStatus === 'string'
                                ? { retail: stock.subscriptionStatus, nii: '-', qib: '-', total: stock.subscriptionStatus }
                                : stock.subscriptionStatus;
                              return [
                                { label: 'Retail', value: sub.retail },
                                { label: 'NII', value: sub.nii },
                                { label: 'QIB', value: sub.qib },
                                { label: 'Total', value: sub.total },
                              ];
                            })().map((sub) => (
                              <div key={sub.label} className="text-center">
                                <p className="text-base font-bold text-brand-light">{sub.value}x</p>
                                <p className="text-[10px] text-surface-600">{sub.label}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {id === 'financials' && (
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {[
                        { label: 'Revenue', value: stock.revenue, positive: true },
                        { label: 'Net Income', value: stock.netIncome, positive: !stock.netIncome.startsWith('-') },
                        { label: 'Revenue Growth', value: stock.revenueGrowth, positive: stock.revenueGrowth.startsWith('+') },
                        { label: 'Profit Margin', value: stock.profitMargin, positive: parseFloat(stock.profitMargin) > 0 },
                        { label: 'Debt', value: stock.debt },
                        { label: 'ROCE', value: stock.roce, positive: !stock.roce.startsWith('-') },
                        { label: 'EPS', value: stock.eps, positive: !stock.eps.startsWith('-') },
                        { label: 'P/E Ratio', value: stock.peRatio },
                      ].map((item) => (
                        <div key={item.label} className="bg-surface-100 border border-surface-300/40 rounded-md p-2.5">
                          <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mb-0.5">{item.label}</p>
                          <p className={`text-[13px] font-semibold ${
                            item.positive === true ? 'text-success' :
                            item.positive === false ? 'text-danger' : 'text-surface-white'
                          }`}>{item.value}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {id === 'strengths' && (
                    <div className="space-y-2">
                      {stock.strengths.map((s, i) => (
                        <div key={i} className="flex items-start gap-2.5 bg-success-muted border border-success-border rounded-md p-2.5">
                          <TrendingUp className="w-3.5 h-3.5 text-success flex-shrink-0 mt-0.5" />
                          <p className="text-[12px] text-surface-800 leading-relaxed">{s}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {id === 'risks' && (
                    <div className="space-y-2">
                      {stock.risks.length > 0 ? (
                        stock.risks.map((r, i) => {
                          const severity = getRiskSeverity(r.indicator);

                          return (
                            <div key={i} className="bg-danger-muted border border-danger-border rounded-md p-3">
                              <div className="flex items-start gap-2.5">
                                <TrendingDown className="w-3.5 h-3.5 text-danger flex-shrink-0 mt-0.5" />
                                <div className="min-w-0 flex-1">
                                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                                    <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${severity.className}`}>
                                      {severity.label} Risk
                                    </span>
                                  </div>
                                  <p className="text-[12px] text-surface-900 leading-relaxed">{r.text}</p>
                                </div>
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <div className="bg-surface-100 border border-surface-300/40 rounded-md p-3">
                          <p className="text-[12px] text-surface-700 leading-relaxed">
                            No specific risk details are available for this IPO yet.
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {id === 'ai' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
                        {[
                          { label: 'Overall', score: stock.aiScores.overall },
                          { label: 'Fundamentals', score: stock.aiScores.fundamentals },
                          { label: 'Valuation', score: stock.aiScores.valuation },
                          { label: 'Growth', score: stock.aiScores.growth },
                          { label: 'Management', score: stock.aiScores.management },
                          { label: 'Sentiment', score: stock.aiScores.marketSentiment },
                        ].map((item) => (
                          <ScoreRing
                            key={item.label}
                            score={item.score}
                            size={64}
                            strokeWidth={4}
                            label={item.label}
                          />
                        ))}
                      </div>

                      <div className="bg-surface-200/50 border border-surface-300 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2.5">
                          <Brain className="w-4 h-4 text-brand-light" />
                          <h4 className="font-semibold text-[13px] text-surface-white">AI Analysis Report</h4>
                        </div>
                        <p className="text-[13px] text-surface-800 leading-relaxed">{stock.aiAnalysis}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
