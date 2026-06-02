import { useMemo, useState } from 'react';
import { Search, Gift, Sparkles, ChevronDown, ChevronUp, TrendingUp, TrendingDown, Globe, Shield, ArrowLeft, ExternalLink, AtSign, MessageCircle, Send, Brain } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { cryptoProjects } from '../data/cryptoData';
import type { CryptoProject } from '../data/cryptoData';
import Badge from '../components/Badge';
import PageSeo from '../components/PageSeo';
import Breadcrumbs, { type Crumb } from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';
import { slugify } from '../seo/config';
import { financialProductSchema } from '../seo/schema';

const AIRDROPS = cryptoProjects.filter((p) => p.category === 'airdrop');

const RISK_LABELS: Record<string, string> = {
  overallRisk: 'Overall',
  smartContractRisk: 'Smart Contract',
  teamRisk: 'Team',
  marketRisk: 'Market',
  regulatoryRisk: 'Regulatory',
  rugPullPotential: 'Rug Pull',
  liquidityRisk: 'Liquidity',
  dilutionRisk: 'Dilution',
};

const RISK_ORDER = ['overallRisk', 'smartContractRisk', 'teamRisk', 'marketRisk', 'regulatoryRisk', 'rugPullPotential', 'liquidityRisk', 'dilutionRisk'];

function makeAirdropSlug(p: CryptoProject): string {
  return `${slugify(p.name)}-${p.id}`;
}

function RiskBadge({ level }: { level: string }) {
  const color =
    level === 'low'
      ? 'bg-success-muted text-success border-success-border'
      : level === 'high'
        ? 'bg-danger-muted text-danger border-danger-border'
        : 'bg-warning-muted text-warning border-warning-border';
  return (
    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${color} font-medium uppercase tracking-wider`}>
      {level}
    </span>
  );
}

function SocialIcon({ url, icon: Icon, label }: { url: string; icon: React.ElementType; label: string }) {
  if (!url) return null;
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      title={label}
      className="w-7 h-7 rounded-md bg-surface-200 border border-surface-300 flex items-center justify-center hover:bg-surface-300 hover:border-surface-500 transition-all"
      aria-label={label}
    >
      <Icon className="w-3.5 h-3.5 text-surface-700" />
    </a>
  );
}

function AirdropCardInline({
  project,
  index,
  expandedSlug,
  onToggle,
}: {
  project: CryptoProject;
  index: number;
  expandedSlug: string | null;
  onToggle: (slug: string | null) => void;
}) {
  const slug = makeAirdropSlug(project);
  const isExpanded = expandedSlug === slug;
  const ai = project.aiAnalysis;
  const statusColor =
    project.status === 'active' ? 'success' : project.status === 'upcoming' ? 'warning' : 'info';

  return (
    <div
      className="bg-surface-100 border border-surface-300/60 rounded-xl overflow-hidden animate-fade-in"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div className="p-5">
        <div className="flex items-start justify-between mb-3 gap-3">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className="w-10 h-10 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center shrink-0">
              <Gift className="w-5 h-5 text-surface-700" />
            </div>
            <div className="min-w-0">
              <h3 className="font-semibold text-surface-white text-[15px] leading-tight">
                <Link to={`/airdrops/${slug}`} className="hover:text-brand-light transition-colors">
                  {project.name}
                </Link>
              </h3>
              <p className="text-[12px] text-surface-600 mt-0.5 font-mono">
                {project.ticker} · {project.chain}
              </p>
            </div>
          </div>
          <Badge variant={statusColor} size="sm">
            {project.status}
          </Badge>
        </div>

        <p className="text-[13px] text-surface-700 leading-relaxed mb-3 line-clamp-2">
          {project.description}
        </p>

        <div className="grid grid-cols-3 gap-2 mb-3 text-[12px]">
          {project.estimatedValue && (
            <div>
              <p className="text-[10px] text-surface-600 uppercase tracking-wider">Est. Value</p>
              <p className="font-semibold text-surface-white">{project.estimatedValue}</p>
            </div>
          )}
          {project.tgeDate && (
            <div>
              <p className="text-[10px] text-surface-600 uppercase tracking-wider">TGE</p>
              <p className="font-semibold text-surface-white">{project.tgeDate}</p>
            </div>
          )}
          {ai && (
            <div>
              <p className="text-[10px] text-surface-600 uppercase tracking-wider">Conviction</p>
              <p className="font-semibold text-surface-white">{ai.convictionScore}/100</p>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-surface-300/40">
          <div className="flex items-center gap-2 text-[12px] text-surface-700">
            <Brain className="w-3.5 h-3.5" />
            <span>{ai ? ai.sentiment : 'No analysis'}</span>
          </div>
          <button
            type="button"
            onClick={() => onToggle(isExpanded ? null : slug)}
            className="flex items-center gap-1 text-[12px] font-medium text-surface-700 hover:text-brand-light transition-colors"
            aria-expanded={isExpanded}
          >
            {isExpanded ? 'Hide details' : 'View details'}
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {isExpanded && ai && (
        <div className="px-5 pb-5 border-t border-surface-300/40 bg-surface-50/40 animate-fade-in">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-4">
            {RISK_ORDER.map((key) => {
              const level = (ai.riskAssessment as Record<string, string>)[key] || 'medium';
              return (
                <div key={key} className="flex items-center justify-between p-2 bg-surface-200/40 rounded-md">
                  <span className="text-[11px] text-surface-700">{RISK_LABELS[key]}</span>
                  <RiskBadge level={level} />
                </div>
              );
            })}
          </div>
          {ai.keyDrivers.length > 0 && (
            <div className="mt-4">
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-2">Key Drivers</p>
              <ul className="space-y-1">
                {ai.keyDrivers.slice(0, 3).map((d, i) => (
                  <li key={i} className="text-[12px] text-surface-700 flex items-start gap-1.5">
                    <TrendingUp className="w-3 h-3 text-success mt-0.5 shrink-0" />
                    <span>{d}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {ai.verdict && (
            <div className="mt-4 p-3 bg-brand-muted border border-brand-border rounded-md">
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1">Verdict</p>
              <p className="text-[12px] text-surface-700 leading-relaxed">{ai.verdict}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AirdropDetailView({ project }: { project: CryptoProject }) {
  const ai = project.aiAnalysis;
  const slug = makeAirdropSlug(project);
  const schema = financialProductSchema({
    name: project.name,
    description: project.description,
    urlPath: `/airdrops/${slug}`,
    category: 'Airdrop',
    identifier: project.ticker,
  });
  return (
    <article className="max-w-3xl mx-auto">
      <PageSeo
        meta={{
          ...ROUTES.airdrops,
          title: `${project.name} Airdrop | PulseTrends`,
          description: project.description.slice(0, 160),
          path: `/airdrops/${slug}`,
          ogType: 'website',
        }}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Airdrops', path: '/airdrops' },
          { name: project.name, path: `/airdrops/${slug}` },
        ]}
      />
      <script type="application/ld+json">{JSON.stringify(schema)}</script>

      <Link
        to="/airdrops"
        className="inline-flex items-center gap-1.5 text-[12px] text-surface-600 hover:text-surface-900 transition-colors mb-4"
      >
        <ArrowLeft className="w-3 h-3" />
        Back to all airdrops
      </Link>

      <div className="border-b border-surface-300/60 pb-6 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Badge variant="success" size="md">Airdrop</Badge>
          <Badge variant={project.status === 'active' ? 'success' : project.status === 'upcoming' ? 'warning' : 'info'} size="md">
            {project.status}
          </Badge>
        </div>
        <h1 className="text-3xl font-bold text-surface-white tracking-tight">{project.name}</h1>
        <p className="text-[14px] text-surface-600 mt-2 font-mono">
          {project.ticker} · {project.chain}
        </p>
        <p className="text-[15px] text-surface-700 mt-4 leading-relaxed">{project.description}</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
        {project.estimatedValue && (
          <div className="bg-surface-100 border border-surface-300/60 rounded-lg p-3">
            <p className="text-[10px] text-surface-600 uppercase tracking-wider">Est. Value</p>
            <p className="text-[15px] font-semibold text-surface-white mt-1">{project.estimatedValue}</p>
          </div>
        )}
        {project.tgeDate && (
          <div className="bg-surface-100 border border-surface-300/60 rounded-lg p-3">
            <p className="text-[10px] text-surface-600 uppercase tracking-wider">TGE</p>
            <p className="text-[15px] font-semibold text-surface-white mt-1">{project.tgeDate}</p>
          </div>
        )}
        {ai && (
          <div className="bg-surface-100 border border-surface-300/60 rounded-lg p-3">
            <p className="text-[10px] text-surface-600 uppercase tracking-wider">Conviction</p>
            <p className="text-[15px] font-semibold text-surface-white mt-1">{ai.convictionScore}/100</p>
          </div>
        )}
      </div>

      {(project.socialLinks.website || project.socialLinks.twitter || project.socialLinks.discord || project.socialLinks.telegram) && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-surface-white mb-3 flex items-center gap-2">
            <Globe className="w-4 h-4" />
            Official Links
          </h2>
          <div className="flex flex-wrap gap-2">
            <SocialIcon url={project.socialLinks.website} icon={Globe} label="Website" />
            <SocialIcon url={project.socialLinks.twitter} icon={AtSign} label="Twitter" />
            <SocialIcon url={project.socialLinks.discord} icon={MessageCircle} label="Discord" />
            <SocialIcon url={project.socialLinks.telegram} icon={Send} label="Telegram" />
            {project.website && (
              <a
                href={project.website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-brand text-white text-[12px] font-medium rounded-md hover:bg-brand-hover transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
                Visit Project
              </a>
            )}
          </div>
        </section>
      )}

      {ai && (
        <section className="space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-surface-white mb-3 flex items-center gap-2">
              <Brain className="w-4 h-4" />
              AI Analysis
            </h2>
            {ai.summary && <p className="text-[14px] text-surface-700 leading-relaxed">{ai.summary}</p>}
          </div>

          <div className="bg-surface-100 border border-surface-300/60 rounded-xl p-5">
            <h3 className="text-[15px] font-semibold text-surface-white mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Risk Assessment
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {RISK_ORDER.map((key) => {
                const level = (ai.riskAssessment as Record<string, string>)[key] || 'medium';
                return (
                  <div key={key} className="flex items-center justify-between p-2 bg-surface-200/40 rounded-md">
                    <span className="text-[11px] text-surface-700">{RISK_LABELS[key]}</span>
                    <RiskBadge level={level} />
                  </div>
                );
              })}
            </div>
          </div>

          {ai.keyDrivers.length > 0 && (
            <div>
              <h3 className="text-[15px] font-semibold text-surface-white mb-2 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-success" />
                Key Drivers
              </h3>
              <ul className="space-y-1.5">
                {ai.keyDrivers.map((d, i) => (
                  <li key={i} className="text-[13px] text-surface-700 flex items-start gap-2">
                    <TrendingUp className="w-3.5 h-3.5 text-success mt-0.5 shrink-0" />
                    <span>{d}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {ai.risks && ai.risks.length > 0 && (
            <div>
              <h3 className="text-[15px] font-semibold text-surface-white mb-2 flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-danger" />
                Key Risks
              </h3>
              <ul className="space-y-1.5">
                {ai.risks.map((r, i) => (
                  <li key={i} className="text-[13px] text-surface-700 flex items-start gap-2">
                    <TrendingDown className="w-3.5 h-3.5 text-danger mt-0.5 shrink-0" />
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {ai.verdict && (
            <div className="p-4 bg-brand-muted border border-brand-border rounded-lg">
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1">AI Verdict</p>
              <p className="text-[14px] text-surface-800 leading-relaxed">{ai.verdict}</p>
            </div>
          )}
        </section>
      )}
    </article>
  );
}

export default function AirdropsPage() {
  const { slug } = useParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSlug, setExpandedSlug] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = searchQuery.toLowerCase();
    return AIRDROPS.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.ticker.toLowerCase().includes(q) ||
        p.chain.toLowerCase().includes(q),
    );
  }, [searchQuery]);

  if (slug) {
    const project = AIRDROPS.find((p) => makeAirdropSlug(p) === slug);
    if (!project) {
      return (
        <>
          <PageSeo
            meta={{ ...ROUTES.airdrops, title: 'Airdrop Not Found | PulseTrends', path: `/airdrops/${slug}` }}
            breadcrumbs={[
              { name: 'Home', path: '/' },
              { name: 'Airdrops', path: '/airdrops' },
              { name: 'Not Found', path: `/airdrops/${slug}` },
            ]}
          />
          <Breadcrumbs items={[
            { name: 'Home', path: '/' },
            { name: 'Airdrops' },
            { name: 'Not Found' },
          ] as Crumb[]} />
          <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
            <h1 className="text-xl font-semibold text-surface-white">Airdrop Not Found</h1>
            <p className="text-[14px] text-surface-600 mt-2">The airdrop "{slug}" could not be found.</p>
            <Link to="/airdrops" className="inline-block mt-4 px-4 py-2 bg-brand text-white text-[13px] font-medium rounded-md hover:bg-brand-hover">
              Browse all airdrops
            </Link>
          </div>
        </>
      );
    }
    return <AirdropDetailView project={project} />;
  }

  return (
    <>
      <PageSeo
        meta={ROUTES.airdrops}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Airdrops', path: '/airdrops' },
        ]}
      />
      <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Airdrops' }] as Crumb[]} />
      <div className="space-y-6">
        <div className="border-b border-surface-300/60 pb-6">
          <Badge variant="default" size="md">Airdrop Intelligence</Badge>
          <h1 className="text-2xl font-bold text-surface-white mt-3 tracking-tight">Crypto Airdrops</h1>
          <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">
            AI-powered analysis of active and upcoming crypto airdrop campaigns.
          </p>
          <div className="flex items-center gap-5 mt-4">
            <div className="flex items-center gap-1.5">
              <Gift className="w-3.5 h-3.5 text-surface-600" />
              <span className="text-[12px] text-surface-700">
                <span className="font-semibold text-surface-white">
                  {AIRDROPS.filter((p) => p.status === 'active').length}
                </span>{' '}
                Active Airdrops
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-surface-600" />
              <span className="text-[12px] text-surface-700">
                <span className="font-semibold text-surface-white">{AIRDROPS.length}</span> Total Tracked
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <Brain className="w-3.5 h-3.5 text-surface-600" />
              <span className="text-[12px] text-surface-700">AI Scored</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-600" />
            <input
              type="text"
              placeholder="Search by name, ticker, or chain..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-surface-200 border border-surface-300 rounded-lg text-[13px] text-surface-white placeholder-surface-600 focus:outline-none focus:border-surface-500 transition-colors"
              aria-label="Search airdrops"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtered.map((project, i) => (
            <AirdropCardInline
              key={project.id}
              project={project}
              index={i}
              expandedSlug={expandedSlug}
              onToggle={setExpandedSlug}
            />
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
            <p className="text-surface-600 text-[14px]">No airdrops match your criteria</p>
          </div>
        )}
      </div>
    </>
  );
}
