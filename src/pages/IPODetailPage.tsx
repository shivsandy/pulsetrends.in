import { Link, useParams } from 'react-router-dom';
import { ipoStocks } from '../data/ipoData';
import type { IPOStock } from '../data/ipoData';
import PageSeo from '../components/PageSeo';
import Breadcrumbs, { type Crumb } from '../components/Breadcrumbs';
import { canonical } from '../seo/config';
import { financialProductSchema } from '../seo/schema';
import { ArrowLeft, Building2, Calendar, Shield, AlertTriangle, Brain, Cpu, Leaf, FlaskConical, Landmark, Sprout, Sparkles, ExternalLink, Link2 } from 'lucide-react';
import Badge from '../components/Badge';
import ScoreRing from '../components/ScoreRing';
import { slugify } from '../seo/config';

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

function getRiskSeverity(indicator: string) {
  if (indicator.includes('🔴')) return { label: 'High', className: 'bg-danger-muted text-danger border-danger-border' };
  if (indicator.includes('🟢')) return { label: 'Low', className: 'bg-success-muted text-success border-success-border' };
  return { label: 'Medium', className: 'bg-warning-muted text-warning border-warning-border' };
}

interface IPODetailPageProps {
  slug?: string;
  onBack?: () => void;
}

export default function IPODetailPage({ slug: propSlug, onBack }: IPODetailPageProps) {
  const params = useParams();
  const slug = propSlug || params.slug || '';

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
  const financialSchema = financialProductSchema({
    name: stock.company,
    description: stock.description || `${stock.company} (${stock.ticker}) — IPO analysis with AI scoring and risk assessment.`,
    urlPath: path,
    category: stock.sector,
    identifier: stock.ticker,
  });

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

      <article className="max-w-3xl mx-auto">
        <Breadcrumbs items={([
          { name: 'Home', path: '/' },
          { name: 'IPO Analysis', path: '/ipo-analysis' },
          { name: stock.company },
        ] as Crumb[])} />

        {onBack ? (
          <button onClick={onBack} className="mb-4 inline-flex items-center gap-2 text-[13px] text-surface-700 hover:text-surface-white transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to IPO list
          </button>
        ) : (
          <Link to="/ipo-analysis" className="mb-4 inline-flex items-center gap-2 text-[13px] text-surface-700 hover:text-surface-white transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to IPO list
          </Link>
        )}

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

          {stock.aiVerdict && (
            <div className="mt-4 px-4 py-3 rounded-lg bg-brand-muted border border-brand-border flex items-center gap-3">
              <Sparkles className="w-4 h-4 text-brand-light flex-shrink-0" />
              <p className="text-[13px] font-semibold text-brand-light">{stock.aiVerdict}</p>
            </div>
          )}
        </header>

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
          <div className="bg-surface-100 border border-surface-300/40 rounded-lg p-3">
            <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Registrar</p>
            <p className="text-[14px] font-semibold text-surface-white mt-1">{stock.registrar || 'TBA'}</p>
          </div>
        </section>

        <section className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-6">
          <h2 className="text-lg font-semibold text-surface-white mb-2">Company Overview</h2>
          <p className="text-[14px] text-surface-700 leading-relaxed">{stock.description}</p>
          {stock.about && stock.about !== stock.description && (
            <p className="text-[14px] text-surface-700 leading-relaxed mt-3">{stock.about}</p>
          )}
        </section>

        {stock.strengths.length > 0 && (
          <section className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-6">
            <h2 className="text-lg font-semibold text-surface-white mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-success" /> Strengths
            </h2>
            <ul className="space-y-2">
              {stock.strengths.map((s, i) => (
                <li key={i} className="text-[13px] text-surface-700 leading-relaxed flex items-start gap-2">
                  <span className="text-success mt-1">✓</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {stock.risks.length > 0 && (
          <section className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-6">
            <h2 className="text-lg font-semibold text-surface-white mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-warning" /> Risks
            </h2>
            <ul className="space-y-2">
              {stock.risks.map((r, i) => {
                const sev = getRiskSeverity(r.indicator);
                return (
                  <li key={i} className="text-[13px] text-surface-700 leading-relaxed flex items-start gap-2">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded border font-medium uppercase tracking-wider mt-0.5 ${sev.className}`}>{sev.label}</span>
                    <span>{r.text}</span>
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        {stock.aiAnalysis && (
          <section className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-6">
            <h2 className="text-lg font-semibold text-surface-white mb-3 flex items-center gap-2">
              <Brain className="w-4 h-4 text-brand-light" /> AI Analysis
            </h2>
            <div className="text-[13px] text-surface-700 leading-relaxed whitespace-pre-line">{stock.aiAnalysis}</div>
          </section>
        )}

        <section className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-6">
          <h2 className="text-lg font-semibold text-surface-white mb-3">AI Scores</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(stock.aiScores).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between p-2.5 bg-surface-50 border border-surface-300/40 rounded-md">
                <span className="text-[12px] text-surface-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                <span className="text-[14px] font-bold text-surface-white">{value}/100</span>
              </div>
            ))}
          </div>
        </section>

        {stock.rhpUrl && (
          <section className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 mb-6">
            <h2 className="text-lg font-semibold text-surface-white mb-3 flex items-center gap-2">
              <Link2 className="w-4 h-4" /> Documents
            </h2>
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
          </section>
        )}

        <footer className="text-[11px] text-surface-500 mt-8 mb-4">
          <p>Canonical URL: <a href={url} className="text-brand hover:underline">{url}</a></p>
        </footer>
      </article>
    </>
  );
}
