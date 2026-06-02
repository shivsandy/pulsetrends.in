import { useState } from 'react';
import { Search, Gift, Sparkles, ExternalLink, ChevronDown, ChevronUp, Brain, TrendingUp, TrendingDown, ListChecks, Globe, Shield, Wallet } from 'lucide-react';
import { cryptoProjects } from '../data/cryptoData';
import type { CryptoProject } from '../data/cryptoData';
import Badge from './Badge';

const AIRDROPS = cryptoProjects.filter(p => p.category === 'airdrop');

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

function RiskBadge({ level }: { level: string }) {
  const color = level === 'low' ? 'bg-success-muted text-success border-success-border' :
    level === 'high' ? 'bg-danger-muted text-danger border-danger-border' :
    'bg-warning-muted text-warning border-warning-border';
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
    >
      <Icon className="w-3.5 h-3.5 text-surface-700" />
    </a>
  );
}

export default function CryptoAirdropSection() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered = AIRDROPS.filter((p) => {
    const matchesSearch = searchQuery === '' ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.chain.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div className="border-b border-surface-300/60 pb-6">
        <Badge variant="default" size="md">Airdrop Intelligence</Badge>
        <h2 className="text-2xl font-bold text-surface-white mt-3 tracking-tight">
          Crypto Airdrops
        </h2>
        <p className="text-[14px] text-surface-700 mt-1.5 max-w-2xl leading-relaxed">
          AI-powered analysis of active and upcoming crypto airdrop campaigns.
        </p>
        <div className="flex items-center gap-5 mt-4">
          <div className="flex items-center gap-1.5">
            <Gift className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">{AIRDROPS.filter(p => p.status === 'active').length}</span> Active Airdrops</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">{AIRDROPS.length}</span> Total Tracked</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Brain className="w-3.5 h-3.5 text-surface-600" />
            <span className="text-[12px] text-surface-700"><span className="font-semibold text-surface-white">AI</span> Risk Scored</span>
          </div>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-600" />
        <input
          type="text"
          placeholder="Search airdrops by name, ticker, chain..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2 bg-surface-200 border border-surface-300 rounded-lg text-[13px] text-surface-white placeholder-surface-600 focus:outline-none focus:border-surface-500 transition-colors"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filtered.map((project, i) => (
          <AirdropCard key={project.id} project={project} index={i} expandedId={expandedId} setExpandedId={setExpandedId} />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 border border-surface-300/40 rounded-xl bg-surface-50">
          <Gift className="w-10 h-10 text-surface-500 mx-auto mb-3" />
          <p className="text-surface-600 text-[14px]">No airdrops match your search</p>
          <p className="text-surface-500 text-[12px] mt-1">Try adjusting your search query</p>
        </div>
      )}
    </div>
  );
}

function AirdropCard({ project, index, expandedId, setExpandedId }: {
  project: CryptoProject;
  index: number;
  expandedId: string | null;
  setExpandedId: (id: string | null) => void;
}) {
  const analysis = project.aiAnalysis;
  const isExpanded = expandedId === project.id;
  const sentiment = analysis?.sentiment || 'neutral';
  const ra = analysis?.riskAssessment;

  return (
    <div className="bg-surface-100 border border-surface-300/60 rounded-xl hover:border-surface-500 transition-all duration-200 animate-fade-in group"
      style={{ animationDelay: `${index * 80}ms` }}>
      <div className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center shrink-0">
              <Gift className="w-5 h-5 text-brand" />
            </div>
            <div className="min-w-0">
              <h3 className="font-semibold text-surface-white text-[15px] leading-tight truncate">{project.name}</h3>
              <div className="flex items-center gap-2 text-[12px] text-surface-600 mt-0.5">
                <span className="font-mono">{project.ticker}</span>
                {project.chain && <><span className="text-surface-500">/</span><span className="truncate">{project.chain}</span></>}
              </div>
            </div>
          </div>
          <Badge variant={project.status === 'active' ? 'success' : project.status === 'upcoming' ? 'warning' : 'outline'} size="sm">{project.status}</Badge>
        </div>

        {(project.estimatedValue || project.tgeDate) && (
          <div className="grid grid-cols-2 gap-2 mb-3">
            {project.estimatedValue && (
              <div className="bg-brand-muted border border-brand-border rounded-md px-3 py-2">
                <span className="text-[10px] text-brand-light uppercase tracking-wider font-medium">Est. Value</span>
                <p className="text-[13px] font-semibold text-brand-light truncate">{project.estimatedValue}</p>
              </div>
            )}
            {project.tgeDate && (
              <div className="bg-success-muted border border-success-border rounded-md px-3 py-2">
                <span className="text-[10px] text-success uppercase tracking-wider font-medium">TGE Date</span>
                <p className="text-[12px] font-semibold text-success truncate">{project.tgeDate}</p>
              </div>
            )}
          </div>
        )}

        {project.description && (
          <p className="text-[13px] text-surface-700 mb-3 line-clamp-2 leading-relaxed">{project.description}</p>
        )}

        {project.eligibility && (
          <div className="flex items-start gap-1.5 mb-3 text-[12px] text-surface-700">
            <Wallet className="w-3.5 h-3.5 text-surface-600 mt-0.5 shrink-0" />
            <span>{project.eligibility}</span>
          </div>
        )}

        <div className="flex items-center gap-1.5 mb-3 flex-wrap">
          {project.website && (
            <a href={project.website} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-[11px] text-brand-light hover:text-brand transition-colors">
              <Globe className="w-3 h-3" /> Website <ExternalLink className="w-2.5 h-2.5" />
            </a>
          )}
          <SocialIcon url={project.socialLinks?.twitter} icon={XLogo} label="Twitter / X" />
          <SocialIcon url={project.socialLinks?.discord} icon={DiscordLogo} label="Discord" />
          <SocialIcon url={project.socialLinks?.telegram} icon={TelegramLogo} label="Telegram" />
        </div>

        {analysis && (
          <div className="bg-surface-200/50 border border-surface-300/40 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1.5">
              <Brain className="w-3.5 h-3.5 text-brand-light" />
              <span className="text-[12px] font-semibold text-surface-900">AI Analysis</span>
              <div className="flex items-center gap-1 ml-auto">
                {sentiment === 'bullish' ? <TrendingUp className="w-3 h-3 text-success" /> :
                 sentiment === 'bearish' ? <TrendingDown className="w-3 h-3 text-danger" /> : null}
                <span className={`text-[12px] font-semibold ${
                  sentiment === 'bullish' ? 'text-success' :
                  sentiment === 'bearish' ? 'text-danger' : 'text-surface-700'
                }`}>
                  {analysis.convictionScore}/100
                </span>
              </div>
            </div>
            <p className="text-[12px] text-surface-700 leading-relaxed line-clamp-3">{analysis.summary}</p>

            {ra && (
              <div className="mt-2 pt-2 border-t border-surface-300/30">
                <div className="flex items-center gap-1 mb-1.5">
                  <Shield className="w-3 h-3 text-surface-600" />
                  <span className="text-[11px] font-semibold text-surface-800">Risk Assessment</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {RISK_ORDER.map(key => {
                    const val = ra[key as keyof typeof ra];
                    if (!val) return null;
                    return (
                      <div key={key} className="flex items-center gap-1 text-[10px] text-surface-700 bg-surface-200/50 rounded px-1.5 py-0.5 border border-surface-300/30">
                        <span className="font-medium">{RISK_LABELS[key]}:</span>
                        <RiskBadge level={val} />
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {analysis.keyDrivers.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {analysis.keyDrivers.slice(0, 3).map((d, i) => (
                  <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-success-muted border border-success-border text-success truncate max-w-[200px]">{d}</span>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="flex items-center justify-between pt-3 mt-3 border-t border-surface-300/40">
          <span className="text-[12px] text-surface-700 font-medium">
            {analysis?.verdict ? `Verdict: ${analysis.verdict.slice(0, 60)}...` : 'No AI verdict'}
          </span>
          <button
            onClick={() => setExpandedId(isExpanded ? null : project.id)}
            className="flex items-center gap-1 text-[11px] text-brand-light hover:text-brand transition-colors"
          >
            {isExpanded ? 'Less' : 'Steps'}
            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {isExpanded && project.steps && project.steps.length > 0 && (
        <div className="border-t border-surface-300/40 bg-surface-200/30 rounded-b-xl px-5 py-4">
          <div className="flex items-center gap-1.5 mb-2">
            <ListChecks className="w-3.5 h-3.5 text-brand-light" />
            <span className="text-[12px] font-semibold text-surface-900">How to Participate</span>
          </div>
          <ol className="space-y-2">
            {project.steps.map((step, si) => (
              <li key={si} className="flex items-start gap-2 text-[12px] text-surface-700 leading-relaxed">
                <span className="w-4 h-4 rounded-full bg-brand/20 text-brand-light text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">{si + 1}</span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {isExpanded && (!project.steps || project.steps.length === 0) && (
        <div className="border-t border-surface-300/40 bg-surface-200/30 rounded-b-xl px-5 py-4">
          <p className="text-[12px] text-surface-600 italic">No step-by-step guide available for this airdrop.</p>
        </div>
      )}
    </div>
  );
}

function XLogo(props: any) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
    </svg>
  );
}

function DiscordLogo(props: any) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189z"/>
    </svg>
  );
}

function TelegramLogo(props: any) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="currentColor">
      <path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
    </svg>
  );
}
