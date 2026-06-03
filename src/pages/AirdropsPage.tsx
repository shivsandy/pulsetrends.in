import { useMemo, useState } from 'react';
import { Search, Gift, Sparkles, TrendingUp, TrendingDown, Globe, Shield, ArrowLeft, ExternalLink, AtSign, MessageCircle, Send, Brain, Clock, DollarSign, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, Star, Users, BarChart3, Layers, Coins, Target, Filter, SlidersHorizontal } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { airdropProjects, type AirdropProject, ratingLabel, ratingColor } from '../data/airdropData';
import Badge from '../components/Badge';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';
import { slugify } from '../seo/config';

// ── Slug Helpers ────────────────────────────────────────────────

function makeSlug(p: AirdropProject): string {
  return `${slugify(p.name)}-${p.id}`;
}

// ── Score display ring ──────────────────────────────────────────

function ScoreRing({ score, size = 40, stroke = 3 }: { score: number; size?: number; stroke?: number }) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 80 ? '#22c55e' : score >= 70 ? '#eab308' : score >= 60 ? '#f97316' : '#ef4444';
  return (
    <svg width={size} height={size} className="shrink-0">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="currentColor" strokeWidth={stroke} className="text-surface-300/50" />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke} strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round" transform={`rotate(-90 ${size / 2} ${size / 2})`} />
      <text x={size / 2} y={size / 2} textAnchor="middle" dominantBaseline="central" fill="currentColor" fontSize={size * 0.3} fontWeight="700" className="text-surface-white">
        {score}
      </text>
    </svg>
  );
}

// ── Difficulty Badge ────────────────────────────────────────────

function DifficultyBadge({ level }: { level: string }) {
  const cfg: Record<string, { color: string; label: string }> = {
    Easy: { color: 'bg-success-muted text-success border-success-border', label: 'Easy' },
    Medium: { color: 'bg-warning-muted text-warning border-warning-border', label: 'Medium' },
    Hard: { color: 'bg-danger-muted text-danger border-danger-border', label: 'Hard' },
  };
  const c = cfg[level] || cfg.Medium;
  return <span className={`text-[10px] px-1.5 py-0.5 rounded border font-medium uppercase tracking-wider ${c.color}`}>{c.label}</span>;
}

// ── Risk Flag ───────────────────────────────────────────────────

function RiskFlag({ flag }: { flag: string }) {
  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-danger-muted border border-danger-border text-[12px] text-danger">
      <AlertTriangle className="w-3 h-3 shrink-0" />
      <span>{flag}</span>
    </div>
  );
}

// ── Section Header for Detail Page ──────────────────────────────

function DetailSection({ title, icon, children, defaultOpen = true }: { title: string; icon: React.ReactNode; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-surface-300/60 rounded-xl overflow-hidden bg-surface-100">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between p-4 hover:bg-surface-200 transition-colors text-left" aria-expanded={open}>
        <h2 className="text-[15px] font-semibold text-surface-white flex items-center gap-2.5">{icon} {title}</h2>
        {open ? <ChevronUp className="w-4 h-4 text-surface-600" /> : <ChevronDown className="w-4 h-4 text-surface-600" />}
      </button>
      {open && <div className="px-4 pb-4 border-t border-surface-300/40 pt-4">{children}</div>}
    </div>
  );
}

// ═════════════════════════════════════════════════════════════════
//  DETAIL VIEW
// ═════════════════════════════════════════════════════════════════

function AirdropDetailView({ project }: { project: AirdropProject }) {
  const s = project.scores;
  const ai = project.aiAnalysis;
  const about = project.about;
  const pg = project.participationGuide;

  const scoreItems = [
    { label: 'Team', score: s.team, icon: <Users className="w-3.5 h-3.5" /> },
    { label: 'Investors', score: s.investors, icon: <Shield className="w-3.5 h-3.5" /> },
    { label: 'Product', score: s.product, icon: <Layers className="w-3.5 h-3.5" /> },
    { label: 'Market', score: s.market, icon: <BarChart3 className="w-3.5 h-3.5" /> },
    { label: 'Community', score: s.community, icon: <Users className="w-3.5 h-3.5" /> },
    { label: 'Token', score: s.token, icon: <Coins className="w-3.5 h-3.5" /> },
    { label: 'Airdrop', score: s.airdrop, icon: <Gift className="w-3.5 h-3.5" /> },
  ];

  return (
    <article className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Breadcrumbs & Back */}
      <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Airdrops', path: '/airdrops' }, { name: project.name }]} />
      <Link to="/airdrops" className="inline-flex items-center gap-1.5 text-[12px] text-surface-600 hover:text-surface-900 transition-colors">
        <ArrowLeft className="w-3 h-3" /> Back to all airdrops
      </Link>

      {/* Header */}
      <div className="bg-surface-100 border border-surface-300/60 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-xl bg-surface-200 border border-surface-300 flex items-center justify-center shrink-0">
            <Gift className="w-7 h-7 text-surface-700" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <Badge variant={project.status === 'active' ? 'success' : 'warning'} size="sm">{project.status}</Badge>
              <Badge variant="info" size="sm">{project.blockchain}</Badge>
              <Badge variant="outline" size="sm">{project.category}</Badge>
            </div>
            <h1 className="text-2xl font-bold text-surface-white leading-tight">{project.name}</h1>
            <p className="text-[13px] text-surface-600 mt-1">{project.ticker} · {project.estimatedReward}</p>
            {project.website && (
              <a href={project.website} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-[12px] text-brand hover:text-brand-light mt-1">
                <ExternalLink className="w-3 h-3" /> Website
              </a>
            )}
          </div>
          <div className="flex flex-col items-center gap-1">
            <ScoreRing score={s.overall} size={64} stroke={5} />
            <span className={`text-[10px] font-semibold uppercase tracking-wider ${ratingColor(s.overall)}`}>{ratingLabel(s.overall)}</span>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      <DetailSection title="Score Breakdown" icon={<Star className="w-4 h-4 text-warning" />}>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {scoreItems.map((item) => (
            <div key={item.label} className="flex items-center justify-between bg-surface-50 border border-surface-300/40 rounded-lg p-3">
              <div className="flex items-center gap-1.5">
                <span className="text-surface-600">{item.icon}</span>
                <span className="text-[11px] text-surface-600">{item.label}</span>
              </div>
              <ScoreRing score={item.score} size={36} stroke={3} />
            </div>
          ))}
        </div>
        <div className="mt-4 p-3 bg-brand-muted border border-brand-border rounded-lg text-center">
          <p className="text-[11px] text-surface-600 uppercase tracking-wider">Overall Score</p>
          <p className={`text-xl font-bold ${ratingColor(s.overall)}`}>{s.overall}/100 · {ratingLabel(s.overall)}</p>
        </div>
      </DetailSection>

      {/* Overview */}
      <DetailSection title="Overview" icon={<Target className="w-4 h-4 text-brand-light" />}>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          <InfoBox label="Category" value={project.category} />
          <InfoBox label="Blockchain" value={project.blockchain} />
          <InfoBox label="Status" value={project.status} />
          <InfoBox label="Est. Reward" value={project.estimatedReward} />
        </div>
        {ai?.summary && <p className="text-[13px] text-surface-700 leading-relaxed">{ai.summary}</p>}
      </DetailSection>

      {/* About */}
      {about && (
        <DetailSection title="About" icon={<Globe className="w-4 h-4 text-brand-light" />}>
          <div className="space-y-4 text-[13px] text-surface-700 leading-relaxed">
            <div>
              <h3 className="font-semibold text-surface-white mb-1">About Project</h3>
              <p>{about.aboutProject}</p>
            </div>
            <div>
              <h3 className="font-semibold text-surface-white mb-1">Project Overview</h3>
              <p>{about.projectOverview}</p>
            </div>
            <div>
              <h3 className="font-semibold text-surface-white mb-1">Product Description</h3>
              <p>{about.productDescription}</p>
            </div>
            {about.useCases.length > 0 && (
              <div>
                <h3 className="font-semibold text-surface-white mb-1">Use Cases</h3>
                <ul className="list-disc list-inside space-y-0.5">
                  {about.useCases.map((u, i) => <li key={i}>{u}</li>)}
                </ul>
              </div>
            )}
          </div>
        </DetailSection>
      )}

      {/* Funding & Investors */}
      {about && (
        <DetailSection title="Funding & Investors" icon={<DollarSign className="w-4 h-4 text-success" />}>
          <div className="space-y-3 text-[13px] text-surface-700">
            <div>
              <h3 className="font-semibold text-surface-white mb-1">Funding</h3>
              <p>{about.fundingInfo}</p>
            </div>
            {about.investors.length > 0 && (
              <div>
                <h3 className="font-semibold text-surface-white mb-1">Investors</h3>
                <div className="flex flex-wrap gap-2">
                  {about.investors.map((inv, i) => (
                    <span key={i} className="px-2.5 py-1 bg-surface-50 border border-surface-300/40 rounded-md text-[12px] text-surface-700">{inv}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </DetailSection>
      )}

      {/* Participation Guide */}
      {pg && (
        <DetailSection title="How To Participate" icon={<CheckCircle2 className="w-4 h-4 text-success" />}>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <InfoBox label="Difficulty" value={<DifficultyBadge level={pg.difficulty} />} />
            <InfoBox label="Time Required" value={pg.estimatedTime} />
            <InfoBox label="Estimated Cost" value={pg.estimatedCost} />
          </div>
          <ol className="space-y-2">
            {pg.steps.map((step, i) => (
              <li key={i} className="flex items-start gap-3 text-[13px] text-surface-700">
                <span className="w-5 h-5 rounded-full bg-brand-muted border border-brand-border text-brand-light text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">{i + 1}</span>
                <span className="leading-relaxed">{step}</span>
              </li>
            ))}
          </ol>
        </DetailSection>
      )}

      {/* AI Analysis */}
      {ai && (
        <DetailSection title="AI Analysis" icon={<Brain className="w-4 h-4 text-brand-light" />}>
          <div className="space-y-4">
            <div className="p-3 bg-success-muted border border-success-border rounded-lg">
              <h3 className="text-[12px] font-semibold text-success mb-1 flex items-center gap-1.5"><TrendingUp className="w-3 h-3" /> Bull Case</h3>
              <p className="text-[13px] text-surface-700 leading-relaxed">{ai.bullCase}</p>
            </div>
            <div className="p-3 bg-danger-muted border border-danger-border rounded-lg">
              <h3 className="text-[12px] font-semibold text-danger mb-1 flex items-center gap-1.5"><TrendingDown className="w-3 h-3" /> Bear Case</h3>
              <p className="text-[13px] text-surface-700 leading-relaxed">{ai.bearCase}</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                <h3 className="text-[11px] font-semibold text-surface-600 uppercase tracking-wider mb-1">Competitive Analysis</h3>
                <p className="text-[13px] text-surface-700">{ai.competitiveAnalysis}</p>
              </div>
              <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
                <h3 className="text-[11px] font-semibold text-surface-600 uppercase tracking-wider mb-1">Market Opportunity</h3>
                <p className="text-[13px] text-surface-700">{ai.marketOpportunity}</p>
              </div>
            </div>
            <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
              <h3 className="text-[11px] font-semibold text-surface-600 uppercase tracking-wider mb-1">Airdrop Attractiveness</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
                {[
                  ['Reward Potential', ai.airdropAttractiveness.rewardPotential],
                  ['Effort Required', ai.airdropAttractiveness.effortRequired],
                  ['Cost Required', ai.airdropAttractiveness.costRequired],
                  ['Expected ROI', ai.airdropAttractiveness.expectedROI],
                ].map(([label, value]) => (
                  <div key={label} className="bg-surface-100 border border-surface-300/40 rounded p-2 text-center">
                    <p className="text-[10px] text-surface-600 uppercase tracking-wider">{label}</p>
                    <p className="text-[12px] font-semibold text-surface-white mt-0.5">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </DetailSection>
      )}

      {/* Risks */}
      {project.riskFlags.length > 0 && (
        <DetailSection title="Risk Flags" icon={<AlertTriangle className="w-4 h-4 text-danger" />}>
          <div className="space-y-2">
            {project.riskFlags.map((flag, i) => <RiskFlag key={i} flag={flag} />)}
          </div>
        </DetailSection>
      )}

      {/* Verdict */}
      <DetailSection title="Final Verdict" icon={<Sparkles className="w-4 h-4 text-warning" />} defaultOpen={true}>
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 rounded-full bg-brand-muted border border-brand-border flex items-center justify-center shrink-0">
            <Brain className="w-6 h-6 text-brand-light" />
          </div>
          <div>
            <p className="text-[12px] text-surface-600 font-semibold uppercase tracking-wider mb-1">AI-Generated Conclusion</p>
            <p className="text-[14px] text-surface-700 leading-relaxed">{project.verdict}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-[11px] text-surface-600">Overall Rating:</span>
              <span className={`text-[13px] font-bold ${ratingColor(s.overall)}`}>{s.overall}/100 · {ratingLabel(s.overall)}</span>
            </div>
          </div>
        </div>
      </DetailSection>

      {/* Social Links */}
      {project.socialLinks && (project.socialLinks.twitter || project.socialLinks.discord || project.socialLinks.telegram) && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[12px] text-surface-600 font-medium">Social:</span>
          {project.socialLinks.twitter && <a href={project.socialLinks.twitter} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center hover:bg-surface-300 transition-colors" aria-label="Twitter"><AtSign className="w-4 h-4 text-surface-700" /></a>}
          {project.socialLinks.discord && <a href={project.socialLinks.discord} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center hover:bg-surface-300 transition-colors" aria-label="Discord"><MessageCircle className="w-4 h-4 text-surface-700" /></a>}
          {project.socialLinks.telegram && <a href={project.socialLinks.telegram} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center hover:bg-surface-300 transition-colors" aria-label="Telegram"><Send className="w-4 h-4 text-surface-700" /></a>}
        </div>
      )}

      {/* Source */}
      <p className="text-[11px] text-surface-500 text-center">Source: {project.source}</p>
    </article>
  );
}

// ── Info Box ────────────────────────────────────────────────────

function InfoBox({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-3">
      <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">{label}</p>
      <div className="text-[13px] font-semibold text-surface-white mt-1">{value}</div>
    </div>
  );
}

// ═════════════════════════════════════════════════════════════════
//  LISTING VIEW
// ═════════════════════════════════════════════════════════════════

type SortKey = 'score' | 'name' | 'reward' | 'difficulty';

export default function AirdropsPage() {
  const { slug } = useParams();
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'upcoming'>('all');
  const [sortBy, setSortBy] = useState<SortKey>('score');

  // Stats (safe before conditional return - not hooks)
  const activeCount = airdropProjects.filter((p) => p.status === 'active').length;
  const totalCount = airdropProjects.length;

  // Filtered & sorted (hook - must be before any conditional return)
  const filtered = useMemo(() => {
    let result = [...airdropProjects];
    if (filterStatus !== 'all') result = result.filter((p) => p.status === filterStatus);
    if (search) {
      const q = search.toLowerCase();
      result = result.filter((p) => p.name.toLowerCase().includes(q) || p.ticker.toLowerCase().includes(q) || p.blockchain.toLowerCase().includes(q));
    }
    result.sort((a, b) => {
      if (sortBy === 'score') return b.scores.overall - a.scores.overall;
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'reward') {
        const ra = a.estimatedReward ? parseInt(a.estimatedReward.replace(/[^0-9]/g, '')) || 0 : 0;
        const rb = b.estimatedReward ? parseInt(b.estimatedReward.replace(/[^0-9]/g, '')) || 0 : 0;
        return rb - ra;
      }
      if (sortBy === 'difficulty') {
        const d = { Easy: 0, Medium: 1, Hard: 2 };
        return (d[a.participationGuide?.difficulty || 'Medium'] || 1) - (d[b.participationGuide?.difficulty || 'Medium'] || 1);
      }
      return 0;
    });
    return result;
  }, [search, filterStatus, sortBy]);

  // Detail view (after all hooks to avoid React hooks ordering violation)
  if (slug) {
    const project = airdropProjects.find((p) => makeSlug(p) === slug);
    if (!project) {
      return (
        <>
          <PageSeo meta={{ ...ROUTES.airdrops, title: 'Airdrop Not Found | PulseTrends', path: `/airdrops/${slug}` }} />
          <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Airdrops', path: '/airdrops' }, { name: 'Not Found' }]} />
          <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
            <h1 className="text-xl font-semibold text-surface-white">Airdrop Not Found</h1>
            <p className="text-[14px] text-surface-600 mt-2">This airdrop is not in our database.</p>
            <Link to="/airdrops" className="inline-block mt-4 px-4 py-2 bg-brand text-white text-[13px] font-medium rounded-md hover:bg-brand-hover">Browse all airdrops</Link>
          </div>
        </>
      );
    }
    return <AirdropDetailView project={project} />;
  }

  return (
    <>
      <PageSeo meta={ROUTES.airdrops} breadcrumbs={[{ name: 'Home', path: '/' }, { name: 'Airdrops', path: '/airdrops' }]} />
      <div className="space-y-6 animate-fade-in">
        {/* Breadcrumbs */}
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Airdrops' }]} />

        {/* ── Hero Section ─────────────────────────────────────── */}
        <div className="bg-surface-100 border border-surface-300/60 rounded-xl p-6 sm:p-8">
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-brand-muted border border-brand-border text-[11px] font-semibold text-brand-light uppercase tracking-wider">
              <Gift className="w-3 h-3" /> Airdrop Intelligence
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-surface-white mt-2 tracking-tight">Airdrop Intelligence Platform</h1>
          <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">Investor-grade research & AI-powered analysis of the most promising crypto airdrops. Track, analyze, and participate with confidence.</p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
            {[
              { value: activeCount.toString(), label: 'Active Airdrops', icon: Gift },
              { value: totalCount.toString(), label: 'Total Tracked', icon: Target },
              { value: 'Daily', label: 'Updated', icon: Clock },
              { value: 'AI-Powered', label: 'Analysis', icon: Brain },
            ].map((stat) => (
              <div key={stat.label} className="bg-surface-50 border border-surface-300/40 rounded-lg p-4 text-center">
                <stat.icon className="w-5 h-5 text-brand-light mx-auto mb-2" />
                <p className="text-xl font-bold text-surface-white">{stat.value}</p>
                <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── Filters & Search ──────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-600" />
            <input type="text" placeholder="Search by name, ticker, or chain..." value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-surface-200 border border-surface-300 rounded-lg text-[13px] text-surface-white placeholder-surface-600 focus:outline-none focus:border-surface-500 transition-colors"
              aria-label="Search airdrops" />
          </div>
          <div className="flex items-center gap-1.5">
            <SlidersHorizontal className="w-3.5 h-3.5 text-surface-600 mr-1 shrink-0" />
            {(['all', 'active', 'upcoming'] as const).map((s) => (
              <button key={s} type="button" onClick={() => setFilterStatus(s)}
                className={`px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all capitalize ${filterStatus === s ? 'bg-surface-300 text-surface-white' : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'}`}
                aria-pressed={filterStatus === s}>{s}</button>
            ))}
          </div>
          <div className="flex items-center gap-1.5">
            <Filter className="w-3.5 h-3.5 text-surface-600 mr-1 shrink-0" />
            {(['score', 'name', 'reward', 'difficulty'] as const).map((s) => (
              <button key={s} type="button" onClick={() => setSortBy(s)}
                className={`px-2.5 py-1.5 rounded-md text-[12px] font-medium transition-all capitalize ${sortBy === s ? 'bg-surface-300 text-surface-white' : 'text-surface-600 hover:text-surface-800 hover:bg-surface-200'}`}
                aria-pressed={sortBy === s}>{s === 'score' ? 'Highest Score' : s === 'reward' ? 'Highest Reward' : s}</button>
            ))}
          </div>
        </div>

        {/* ── Airdrop Grid ──────────────────────────────────────── */}
        {filtered.length === 0 ? (
          <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
            <p className="text-surface-600 text-[14px]">No airdrops match your criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((project, i) => {
              const slug = makeSlug(project);
              const pg = project.participationGuide;
              return (
                <Link key={project.id} to={`/airdrops/${slug}`}
                  className="bg-surface-100 border border-surface-300/60 rounded-xl p-5 hover:border-surface-500 transition-all duration-200 group animate-fade-in block"
                  style={{ animationDelay: `${i * 40}ms` }}>
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3 gap-3">
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <div className="w-10 h-10 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center shrink-0">
                        <Gift className="w-5 h-5 text-surface-700" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="font-semibold text-surface-white text-[14px] leading-tight truncate group-hover:text-brand-light transition-colors">{project.name}</h3>
                        <p className="text-[11px] text-surface-600 font-mono truncate">{project.ticker} · {project.blockchain}</p>
                      </div>
                    </div>
                    <ScoreRing score={project.scores.overall} size={36} stroke={3} />
                  </div>

                  {/* Badges */}
                  <div className="flex flex-wrap items-center gap-1.5 mb-3">
                    <Badge variant={project.status === 'active' ? 'success' : 'warning'} size="sm">{project.status}</Badge>
                    <Badge variant="outline" size="sm">{project.category}</Badge>
                    {pg && <DifficultyBadge level={pg.difficulty} />}
                  </div>

                  {/* Quick stats */}
                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div>
                      <p className="text-surface-600 uppercase tracking-wider">Reward</p>
                      <p className="font-semibold text-surface-white truncate">{project.estimatedReward}</p>
                    </div>
                    {pg && (
                      <>
                        <div>
                          <p className="text-surface-600 uppercase tracking-wider">Cost</p>
                          <p className="font-semibold text-surface-white">{pg.estimatedCost}</p>
                        </div>
                        <div>
                          <p className="text-surface-600 uppercase tracking-wider">Time</p>
                          <p className="font-semibold text-surface-white">{pg.estimatedTime}</p>
                        </div>
                        <div>
                          <p className="text-surface-600 uppercase tracking-wider">Score</p>
                          <p className={`font-bold ${project.scores.overall >= 80 ? 'text-success' : project.scores.overall >= 70 ? 'text-warning' : 'text-surface-white'}`}>{project.scores.overall}/100</p>
                        </div>
                      </>
                    )}
                  </div>

                  {/* AI Summary */}
                  {project.aiAnalysis?.summary && (
                    <div className="mt-2 p-2.5 rounded-lg bg-surface-50 border border-surface-300/40">
                      <p className="text-[11px] font-semibold text-surface-600 uppercase tracking-wider mb-1 flex items-center gap-1">
                        <Brain className="w-3 h-3" /> AI Analysis
                      </p>
                      <p className="text-[12px] text-surface-700 leading-relaxed line-clamp-2">{project.aiAnalysis.summary}</p>
                    </div>
                  )}

                  {/* Participation Steps Preview */}
                  {pg && pg.steps.length > 0 && (
                    <div className="mt-2 p-2.5 rounded-lg bg-surface-50 border border-surface-300/40">
                      <p className="text-[11px] font-semibold text-surface-600 uppercase tracking-wider mb-1 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-success" /> How To Participate
                      </p>
                      <ol className="space-y-0.5">
                        {pg.steps.slice(0, 2).map((step, si) => (
                          <li key={si} className="flex items-start gap-1.5 text-[12px] text-surface-700">
                            <span className="w-4 h-4 rounded-full bg-brand-muted border border-brand-border text-brand-light text-[9px] font-bold flex items-center justify-center shrink-0 mt-0.5">{si + 1}</span>
                            <span className="leading-relaxed truncate min-w-0">{step}</span>
                          </li>
                        ))}
                        {pg.steps.length > 2 && (
                          <li className="text-[11px] text-surface-600 italic pl-6">+{pg.steps.length - 2} more steps</li>
                        )}
                      </ol>
                    </div>
                  )}

                  {/* Verdict */}
                  <div className="mt-3 pt-3 border-t border-surface-300/40 flex items-center justify-between text-[11px] text-surface-600">
                    <span className="truncate">{project.verdict.slice(0, 60)}...</span>
                    <Sparkles className="w-3 h-3 text-brand-light shrink-0 ml-2" />
                  </div>
                </Link>
              );
            })}
          </div>
        )}

        {/* Footer Stats */}
        <div className="border-t border-surface-300/60 pt-4 text-center">
          <p className="text-[12px] text-surface-600">
            Tracking <span className="font-semibold text-surface-white">{activeCount}</span> active airdrops ·{' '}
            <span className="font-semibold text-surface-white">{totalCount}</span> total projects ·{' '}
            Updated <span className="font-semibold text-surface-white">daily</span>
          </p>
        </div>
      </div>
    </>
  );
}
