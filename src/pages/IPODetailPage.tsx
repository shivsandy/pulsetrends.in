import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ipoStocks } from '../data/ipoData';
import type { IPOStock } from '../data/ipoData';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { canonical, slugify } from '../seo/config';
import { financialProductSchema } from '../seo/schema';
import {
  ArrowLeft, Building2, Calendar, AlertTriangle, Brain,
  Cpu, Leaf, FlaskConical, Landmark, Sprout, Sparkles, ExternalLink,
  BarChart3, LineChart, TrendingUp, Users, Flag, Target, FileText,
  CheckCircle2, XCircle, ChevronDown, ChevronUp
} from 'lucide-react';
import Badge from '../components/Badge';
import ScoreRing from '../components/ScoreRing';

// ── Types ──────────────────────────────────────────────────────────
interface PeerData {
  name: string; pe: number; pb: number; ev_ebitda: number; mcap: number;
}

interface FinRow {
  metric: string; y1: string; y2: string; y3: string; trend: string;
}

interface SeverityItem {
  risk: string; severity: string;
}

interface ComprehensiveAnalysis {
  slug: string;
  company: string;
  ticker: string;
  sector: string;
  business_overview: {
    business_model: string;
    revenue_sources: string[];
    competitive_advantages: string[];
    moat_assessment: string;
  };
  industry_analysis: {
    industry_size: string;
    key_competitors: string[];
    market_share_position: string;
    industry_risks: string[];
    industry_opportunities: string[];
  };
  financial_analysis: {
    table_data: FinRow[];
    overall_trend: string;
    revenue_growth: string;
    profit_growth: string;
    ebitda_growth: string;
    operating_margins: string;
    net_margins: string;
    roe_value: string;
    roce_value: string;
    debt_to_equity: string;
    interest_coverage: string;
    operating_cash_flow_val: string;
    free_cash_flow_val: string;
  };
  valuation_analysis: {
    pe_ratio: string;
    pb_ratio: string;
    ev_ebitda: string;
    market_cap: string;
    peer_comparison: PeerData[];
    valuation_assessment: string;
    reasoning: string;
  };
  ipo_details: {
    issue_size: string;
    fresh_issue: string;
    offer_for_sale: string;
    promoter_holding_before: string;
    promoter_holding_after: string;
    use_of_proceeds: string[];
    value_accretive: string;
  };
  risk_assessment: {
    business_risks: string[];
    industry_risks: string[];
    regulatory_risks: string[];
    customer_concentration_risks: string[];
    debt_risks: string[];
    governance_concerns: string[];
    ranked_by_severity: SeverityItem[];
  };
  management_quality: {
    promoter_background: string;
    management_experience: string;
    track_record: string;
    governance_concerns: string;
    related_party_transactions: string;
    score_out_of_10: number;
  };
  red_flags: string[];
  positive_catalysts: string[];
  investment_verdict: {
    scores: {
      business_quality: number;
      financial_strength: number;
      valuation_attractiveness: number;
      management_quality: number;
      industry_outlook: number;
      overall_score: number;
    };
    decision: string;
    investment_horizon: {
      listing_gain: string;
      one_to_three_year: string;
      three_to_five_year: string;
    };
  };
  executive_summary: string;
}

// ── Helpers ────────────────────────────────────────────────────────
const sectorIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'Technology / Semiconductors': Cpu,
  'Renewable Energy': Leaf,
  'Healthcare / Biotech': FlaskConical,
  'Fintech / Digital Banking': Landmark,
  'AgriTech': Sprout,
};

function makeSlug(s: IPOStock): string {
  return `${slugify(s.company)}-${s.id}`;
}

function trendColor(trend: string) {
  if (trend === 'improving') return 'text-success';
  if (trend === 'deteriorating') return 'text-danger';
  return 'text-warning';
}

function trendIcon(trend: string) {
  if (trend === 'improving') return '▲';
  if (trend === 'deteriorating') return '▼';
  return '◆';
}

function severityColor(s: string) {
  if (s === 'High') return 'bg-danger-muted text-danger border-danger-border';
  if (s === 'Low') return 'bg-success-muted text-success border-success-border';
  return 'bg-warning-muted text-warning border-warning-border';
}

function getDecisionColor(decision: string) {
  switch (decision) {
    case 'Strong Buy': return 'text-success';
    case 'Buy': return 'text-brand-light';
    case 'Neutral': return 'text-warning';
    case 'Avoid': return 'text-danger';
    default: return 'text-surface-700';
  }
}

function getDecisionBg(decision: string) {
  switch (decision) {
    case 'Strong Buy': return 'bg-success-muted border-success-border';
    case 'Buy': return 'bg-brand-muted border-brand-border';
    case 'Neutral': return 'bg-warning-muted border-warning-border';
    case 'Avoid': return 'bg-danger-muted border-danger-border';
    default: return 'bg-surface-100 border-surface-300';
  }
}

// ── Sub-components ────────────────────────────────────────────────
function SectionBox({ title, icon, children, className = '' }: {
  title: string; icon?: React.ReactNode; children: React.ReactNode; className?: string;
}) {
  return (
    <section className={`bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-6 ${className}`}>
      {icon ? (
        <h2 className="text-lg font-semibold text-surface-white mb-4 flex items-center gap-2.5">{icon} {title}</h2>
      ) : (
        <h2 className="text-lg font-semibold text-surface-white mb-4">{title}</h2>
      )}
      {children}
    </section>
  );
}

function ScoreCard({ label, score }: { label: string; score: number }) {
  const color = score >= 75 ? '#22c55e' : score >= 60 ? '#eab308' : score >= 45 ? '#f97316' : '#ef4444';
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

// ── Main Component ────────────────────────────────────────────────
export default function IPODetailPage() {
  const params = useParams();
  const slug = params.slug || '';
  const [analysis, setAnalysis] = useState<ComprehensiveAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSection, setExpandedSection] = useState<string | null>('executive');

  const stock = ipoStocks.find((s) => makeSlug(s) === slug);
  const SectorIcon = (stock && sectorIcons[stock.sector]) || Building2;

  useEffect(() => {
    if (!slug) { setLoading(false); return; }
    import('../data/ipoComprehensiveAnalysis.json').then((mod) => {
      const data = (mod.default || mod) as Record<string, ComprehensiveAnalysis>;
      setAnalysis(data[slug] || null);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [slug]);

  if (!stock) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center">
        <h1 className="text-2xl font-bold text-surface-white">IPO Not Found</h1>
        <p className="text-surface-600 mt-2">The IPO you are looking for does not exist or has been removed.</p>
        <Link to="/ipo-analysis" className="inline-flex items-center gap-2 mt-6 text-brand hover:text-brand-light">
          <ArrowLeft className="w-4 h-4" /> Back to IPO Analysis
        </Link>
      </div>
    );
  }

  const path = `/ipo-analysis/${slug}`;
  const url = canonical(path);
  const financialSchema = financialProductSchema({
    name: stock.company,
    description: stock.description || `${stock.company} (${stock.ticker}) — IPO analysis with AI scoring and risk assessment.`,
    urlPath: path,
    category: stock.sector,
    identifier: stock.ticker,
  });

  const a = analysis;
  const scores = a?.investment_verdict?.scores;

  const toggleSection = (id: string) => {
    setExpandedSection((prev) => prev === id ? null : id);
  };

  const SectionHeader = ({ id, title, icon }: { id: string; title: string; icon?: React.ReactNode }) => {
    const isOpen = expandedSection === id;
    return (
      <button
        onClick={() => toggleSection(id)}
        className="w-full flex items-center justify-between p-4 bg-surface-100 border border-surface-300/60 rounded-xl mb-2 hover:bg-surface-200 transition-colors text-left"
      >
        <h2 className="text-base font-semibold text-surface-white flex items-center gap-2.5">{icon} {title}</h2>
        {isOpen ? <ChevronUp className="w-4 h-4 text-surface-600" /> : <ChevronDown className="w-4 h-4 text-surface-600" />}
      </button>
    );
  };

  const SectionContent = ({ id, children }: { id: string; children: React.ReactNode }) => {
    if (expandedSection !== id) return null;
    return (
      <div className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-4 -mt-2">
        {children}
      </div>
    );
  };

  return (
    <>
      <PageSeo
        meta={{
          path,
          title: `${stock.company} (${stock.ticker}) IPO Analysis | PulseTrends`,
          description: `${stock.company} IPO analysis: company overview, financial snapshot, AI scoring (${stock.aiScores.overall}/100), strengths, and risks. ${stock.description || ''}`.slice(0, 160),
          ogType: 'article',
          schema: financialSchema,
        }}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'IPO Analysis', path: '/ipo-analysis' },
          { name: stock.company, path: `/ipo-analysis/${slug}` },
        ]}
      />

      <article className="max-w-4xl mx-auto">
        <Breadcrumbs items={[
          { name: 'Home', path: '/' },
          { name: 'IPO Analysis', path: '/ipo-analysis' },
          { name: stock.company },
        ]} />

        <Link to="/ipo-analysis" className="mb-4 inline-flex items-center gap-2 text-[13px] text-surface-700 hover:text-surface-white transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to IPO list
        </Link>

        {/* HEADER */}
        <header className="bg-surface-100 border border-surface-300/60 rounded-xl p-6 mb-6">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-xl bg-surface-200 border border-surface-300 flex items-center justify-center shrink-0">
              <SectorIcon className="w-7 h-7 text-surface-700" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Badge variant={stock.status === 'open' ? 'success' : stock.status === 'upcoming' ? 'warning' : 'info'} size="sm">
                  {stock.status}
                </Badge>
                <span className="text-[11px] text-surface-600 font-mono">{stock.ticker}</span>
                {a && (
                  <Badge variant={
                    a.investment_verdict.decision === 'Strong Buy' || a.investment_verdict.decision === 'Buy'
                      ? 'success' : a.investment_verdict.decision === 'Neutral' ? 'warning' : 'danger'
                  } size="sm">
                    {a.investment_verdict.decision}
                  </Badge>
                )}
              </div>
              <h1 className="text-2xl font-bold text-surface-white leading-tight">{stock.company}</h1>
              <p className="text-[13px] text-surface-600 mt-1">{stock.sector} · {stock.listingExchange}</p>
            </div>
            <div className="flex flex-col items-center">
              <ScoreRing score={scores?.overall_score ?? stock.aiScores.overall} size={64} strokeWidth={5} showLabel />
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mt-1">AI Score</p>
            </div>
          </div>

          {a?.investment_verdict && (
            <div className={`mt-4 px-4 py-3 rounded-lg border flex items-center gap-3 ${getDecisionBg(a.investment_verdict.decision)}`}>
              <Sparkles className="w-4 h-4 shrink-0" style={{ color: a.investment_verdict.decision === 'Avoid' ? '#ef4444' : '#f59e0b' }} />
              <div>
                <p className="text-[13px] font-semibold text-surface-white">
                  {a.investment_verdict.decision} · {a.investment_verdict.scores.overall_score}/100
                </p>
                <p className="text-[12px] text-surface-600 mt-0.5">{a.executive_summary.slice(0, 200)}...</p>
              </div>
            </div>
          )}
        </header>

        {/* QUICK INFO */}
        <section className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
          <div className="bg-surface-100 border border-surface-300/40 rounded-lg p-3">
            <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Price Band</p>
            <p className="text-[14px] font-semibold text-surface-white mt-1">{stock.priceRange || 'TBA'}</p>
          </div>
          <div className="bg-surface-100 border border-surface-300/40 rounded-lg p-3">
            <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Lot Size</p>
            <p className="text-[14px] font-semibold text-surface-white mt-1">{stock.lotSize || 'TBA'}</p>
          </div>
          <div className="bg-surface-100 border border-surface-300/40 rounded-lg p-3">
            <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Issue Size</p>
            <p className="text-[14px] font-semibold text-surface-white mt-1">{stock.issueSize || 'TBA'}</p>
          </div>
          {stock.expectedDate && (
            <div className="bg-surface-100 border border-surface-300/40 rounded-lg p-3">
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Expected Date</p>
              <p className="text-[14px] font-semibold text-surface-white mt-1 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" /> {stock.expectedDate}
              </p>
            </div>
          )}
          {stock.headquarters && (
            <div className="bg-surface-100 border border-surface-300/40 rounded-lg p-3">
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Headquarters</p>
              <p className="text-[14px] font-semibold text-surface-white mt-1">{stock.headquarters}</p>
            </div>
          )}
          {a && (
            <div className="bg-surface-100 border border-surface-300/40 rounded-lg p-3">
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">P/E Ratio</p>
              <p className="text-[14px] font-semibold text-surface-white mt-1">{a.valuation_analysis.pe_ratio}</p>
            </div>
          )}
        </section>

        {/* LOADING */}
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin w-8 h-8 border-2 border-brand border-t-transparent rounded-full mx-auto mb-2" />
            <p className="text-surface-600 text-[13px]">Loading detailed analysis...</p>
          </div>
        )}

        {/* 11-POINT ANALYSIS */}
        {!loading && !a && (
          <SectionBox title="Company Overview">
            <p className="text-[14px] text-surface-700 leading-relaxed">{stock.description}</p>
            {stock.about && stock.about !== stock.description && (
              <p className="text-[14px] text-surface-700 leading-relaxed mt-3">{stock.about}</p>
            )}
          </SectionBox>
        )}

        {a && (
          <div className="space-y-1 mb-6">
            {/* 1. EXECUTIVE SUMMARY (always open) */}
            <SectionHeader
              id="executive"
              title="1. Executive Summary"
              icon={<FileText className="w-4 h-4 text-brand-light" />}
            />
            <SectionContent id="executive">
              <div className="text-[14px] text-surface-700 leading-relaxed whitespace-pre-line">{a.executive_summary}</div>
            </SectionContent>

            {/* 2. BUSINESS OVERVIEW */}
            <SectionHeader
              id="business"
              title="2. Business Overview"
              icon={<Building2 className="w-4 h-4 text-brand-light" />}
            />
            <SectionContent id="business">
              <div className="space-y-4">
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Business Model</h3>
                  <p className="text-[13px] text-surface-700 leading-relaxed">{a.business_overview.business_model}</p>
                </div>
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Revenue Sources</h3>
                  <ul className="space-y-1">
                    {a.business_overview.revenue_sources.map((s, i) => (
                      <li key={i} className="text-[13px] text-surface-700 flex items-start gap-2">
                        <span className="text-brand-light mt-1">•</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Competitive Advantages</h3>
                  <ul className="space-y-1">
                    {a.business_overview.competitive_advantages.map((s, i) => (
                      <li key={i} className="text-[13px] text-surface-700 flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Moat Assessment</h3>
                  <p className="text-[13px] text-surface-700 leading-relaxed">{a.business_overview.moat_assessment}</p>
                </div>
              </div>
            </SectionContent>

            {/* 3. INDUSTRY ANALYSIS */}
            <SectionHeader
              id="industry"
              title="3. Industry Analysis"
              icon={<BarChart3 className="w-4 h-4 text-brand-light" />}
            />
            <SectionContent id="industry">
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                    <p className="text-[11px] text-surface-600 uppercase tracking-wider">Market Size</p>
                    <p className="text-[14px] font-semibold text-surface-white mt-1">{a.industry_analysis.industry_size}</p>
                  </div>
                  <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                    <p className="text-[11px] text-surface-600 uppercase tracking-wider">Market Position</p>
                    <p className="text-[14px] font-semibold text-surface-white mt-1">{a.industry_analysis.market_share_position}</p>
                  </div>
                </div>
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Key Competitors</h3>
                  <div className="flex flex-wrap gap-2">
                    {a.industry_analysis.key_competitors.map((c, i) => (
                      <span key={i} className="text-[11px] px-2 py-1 bg-surface-50 border border-surface-300/40 rounded-md text-surface-700">{c}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Industry Opportunities</h3>
                  <ul className="space-y-1">
                    {a.industry_analysis.industry_opportunities.map((o, i) => (
                      <li key={i} className="text-[13px] text-surface-700 flex items-start gap-2">
                        <TrendingUp className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />
                        <span>{o}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Industry Risks</h3>
                  <ul className="space-y-1">
                    {a.industry_analysis.industry_risks.map((r, i) => (
                      <li key={i} className="text-[13px] text-surface-700 flex items-start gap-2">
                        <AlertTriangle className="w-3.5 h-3.5 text-warning shrink-0 mt-0.5" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </SectionContent>

            {/* 4. FINANCIAL ANALYSIS */}
            <SectionHeader
              id="financial"
              title="4. Financial Analysis (3-Year Trend)"
              icon={<LineChart className="w-4 h-4 text-brand-light" />}
            />
            <SectionContent id="financial">
              <div className="space-y-4">
                <div className="overflow-x-auto">
                  <table className="w-full text-[12px]">
                    <thead>
                      <tr className="border-b border-surface-300/40">
                        <th className="text-left py-2 pr-4 text-surface-600 font-medium">Metric</th>
                        <th className="text-right py-2 px-3 text-surface-600 font-medium">Year 1</th>
                        <th className="text-right py-2 px-3 text-surface-600 font-medium">Year 2</th>
                        <th className="text-right py-2 px-3 text-surface-600 font-medium">Year 3</th>
                        <th className="text-right py-2 pl-3 text-surface-600 font-medium">Trend</th>
                      </tr>
                    </thead>
                    <tbody>
                      {a.financial_analysis.table_data.map((row, i) => (
                        <tr key={i} className="border-b border-surface-300/20 hover:bg-surface-50/50">
                          <td className="py-2 pr-4 text-surface-white font-medium">{row.metric}</td>
                          <td className="text-right py-2 px-3 text-surface-700">{row.y1}</td>
                          <td className="text-right py-2 px-3 text-surface-700">{row.y2}</td>
                          <td className="text-right py-2 px-3 text-surface-700">{row.y3}</td>
                          <td className={`text-right py-2 pl-3 ${trendColor(row.trend)} font-medium`}>
                            {trendIcon(row.trend)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="text-[12px] text-surface-600 bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                  <span className="font-semibold text-surface-white">Overall Trend:</span>{' '}
                  <span className={`font-medium ${trendColor(a.financial_analysis.overall_trend)}`}>
                    {a.financial_analysis.overall_trend.charAt(0).toUpperCase() + a.financial_analysis.overall_trend.slice(1)}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
                  {[
                    ['Revenue Growth', a.financial_analysis.revenue_growth],
                    ['Profit Growth', a.financial_analysis.profit_growth],
                    ['EBITDA Growth', a.financial_analysis.ebitda_growth],
                    ['Operating Margin', a.financial_analysis.operating_margins],
                    ['Net Margin', a.financial_analysis.net_margins],
                    ['ROE', a.financial_analysis.roe_value],
                    ['ROCE', a.financial_analysis.roce_value],
                    ['Debt/Equity', a.financial_analysis.debt_to_equity],
                    ['Interest Coverage', a.financial_analysis.interest_coverage],
                  ].map(([label, value]) => (
                    <div key={label} className="bg-surface-50 border border-surface-300/40 rounded-lg p-2.5">
                      <p className="text-[10px] text-surface-600 uppercase tracking-wider">{label}</p>
                      <p className="text-[13px] font-semibold text-surface-white mt-0.5">{value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </SectionContent>

            {/* 5. IPO DETAILS */}
            <SectionHeader
              id="ipodetails"
              title="5. IPO Details"
              icon={<Target className="w-4 h-4 text-brand-light" />}
            />
            <SectionContent id="ipodetails">
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    ['Issue Size', a.ipo_details.issue_size || stock.issueSize || 'TBA'],
                    ['Fresh Issue', a.ipo_details.fresh_issue],
                    ['Offer for Sale', a.ipo_details.offer_for_sale],
                    ['Pre-IPO Promoter Holding', a.ipo_details.promoter_holding_before],
                    ['Post-IPO Promoter Holding', a.ipo_details.promoter_holding_after],
                  ].map(([label, value]) => (
                    <div key={label} className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                      <p className="text-[11px] text-surface-600 uppercase tracking-wider">{label}</p>
                      <p className="text-[13px] font-semibold text-surface-white mt-1">{label === 'Issue Size' ? (value || stock.issueSize || 'TBA') : value}</p>
                    </div>
                  ))}
                </div>
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Use of Proceeds</h3>
                  <ul className="space-y-1">
                    {a.ipo_details.use_of_proceeds.map((p, i) => (
                      <li key={i} className="text-[13px] text-surface-700 flex items-start gap-2">
                        <span className="text-brand-light mt-1.5">•</span>
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-brand-muted border border-brand-border rounded-lg p-3">
                  <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Value Accretive Assessment</p>
                  <p className="text-[13px] text-surface-700 leading-relaxed">{a.ipo_details.value_accretive}</p>
                </div>
              </div>
            </SectionContent>

            {/* 6. VALUATION ANALYSIS */}
            <SectionHeader
              id="valuation"
              title="6. Valuation Analysis"
              icon={<BarChart3 className="w-4 h-4 text-brand-light" />}
            />
            <SectionContent id="valuation">
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    ['P/E Ratio', a.valuation_analysis.pe_ratio],
                    ['P/B Ratio', a.valuation_analysis.pb_ratio],
                    ['EV/EBITDA', a.valuation_analysis.ev_ebitda],
                    ['Market Cap', a.valuation_analysis.market_cap],
                  ].map(([label, value]) => (
                    <div key={label} className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                      <p className="text-[10px] text-surface-600 uppercase tracking-wider">{label}</p>
                      <p className="text-[14px] font-bold text-surface-white mt-1">{value}</p>
                    </div>
                  ))}
                </div>

                <div className={`px-4 py-3 rounded-lg border text-[13px] ${
                  a.valuation_analysis.valuation_assessment === 'Undervalued' ? 'bg-success-muted border-success-border text-success' :
                  a.valuation_analysis.valuation_assessment === 'Overvalued' ? 'bg-danger-muted border-danger-border text-danger' :
                  'bg-warning-muted border-warning-border text-warning'
                } font-medium`}>
                  {a.valuation_analysis.valuation_assessment}
                </div>

                <p className="text-[13px] text-surface-700 leading-relaxed">{a.valuation_analysis.reasoning}</p>

                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-2">Peer Comparison</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-[12px]">
                      <thead>
                        <tr className="border-b border-surface-300/40">
                          <th className="text-left py-2 pr-3 text-surface-600 font-medium">Peer</th>
                          <th className="text-right py-2 px-2 text-surface-600 font-medium">P/E</th>
                          <th className="text-right py-2 px-2 text-surface-600 font-medium">P/B</th>
                          <th className="text-right py-2 px-2 text-surface-600 font-medium">EV/EBITDA</th>
                          <th className="text-right py-2 pl-2 text-surface-600 font-medium">M Cap</th>
                        </tr>
                      </thead>
                      <tbody>
                        {a.valuation_analysis.peer_comparison.map((p, i) => (
                          <tr key={i} className="border-b border-surface-300/20">
                            <td className="py-2 pr-3 text-surface-white">{p.name}</td>
                            <td className="text-right py-2 px-2 text-surface-700">{p.pe}x</td>
                            <td className="text-right py-2 px-2 text-surface-700">{p.pb}x</td>
                            <td className="text-right py-2 px-2 text-surface-700">{p.ev_ebitda}x</td>
                            <td className="text-right py-2 pl-2 text-surface-700">{p.mcap.toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </SectionContent>

            {/* 7. RISK ASSESSMENT */}
            <SectionHeader
              id="risks"
              title="7. Risk Assessment"
              icon={<AlertTriangle className="w-4 h-4 text-warning" />}
            />
            <SectionContent id="risks">
              <div className="space-y-4">
                <div>
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Risks by Severity</h3>
                  <div className="space-y-2">
                    {a.risk_assessment.ranked_by_severity.map((r, i) => (
                      <div key={i} className="flex items-start gap-3 p-2.5 bg-surface-50 border border-surface-300/40 rounded-lg">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold uppercase tracking-wider shrink-0 ${severityColor(r.severity)}`}>
                          {r.severity}
                        </span>
                        <span className="text-[13px] text-surface-700">{r.risk}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                    <h4 className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Business Risks</h4>
                    <ul className="space-y-1">
                      {a.risk_assessment.business_risks.map((r, i) => (
                        <li key={i} className="text-[12px] text-surface-700 flex items-start gap-1.5">
                          <span className="text-danger shrink-0">•</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                    <h4 className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Regulatory Risks</h4>
                    <ul className="space-y-1">
                      {a.risk_assessment.regulatory_risks.map((r, i) => (
                        <li key={i} className="text-[12px] text-surface-700 flex items-start gap-1.5">
                          <span className="text-warning shrink-0">•</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                  <h4 className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Customer Concentration</h4>
                  <p className="text-[13px] text-surface-700">{a.risk_assessment.customer_concentration_risks[0]}</p>
                </div>
                <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                  <h4 className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Debt & Governance</h4>
                  <p className="text-[13px] text-surface-700">{a.risk_assessment.debt_risks[0]}</p>
                  <p className="text-[13px] text-surface-700 mt-1">{a.risk_assessment.governance_concerns[0]}</p>
                </div>
              </div>
            </SectionContent>

            {/* 8. MANAGEMENT QUALITY */}
            <SectionHeader
              id="management"
              title="8. Management & Promoter Quality"
              icon={<Users className="w-4 h-4 text-brand-light" />}
            />
            <SectionContent id="management">
              <div className="space-y-4">
                <div className="flex items-center gap-3 mb-3">
                  <ScoreRing score={a.management_quality.score_out_of_10 * 10} size={48} strokeWidth={4} />
                  <div>
                    <p className="text-[13px] font-semibold text-surface-white">Management Score</p>
                    <p className="text-[12px] text-surface-600">{a.management_quality.score_out_of_10}/10</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    ['Promoter Background', a.management_quality.promoter_background],
                    ['Management Experience', a.management_quality.management_experience],
                    ['Track Record', a.management_quality.track_record],
                    ['Governance', a.management_quality.governance_concerns],
                    ['Related-Party Transactions', a.management_quality.related_party_transactions],
                  ].map(([label, value]) => (
                    <div key={label} className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                      <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">{label}</p>
                      <p className="text-[12px] text-surface-700 leading-relaxed">{value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </SectionContent>

            {/* 9. RED FLAGS */}
            <SectionHeader
              id="redflags"
              title="9. Red Flags"
              icon={<XCircle className="w-4 h-4 text-danger" />}
            />
            <SectionContent id="redflags">
              <ul className="space-y-2">
                {a.red_flags.map((f, i) => (
                  <li key={i} className="flex items-start gap-2 p-3 bg-danger-muted border border-danger-border rounded-lg">
                    <span className="text-danger shrink-0 mt-0.5">⚠</span>
                    <span className="text-[13px] text-surface-700">{f}</span>
                  </li>
                ))}
              </ul>
            </SectionContent>

            {/* 10. POSITIVE CATALYSTS */}
            <SectionHeader
              id="catalysts"
              title="10. Positive Catalysts"
              icon={<Flag className="w-4 h-4 text-success" />}
            />
            <SectionContent id="catalysts">
              <ul className="space-y-2">
                {a.positive_catalysts.map((c, i) => (
                  <li key={i} className="flex items-start gap-2 p-3 bg-success-muted border border-success-border rounded-lg">
                    <CheckCircle2 className="w-4 h-4 text-success shrink-0 mt-0.5" />
                    <span className="text-[13px] text-surface-700">{c}</span>
                  </li>
                ))}
              </ul>
            </SectionContent>

            {/* 11. INVESTMENT VERDICT */}
            <SectionHeader
              id="verdict"
              title="11. Investment Verdict"
              icon={<Sparkles className="w-4 h-4 text-warning" />}
            />
            <SectionContent id="verdict">
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <ScoreCard label="Business Quality" score={a.investment_verdict.scores.business_quality} />
                  <ScoreCard label="Financial Strength" score={a.investment_verdict.scores.financial_strength} />
                  <ScoreCard label="Valuation" score={a.investment_verdict.scores.valuation_attractiveness} />
                  <ScoreCard label="Management" score={a.investment_verdict.scores.management_quality} />
                  <ScoreCard label="Industry Outlook" score={a.investment_verdict.scores.industry_outlook} />
                  <ScoreCard label="Overall IPO Score" score={a.investment_verdict.scores.overall_score} />
                </div>

                <div className={`text-center py-4 rounded-lg border ${getDecisionBg(a.investment_verdict.decision)}`}>
                  <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Decision</p>
                  <p className={`text-xl font-bold ${getDecisionColor(a.investment_verdict.decision)}`}>
                    {a.investment_verdict.decision}
                  </p>
                </div>

                <div className="space-y-2">
                  <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Investment Horizon</h3>
                  {[
                    ['Listing Gain', a.investment_verdict.investment_horizon.listing_gain],
                    ['1-3 Year', a.investment_verdict.investment_horizon.one_to_three_year],
                    ['3-5 Year', a.investment_verdict.investment_horizon.three_to_five_year],
                  ].map(([label, value]) => (
                    <div key={label} className="bg-surface-50 border border-surface-300/40 rounded-lg p-3 flex items-start gap-3">
                      <Badge variant="outline" size="sm">{label}</Badge>
                      <span className="text-[13px] text-surface-700">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </SectionContent>
          </div>
        )}

        {/* AI ANALYSIS */}
        {stock.aiAnalysis && (
          <SectionBox title="AI Research Analysis" icon={<Brain className="w-4 h-4 text-brand-light" />}>
            <div className="text-[13px] text-surface-700 leading-relaxed whitespace-pre-line">{stock.aiAnalysis}</div>
          </SectionBox>
        )}



        {/* SCORES */}
        <SectionBox title="AI Scores">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(stock.aiScores).map(([key, value]) => (
              <ScoreCard key={key} label={key.replace(/([A-Z])/g, ' $1')} score={value} />
            ))}
          </div>
        </SectionBox>

        {/* DOCUMENTS */}
        {(stock.drhpUrl || stock.rhpUrl) && (
          <SectionBox title="Documents" icon={<ExternalLink className="w-4 h-4" />}>
            <div className="flex flex-wrap gap-2">
              {stock.drhpUrl && (
                <a href={stock.drhpUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium text-surface-700 bg-surface-200 hover:bg-surface-300 rounded-md transition-colors">
                  DRHP <ExternalLink className="w-3 h-3" />
                </a>
              )}
              {stock.rhpUrl && (
                <a href={stock.rhpUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium text-surface-700 bg-surface-200 hover:bg-surface-300 rounded-md transition-colors">
                  RHP <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </SectionBox>
        )}

        <footer className="text-[11px] text-surface-500 mt-8 mb-4">
          <p>Canonical: <a href={url} className="text-brand hover:underline">{url}</a></p>
          <p className="mt-1">Disclaimer: This analysis is AI-generated based on available data and should not be considered financial advice. Always consult a qualified financial advisor before making investment decisions.</p>
        </footer>
      </article>
    </>
  );
}
