import { Link, useParams } from 'react-router-dom';
import { ipoStocks } from '../data/ipoData';
import type { IPOStock } from '../data/ipoData';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { canonical, slugify } from '../seo/config';
import { financialProductSchema } from '../seo/schema';
import {
  ArrowLeft, Building2, Calendar, Brain,
  Cpu, Leaf, FlaskConical, Landmark, Sprout, ExternalLink
} from 'lucide-react';
import Badge from '../components/Badge';
import ScoreRing from '../components/ScoreRing';

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

// ── Main Component ────────────────────────────────────────────────
export default function IPODetailPage() {
  const params = useParams();
  const slug = params.slug || '';
  const stock = ipoStocks.find((s) => makeSlug(s) === slug);
  const SectorIcon = (stock && sectorIcons[stock.sector]) || Building2;

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
              </div>
              <h1 className="text-2xl font-bold text-surface-white leading-tight">{stock.company}</h1>
              <p className="text-[13px] text-surface-600 mt-1">{stock.sector} · {stock.listingExchange}</p>
            </div>
            <div className="flex flex-col items-center">
              <ScoreRing score={stock.aiScores.overall} size={64} strokeWidth={5} showLabel />
              <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mt-1">AI Score</p>
            </div>
          </div>
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
        </section>

        {/* COMPANY OVERVIEW */}
        <SectionBox title="Company Overview">
          <p className="text-[14px] text-surface-700 leading-relaxed">{stock.description}</p>
          {stock.about && stock.about !== stock.description && (
            <p className="text-[14px] text-surface-700 leading-relaxed mt-3">{stock.about}</p>
          )}
        </SectionBox>

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
