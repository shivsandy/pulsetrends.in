import { useState } from 'react';
import {
  X, ChevronDown, ChevronUp, Globe, Camera, DollarSign, Coins, CheckCircle2,
  ListChecks, ClipboardList, Target, Clock, PieChart, Users, Map, TrendingUp as TUp,
  Shield, AlertTriangle, Brain, Sparkles, ArrowUpRight, ArrowDownRight, Percent,
  GitCompare, Lock, Pickaxe, Gavel, ExternalLink, Link, Hexagon, Layers, Gem
} from 'lucide-react';
import type { CryptoAirdrop } from '../data/cryptoData';
import ScoreRing from './ScoreRing';
import Badge from './Badge';

interface Props {
  airdrop: CryptoAirdrop;
  onClose: () => void;
}

const categoryIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'Infrastructure': Link,
  'Layer 1': Hexagon,
  'Layer 1 / DeFi': Hexagon,
  'Layer 2': Layers,
  'DeFi / Perps': Gem,
};

interface SectionDef {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
}

const sectionDefs: SectionDef[] = [
  { id: 'overview', title: 'Project Overview', icon: Globe },
  { id: 'snapshot', title: 'Airdrop Snapshot', icon: Camera },
  { id: 'funding', title: 'Funding & Investors', icon: DollarSign },
  { id: 'token', title: 'Token Information', icon: Coins },
  { id: 'eligibility', title: 'Eligibility Requirements', icon: CheckCircle2 },
  { id: 'guide', title: 'Step-by-Step Participation Guide', icon: ListChecks },
  { id: 'tasks', title: 'Tasks & Requirements', icon: ClipboardList },
  { id: 'reward', title: 'Estimated Reward Potential', icon: Target },
  { id: 'snapshotDetails', title: 'Snapshot Details', icon: Clock },
  { id: 'tokenomics', title: 'Tokenomics Overview', icon: PieChart },
  { id: 'team', title: 'Team & Backers', icon: Users },
  { id: 'roadmap', title: 'Roadmap & Milestones', icon: Map },
  { id: 'community', title: 'Community Growth', icon: TUp },
  { id: 'strengths', title: 'Strengths', icon: Shield },
  { id: 'risks', title: 'Risks & Red Flags', icon: AlertTriangle },
  { id: 'aiScore', title: 'AI Score', icon: Brain },
  { id: 'aiAnalysis', title: 'AI Analysis', icon: Sparkles },
  { id: 'bull', title: 'Bull Case', icon: ArrowUpRight },
  { id: 'bear', title: 'Bear Case', icon: ArrowDownRight },
  { id: 'probability', title: 'Probability of Airdrop', icon: Percent },
  { id: 'historical', title: 'Historical Comparisons', icon: GitCompare },
  { id: 'security', title: 'Security Considerations', icon: Lock },
  { id: 'worthFarming', title: 'Worth Farming?', icon: Pickaxe },
  { id: 'verdict', title: 'Final Verdict', icon: Gavel },
];

export default function AirdropDetailModal({ airdrop, onClose }: Props) {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(['overview']));
  const CategoryIcon = categoryIcons[airdrop.category] || Hexagon;

  const toggle = (id: string) => {
    setOpenSections(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const expandAll = () => setOpenSections(new Set(sectionDefs.map(s => s.id)));
  const collapseAll = () => setOpenSections(new Set());

  const isOpen = (id: string) => openSections.has(id);

  const importanceBadge = (imp: string) => {
    if (imp === 'Critical') return 'danger';
    if (imp === 'High') return 'warning';
    if (imp === 'Medium') return 'info';
    return 'outline';
  };

  const statusDot = (status: string) => {
    if (status === 'completed') return 'bg-success';
    if (status === 'in-progress') return 'bg-warning';
    return 'bg-surface-500';
  };

  // ---- Field renderer helpers ----
  const KV = ({ label, value, className }: { label: string; value: string; className?: string }) => (
    <div className="bg-surface-100 border border-surface-300/40 rounded-md p-2.5">
      <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mb-0.5">{label}</p>
      <p className={`text-[12px] font-medium text-surface-white ${className ?? ''}`}>{value}</p>
    </div>
  );

  // ---- Section content renderers ----
  const renderContent = (id: string) => {
    switch (id) {

      case 'overview':
        return (
          <div className="space-y-3">
            <p className="text-[13px] text-surface-800 leading-relaxed">{airdrop.overview.summary}</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <KV label="Launch Date" value={airdrop.overview.launchDate} />
              <KV label="Mainnet Status" value={airdrop.overview.mainnet} />
              <KV label="TVL" value={airdrop.overview.tvl} />
              <KV label="Unique Users" value={airdrop.overview.uniqueUsers} />
              <KV label="Transactions" value={airdrop.overview.transactionsProcessed} />
              <KV label="Consensus" value={airdrop.overview.consensusMechanism} />
            </div>
          </div>
        );

      case 'snapshot':
        return (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <KV label="Type" value={airdrop.airdropSnapshot.type} />
            <KV label="Allocation" value={airdrop.airdropSnapshot.totalAllocation} />
            <KV label="Est. Value" value={airdrop.airdropSnapshot.estimatedValue} />
            <KV label="Snapshot Date" value={airdrop.airdropSnapshot.snapshotDate} />
            <KV label="Claim Deadline" value={airdrop.airdropSnapshot.claimDeadline} />
            <KV label="Distribution" value={airdrop.airdropSnapshot.distributionMethod} />
            <KV label="Vesting" value={airdrop.airdropSnapshot.vestingSchedule} />
            <KV label="Claim Platform" value={airdrop.airdropSnapshot.claimPlatform} />
          </div>
        );

      case 'funding':
        return (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <KV label="Total Raised" value={airdrop.funding.totalRaised} />
              <KV label="Valuation" value={airdrop.funding.valuation} />
            </div>
            {airdrop.funding.rounds.length > 0 && (
              <div>
                <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Funding Rounds</p>
                <div className="space-y-1">
                  {airdrop.funding.rounds.map((r, i) => (
                    <div key={i} className="flex items-center justify-between bg-surface-100 border border-surface-300/40 rounded-md px-3 py-2">
                      <span className="text-[12px] font-medium text-surface-white">{r.name}</span>
                      <span className="text-[12px] text-surface-800">{r.amount}</span>
                      <span className="text-[11px] text-surface-600">{r.date}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Lead Investors</p>
              <div className="flex flex-wrap gap-1.5">
                {airdrop.funding.leadInvestors.length > 0 ? airdrop.funding.leadInvestors.map(inv => (
                  <Badge key={inv} variant="default" size="sm">{inv}</Badge>
                )) : <span className="text-[12px] text-surface-600">No external investors</span>}
              </div>
            </div>
            {airdrop.funding.otherInvestors.length > 0 && (
              <div>
                <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Other Investors</p>
                <div className="flex flex-wrap gap-1.5">
                  {airdrop.funding.otherInvestors.map(inv => (
                    <Badge key={inv} variant="outline" size="sm">{inv}</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case 'token':
        return (
          <div className="space-y-3">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <KV label="Token Name" value={airdrop.tokenInfo.tokenName} />
              <KV label="Ticker" value={airdrop.tokenInfo.ticker} />
              <KV label="Type" value={airdrop.tokenInfo.tokenType} />
              <KV label="Total Supply" value={airdrop.tokenInfo.totalSupply} />
              <KV label="Initial Circulating" value={airdrop.tokenInfo.initialCirculating} />
            </div>
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Token Utility</p>
              <div className="space-y-1">
                {airdrop.tokenInfo.utility.map((u, i) => (
                  <div key={i} className="flex items-start gap-2 text-[12px] text-surface-800">
                    <CheckCircle2 className="w-3.5 h-3.5 text-brand-light flex-shrink-0 mt-0.5" />
                    {u}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'eligibility':
        return (
          <div className="space-y-1.5">
            {airdrop.eligibility.map((e, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-surface-100 border border-surface-300/40 rounded-md p-2.5 text-[12px] text-surface-800">
                <CheckCircle2 className="w-3.5 h-3.5 text-success flex-shrink-0 mt-0.5" />
                {e}
              </div>
            ))}
          </div>
        );

      case 'guide':
        return (
          <div className="space-y-2">
            {airdrop.participationGuide.map(s => (
              <div key={s.step} className="flex gap-3 bg-surface-100 border border-surface-300/40 rounded-md p-3">
                <span className="w-6 h-6 rounded bg-brand-muted flex items-center justify-center text-[11px] font-bold text-brand-light flex-shrink-0 mt-0.5">
                  {s.step}
                </span>
                <div>
                  <p className="text-[13px] font-medium text-surface-white mb-0.5">{s.title}</p>
                  <p className="text-[12px] text-surface-700 leading-relaxed">{s.description}</p>
                </div>
              </div>
            ))}
          </div>
        );

      case 'tasks':
        return (
          <div className="space-y-1.5">
            {airdrop.tasks.map((t, i) => (
              <div key={i} className="flex items-center justify-between bg-surface-100 border border-surface-300/40 rounded-md px-3 py-2.5">
                <span className="text-[12px] text-surface-800 flex-1 mr-3">{t.task}</span>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Badge variant={importanceBadge(t.importance)} size="sm">{t.importance}</Badge>
                  <span className="text-[11px] text-surface-600 w-16 text-right">{t.estimatedTime}</span>
                </div>
              </div>
            ))}
          </div>
        );

      case 'reward':
        return (
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-surface-100 border border-surface-300/40 rounded-md p-3 text-center">
                <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium mb-1">Low</p>
                <p className="text-lg font-bold text-surface-800">{airdrop.rewardPotential.lowEstimate}</p>
              </div>
              <div className="bg-brand-muted border border-brand-border rounded-md p-3 text-center">
                <p className="text-[10px] text-brand-light uppercase tracking-wider font-medium mb-1">Mid</p>
                <p className="text-lg font-bold text-brand-light">{airdrop.rewardPotential.midEstimate}</p>
              </div>
              <div className="bg-success-muted border border-success-border rounded-md p-3 text-center">
                <p className="text-[10px] text-success uppercase tracking-wider font-medium mb-1">High</p>
                <p className="text-lg font-bold text-success">{airdrop.rewardPotential.highEstimate}</p>
              </div>
            </div>
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Factors Affecting Reward</p>
              <div className="space-y-1">
                {airdrop.rewardPotential.factors.map((f, i) => (
                  <div key={i} className="flex items-start gap-2 text-[12px] text-surface-800">
                    <Target className="w-3.5 h-3.5 text-surface-600 flex-shrink-0 mt-0.5" />
                    {f}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'snapshotDetails':
        return (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <KV label="Snapshot Date" value={airdrop.snapshotDetails.date} />
              <KV label="Block Number" value={airdrop.snapshotDetails.blockNumber} />
            </div>
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Criteria</p>
              <div className="space-y-1">
                {airdrop.snapshotDetails.criteria.map((c, i) => (
                  <div key={i} className="flex items-start gap-2 text-[12px] text-surface-800">
                    <CheckCircle2 className="w-3.5 h-3.5 text-brand-light flex-shrink-0 mt-0.5" />
                    {c}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Anti-Sybil Measures</p>
              <div className="space-y-1">
                {airdrop.snapshotDetails.antiSybil.map((a, i) => (
                  <div key={i} className="flex items-start gap-2 text-[12px] text-surface-800">
                    <Shield className="w-3.5 h-3.5 text-warning flex-shrink-0 mt-0.5" />
                    {a}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'tokenomics':
        return (
          <div className="space-y-1.5">
            <div className="grid grid-cols-[1fr_80px_1fr] gap-1 px-3 py-1.5">
              <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Category</span>
              <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium text-center">%</span>
              <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Vesting</span>
            </div>
            {airdrop.tokenomics.distribution.map((d, i) => (
              <div key={i} className="grid grid-cols-[1fr_80px_1fr] gap-1 bg-surface-100 border border-surface-300/40 rounded-md px-3 py-2.5 items-center">
                <span className="text-[12px] font-medium text-surface-white">{d.category}</span>
                <span className="text-[13px] font-bold text-brand-light text-center">{d.percentage}</span>
                <span className="text-[11px] text-surface-700">{d.vesting}</span>
              </div>
            ))}
          </div>
        );

      case 'team':
        return (
          <div className="space-y-2">
            {airdrop.team.map((t, i) => (
              <div key={i} className="bg-surface-100 border border-surface-300/40 rounded-md p-3">
                <div className="flex items-center gap-2 mb-1">
                  <p className="text-[13px] font-semibold text-surface-white">{t.name}</p>
                  <Badge variant="outline" size="sm">{t.role}</Badge>
                </div>
                <p className="text-[12px] text-surface-700 leading-relaxed">{t.background}</p>
              </div>
            ))}
          </div>
        );

      case 'roadmap':
        return (
          <div className="space-y-1">
            {airdrop.roadmap.map((r, i) => (
              <div key={i} className="flex items-center gap-3 bg-surface-100 border border-surface-300/40 rounded-md px-3 py-2.5">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${statusDot(r.status)}`} />
                <span className="text-[11px] text-surface-600 w-16 flex-shrink-0 font-mono">{r.date}</span>
                <span className="text-[12px] text-surface-800 flex-1">{r.milestone}</span>
                <Badge variant={r.status === 'completed' ? 'success' : r.status === 'in-progress' ? 'warning' : 'outline'} size="sm">
                  {r.status}
                </Badge>
              </div>
            ))}
          </div>
        );

      case 'community':
        return (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <KV label="Twitter/X" value={airdrop.community.twitter} />
            <KV label="Discord" value={airdrop.community.discord} />
            <KV label="Telegram" value={airdrop.community.telegram} />
            <KV label="GitHub" value={airdrop.community.github} />
            <KV label="Growth Rate" value={airdrop.community.growthRate} />
          </div>
        );

      case 'strengths':
        return (
          <div className="space-y-1.5">
            {airdrop.strengths.map((s, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-success-muted border border-success-border rounded-md p-2.5">
                <TUp className="w-3.5 h-3.5 text-success flex-shrink-0 mt-0.5" />
                <p className="text-[12px] text-surface-800 leading-relaxed">{s}</p>
              </div>
            ))}
          </div>
        );

      case 'risks':
        return (
          <div className="space-y-1.5">
            {airdrop.risks.map((r, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-danger-muted border border-danger-border rounded-md p-2.5">
                <AlertTriangle className="w-3.5 h-3.5 text-danger flex-shrink-0 mt-0.5" />
                <p className="text-[12px] text-surface-800 leading-relaxed">{r}</p>
              </div>
            ))}
          </div>
        );

      case 'aiScore':
        return (
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-4 py-1">
            {[
              { label: 'Overall', score: airdrop.aiScores.overall },
              { label: 'Fundamentals', score: airdrop.aiScores.fundamentals },
              { label: 'Team', score: airdrop.aiScores.teamCredibility },
              { label: 'Tokenomics', score: airdrop.aiScores.tokenomicsQuality },
              { label: 'Community', score: airdrop.aiScores.communityStrength },
              { label: 'Generosity', score: airdrop.aiScores.airdropGenerosity },
              { label: 'Risk Factor', score: airdrop.aiScores.riskFactor },
            ].map(item => (
              <ScoreRing key={item.label} score={item.score} size={64} strokeWidth={4} label={item.label} />
            ))}
          </div>
        );

      case 'aiAnalysis':
        return (
          <div className="bg-surface-200/50 border border-surface-300 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2.5">
              <Brain className="w-4 h-4 text-brand-light" />
              <h4 className="font-semibold text-[13px] text-surface-white">AI Deep Analysis</h4>
            </div>
            <p className="text-[13px] text-surface-800 leading-relaxed">{airdrop.aiAnalysis}</p>
          </div>
        );

      case 'bull':
        return (
          <div className="space-y-1.5">
            {airdrop.bullCase.map((b, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-success-muted border border-success-border rounded-md p-2.5">
                <ArrowUpRight className="w-3.5 h-3.5 text-success flex-shrink-0 mt-0.5" />
                <p className="text-[12px] text-surface-800 leading-relaxed">{b}</p>
              </div>
            ))}
          </div>
        );

      case 'bear':
        return (
          <div className="space-y-1.5">
            {airdrop.bearCase.map((b, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-danger-muted border border-danger-border rounded-md p-2.5">
                <ArrowDownRight className="w-3.5 h-3.5 text-danger flex-shrink-0 mt-0.5" />
                <p className="text-[12px] text-surface-800 leading-relaxed">{b}</p>
              </div>
            ))}
          </div>
        );

      case 'probability':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <ScoreRing score={airdrop.airdropProbability.percentage} size={80} strokeWidth={6} showLabel={false} />
              <div>
                <p className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Probability</p>
                <p className="text-2xl font-bold text-surface-white">{airdrop.airdropProbability.percentage}%</p>
              </div>
            </div>
            <p className="text-[13px] text-surface-800 leading-relaxed">{airdrop.airdropProbability.reasoning}</p>
          </div>
        );

      case 'historical':
        return (
          <div className="space-y-1.5">
            {airdrop.historicalComparisons.map((h, i) => (
              <div key={i} className="bg-surface-100 border border-surface-300/40 rounded-md p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[13px] font-semibold text-surface-white">{h.project}</span>
                  <span className="text-[12px] font-semibold text-success">{h.airdropValue}</span>
                </div>
                <p className="text-[11px] text-surface-700">{h.similarity}</p>
              </div>
            ))}
          </div>
        );

      case 'security':
        return (
          <div className="space-y-3">
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Audits</p>
              <div className="flex flex-wrap gap-1.5">
                {airdrop.security.audits.map(a => <Badge key={a} variant="success" size="sm">{a}</Badge>)}
              </div>
            </div>
            {airdrop.security.knownIssues.length > 0 && (
              <div>
                <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Known Issues</p>
                {airdrop.security.knownIssues.map((k, i) => (
                  <div key={i} className="flex items-start gap-2 text-[12px] text-surface-800 mb-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-warning flex-shrink-0 mt-0.5" />
                    {k}
                  </div>
                ))}
              </div>
            )}
            <div className="grid grid-cols-2 gap-2">
              <KV label="Contract Verified" value={airdrop.security.contractVerified ? 'Yes' : 'No'} />
              <KV label="Bug Bounty" value={airdrop.security.bugBounty} />
            </div>
          </div>
        );

      case 'worthFarming': {
        const verdictColor =
          airdrop.worthFarming.verdict === 'Strongly Yes' ? 'success' :
          airdrop.worthFarming.verdict === 'Yes' ? 'success' :
          airdrop.worthFarming.verdict === 'Maybe' ? 'warning' : 'danger';
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Badge variant={verdictColor} size="md">{airdrop.worthFarming.verdict}</Badge>
            </div>
            <p className="text-[13px] text-surface-800 leading-relaxed">{airdrop.worthFarming.reasoning}</p>
            <div className="grid grid-cols-3 gap-2">
              <KV label="Est. Cost" value={airdrop.worthFarming.estimatedCost} />
              <KV label="Time Needed" value={airdrop.worthFarming.estimatedTimeCommitment} />
              <KV label="Risk/Reward" value={airdrop.worthFarming.riskRewardRatio} />
            </div>
          </div>
        );
      }

      case 'verdict': {
        const ratingColor =
          airdrop.finalVerdict.rating === 'S' || airdrop.finalVerdict.rating.startsWith('A') ? 'success' :
          airdrop.finalVerdict.rating.startsWith('B') ? 'info' :
          airdrop.finalVerdict.rating.startsWith('C') ? 'warning' : 'danger';
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="text-[10px] text-surface-600 uppercase tracking-wider font-medium">Rating</span>
              <Badge variant={ratingColor} size="md">{airdrop.finalVerdict.rating}</Badge>
            </div>
            <p className="text-[13px] text-surface-800 leading-relaxed">{airdrop.finalVerdict.summary}</p>
            <div>
              <p className="text-[11px] text-surface-600 uppercase tracking-wider font-medium mb-1.5">Action Items</p>
              <div className="space-y-1.5">
                {airdrop.finalVerdict.actionItems.map((a, i) => (
                  <div key={i} className="flex items-start gap-2.5 bg-brand-muted border border-brand-border rounded-md p-2.5 text-[12px] text-surface-800">
                    <span className="w-4 h-4 rounded bg-brand/20 flex items-center justify-center text-[10px] font-bold text-brand-light flex-shrink-0 mt-0.5">{i + 1}</span>
                    {a}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      }

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center" onClick={onClose}>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-2xl bg-surface-100 border border-surface-300 rounded-xl shadow-2xl shadow-black/40 animate-slide-up my-4 mx-4 max-h-[calc(100vh-2rem)] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Sticky Header */}
        <div className="flex-shrink-0 bg-surface-100/95 backdrop-blur-lg rounded-t-xl border-b border-surface-300/60 px-5 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-lg bg-surface-200 border border-surface-300 flex items-center justify-center flex-shrink-0">
              <CategoryIcon className="w-4 h-4 text-surface-700" />
            </div>
            <div className="min-w-0">
              <h2 className="text-[16px] font-semibold text-surface-white leading-tight truncate">{airdrop.name}</h2>
              <p className="text-[11px] text-surface-600 font-mono">{airdrop.ticker} / {airdrop.chain} / {airdrop.category}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <a href={`https://${airdrop.website}`} target="_blank" rel="noopener noreferrer" className="p-1.5 rounded-md hover:bg-surface-300 text-surface-600 hover:text-surface-white transition-colors" title="Visit website">
              <ExternalLink className="w-4 h-4" />
            </a>
            <button onClick={onClose} className="p-1.5 rounded-md hover:bg-surface-300 text-surface-600 hover:text-surface-white transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Expand/Collapse controls */}
        <div className="flex-shrink-0 px-5 py-2 border-b border-surface-300/30 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Badge variant={airdrop.status === 'active' ? 'success' : airdrop.status === 'upcoming' ? 'warning' : 'outline'} size="sm">{airdrop.status}</Badge>
            <Badge variant={airdrop.riskLevel === 'Low' ? 'success' : airdrop.riskLevel === 'Medium' ? 'warning' : 'danger'} size="sm">Risk: {airdrop.riskLevel}</Badge>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={expandAll} className="text-[11px] text-surface-600 hover:text-surface-white transition-colors font-medium">Expand All</button>
            <span className="text-surface-500">|</span>
            <button onClick={collapseAll} className="text-[11px] text-surface-600 hover:text-surface-white transition-colors font-medium">Collapse All</button>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto px-4 py-3 space-y-1">
          {sectionDefs.map(({ id, title, icon: Icon }) => (
            <div key={id} className="rounded-lg border border-surface-300/40 overflow-hidden bg-surface-50">
              <button
                onClick={() => toggle(id)}
                className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-surface-200/50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4 text-surface-600" />
                  <span className="font-medium text-[13px] text-surface-900">{title}</span>
                </div>
                {isOpen(id) ? <ChevronUp className="w-4 h-4 text-surface-600" /> : <ChevronDown className="w-4 h-4 text-surface-600" />}
              </button>
              {isOpen(id) && (
                <div className="px-4 pb-3.5 animate-fade-in">
                  {renderContent(id)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
