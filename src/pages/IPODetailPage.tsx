import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ipoStocks } from '../data/ipoData';
import type { IPOStock } from '../data/ipoData';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { canonical, slugify } from '../seo/config';
import { financialProductSchema } from '../seo/schema';
import {
  ArrowLeft, Building2, Calendar, Brain,
  Cpu, Leaf, FlaskConical, Landmark, Sprout, Sparkles, ExternalLink,
  BarChart3, TrendingUp, Users, Target, FileText,
  ChevronDown, ChevronUp, Shield,
  DollarSign, Scale,
  Database, Activity, Award
} from 'lucide-react';
import Badge from '../components/Badge';
import ScoreRing from '../components/ScoreRing';

// ── Types ──────────────────────────────────────────────────────────
interface ScorecardCategory {
  key: string; label: string; score: number;
}

interface ComprehensiveAnalysis {
  slug: string; company: string; ticker: string; sector: string;
  executive_summary: string;
  business_overview: string;
  industry_analysis: string;
  financial_analysis: string;
  balance_sheet_analysis: string;
  cash_flow_analysis: string;
  ipo_details: string;
  valuation_analysis: string;
  management_quality: string;
  risk_assessment: string;
  strengths_weaknesses: string;
  market_sentiment: string;
  red_flags: string[];
  positive_catalysts: string[];
  final_verdict: string;
  section_13_market_performance: { stock_pe: string; analysis: string };
  section_20_scorecard: {
    categories: ScorecardCategory[];
    total_score: number; interpretation: string;
  };
  section_21_final_verdict: {
    long_term_rating: string;
    subscription_recommendation: string;
    summary: string;
  };
  investment_verdict: Record<string, unknown>;
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

// ── Section Renderers ──────────────────────────────────────────────
function MarkdownSection(content: string) {
  if (!content) return <p className="text-[13px] text-surface-700">No data available.</p>;
  const lines = content.split('\n');
  const elements: React.ReactNode[] = [];
  let tableRows: React.ReactNode[] = [];

  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (!trimmed) return;
    if (trimmed.startsWith('### ')) {
      elements.push(<h3 key={i} className="text-[14px] font-semibold text-surface-white mt-4 mb-2">{trimmed.slice(4)}</h3>);
    } else if (trimmed.startsWith('## ')) {
      elements.push(<h2 key={i} className="text-[15px] font-semibold text-surface-white mt-5 mb-2">{trimmed.slice(3)}</h2>);
    } else if (trimmed.startsWith('|')) {
      const cells = trimmed.split('|').filter(Boolean).map(c => c.trim()).filter(c => c && !c.startsWith('-'));
      if (cells.length > 0) {
        tableRows.push(<tr key={i}>{cells.map((c, j) => <td key={j} className="border border-surface-300/60 px-2 py-1.5 text-surface-700 text-[12px]">{c}</td>)}</tr>);
      }
    } else if (trimmed.startsWith('•') || trimmed.startsWith('-')) {
      const text = trimmed.replace(/^[•\-]\s*/, '');
      const bold = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      elements.push(<li key={i} className="text-[13px] text-surface-700 leading-relaxed ml-4 list-disc" dangerouslySetInnerHTML={{ __html: bold }} />);
    } else {
      const rendered = trimmed.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      elements.push(<p key={i} className="text-[13px] text-surface-700 leading-relaxed mt-1" dangerouslySetInnerHTML={{ __html: rendered }} />);
    }
  });

  if (tableRows.length > 0) {
    elements.push(<table key="tbl" className="w-full text-[12px] mb-4 border-collapse">{tableRows}</table>);
  }

  return <div className="space-y-0.5">{elements}</div>;
}

function SectionContentText(content: string) {
  if (!content) return <p className="text-[13px] text-surface-700">No data available.</p>;
  return MarkdownSection(content);
}

// ── Main Component ────────────────────────────────────────────────
export default function IPODetailPage() {
  const params = useParams();
  const slug = params.slug || '';
  const [analysis, setAnalysis] = useState<ComprehensiveAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSection, setExpandedSection] = useState<string | null>('s1');

  const stock = ipoStocks.find((s) => makeSlug(s) === slug);
  const SectorIcon = (stock && sectorIcons[stock.sector]) || Building2;

  useEffect(() => {
    if (!slug) { setLoading(false); return; }
    fetch('/data/ipoComprehensiveAnalysis.json')
      .then((r) => { if (!r.ok) throw new Error('Failed to load'); return r.json(); })
      .then((data: Record<string, ComprehensiveAnalysis>) => {
        setAnalysis(data[slug] || null);
        setLoading(false);
      })
      .catch(() => setLoading(false));
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
  const financialSchema = {
    '@context': 'https://schema.org',
    '@graph': [
      financialProductSchema({
        name: stock.company,
        description: stock.description || `${stock.company} (${stock.ticker}) — IPO analysis with AI scoring and risk assessment.`,
        urlPath: path,
        category: stock.sector,
        identifier: stock.ticker,
      }),
      {
        '@type': 'Article',
        headline: `${stock.company} (${stock.ticker}) IPO Analysis`,
        description: `Comprehensive 21-section IPO analysis report for ${stock.company} covering financials, valuation, SWOT, risk assessment, and investment verdict.`,
        datePublished: stock.openDate || new Date().toISOString().split('T')[0],
        dateModified: new Date().toISOString().split('T')[0],
        author: {
          '@type': 'Person',
          name: 'Shiva Sandeep',
          url: 'https://pulsetrends.in/about',
        },
        publisher: {
          '@type': 'Organization',
          name: 'PulseTrends',
          logo: { '@type': 'ImageObject', url: 'https://pulsetrends.in/og-default.png' },
        },
        mainEntityOfPage: { '@type': 'WebPage', '@id': url },
      },
    ],
  };

  const a = analysis;
  const scores = a?.investment_verdict?.scores as (Record<string, number> | undefined);

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

  const sections: { id: string; title: string; icon: React.ReactNode; render: () => React.ReactNode }[] = a ? [
    { id: 's1', title: 'Executive Summary', icon: <FileText className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.executive_summary) },
    { id: 's2', title: 'Business Overview', icon: <Building2 className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.business_overview) },
    { id: 's3', title: 'Industry & Market Analysis', icon: <BarChart3 className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.industry_analysis) },
    { id: 's4', title: 'Financial Performance (P&L)', icon: <DollarSign className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.financial_analysis) },
    { id: 's5', title: 'Balance Sheet Analysis', icon: <Database className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.balance_sheet_analysis) },
    { id: 's6', title: 'Cash Flow Analysis', icon: <Activity className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.cash_flow_analysis) },
    { id: 's7', title: 'IPO Issue Details', icon: <Target className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.ipo_details) },
    { id: 's8', title: 'Valuation Analysis', icon: <Scale className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.valuation_analysis) },
    { id: 's9', title: 'Promoter & Management Quality', icon: <Users className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.management_quality) },
    { id: 's10', title: 'Risk Assessment', icon: <Shield className="w-4 h-4 text-warning" />, render: () => SectionContentText(a.risk_assessment) },
    { id: 's11', title: 'Strengths & Weaknesses', icon: <Award className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.strengths_weaknesses) },
    { id: 's12', title: 'Market Sentiment', icon: <TrendingUp className="w-4 h-4 text-brand-light" />, render: () => SectionContentText(a.market_sentiment) },
    { id: 's13', title: 'Red Flags & Final Verdict', icon: <Sparkles className="w-4 h-4 text-warning" />, render: () => SectionContentText(a.final_verdict) },
  ] : [];

  return (
    <>
      <PageSeo
        meta={{
          path,
          title: `${stock.company} (${stock.ticker}) IPO Analysis | PulseTrends`,
          description: `${stock.company} IPO analysis: 21-section comprehensive research report with financials, valuation, SWOT, risk assessment, and investment verdict.`,
          ogType: 'article',
          schema: financialSchema,
          keywords: `${stock.company}, ${stock.ticker}, IPO, ${stock.sector}, ${stock.industry}, stock analysis, IPO review, financial analysis, investment`,
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
                    a.section_21_final_verdict.long_term_rating === 'Strong Buy' || a.section_21_final_verdict.long_term_rating === 'Buy'
                      ? 'success' : a.section_21_final_verdict.long_term_rating === 'Hold / Neutral' ? 'warning' : 'danger'
                  } size="sm">
                    {a.section_21_final_verdict.long_term_rating}
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

          {a && (
            <div className={`mt-4 px-4 py-3 rounded-lg border flex items-center gap-3 ${a.section_21_final_verdict.long_term_rating === 'Strong Buy' || a.section_21_final_verdict.long_term_rating === 'Buy' ? 'bg-success-muted border-success-border' : a.section_21_final_verdict.long_term_rating === 'Hold / Neutral' ? 'bg-warning-muted border-warning-border' : 'bg-danger-muted border-danger-border'}`}>
              <Sparkles className="w-4 h-4 shrink-0" style={{ color: a.section_21_final_verdict.long_term_rating === 'Avoid' ? '#ef4444' : '#f59e0b' }} />
              <div>
                <p className="text-[13px] font-semibold text-surface-white">
                  {a.section_21_final_verdict.long_term_rating} · {a.section_20_scorecard.total_score}/100
                </p>
                <p className="text-[12px] text-surface-600 mt-0.5">{a.section_21_final_verdict.summary.slice(0, 180)}...</p>
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
              <p className="text-[14px] font-semibold text-surface-white mt-1">{a.section_13_market_performance.stock_pe}</p>
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

        {/* 21-SECTION ANALYSIS */}
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
            {sections.map((sec) => (
              <div key={sec.id}>
                <SectionHeader id={sec.id} title={sec.title} icon={sec.icon} />
                <SectionContent id={sec.id}>{sec.render()}</SectionContent>
              </div>
            ))}
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
