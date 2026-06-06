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
  BarChart3, LineChart, TrendingUp, Users, Target, FileText,
  CheckCircle2, XCircle, ChevronDown, ChevronUp, Shield,
  PieChart, DollarSign, Scale, BookOpen, Clock, Layers,
  GitCompare, Database, Activity, Award, ThumbsUp, ThumbsDown
} from 'lucide-react';
import Badge from '../components/Badge';
import ScoreRing from '../components/ScoreRing';

// ── Types ──────────────────────────────────────────────────────────
interface TimelineEvent {
  year: string; event: string; impact: string;
}
interface PeerItem {
  name: string; mcap: string; rev: string; ebitda: string; pat: string;
  pe: string; ev_ebitda: string; roe: string; roce: string; de: string; rev_growth: string;
}
interface ChartItem {
  name: string; description: string; values?: number[]; unit?: string;
}
interface RiskItem {
  category: string; rating: string; detail: string;
}
interface ScorecardCategory {
  key: string; label: string; score: number;
}
interface QuarterRow {
  quarter: string; revenue: string; ebitda: string; pat: string; eps: string;
  ebitda_margin: string; net_margin: string;
}
interface BSRow {
  metric: string; y1: string; y2: string; y3: string; y4?: string; y5?: string;
}
interface SWOTItem {
  item: string; evidence: string;
}
interface HistoricalTrend {
  quarter: string; promoters: string; fiis: string; dii: string; retail: string;
}

interface ComprehensiveAnalysis {
  slug: string; company: string; ticker: string; sector: string;
  business_overview: Record<string, unknown>;
  industry_analysis: Record<string, unknown>;
  financial_analysis: Record<string, unknown>;
  valuation_analysis: Record<string, unknown>;
  ipo_details: Record<string, unknown>;
  risk_assessment: Record<string, unknown>;
  management_quality: Record<string, unknown>;
  red_flags: string[];
  positive_catalysts: string[];
  investment_verdict: Record<string, unknown>;
  executive_summary: string;

  section_1_executive_summary: {
    company_name: string; industry: string; sector: string; exchange: string;
    ticker: string; market_cap: string; share_price: string; high_52w: string;
    low_52w: string; face_value: string; book_value: string; dividend_yield: string;
    stock_pe: string; industry_pe: string; roe: string; roce: string;
    debt_to_equity: string; summary: string;
  };
  section_2_history_timeline: {
    founding_year: number; founder_background: string;
    timeline_table: TimelineEvent[]; analysis: string;
  };
  section_3_business_model: {
    revenue_streams: string; business_segments: string[];
    products_services: string[]; geo_distribution: Record<string, string>;
    customer_segments: string[]; distribution_channels: string[];
    competitive_advantages: string[]; economic_moat: string;
    scalability: string; recurring_revenue: string;
    revenue_drivers: string; growth_levers: string[];
  };
  section_4_ipo_rationale: {
    fresh_issue_pct: string; ofs_pct: string;
    promoter_holding_before: string; promoter_holding_after: string;
    use_of_proceeds: Record<string, string>;
    growth_oriented: boolean; exit_event: boolean;
    valuation_justified: boolean; conclusions: string;
  };
  section_5_industry_analysis: {
    industry_overview: string; market_size: string; industry_cagr: string;
    tam: string; sam: string; growth_drivers: string[];
    regulatory_environment: string[]; industry_trends: string[];
    porters_five_forces: Record<string, string>;
  };
  section_6_management_governance: {
    promoters: string; ceo: string; cfo: string;
    board_members: string[]; independent_directors: string;
    track_record: string; governance_quality: string;
    capital_allocation: string; related_party_transactions: string;
    auditor_history: string; governance_concerns: string; score_out_of_10: number;
  };
  section_7_shareholding_pattern: {
    current_pattern: Record<string, string>;
    historical_trends: HistoricalTrend[];
    analysis: string;
  };
  section_8_profit_loss: {
    income_statement: BSRow[];
    cagr_analysis: Record<string, string>;
    margin_analysis: string; profitability_trends: string;
  };
  section_9_balance_sheet: {
    balance_sheet: BSRow[];
    financial_strength: string;
  };
  section_10_cash_flow: {
    cash_flow: BSRow[];
    analysis: Record<string, string>;
  };
  section_11_quarterly_performance: {
    quarterly_data: QuarterRow[];
    patterns: Record<string, string>;
  };
  section_12_financial_ratios: {
    profitability_ratios: Record<string, string>;
    liquidity_ratios: Record<string, string>;
    leverage_ratios: Record<string, string>;
    efficiency_ratios: Record<string, string>;
    analysis: string;
  };
  section_13_market_performance: {
    market_cap: string; enterprise_value: string; current_price: string;
    high_52w: string; low_52w: string; book_value: string;
    dividend_yield: string; face_value: string; stock_pe: string;
    peg_ratio: string; ev_ebitda_ratio: string; analysis: string;
  };
  section_14_peer_comparison: {
    peers: PeerItem[]; ranking: string;
    premium_discount_valuation: string;
    premium_discount_profitability: string;
    premium_discount_growth: string;
  };
  section_15_graph_dashboard: {
    charts: ChartItem[];
  };
  section_16_swot: {
    strengths: SWOTItem[]; weaknesses: SWOTItem[];
    opportunities: string[]; threats: string[];
    conclusions: string;
  };
  section_17_risk_analysis: {
    risks: RiskItem[]; overall_risk_profile: string;
  };
  section_18_valuation_analysis: {
    relative_valuation: Record<string, string>;
    intrinsic_valuation: Record<string, string>;
    fair_value_estimate: string; upside_potential: string;
    downside_risk: string; assumptions: string;
  };
  section_19_investment_thesis: {
    bull_case: string[]; bear_case: string[];
    key_catalysts: string[]; key_risks: string[];
  };
  section_20_scorecard: {
    categories: ScorecardCategory[];
    total_score: number; max_score: number;
    interpretation: string; interpretation_range: string;
  };
  section_21_final_verdict: {
    long_term_rating: string; subscription_recommendation: string;
    fair_value_estimate: string; margin_of_safety: string;
    investment_horizon: string; summary: string;
  };
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

function severityColor(s: string) {
  if (s === 'High') return 'bg-danger-muted text-danger border-danger-border';
  if (s === 'Low') return 'bg-success-muted text-success border-success-border';
  return 'bg-warning-muted text-warning border-warning-border';
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

function DataTable({ headers, rows }: { headers: string[]; rows: (string | React.ReactNode)[][] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[12px]">
        <thead>
          <tr className="border-b border-surface-300/40">
            {headers.map((h, i) => (
              <th key={i} className={`${i === 0 ? 'text-left' : 'text-right'} py-2 px-2 text-surface-600 font-medium`}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className="border-b border-surface-300/20 hover:bg-surface-50/50">
              {row.map((cell, ci) => (
                <td key={ci} className={`${ci === 0 ? 'text-left text-surface-white' : 'text-right text-surface-700'} py-2 px-2 font-medium`}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function InfoGrid({ items }: { items: { label: string; value: string }[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {items.map((item, i) => (
        <div key={i} className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">{item.label}</p>
          <p className="text-[13px] font-semibold text-surface-white mt-1">{item.value}</p>
        </div>
      ))}
    </div>
  );
}

function ListItems({ items, icon }: { items: string[]; icon?: React.ReactNode }) {
  return (
    <ul className="space-y-1">
      {items.map((item, i) => (
        <li key={i} className="text-[13px] text-surface-700 flex items-start gap-2">
          {icon || <span className="text-brand-light mt-1">•</span>}
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

// ── Section Renderers ──────────────────────────────────────────────
function SectionExecutiveSummary(data: ComprehensiveAnalysis['section_1_executive_summary']) {
  return (
    <div className="space-y-4">
      <InfoGrid items={[
        { label: 'Company', value: data.company_name },
        { label: 'Industry', value: data.industry },
        { label: 'Sector', value: data.sector },
        { label: 'Exchange', value: data.exchange },
        { label: 'Ticker', value: data.ticker },
        { label: 'Market Cap', value: data.market_cap },
        { label: 'Share Price', value: data.share_price },
        { label: '52W High', value: data.high_52w },
        { label: '52W Low', value: data.low_52w },
        { label: 'Face Value', value: data.face_value },
        { label: 'Book Value', value: data.book_value },
        { label: 'Dividend Yield', value: data.dividend_yield },
        { label: 'Stock P/E', value: data.stock_pe },
        { label: 'Industry P/E', value: data.industry_pe },
        { label: 'ROE', value: data.roe },
        { label: 'ROCE', value: data.roce },
        { label: 'D/E Ratio', value: data.debt_to_equity },
      ]} />
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-4">
        <h3 className="text-[13px] font-semibold text-surface-white mb-2">Investment Summary</h3>
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.summary}</p>
      </div>
    </div>
  );
}

function SectionHistoryTimeline(data: ComprehensiveAnalysis['section_2_history_timeline']) {
  return (
    <div className="space-y-4">
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Founding Year</p>
        <p className="text-[14px] font-semibold text-surface-white">{data.founding_year}</p>
      </div>
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Founder Background</p>
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.founder_background}</p>
      </div>
      <DataTable
        headers={['Year', 'Event', 'Strategic Impact']}
        rows={data.timeline_table.map(t => [t.year, t.event, t.impact])}
      />
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.analysis}</p>
      </div>
    </div>
  );
}

function SectionBusinessModel(data: ComprehensiveAnalysis['section_3_business_model']) {
  return (
    <div className="space-y-4">
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Revenue Streams</p>
        <p className="text-[13px] text-surface-700">{data.revenue_streams}</p>
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Business Segments</h3>
        <ListItems items={data.business_segments} />
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Products & Services</h3>
        <ListItems items={data.products_services} />
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Geographic Distribution</h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(data.geo_distribution).map(([region, pct]) => (
            <div key={region} className="bg-surface-50 border border-surface-300/40 rounded-lg p-2.5 flex justify-between">
              <span className="text-[12px] text-surface-700">{region}</span>
              <span className="text-[12px] font-semibold text-surface-white">{pct}</span>
            </div>
          ))}
        </div>
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Customer Segments</h3>
        <ListItems items={data.customer_segments} />
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Distribution Channels</h3>
        <ListItems items={data.distribution_channels} />
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Economic Moat</h3>
        <p className="text-[13px] text-surface-700">{data.economic_moat}</p>
      </div>
      <InfoGrid items={[
        { label: 'Scalability', value: data.scalability },
        { label: 'Recurring Revenue', value: data.recurring_revenue },
        { label: 'Revenue Drivers', value: data.revenue_drivers },
      ]} />
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Growth Levers</h3>
        <ListItems items={data.growth_levers} icon={<TrendingUp className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />} />
      </div>
    </div>
  );
}

function SectionIPORationale(data: ComprehensiveAnalysis['section_4_ipo_rationale']) {
  return (
    <div className="space-y-4">
      <InfoGrid items={[
        { label: 'Fresh Issue', value: data.fresh_issue_pct },
        { label: 'Offer for Sale', value: data.ofs_pct },
        { label: 'Promoter Holding (Pre-IPO)', value: data.promoter_holding_before },
        { label: 'Promoter Holding (Post-IPO)', value: data.promoter_holding_after },
      ]} />
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Use of Proceeds</h3>
        <div className="space-y-2">
          {Object.entries(data.use_of_proceeds).map(([key, val]) => (
            <div key={key} className="flex items-center justify-between bg-surface-50 border border-surface-300/40 rounded-lg p-2.5">
              <span className="text-[13px] text-surface-700 capitalize">{key.replace(/_/g, ' ')}</span>
              <span className="text-[13px] font-semibold text-surface-white">{val}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className={`p-3 rounded-lg border ${data.growth_oriented ? 'bg-success-muted border-success-border' : 'bg-warning-muted border-warning-border'}`}>
          <p className="text-[11px] text-surface-600 uppercase tracking-wider">Growth-Oriented</p>
          <p className="text-[13px] font-semibold text-surface-white mt-1">{data.growth_oriented ? 'Yes' : 'Partial'}</p>
        </div>
        <div className={`p-3 rounded-lg border ${data.exit_event ? 'bg-warning-muted border-warning-border' : 'bg-success-muted border-success-border'}`}>
          <p className="text-[11px] text-surface-600 uppercase tracking-wider">Exit Event</p>
          <p className="text-[13px] font-semibold text-surface-white mt-1">{data.exit_event ? 'Partial Exit' : 'Minimal'}</p>
        </div>
        <div className={`p-3 rounded-lg border ${data.valuation_justified ? 'bg-success-muted border-success-border' : 'bg-danger-muted border-danger-border'}`}>
          <p className="text-[11px] text-surface-600 uppercase tracking-wider">Valuation Justified</p>
          <p className="text-[13px] font-semibold text-surface-white mt-1">{data.valuation_justified ? 'Yes' : 'Stretched'}</p>
        </div>
      </div>
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.conclusions}</p>
      </div>
    </div>
  );
}

function SectionIndustryAnalysis(data: ComprehensiveAnalysis['section_5_industry_analysis']) {
  const pf = data.porters_five_forces;
  const forceColors: Record<string, string> = {
    Low: 'bg-success-muted text-success border-success-border',
    Medium: 'bg-warning-muted text-warning border-warning-border',
    High: 'bg-danger-muted text-danger border-danger-border',
  };
  return (
    <div className="space-y-4">
      <InfoGrid items={[
        { label: 'Industry Overview', value: data.industry_overview },
        { label: 'Market Size', value: data.market_size },
        { label: 'Industry CAGR', value: data.industry_cagr },
        { label: 'TAM', value: data.tam },
        { label: 'SAM', value: data.sam },
      ]} />
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Porter&apos;s Five Forces</h3>
        <div className="space-y-2">
          {[
            ['Competitive Rivalry', pf.competitive_rivalry, pf.competitive_rivalry_detail],
            ['Supplier Power', pf.supplier_power, pf.supplier_power_detail],
            ['Buyer Power', pf.buyer_power, pf.buyer_power_detail],
            ['Threat of Substitutes', pf.threat_of_substitutes, pf.threat_of_substitutes_detail],
            ['Threat of New Entrants', pf.threat_of_new_entrants, pf.threat_of_new_entrants_detail],
          ].map(([name, rating, detail]) => (
            <div key={name as string} className="flex items-start gap-3 p-2.5 bg-surface-50 border border-surface-300/40 rounded-lg">
              <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold uppercase shrink-0 ${forceColors[rating as string] || 'bg-surface-200 text-surface-600'}`}>{rating as string}</span>
              <div>
                <p className="text-[12px] font-semibold text-surface-white">{name as string}</p>
                <p className="text-[12px] text-surface-700 mt-0.5">{detail as string}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Growth Drivers</h3>
        <ListItems items={data.growth_drivers} icon={<TrendingUp className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />} />
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Industry Trends</h3>
        <ListItems items={data.industry_trends} />
      </div>
    </div>
  );
}

function SectionManagementGovernance(data: ComprehensiveAnalysis['section_6_management_governance']) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <ScoreRing score={data.score_out_of_10 * 10} size={48} strokeWidth={4} />
        <div>
          <p className="text-[13px] font-semibold text-surface-white">Governance Score</p>
          <p className="text-[12px] text-surface-600">{data.score_out_of_10}/10</p>
        </div>
      </div>
      <InfoGrid items={[
        { label: 'CEO', value: data.ceo },
        { label: 'CFO', value: data.cfo },
        { label: 'Independent Directors', value: data.independent_directors },
      ]} />
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Promoters</p>
          <p className="text-[12px] text-surface-700 leading-relaxed">{data.promoters}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Track Record</p>
          <p className="text-[12px] text-surface-700 leading-relaxed">{data.track_record}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Governance Quality</p>
          <p className="text-[12px] text-surface-700 leading-relaxed">{data.governance_quality}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Capital Allocation</p>
          <p className="text-[12px] text-surface-700 leading-relaxed">{data.capital_allocation}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Related-Party Transactions</p>
          <p className="text-[12px] text-surface-700 leading-relaxed">{data.related_party_transactions}</p>
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Auditor History</p>
          <p className="text-[12px] text-surface-700 leading-relaxed">{data.auditor_history}</p>
        </div>
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Board Members</h3>
        <ListItems items={data.board_members} />
      </div>
      {data.governance_concerns && (
        <div className="bg-warning-muted border border-warning-border rounded-lg p-3">
          <p className="text-[12px] font-semibold text-warning mb-1">⚠ Governance Notes</p>
          <p className="text-[12px] text-surface-700">{data.governance_concerns}</p>
        </div>
      )}
    </div>
  );
}

function SectionShareholding(data: ComprehensiveAnalysis['section_7_shareholding_pattern']) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Current Shareholding Pattern</h3>
        <div className="space-y-2">
          {Object.entries(data.current_pattern).map(([key, val]) => (
            <div key={key} className="flex items-center justify-between bg-surface-50 border border-surface-300/40 rounded-lg p-2.5">
              <span className="text-[13px] text-surface-700 capitalize">{key.replace(/_/g, ' ')}</span>
              <span className="text-[13px] font-semibold text-surface-white">{val}</span>
            </div>
          ))}
        </div>
      </div>
      <div>
        <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">Historical Trends</h3>
        <DataTable
          headers={['Quarter', 'Promoters', 'FIIs', 'DIIs', 'Retail']}
          rows={data.historical_trends.map(t => [t.quarter, t.promoters, t.fiis, t.dii, t.retail])}
        />
      </div>
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.analysis}</p>
      </div>
    </div>
  );
}

function SectionProfitLoss(data: ComprehensiveAnalysis['section_8_profit_loss']) {
  return (
    <div className="space-y-4">
      <DataTable
        headers={['Metric', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']}
        rows={data.income_statement.map(r => [r.metric, r.y1, r.y2, r.y3, r.y4, r.y5])}
      />
      <InfoGrid items={Object.entries(data.cagr_analysis).map(([k, v]) => ({ label: k.replace(/_/g, ' ').toUpperCase(), value: v }))} />
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.margin_analysis}</p>
      </div>
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.profitability_trends}</p>
      </div>
    </div>
  );
}

function SectionBalanceSheet(data: ComprehensiveAnalysis['section_9_balance_sheet']) {
  return (
    <div className="space-y-4">
      <DataTable
        headers={['Metric', 'Year 1', 'Year 2', 'Year 3']}
        rows={data.balance_sheet.map(r => [r.metric, r.y1, r.y2, r.y3])}
      />
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.financial_strength}</p>
      </div>
    </div>
  );
}

function SectionCashFlow(data: ComprehensiveAnalysis['section_10_cash_flow']) {
  return (
    <div className="space-y-4">
      <DataTable
        headers={['Metric', 'Year 1', 'Year 2', 'Year 3']}
        rows={data.cash_flow.map(r => [r.metric, r.y1, r.y2, r.y3])}
      />
      <InfoGrid items={Object.entries(data.analysis).map(([k, v]) => ({
        label: k.replace(/_/g, ' ').toUpperCase(),
        value: v,
      }))} />
    </div>
  );
}

function SectionQuarterlyPerformance(data: ComprehensiveAnalysis['section_11_quarterly_performance']) {
  return (
    <div className="space-y-4">
      <DataTable
        headers={['Quarter', 'Revenue', 'EBITDA', 'PAT', 'EPS', 'EBITDA Margin', 'Net Margin']}
        rows={data.quarterly_data.map(q => [q.quarter, q.revenue, q.ebitda, q.pat, q.eps, q.ebitda_margin, q.net_margin])}
      />
      <InfoGrid items={Object.entries(data.patterns).map(([k, v]) => ({ label: k.toUpperCase(), value: v }))} />
    </div>
  );
}

function SectionFinancialRatios(data: ComprehensiveAnalysis['section_12_financial_ratios']) {
  const RatioTable = ({ title, ratios }: { title: string; ratios: Record<string, string> }) => (
    <div>
      <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">{title}</h3>
      <div className="space-y-1">
        {Object.entries(ratios).map(([k, v]) => (
          <div key={k} className="flex items-center justify-between bg-surface-50 border border-surface-300/40 rounded-lg p-2">
            <span className="text-[12px] text-surface-700 capitalize">{k.replace(/_/g, ' ')}</span>
            <span className="text-[12px] font-semibold text-surface-white">{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <RatioTable title="Profitability Ratios" ratios={data.profitability_ratios} />
        <RatioTable title="Liquidity Ratios" ratios={data.liquidity_ratios} />
        <RatioTable title="Leverage Ratios" ratios={data.leverage_ratios} />
        <RatioTable title="Efficiency Ratios" ratios={data.efficiency_ratios} />
      </div>
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.analysis}</p>
      </div>
    </div>
  );
}

function SectionMarketPerformance(data: ComprehensiveAnalysis['section_13_market_performance']) {
  return (
    <div className="space-y-4">
      <InfoGrid items={[
        { label: 'Market Cap', value: data.market_cap },
        { label: 'Enterprise Value', value: data.enterprise_value },
        { label: 'Current Price', value: data.current_price },
        { label: '52W High', value: data.high_52w },
        { label: '52W Low', value: data.low_52w },
        { label: 'Book Value', value: data.book_value },
        { label: 'Dividend Yield', value: data.dividend_yield },
        { label: 'Face Value', value: data.face_value },
        { label: 'Stock P/E', value: data.stock_pe },
        { label: 'PEG Ratio', value: data.peg_ratio },
        { label: 'EV/EBITDA', value: data.ev_ebitda_ratio },
      ]} />
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.analysis}</p>
      </div>
    </div>
  );
}

function SectionPeerComparison(data: ComprehensiveAnalysis['section_14_peer_comparison']) {
  return (
    <div className="space-y-4">
      <DataTable
        headers={['Company', 'M Cap', 'Revenue', 'EBITDA', 'PAT', 'P/E', 'EV/EBITDA', 'ROE', 'ROCE', 'D/E', 'Rev Growth']}
        rows={data.peers.map(p => [p.name, p.mcap, p.rev, p.ebitda, p.pat, p.pe, p.ev_ebitda, p.roe, p.roce, p.de, p.rev_growth])}
      />
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.ranking}</p>
      </div>
      <InfoGrid items={[
        { label: 'Valuation Premium/Discount', value: data.premium_discount_valuation },
        { label: 'Profitability Premium/Discount', value: data.premium_discount_profitability },
        { label: 'Growth Premium/Discount', value: data.premium_discount_growth },
      ]} />
    </div>
  );
}

function SectionGraphDashboard(data: ComprehensiveAnalysis['section_15_graph_dashboard']) {
  return (
    <div className="space-y-4">
      {data.charts.map((chart, i) => {
        const hasBars = chart.values && chart.values.length > 1;
        const maxVal = hasBars ? Math.max(...chart.values) : 1;
        return (
          <div key={i} className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
            <p className="text-[12px] font-semibold text-surface-white mb-0.5">{chart.name}</p>
            <p className="text-[11px] text-surface-700 mb-2">{chart.description}</p>
            {hasBars && (
              <div className="flex items-end gap-1.5 h-24">
                {chart.values.map((v, vi) => {
                  const pct = (v / maxVal) * 100;
                  const color = chart.name.includes('Debt')
                    ? 'bg-amber-400'
                    : ['bg-emerald-400', 'bg-blue-400', 'bg-violet-400', 'bg-cyan-400'][vi % 4];
                  return (
                    <div key={vi} className="flex-1 flex flex-col items-center justify-end h-full">
                      <span className="text-[9px] text-surface-700 mb-0.5 font-medium">
                        {chart.unit === '%' ? `${Math.round(v)}%` : chart.unit ? `${chart.unit}${v >= 1000 ? `${(v/1000).toFixed(1)}k` : v.toLocaleString()}` : v.toLocaleString()}
                      </span>
                      <div
                        className={`w-full ${color} rounded-t-sm transition-all duration-300`}
                        style={{ height: `${Math.max(pct, 4)}%` }}
                      />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function SectionSWOT(data: ComprehensiveAnalysis['section_16_swot']) {
  const SWOTBox = ({ title, items, color }: { title: string; items: SWOTItem[] | string[]; color: string }) => {
    const isSWOT = items.length > 0 && typeof items[0] === 'object';
    return (
      <div className={`bg-surface-50 border-l-4 ${color} rounded-lg p-3`}>
        <h3 className="text-[13px] font-semibold text-surface-white mb-2">{title}</h3>
        <ul className="space-y-1.5">
          {(isSWOT ? items as SWOTItem[] : (items as string[]).map(s => ({ item: s, evidence: '' }))).map((item, i) => (
            <li key={i} className="text-[12px] text-surface-700">
              <span className="font-medium text-surface-white">{item.item}</span>
              {item.evidence && <span className="block text-[11px] text-surface-600 mt-0.5">{item.evidence}</span>}
            </li>
          ))}
        </ul>
      </div>
    );
  };
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <SWOTBox title="Strengths" items={data.strengths} color="border-success" />
        <SWOTBox title="Weaknesses" items={data.weaknesses} color="border-danger" />
        <SWOTBox title="Opportunities" items={data.opportunities} color="border-brand-light" />
        <SWOTBox title="Threats" items={data.threats} color="border-warning" />
      </div>
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.conclusions}</p>
      </div>
    </div>
  );
}

function SectionRiskAnalysis(data: ComprehensiveAnalysis['section_17_risk_analysis']) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        {data.risks.map((r, i) => (
          <div key={i} className="flex items-start gap-3 p-2.5 bg-surface-50 border border-surface-300/40 rounded-lg">
            <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold uppercase shrink-0 ${severityColor(r.rating)}`}>{r.rating}</span>
            <div>
              <p className="text-[12px] font-semibold text-surface-white">{r.category}</p>
              <p className="text-[12px] text-surface-700 mt-0.5">{r.detail}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] font-semibold text-surface-white mb-1">Overall Risk Profile</p>
        <p className="text-[13px] text-surface-700">{data.overall_risk_profile}</p>
      </div>
    </div>
  );
}

function SectionValuation(data: ComprehensiveAnalysis['section_18_valuation_analysis']) {
  const VTable = ({ title, ratios }: { title: string; ratios: Record<string, string> }) => (
    <div>
      <h3 className="text-[13px] font-semibold text-surface-white mb-1.5">{title}</h3>
      <div className="space-y-1">
        {Object.entries(ratios).map(([k, v]) => (
          <div key={k} className="flex items-center justify-between bg-surface-50 border border-surface-300/40 rounded-lg p-2">
            <span className="text-[12px] text-surface-700 capitalize">{k.replace(/_/g, ' ')}</span>
            <span className="text-[12px] font-semibold text-surface-white">{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <VTable title="Relative Valuation" ratios={data.relative_valuation} />
        <VTable title="Intrinsic Valuation (DCF)" ratios={data.intrinsic_valuation} />
      </div>
      <InfoGrid items={[
        { label: 'Fair Value Estimate', value: data.fair_value_estimate },
        { label: 'Upside Potential', value: data.upside_potential },
        { label: 'Downside Risk', value: data.downside_risk },
      ]} />
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
        <p className="text-[13px] font-semibold text-surface-white mb-1">Assumptions</p>
        <p className="text-[12px] text-surface-700 leading-relaxed">{data.assumptions}</p>
      </div>
    </div>
  );
}

function SectionInvestmentThesis(data: ComprehensiveAnalysis['section_19_investment_thesis']) {
  return (
    <div className="space-y-4">
      <div className="bg-success-muted border border-success-border rounded-lg p-4">
        <h3 className="text-[13px] font-semibold text-success flex items-center gap-2 mb-2"><ThumbsUp className="w-4 h-4" /> Bull Case — Reasons to Invest</h3>
        <ListItems items={data.bull_case} icon={<CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />} />
      </div>
      <div className="bg-danger-muted border border-danger-border rounded-lg p-4">
        <h3 className="text-[13px] font-semibold text-danger flex items-center gap-2 mb-2"><ThumbsDown className="w-4 h-4" /> Bear Case — Reasons to Avoid</h3>
        <ListItems items={data.bear_case} icon={<XCircle className="w-3.5 h-3.5 text-danger shrink-0 mt-0.5" />} />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <h3 className="text-[12px] font-semibold text-surface-white mb-1.5 flex items-center gap-1.5"><TrendingUp className="w-3.5 h-3.5 text-success" /> Key Catalysts</h3>
          <ListItems items={data.key_catalysts} />
        </div>
        <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
          <h3 className="text-[12px] font-semibold text-surface-white mb-1.5 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5 text-danger" /> Key Risks</h3>
          <ListItems items={data.key_risks} />
        </div>
      </div>
    </div>
  );
}

function SectionScorecard(data: ComprehensiveAnalysis['section_20_scorecard']) {
  const interpColor = data.interpretation === 'Exceptional' || data.interpretation === 'Strong'
    ? 'text-success' : data.interpretation === 'Good' ? 'text-brand-light'
    : data.interpretation === 'Average' ? 'text-warning' : 'text-danger';
  return (
    <div className="space-y-4">
      <DataTable
        headers={['Category', 'Score']}
        rows={data.categories.map(c => [c.label, `${c.score}/10`])}
      />
      <div className="flex items-center justify-between bg-surface-50 border border-surface-300/40 rounded-lg p-4">
        <div>
          <p className="text-[12px] text-surface-600 uppercase tracking-wider font-medium">Total Score</p>
          <p className="text-2xl font-bold text-surface-white">{data.total_score}/{data.max_score}</p>
        </div>
        <div className="text-right">
          <p className="text-[12px] text-surface-600 uppercase tracking-wider font-medium">Interpretation</p>
          <p className={`text-lg font-bold ${interpColor}`}>{data.interpretation}</p>
          <p className="text-[10px] text-surface-600 mt-0.5">{data.interpretation_range}</p>
        </div>
      </div>
    </div>
  );
}

function SectionFinalVerdict(data: ComprehensiveAnalysis['section_21_final_verdict']) {
  const recColor = data.long_term_rating === 'Strong Buy' ? 'text-success'
    : data.long_term_rating === 'Buy' ? 'text-brand-light'
    : data.long_term_rating === 'Hold / Neutral' ? 'text-warning' : 'text-danger';
  return (
    <div className="space-y-4">
      <InfoGrid items={[
        { label: 'Long-Term Rating', value: data.long_term_rating },
        { label: 'Subscription Recommendation', value: data.subscription_recommendation },
        { label: 'Fair Value Estimate', value: data.fair_value_estimate },
        { label: 'Margin of Safety', value: data.margin_of_safety },
        { label: 'Investment Horizon', value: data.investment_horizon },
      ]} />
      <div className={`text-center py-5 rounded-lg border ${data.long_term_rating === 'Strong Buy' || data.long_term_rating === 'Buy' ? 'bg-success-muted border-success-border' : data.long_term_rating === 'Hold / Neutral' ? 'bg-warning-muted border-warning-border' : 'bg-danger-muted border-danger-border'}`}>
        <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-1">Final Verdict</p>
        <p className={`text-xl font-bold ${recColor}`}>{data.long_term_rating}</p>
        <p className="text-[12px] text-surface-600 mt-1">{data.subscription_recommendation}</p>
      </div>
      <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-4">
        <p className="text-[13px] text-surface-700 leading-relaxed">{data.summary}</p>
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
    { id: 's1', title: '1. Executive Summary', icon: <FileText className="w-4 h-4 text-brand-light" />, render: () => SectionExecutiveSummary(a.section_1_executive_summary) },
    { id: 's2', title: '2. Company History & Timeline', icon: <Clock className="w-4 h-4 text-brand-light" />, render: () => SectionHistoryTimeline(a.section_2_history_timeline) },
    { id: 's3', title: '3. Business Model Analysis', icon: <Building2 className="w-4 h-4 text-brand-light" />, render: () => SectionBusinessModel(a.section_3_business_model) },
    { id: 's4', title: '4. IPO Rationale', icon: <Target className="w-4 h-4 text-brand-light" />, render: () => SectionIPORationale(a.section_4_ipo_rationale) },
    { id: 's5', title: '5. Industry Analysis', icon: <BarChart3 className="w-4 h-4 text-brand-light" />, render: () => SectionIndustryAnalysis(a.section_5_industry_analysis) },
    { id: 's6', title: '6. Management & Corporate Governance', icon: <Users className="w-4 h-4 text-brand-light" />, render: () => SectionManagementGovernance(a.section_6_management_governance) },
    { id: 's7', title: '7. Shareholding Pattern Analysis', icon: <PieChart className="w-4 h-4 text-brand-light" />, render: () => SectionShareholding(a.section_7_shareholding_pattern) },
    { id: 's8', title: '8. Profit & Loss Analysis', icon: <DollarSign className="w-4 h-4 text-brand-light" />, render: () => SectionProfitLoss(a.section_8_profit_loss) },
    { id: 's9', title: '9. Balance Sheet Analysis', icon: <Database className="w-4 h-4 text-brand-light" />, render: () => SectionBalanceSheet(a.section_9_balance_sheet) },
    { id: 's10', title: '10. Cash Flow Analysis', icon: <Activity className="w-4 h-4 text-brand-light" />, render: () => SectionCashFlow(a.section_10_cash_flow) },
    { id: 's11', title: '11. Quarterly Performance Analysis', icon: <LineChart className="w-4 h-4 text-brand-light" />, render: () => SectionQuarterlyPerformance(a.section_11_quarterly_performance) },
    { id: 's12', title: '12. Financial Ratios', icon: <Scale className="w-4 h-4 text-brand-light" />, render: () => SectionFinancialRatios(a.section_12_financial_ratios) },
    { id: 's13', title: '13. Market Performance Analysis', icon: <TrendingUp className="w-4 h-4 text-brand-light" />, render: () => SectionMarketPerformance(a.section_13_market_performance) },
    { id: 's14', title: '14. Peer Comparison', icon: <GitCompare className="w-4 h-4 text-brand-light" />, render: () => SectionPeerComparison(a.section_14_peer_comparison) },
    { id: 's15', title: '15. Historical Financial Graph Dashboard', icon: <BarChart3 className="w-4 h-4 text-brand-light" />, render: () => SectionGraphDashboard(a.section_15_graph_dashboard) },
    { id: 's16', title: '16. SWOT Analysis', icon: <Layers className="w-4 h-4 text-brand-light" />, render: () => SectionSWOT(a.section_16_swot) },
    { id: 's17', title: '17. Risk Analysis', icon: <Shield className="w-4 h-4 text-warning" />, render: () => SectionRiskAnalysis(a.section_17_risk_analysis) },
    { id: 's18', title: '18. Valuation Analysis', icon: <Scale className="w-4 h-4 text-brand-light" />, render: () => SectionValuation(a.section_18_valuation_analysis) },
    { id: 's19', title: '19. Investment Thesis', icon: <BookOpen className="w-4 h-4 text-brand-light" />, render: () => SectionInvestmentThesis(a.section_19_investment_thesis) },
    { id: 's20', title: '20. Final Scorecard', icon: <Award className="w-4 h-4 text-brand-light" />, render: () => SectionScorecard(a.section_20_scorecard) },
    { id: 's21', title: '21. Final Verdict', icon: <Sparkles className="w-4 h-4 text-warning" />, render: () => SectionFinalVerdict(a.section_21_final_verdict) },
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
