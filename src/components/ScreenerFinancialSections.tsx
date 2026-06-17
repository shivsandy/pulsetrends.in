import { Building2, TrendingUp, BarChart3, PieChart, DollarSign, Activity, Users, FileText, AlertTriangle, CheckCircle2, LineChart, Target, Calendar } from 'lucide-react';
import type { CompanyFinancialAnalysis } from '../data/screenerFinancialData';

interface Props {
  financials: CompanyFinancialAnalysis;
}

function SectionBox({ title, icon, children, className = '' }: {
  title: string; icon?: React.ReactNode; children: React.ReactNode; className?: string;
}) {
  return (
    <section className={`bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-4 ${className}`}>
      {icon ? (
        <h3 className="text-sm font-semibold text-surface-white mb-3 flex items-center gap-2">{icon} {title}</h3>
      ) : (
        <h3 className="text-sm font-semibold text-surface-white mb-3">{title}</h3>
      )}
      {children}
    </section>
  );
}

function DataRow({ label, value, className = '' }: { label: string; value: string | number | null | undefined; className?: string }) {
  if (!value && value !== 0) return null;
  return (
    <div className={`flex items-center justify-between py-1.5 border-b border-surface-300/20 last:border-b-0 ${className}`}>
      <span className="text-[12px] text-surface-600">{label}</span>
      <span className="text-[12px] font-medium text-surface-white">{value}</span>
    </div>
  );
}

function FinancialTable({ data }: { data: { headers: string[]; rows: string[][] } }) {
  if (!data.rows || data.rows.length === 0) return <p className="text-[12px] text-surface-500 italic">No data available</p>;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[11px]">
        {data.headers.length > 0 && (
          <thead>
            <tr className="border-b border-surface-300/40">
              {data.headers.map((h, i) => (
                <th key={i} className={`text-left py-1.5 px-2 font-semibold text-surface-700 ${i === 0 ? '' : 'text-right'}`}>{h}</th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {data.rows.map((row, ri) => (
            <tr key={ri} className="border-b border-surface-300/10 hover:bg-surface-50/50">
              {row.map((cell, ci) => (
                <td key={ci} className={`py-1 px-2 text-surface-700 ${ci === 0 ? 'font-medium text-surface-white' : 'text-right'}`}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Tag({ text, variant = 'default' }: { text: string; variant?: 'positive' | 'negative' | 'default' }) {
  const colors = {
    positive: 'bg-green-900/30 text-green-400 border-green-800/50',
    negative: 'bg-red-900/30 text-red-400 border-red-800/50',
    default: 'bg-surface-200 text-surface-700 border-surface-300/50',
  };
  return (
    <span className={`inline-flex px-2.5 py-1 rounded-full text-[10px] font-medium border ${colors[variant]}`}>
      {text}
    </span>
  );
}

export default function ScreenerFinancialSections({ financials }: Props) {
  const { companyOverview, valuationMetrics, prosCons, peerComparison,
    halfYearlyResults, profitLoss, growthMetrics, balanceSheet,
    cashFlow, ratios, insights, shareholdingPattern, announcements, annualReports } = financials;

  return (
    <div className="space-y-4 mt-6">
      {/* Section 1: Company Overview */}
      {companyOverview?.businessDescription && (
        <SectionBox title="Company Overview" icon={<Building2 className="w-4 h-4 text-blue-400" />}>
          <div className="flex flex-wrap gap-2 mb-3">
            {companyOverview.website && <Tag text={companyOverview.website} />}
            {companyOverview.exchange && <Tag text={companyOverview.exchange} />}
          </div>
          <p className="text-[13px] text-surface-700 leading-relaxed">{companyOverview.businessDescription}</p>
          {companyOverview.keyPoints && companyOverview.keyPoints.length > 0 && (
            <ul className="mt-2 space-y-1">
              {companyOverview.keyPoints.map((kp, i) => (
                <li key={i} className="text-[12px] text-surface-600 flex items-start gap-2">
                  <span className="text-brand-light mt-0.5">•</span> {kp}
                </li>
              ))}
            </ul>
          )}
        </SectionBox>
      )}

      {/* Section 2: Stock Price & Valuation Metrics */}
      {valuationMetrics && Object.keys(valuationMetrics).length > 0 && (
        <SectionBox title="Stock Price & Valuation Metrics" icon={<TrendingUp className="w-4 h-4 text-emerald-400" />}>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {valuationMetrics.currentPrice && <DataRow label="Current Price" value={`₹${valuationMetrics.currentPrice}`} />}
            {valuationMetrics.marketCap && <DataRow label="Market Cap" value={`₹${valuationMetrics.marketCap} Cr`} />}
            {valuationMetrics.high && valuationMetrics.low && <DataRow label="High / Low" value={`₹${valuationMetrics.high} / ₹${valuationMetrics.low}`} />}
            {valuationMetrics.stockPE && <DataRow label="Stock P/E" value={valuationMetrics.stockPE} />}
            {valuationMetrics.bookValue && <DataRow label="Book Value" value={`₹${valuationMetrics.bookValue}`} />}
            {valuationMetrics.dividendYield && <DataRow label="Dividend Yield" value={`${valuationMetrics.dividendYield}%`} />}
            {valuationMetrics.roce && <DataRow label="ROCE" value={`${valuationMetrics.roce}%`} />}
            {valuationMetrics.roe && <DataRow label="ROE" value={`${valuationMetrics.roe}%`} />}
            {valuationMetrics.faceValue && <DataRow label="Face Value" value={`₹${valuationMetrics.faceValue}`} />}
          </div>
        </SectionBox>
      )}

      {/* Section 3: Pros & Cons */}
      {(prosCons?.pros?.length > 0 || prosCons?.cons?.length > 0) && (
        <SectionBox title="Pros & Cons" icon={<AlertTriangle className="w-4 h-4 text-amber-400" />}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {prosCons.pros.length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-green-400 mb-2 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3 h-3" /> Pros
                </h4>
                <ul className="space-y-1">
                  {prosCons.pros.map((p, i) => (
                    <li key={i} className="text-[12px] text-surface-700 flex items-start gap-1.5">
                      <span className="text-green-400 mt-0.5 shrink-0">+</span> {p}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {prosCons.cons.length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-red-400 mb-2 flex items-center gap-1.5">
                  <AlertTriangle className="w-3 h-3" /> Cons
                </h4>
                <ul className="space-y-1">
                  {prosCons.cons.map((c, i) => (
                    <li key={i} className="text-[12px] text-surface-700 flex items-start gap-1.5">
                      <span className="text-red-400 mt-0.5 shrink-0">−</span> {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </SectionBox>
      )}

      {/* Section 4: Peer Comparison */}
      {peerComparison && (peerComparison.sector || peerComparison.industry || peerComparison.benchmarkIndex) && (
        <SectionBox title="Peer Comparison" icon={<Users className="w-4 h-4 text-purple-400" />}>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {peerComparison.sector && <DataRow label="Sector" value={peerComparison.sector} />}
            {peerComparison.industry && <DataRow label="Industry" value={peerComparison.industry} />}
            {peerComparison.benchmarkIndex && <DataRow label="Benchmark Index" value={peerComparison.benchmarkIndex} />}
          </div>
        </SectionBox>
      )}

      {/* Section 5: Half Yearly Results */}
      {halfYearlyResults?.rows?.length > 0 && (
        <SectionBox title="Half Yearly Results" icon={<BarChart3 className="w-4 h-4 text-cyan-400" />}>
          <FinancialTable data={halfYearlyResults} />
        </SectionBox>
      )}

      {/* Section 6: Profit & Loss (Annual) */}
      {profitLoss?.rows?.length > 0 && (
        <SectionBox title="Profit & Loss (Annual)" icon={<LineChart className="w-4 h-4 text-indigo-400" />}>
          <FinancialTable data={profitLoss} />
        </SectionBox>
      )}

      {/* Section 7: Growth Metrics */}
      {growthMetrics && (Object.keys(growthMetrics.salesGrowth).length > 0 || Object.keys(growthMetrics.profitGrowth).length > 0) && (
        <SectionBox title="Growth Metrics" icon={<TrendingUp className="w-4 h-4 text-green-400" />}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Object.keys(growthMetrics.salesGrowth).length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-surface-600 mb-1.5">Compounded Sales Growth</h4>
                <div className="space-y-1">
                  {Object.entries(growthMetrics.salesGrowth).map(([period, val]) => (
                    <DataRow key={period} label={period} value={val} />
                  ))}
                </div>
              </div>
            )}
            {Object.keys(growthMetrics.profitGrowth).length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-surface-600 mb-1.5">Compounded Profit Growth</h4>
                <div className="space-y-1">
                  {Object.entries(growthMetrics.profitGrowth).map(([period, val]) => (
                    <DataRow key={period} label={period} value={val} />
                  ))}
                </div>
              </div>
            )}
            {Object.keys(growthMetrics.stockPriceCAGR).length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-surface-600 mb-1.5">Stock Price CAGR</h4>
                <div className="space-y-1">
                  {Object.entries(growthMetrics.stockPriceCAGR).map(([period, val]) => (
                    <DataRow key={period} label={period} value={val} />
                  ))}
                </div>
              </div>
            )}
            {Object.keys(growthMetrics.returnOnEquity).length > 0 && (
              <div>
                <h4 className="text-[11px] font-semibold text-surface-600 mb-1.5">Return on Equity</h4>
                <div className="space-y-1">
                  {Object.entries(growthMetrics.returnOnEquity).map(([period, val]) => (
                    <DataRow key={period} label={period} value={val} />
                  ))}
                </div>
              </div>
            )}
          </div>
        </SectionBox>
      )}

      {/* Section 8: Balance Sheet */}
      {balanceSheet?.rows?.length > 0 && (
        <SectionBox title="Balance Sheet" icon={<PieChart className="w-4 h-4 text-orange-400" />}>
          <FinancialTable data={balanceSheet} />
        </SectionBox>
      )}

      {/* Section 9: Cash Flow Analysis */}
      {cashFlow?.rows?.length > 0 && (
        <SectionBox title="Cash Flow Analysis" icon={<DollarSign className="w-4 h-4 text-green-400" />}>
          <FinancialTable data={cashFlow} />
        </SectionBox>
      )}

      {/* Section 10: Key Financial Ratios */}
      {ratios?.rows?.length > 0 && (
        <SectionBox title="Key Financial Ratios" icon={<Activity className="w-4 h-4 text-rose-400" />}>
          <FinancialTable data={ratios} />
        </SectionBox>
      )}

      {/* Section 11: Key Insights */}
      {insights && Object.keys(insights).length > 0 && (
        <SectionBox title="Key Insights (AI Extracted)" icon={<Target className="w-4 h-4 text-teal-400" />}>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(insights).map(([key, val]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} value={val} />
            ))}
          </div>
        </SectionBox>
      )}

      {/* Section 12: Shareholding Pattern */}
      {shareholdingPattern && (shareholdingPattern.promoterHolding || shareholdingPattern.totalShareholders) && (
        <SectionBox title="Shareholding Pattern" icon={<Users className="w-4 h-4 text-blue-400" />}>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <DataRow label="Promoter Holding" value={shareholdingPattern.promoterHolding} />
            <DataRow label="FII Holding" value={shareholdingPattern.fiiHolding} />
            <DataRow label="Public Holding" value={shareholdingPattern.publicHolding} />
            <DataRow label="Shareholders" value={shareholdingPattern.totalShareholders} />
          </div>
        </SectionBox>
      )}

      {/* Section 13: Recent Announcements */}
      {announcements && announcements.length > 0 && (
        <SectionBox title="Recent Announcements" icon={<Calendar className="w-4 h-4 text-amber-400" />}>
          <ul className="space-y-2">
            {announcements.slice(0, 10).map((ann, i) => (
              <li key={i} className="text-[12px] text-surface-700 leading-relaxed flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                {ann}
              </li>
            ))}
          </ul>
        </SectionBox>
      )}

      {/* Section 14: Annual Reports */}
      {annualReports && annualReports.length > 0 && (
        <SectionBox title="Annual Reports Available" icon={<FileText className="w-4 h-4 text-sky-400" />}>
          <div className="flex flex-wrap gap-2">
            {annualReports.map((report, i) => (
              <Tag key={i} text={report} />
            ))}
          </div>
        </SectionBox>
      )}

      {/* No data fallback */}
      {!companyOverview?.businessDescription && (!valuationMetrics || Object.keys(valuationMetrics).length === 0) && (
        <div className="text-center py-8 border border-surface-300/40 rounded-xl bg-surface-50">
          <p className="text-surface-500 text-[13px]">No screener.in financial data available for this company yet.</p>
        </div>
      )}
    </div>
  );
}
