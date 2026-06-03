// ──────────────────────────────────────────────────────────────
// Airdrop Intelligence Platform — Enhanced Data Models & 61 Projects
// ──────────────────────────────────────────────────────────────

export interface ParticipationGuide {
  steps: string[];
  estimatedTime: string;
  estimatedCost: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
}

export interface AboutInfo {
  aboutProject: string;
  projectOverview: string;
  productDescription: string;
  ecosystemDescription: string;
  useCases: string[];
  teamInfo: string;
  fundingInfo: string;
  investors: string[];
  tokenInfo: string;
  reviewSummary: string;
}

export interface AiAnalysis {
  summary: string;
  bullCase: string;
  bearCase: string;
  competitiveAnalysis: string;
  marketOpportunity: string;
  airdropAttractiveness: {
    rewardPotential: string;
    effortRequired: string;
    costRequired: string;
    expectedROI: string;
  };
}

export interface AirdropScores {
  team: number;
  investors: number;
  product: number;
  market: number;
  community: number;
  token: number;
  airdrop: number;
  overall: number;
}

export type AirdropStatus = 'active' | 'upcoming' | 'ended';
export type Difficulty = 'Easy' | 'Medium' | 'Hard';

export interface AirdropProject {
  id: string;
  name: string;
  ticker: string;
  logo?: string;
  website: string;
  category: string;
  blockchain: string;
  status: AirdropStatus;
  launchDate?: string;
  estimatedReward: string;
  rewardType: string;
  deadline?: string;
  socialLinks: {
    twitter: string;
    discord: string;
    telegram: string;
    website: string;
  };
  about?: AboutInfo;
  participationGuide?: ParticipationGuide;
  aiAnalysis?: AiAnalysis;
  scores: AirdropScores;
  riskFlags: string[];
  verdict: string;
  source: string;
}

/** Weighted scoring: 20% Team + 15% Investors + 20% Product + 15% Market + 10% Community + 10% Token + 10% Airdrop */
export function calculateOverall(scores: Omit<AirdropScores, 'overall'>): number {
  return Math.round(
    scores.team * 0.20 +
    scores.investors * 0.15 +
    scores.product * 0.20 +
    scores.market * 0.15 +
    scores.community * 0.10 +
    scores.token * 0.10 +
    scores.airdrop * 0.10
  );
}

export function ratingLabel(overall: number): string {
  if (overall >= 90) return 'Exceptional';
  if (overall >= 80) return 'Strong';
  if (overall >= 70) return 'Good';
  if (overall >= 60) return 'Speculative';
  return 'Avoid';
}

export function ratingColor(overall: number): string {
  if (overall >= 90) return 'text-emerald-400';
  if (overall >= 80) return 'text-green-400';
  if (overall >= 70) return 'text-yellow-400';
  if (overall >= 60) return 'text-orange-400';
  return 'text-red-400';
}

function s(t: number, i: number, p: number, m: number, c: number, tk: number, a: number): AirdropScores {
  return { team: t, investors: i, product: p, market: m, community: c, token: tk, airdrop: a, overall: calculateOverall({ team: t, investors: i, product: p, market: m, community: c, token: tk, airdrop: a }) };
}

function pGuide(steps: string[], time: string, cost: string, difficulty: Difficulty): ParticipationGuide {
  return { steps, estimatedTime: time, estimatedCost: cost, difficulty };
}

function slots(tw: string, dc: string, tg: string, ws: string) {
  return { twitter: tw, discord: dc, telegram: tg, website: ws };
}

// ── 61 Tracked Airdrops (40 Active + 21 Upcoming) ──────────────

export const airdropProjects: AirdropProject[] = [
  // ═══ ACTIVE (40) ══════════════════════════════════════════════
  {
    id: 'hyperliquid', name: 'Hyperliquid', ticker: 'HYPE', website: 'https://hyperliquid.xyz',
    category: 'DeFi', blockchain: 'Hyperliquid', status: 'active',
    launchDate: '2025-12-15', estimatedReward: '$500-$5,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/hyperliquid', 'https://discord.gg/hyperliquid', '', 'https://hyperliquid.xyz'),
    scores: s(88, 85, 92, 90, 85, 88, 95),
    riskFlags: ['Early Stage', 'Unclear Token Utility'],
    verdict: 'Hyperliquid is a high-performance decentralized perpetual exchange. Its airdrop rewards early traders and liquidity providers generously.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Connect Ethereum wallet (MetaMask)', 'Bridge ETH to Hyperliquid', 'Deposit USDC into Hyperliquid', 'Start trading perpetuals', 'Provide liquidity to pools', 'Complete at least 5 trades', 'Maintain minimum $1,000 volume'],
      '30 Minutes', '$50-$500', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Hyperliquid is a layer-1 blockchain purpose-built for on-chain perpetual futures trading, offering CEX-like performance with DeFi transparency.',
      bullCase: 'First-mover in on-chain perps at scale; strong VC backing; rapidly growing TVL',
      bearCase: 'Competitive perp DEX landscape; regulatory uncertainty for derivatives',
      competitiveAnalysis: 'Competes with dYdX, GMX, and SynFutures. Unique in having its own L1 blockchain.',
      marketOpportunity: 'The perpetual DEX market is projected to exceed $100B monthly volume by 2027.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '2x-10x' }
    },
    about: {
      aboutProject: 'Hyperliquid is a high-performance layer-1 blockchain and decentralized exchange optimized for perpetual futures trading.',
      projectOverview: 'Built from the ground up for low-latency trading, Hyperliquid processes orders in milliseconds with sub-cent fees.',
      productDescription: 'The Hyperliquid DEX offers spot and perpetual trading with up to 50x leverage, deep liquidity, and a self-custodial experience.',
      ecosystemDescription: 'The ecosystem includes the core DEX, HLP vaults for passive liquidity provision, and a growing suite of DeFi primitives.',
      useCases: ['Perpetual futures trading', 'On-chain spot exchange', 'Liquidity provision via HLP', 'Cross-chain settlement'],
      teamInfo: 'Led by anonymous but reputable builder team with backgrounds in HFT and DeFi.',
      fundingInfo: 'Raised undisclosed seed round from top-tier VCs and angel investors.',
      investors: ['Variant Fund', 'Framework Ventures', 'Nascent', 'Angel investors'],
      tokenInfo: 'HYPE is the native token for gas, governance, and fee discounts. Max supply: 1,000,000,000.',
      reviewSummary: 'Hyperliquid is widely considered the most sophisticated on-chain perp exchange, with deep liquidity and a loyal user base.'
    }
  },
  {
    id: 'zksync', name: 'zkSync Era', ticker: 'ZK', website: 'https://zksync.io',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-06-15', estimatedReward: '$100-$3,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/zksync', 'https://discord.gg/zksync', 'https://t.me/zksync', 'https://zksync.io'),
    scores: s(85, 92, 90, 85, 80, 85, 88),
    riskFlags: [],
    verdict: 'zkSync is a leading ZK-rollup scaling Ethereum. Its airdrop rewards early adopters and active ecosystem users.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to zkSync Era', 'Swap tokens on SyncSwap or Mute', 'Provide liquidity on DEXes', 'Use zkSync native bridges', 'Interact with >5 dApps', 'Maintain activity over 3+ months', 'Check eligibility on claim site'],
      '20 Minutes', '$10-$100', 'Easy'
    ),
    aiAnalysis: {
      summary: 'zkSync Era is a zero-knowledge rollup scaling solution for Ethereum, offering low fees and high throughput.',
      bullCase: 'Massive ecosystem with 200+ dApps; strong team (Matter Labs); ZK tech is the future',
      bearCase: 'Competition from Arbitrum, Optimism, and Base; token distribution concerns',
      competitiveAnalysis: 'Competes with Arbitrum, Optimism, Base, Scroll. Differentiated by ZK-proofs and EVM compatibility.',
      marketOpportunity: 'ZK-rollups are expected to dominate L2 scaling, with zkSync positioned as a leader.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-5x' }
    },
    about: {
      aboutProject: 'zkSync Era by Matter Labs is a zero-knowledge rollup that scales Ethereum while preserving security.',
      projectOverview: 'zkSync uses validity proofs to batch thousands of transactions off-chain, posting only a succinct proof to Ethereum.',
      productDescription: 'EVM-compatible smart contract platform with sub-cent transaction fees and near-instant finality.',
      ecosystemDescription: 'Over 200 dApps including SyncSwap, Mute, Maverick, and Orbiter Finance.',
      useCases: ['DeFi trading and lending', 'NFT minting and trading', 'Cross-chain bridging', 'Payments'],
      teamInfo: 'Led by Alex Gluchowski, co-founder of Matter Labs, with a team of 100+ engineers and researchers.',
      fundingInfo: 'Raised $458M from top investors.',
      investors: ['Andreessen Horowitz', 'Dragonfly Capital', 'Blockchain Capital', 'Variant'],
      tokenInfo: 'ZK is used for governance and protocol fees. Total supply: 21 billion.',
      reviewSummary: 'zkSync is a top-tier ZK-rollup with strong technology, ecosystem, and team backing.'
    }
  },
  {
    id: 'scroll', name: 'Scroll', ticker: 'SCR', website: 'https://scroll.io',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-10-15', estimatedReward: '$50-$1,500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/Scroll_ZKP', 'https://discord.gg/scroll', 'https://t.me/scroll', 'https://scroll.io'),
    scores: s(80, 88, 85, 82, 78, 82, 85),
    riskFlags: [],
    verdict: 'Scroll is a ZK-rollup with strong tech and community backing. Its airdrop recognizes early users.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Scroll', 'Swap on Skydrome or Zebra', 'Provide liquidity', 'Use Scroll native bridges', 'Interact with 5+ dApps', 'Maintain wallet activity'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Scroll is a bytecode-level compatible zkEVM rollup scaling Ethereum.',
      bullCase: 'Bytecode-level EVM compatibility; strong community; ZK tech leadership',
      bearCase: 'Crowded L2 space; slower adoption vs Arbitrum',
      competitiveAnalysis: 'Direct competitor to zkSync, Linea, and Polygon zkEVM.',
      marketOpportunity: 'Ethereum scaling market exceeding $1T in locked value.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Scroll is a zkEVM-based ZK-rollup that achieves full EVM equivalence.',
      projectOverview: 'Scroll processes transactions off-chain with ZK-proofs, inheriting Ethereum\'s security.',
      productDescription: 'Full EVM compatibility at scale with significantly lower fees.',
      ecosystemDescription: 'Growing ecosystem of DeFi, NFT, and gaming dApps.',
      useCases: ['DeFi', 'NFTs', 'Gaming', 'Payments'],
      teamInfo: 'Led by researchers and engineers from top universities and crypto projects.',
      fundingInfo: 'Raised $80M from top VCs.',
      investors: ['Polychain Capital', 'Bain Capital Crypto', 'IOSG Ventures'],
      tokenInfo: 'SCR is used for governance and gas fee payments.',
      reviewSummary: 'Scroll is a promising ZK-rollup with strong technical fundamentals.'
    }
  },
  {
    id: 'linea', name: 'Linea', ticker: 'LINEA', website: 'https://linea.build',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-08-15', estimatedReward: '$50-$2,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/LineaBuild', 'https://discord.gg/linea', 'https://t.me/linea', 'https://linea.build'),
    scores: s(82, 85, 83, 80, 76, 80, 82),
    riskFlags: [],
    verdict: 'Linea is ConsenSys\' zkEVM offering strong backing and a growing ecosystem.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Linea', 'Swap on Linea DEXes', 'Provide liquidity', 'Use Linea dApps', 'Bridge back to L1', 'Maintain activity'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Linea is a ZK-rollup developed by ConsenSys, the team behind MetaMask.',
      bullCase: 'Backed by ConsenSys/MetaMask network; strong brand; ZK technology',
      bearCase: 'Late to market vs competitors; unclear tokenomics',
      competitiveAnalysis: 'Competes with zkSync, Scroll, and other zkEVMs.',
      marketOpportunity: 'Growing demand for EVM-compatible scaling solutions.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Linea is ConsenSys\' zkEVM layer-2 scaling solution.',
      projectOverview: 'Linea zkEVM offers Ethereum-equivalent smart contract execution with ZK-rollup efficiency.',
      productDescription: 'Full EVM compatibility with low fees and fast transactions.',
      ecosystemDescription: '100+ dApps integrated across DeFi, gaming, and NFTs.',
      useCases: ['DeFi', 'NFTs', 'Gaming', 'Enterprise'],
      teamInfo: 'Developed by ConsenSys, founded by Joseph Lubin.',
      fundingInfo: 'Funded by ConsenSys, raised $450M+ across entities.',
      investors: ['ConsenSys', 'HSBC', 'Mastercard', 'JP Morgan'],
      tokenInfo: 'Governance token with fee utility on Linea.',
      reviewSummary: 'Linea benefits from ConsenSys backing and MetaMask integration.'
    }
  },
  {
    id: 'monad', name: 'Monad', ticker: 'MONAD', website: 'https://monad.xyz',
    category: 'Infrastructure', blockchain: 'Monad', status: 'active',
    launchDate: '2025-12-01', estimatedReward: '$200-$5,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/monad_xyz', 'https://discord.gg/monad', '', 'https://monad.xyz'),
    scores: s(90, 92, 85, 88, 82, 85, 90),
    riskFlags: ['Early Stage'],
    verdict: 'Monad is a highly anticipated EVM-compatible L1 with parallel execution. Strong investor backing.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join Monad Discord and community', 'Follow Monad on Twitter', 'Run a testnet node', 'Complete testnet transactions', 'Deploy test contracts', 'Report bugs', 'Stay active in community'],
      '1 Hour', '$0-$10', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Monad is a high-performance EVM-compatible layer-1 blockchain with parallel execution.',
      bullCase: 'Paradigm-backed; innovative parallel EVM; strong team; massive hype',
      bearCase: 'Early stage; L1 competition; execution risk',
      competitiveAnalysis: 'Competes with Solana, Sui, Aptos, and other high-throughput L1s.',
      marketOpportunity: 'Demand for high-performance EVM chains with sub-second finality.',
      airdropAttractiveness: { rewardPotential: 'Very High', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '5x-20x' }
    },
    about: {
      aboutProject: 'Monad is a next-generation EVM-compatible layer-1 blockchain with parallel transaction execution.',
      projectOverview: 'Monad achieves 10,000+ TPS through optimistic parallel execution and a custom consensus mechanism.',
      productDescription: 'Fully EVM-compatible L1 with 100x the throughput of Ethereum.',
      ecosystemDescription: 'Pre-launch ecosystem with 50+ projects building on Monad.',
      useCases: ['DeFi', 'High-frequency trading', 'Gaming', 'AI inference'],
      teamInfo: 'Led by team with backgrounds from Jump Trading and top engineering schools.',
      fundingInfo: 'Raised $325M from Paradigm and others.',
      investors: ['Paradigm', 'Dragonfly Capital', 'Coinbase Ventures', 'Greenoaks'],
      tokenInfo: 'MONAD for gas, staking, and governance. Deflationary supply model.',
      reviewSummary: 'One of the most anticipated L1 launches with strong fundamentals.'
    }
  },
  {
    id: 'soneium', name: 'Soneium', ticker: 'SONE', website: 'https://soneium.org',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-11-01', estimatedReward: '$50-$1,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/soneium', 'https://discord.gg/soneium', '', 'https://soneium.org'),
    scores: s(78, 82, 80, 78, 75, 78, 80),
    riskFlags: [],
    verdict: 'Soneium is Sony\'s entry into Ethereum L2 space via OP Stack.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Soneium', 'Swap on Soneium DEXes', 'Provide liquidity', 'Interact with dApps'],
      '10 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Soneium is an OP Stack L2 built by Sony Block Solutions Labs.',
      bullCase: 'Sony brand power; potential PlayStation integration; OP Stack security',
      bearCase: 'Corporate-controlled L2; limited ecosystem',
      competitiveAnalysis: 'Unique position as major brand entering L2 space.',
      marketOpportunity: 'Bridging traditional entertainment with Web3.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Soneium is Sony\'s Ethereum L2 blockchain built on the OP Stack.',
      projectOverview: 'Sony leverages its entertainment ecosystem to onboard millions of users.',
      productDescription: 'OP Stack rollup optimized for entertainment and gaming applications.',
      ecosystemDescription: 'Integration with Sony\'s music, film, and gaming divisions.',
      useCases: ['Gaming', 'NFTs', 'Entertainment', 'Fan engagement'],
      teamInfo: 'Sony Block Solutions Labs, a subsidiary of Sony Group.',
      fundingInfo: 'Funded by Sony Group.',
      investors: ['Sony Group'],
      tokenInfo: 'SONE for governance and ecosystem participation.',
      reviewSummary: 'Soneium leverages Sony\'s massive distribution and brand trust.'
    }
  },
  {
    id: 'layerzero', name: 'LayerZero', ticker: 'ZRO', website: 'https://layerzero.network',
    category: 'Infrastructure', blockchain: 'Multi-Chain', status: 'active',
    launchDate: '2025-06-20', estimatedReward: '$100-$2,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/LayerZero_Labs', 'https://discord.gg/layerzero', '', 'https://layerzero.network'),
    scores: s(85, 92, 90, 88, 82, 85, 85),
    riskFlags: [],
    verdict: 'LayerZero is the leading omnichain interoperability protocol. Strong fundamentals.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Use LayerZero-powered bridges (Stargate)', 'Bridge assets across chains', 'Use LayerZero dApps', 'Provide liquidity on Stargate', 'Maintain cross-chain activity'],
      '20 Minutes', '$20-$100', 'Easy'
    ),
    aiAnalysis: {
      summary: 'LayerZero is an omnichain interoperability protocol connecting 50+ blockchains.',
      bullCase: 'Deep integration across 50+ chains; strong team; raised $293M',
      bearCase: 'Competition from Chainlink CCIP and native bridges',
      competitiveAnalysis: 'Leading omnichain messaging protocol vs Chainlink CCIP, Axelar, Wormhole.',
      marketOpportunity: 'Cross-chain infrastructure market growing with multi-chain adoption.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'Low', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'LayerZero is an omnichain interoperability protocol connecting 50+ blockchains.',
      projectOverview: 'LayerZero enables lightweight message passing across chains via Ultra Light Nodes.',
      productDescription: 'Trustless cross-chain communication for any type of data or asset.',
      ecosystemDescription: '50+ supported chains, 200+ dApps, and $10B+ bridged volume.',
      useCases: ['Cross-chain bridging', 'Omnichain DeFi', 'Multi-chain NFTs'],
      teamInfo: 'Founded by Bryan Pellegrino, Caleb Banister, and Ryan Zarick.',
      fundingInfo: 'Raised $293M at $3B valuation.',
      investors: ['Sequoia Capital', 'Andreessen Horowitz', 'FTX Ventures', 'Coinbase'],
      tokenInfo: 'ZRO for governance and protocol fee payments.',
      reviewSummary: 'LayerZero is the dominant omnichain protocol with unmatched integrations.'
    }
  },
  {
    id: 'eigenlayer', name: 'EigenLayer', ticker: 'EIGEN', website: 'https://eigenlayer.xyz',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-05-10', estimatedReward: '$50-$3,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/eigenlayer', 'https://discord.gg/eigenlayer', '', 'https://eigenlayer.xyz'),
    scores: s(88, 95, 92, 90, 85, 88, 90),
    riskFlags: [],
    verdict: 'EigenLayer introduces restaking to Ethereum. Revolutionary concept with strong adoption.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Deposit LST (stETH, rETH) into EigenLayer', 'Restake with selected AVS', 'Delegate to node operators', 'Monitor rewards', 'Withdraw after unbonding period'],
      '15 Minutes', '$100-$1,000', 'Medium'
    ),
    aiAnalysis: {
      summary: 'EigenLayer is a restaking protocol that extends Ethereum security to external networks.',
      bullCase: 'Innovative restaking concept; rapid TVL growth; strong team from academia',
      bearCase: 'Slashing risks; complexity; regulatory uncertainty',
      competitiveAnalysis: 'First-mover in restaking, now facing competition from Symbiotic, Karak.',
      marketOpportunity: 'Restaking market projected to reach $100B+ TVL.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'Medium', costRequired: 'Medium', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'EigenLayer is a restaking protocol that lets ETH stakers secure multiple protocols.',
      projectOverview: 'Restaking reuses staked ETH to cryptographically guarantee services called AVSs.',
      productDescription: 'Platform for restakers, node operators, and AVSs to bootstrap network security.',
      ecosystemDescription: '15+ AVSs including EigenDA, Lagrange, and AltLayer.',
      useCases: ['Data availability', 'Sequencer security', 'Oracle networks'],
      teamInfo: 'Founded by Sreeram Kannan, PhD from University of Washington.',
      fundingInfo: 'Raised $64M from top VCs.',
      investors: ['Polychain Capital', 'Blockchain Capital', 'Coinbase Ventures'],
      tokenInfo: 'EIGEN for governance and slashing. Non-transferable initially.',
      reviewSummary: 'EigenLayer is a paradigm shift in cryptoeconomic security.'
    }
  },
  {
    id: 'fuel', name: 'Fuel Network', ticker: 'FUEL', website: 'https://fuel.network',
    category: 'Infrastructure', blockchain: 'Fuel', status: 'active',
    launchDate: '2025-12-10', estimatedReward: '$50-$1,500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/fuel_network', 'https://discord.gg/fuel', 'https://t.me/fuel', 'https://fuel.network'),
    scores: s(82, 85, 88, 80, 78, 80, 82),
    riskFlags: [],
    verdict: 'Fuel is a modular execution layer with parallel transaction execution.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Fuel', 'Swap on Fuel DEXes', 'Provide liquidity', 'Use Fuel dApps', 'Deploy contracts'],
      '15 Minutes', '$10-$50', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Fuel is a modular execution layer designed for maximum throughput.',
      bullCase: 'Parallel UTXO execution; strong team; modular architecture',
      bearCase: 'Early stage; competing execution environments',
      competitiveAnalysis: 'Competes as modular execution layer vs Eclipse, Movement.',
      marketOpportunity: 'Growing demand for high-throughput execution in modular stack.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '1x-5x' }
    },
    about: {
      aboutProject: 'Fuel is the world\'s first modular execution layer for the modular blockchain stack.',
      projectOverview: 'Fuel uses parallel UTXO execution to achieve unprecedented throughput.',
      productDescription: 'Fast and secure execution environment for DeFi, payments, and games.',
      ecosystemDescription: 'Early ecosystem with native DEX, perp, and lending dApps.',
      useCases: ['High-throughput DeFi', 'Payments', 'Gaming'],
      teamInfo: 'Core team from UC Berkeley with experience in distributed systems.',
      fundingInfo: 'Raised $80M+ from top investors.',
      investors: ['Blockchain Capital', 'Coinbase Ventures', 'Stratos', 'Hack VC'],
      tokenInfo: 'FUEL for gas fees, staking, and governance.',
      reviewSummary: 'Fuel\'s parallel execution offers unique advantages for throughput.'
    }
  },
  {
    id: 'megaeth', name: 'MegaETH', ticker: 'MEGA', website: 'https://megaeth.com',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2026-01-15', estimatedReward: '$200-$5,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/megaeth', 'https://discord.gg/megaeth', '', 'https://megaeth.com'),
    scores: s(85, 88, 82, 85, 80, 82, 85),
    riskFlags: ['Early Stage'],
    verdict: 'MegaETH aims to be the fastest EVM L2 with real-time block times.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join Discord and community', 'Deposit ETH into testnet', 'Run testnet transactions', 'Bridge assets', 'Provide feedback', 'Report issues'],
      '45 Minutes', '$0-$20', 'Medium'
    ),
    aiAnalysis: {
      summary: 'MegaETH is a real-time Ethereum L2 with 10-100ms block times.',
      bullCase: 'Real-time execution; strong team; Dragonfly-backed; innovative architecture',
      bearCase: 'Extremely ambitious; L2 competition; execution risk',
      competitiveAnalysis: 'Unique ultra-low latency positioning vs all other L2s.',
      marketOpportunity: 'Frontend of Ethereum - capturing latency-sensitive DeFi volume.',
      airdropAttractiveness: { rewardPotential: 'Very High', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '3x-10x' }
    },
    about: {
      aboutProject: 'MegaETH is a real-time blockchain that processes transactions in millisecond ranges.',
      projectOverview: 'MegaETH achieves sub-second finality through specialized node architecture.',
      productDescription: 'EVM-compatible L2 with 100ms block times and 100,000+ TPS.',
      ecosystemDescription: 'Pre-launch ecosystem targeting DeFi, trading, and gaming.',
      useCases: ['HFT-friendly DeFi', 'Real-time gaming', 'Payment infrastructure'],
      teamInfo: 'Led by team from Stanford, MIT, and top crypto projects.',
      fundingInfo: 'Raised $20M led by Dragonfly Capital.',
      investors: ['Dragonfly Capital', 'Variant', 'Figment Capital', 'ConsenSys'],
      tokenInfo: 'MEGA for gas, staking, and governance.',
      reviewSummary: 'MegaETH pushes the boundaries of L2 performance.'
    }
  },
  {
    id: 'bera', name: 'Berachain', ticker: 'BERA', website: 'https://berachain.com',
    category: 'Infrastructure', blockchain: 'Berachain', status: 'active',
    launchDate: '2025-12-15', estimatedReward: '$100-$3,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/berachain', 'https://discord.gg/berachain', '', 'https://berachain.com'),
    scores: s(85, 90, 85, 85, 90, 82, 88),
    riskFlags: [],
    verdict: 'Berachain uses Proof-of-Liquidity consensus. Strong community and investor backing.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge assets to Berachain', 'Provide liquidity to BEX pools', 'Stake BERA validators', 'Participate in governance', 'Use Berachain dApps'],
      '20 Minutes', '$50-$200', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Berachain is an EVM-identical L1 using Proof-of-Liquidity consensus.',
      bullCase: 'Innovative PoL consensus; strong community culture; Polychain-backed',
      bearCase: 'Complex tokenomics; L1 competition',
      competitiveAnalysis: 'Unique PoL consensus differentiates from standard L1s.',
      marketOpportunity: 'Aligning liquidity provision with network security creates novel dynamics.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'Medium', costRequired: 'Medium', expectedROI: '2x-8x' }
    },
    about: {
      aboutProject: 'Berachain is a high-performance EVM-identical L1 blockchain built on Proof-of-Liquidity consensus.',
      projectOverview: 'Berachain\'s Proof-of-Liquidity aligns validator incentives with ecosystem liquidity.',
      productDescription: 'Full EVM compatibility with native liquidity incentives and fast execution.',
      ecosystemDescription: 'Growing DeFi ecosystem with native DEX (BEX), lending, and perps.',
      useCases: ['DeFi', 'Liquidity provision', 'Staking', 'Governance'],
      teamInfo: 'Founded by anonymous team "Homme Bera" with deep DeFi experience.',
      fundingInfo: 'Raised $142M from top investors.',
      investors: ['Polychain Capital', 'Pantera Capital', 'Framework Ventures'],
      tokenInfo: 'BERA for gas, BGT for governance. Dual-token model.',
      reviewSummary: 'Berachain\'s novel PoL consensus creates alignment between validators and LPs.'
    }
  },
  {
    id: 'sui_drop', name: 'Sui', ticker: 'SUI', website: 'https://sui.io',
    category: 'Infrastructure', blockchain: 'Sui', status: 'active',
    launchDate: '2025-09-01', estimatedReward: '$50-$1,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/SuiNetwork', 'https://discord.gg/sui', 'https://t.me/sui', 'https://sui.io'),
    scores: s(82, 88, 85, 83, 80, 82, 78),
    riskFlags: [],
    verdict: 'Sui is a high-performance L1 with object-centric architecture and Move language.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Install Sui Wallet', 'Buy SUI on CEX', 'Bridge to Sui', 'Use Sui dApps (Cetus, Navi)', 'Stake SUI', 'Provide liquidity'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Sui is a high-throughput L1 blockchain built on Move language with parallel execution.',
      bullCase: 'Scalable Move-based L1; strong DeFi ecosystem; growing adoption',
      bearCase: 'L1 competition; Move adoption slower than EVM',
      competitiveAnalysis: 'Competes with Aptos, Solana, and other high-throughput L1s.',
      marketOpportunity: 'Growing demand for scalable L1s with novel architectures.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Sui is a high-performance L1 blockchain designed for fast, private, and secure digital asset ownership.',
      projectOverview: 'Sui uses object-centric data model and parallel execution for horizontal scaling.',
      productDescription: 'Smart contract platform with sub-second finality and low gas fees.',
      ecosystemDescription: '150+ dApps including Cetus, Navi, Turbos, and Bluefin.',
      useCases: ['DeFi', 'Gaming', 'Commerce', 'Social'],
      teamInfo: 'Developed by Mysten Labs, founded by former Meta engineers.',
      fundingInfo: 'Raised $336M at $2B+ valuation.',
      investors: ['Andreessen Horowitz', 'FTX Ventures', 'Coinbase Ventures'],
      tokenInfo: 'SUI for gas, staking, and governance. 10B supply.',
      reviewSummary: 'Sui is a robust L1 with growing ecosystem and strong technical foundations.'
    }
  },
  {
    id: 'babylon', name: 'Babylon', ticker: 'BABY', website: 'https://babylonchain.io',
    category: 'Infrastructure', blockchain: 'Bitcoin', status: 'active',
    launchDate: '2025-12-01', estimatedReward: '$50-$2,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/babylon_chain', 'https://discord.gg/babylon', '', 'https://babylonchain.io'),
    scores: s(85, 88, 82, 85, 78, 82, 85),
    riskFlags: [],
    verdict: 'Babylon brings Bitcoin staking to PoS chains. Strong thesis and backers.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Wrap BTC into Babylon', 'Stake BTC with Babylon', 'Delegate to finality providers', 'Earn yields', 'Monitor voting rounds'],
      '30 Minutes', '$200-$1,000', 'Hard'
    ),
    aiAnalysis: {
      summary: 'Babylon allows Bitcoin holders to stake BTC to secure PoS networks.',
      bullCase: 'Bitcoin security-as-a-service; massive TAM; strong team from academia',
      bearCase: 'Complex security model; regulatory risk for BTC staking',
      competitiveAnalysis: 'Unique in Bitcoin-based restaking; some overlap with EigenLayer.',
      marketOpportunity: 'Unlocks $1T+ BTC as security for PoS networks.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'High', costRequired: 'High', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Babylon is a protocol that brings Bitcoin staking to the PoS ecosystem.',
      projectOverview: 'Bitcoin holders can stake their BTC without third-party bridges or wrapping.',
      productDescription: 'Trustless Bitcoin staking protocol leveraging Bitcoin\'s script language.',
      ecosystemDescription: 'Bitcoin holders staking via Babylon, finality providers operating nodes, and a growing set of PoS chains (Cosmos, Polygon, BNB Chain) integrating Babylon for cryptoeconomic security. The ecosystem also includes liquid staking protocols building on Babylon to offer tradable stBTC derivatives.',
      useCases: ['Bitcoin restaking', 'PoS chain security', 'BTC yield generation'],
      teamInfo: 'Founded by David Tse, Stanford professor and blockchain researcher.',
      fundingInfo: 'Raised $70M from top crypto investors.',
      investors: ['Polychain Capital', 'Framework Ventures', 'HashKey Capital'],
      tokenInfo: 'BABY for governance and slashing. Economic security through BTC staking.',
      reviewSummary: 'Babylon addresses the largest untapped market in crypto: Bitcoin capital.'
    }
  },
  {
    id: 'mode', name: 'Mode', ticker: 'MODE', website: 'https://mode.network',
    category: 'DeFi', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-10-01', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/modenetwork', 'https://discord.gg/mode', '', 'https://mode.network'),
    scores: s(75, 78, 80, 75, 72, 75, 78),
    riskFlags: [],
    verdict: 'Mode is an OP Stack L2 focused on DeFi and AI agents.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Mode', 'Swap on Mode DEXes', 'Provide liquidity', 'Use Mode lending protocols'],
      '10 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Mode is an OP Stack L2 with DeFi and AI agent integrations.',
      bullCase: 'OP Stack security; DeFi focus; AI agent narrative',
      bearCase: 'Crowded L2 space; limited differentiation',
      competitiveAnalysis: 'Competes as a DeFi-focused OP Stack L2.',
      marketOpportunity: 'Growing demand for specialized L2s with DeFi primitives.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Mode is an OP Stack L2 building the superchain for AI and DeFi.',
      projectOverview: 'Mode integrates AI agents into DeFi for automated yield optimization.',
      productDescription: 'Low-fee L2 with native DeFi rewards and AI trading agents.',
      ecosystemDescription: 'Growing ecosystem with DEX, lending, and AI agent platforms.',
      useCases: ['DeFi', 'AI trading agents', 'Yield optimization'],
      teamInfo: 'Team from top DeFi projects and engineering backgrounds.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Optimism Foundation', 'DWF Labs', 'Maven Capital'],
      tokenInfo: 'MODE for governance, fee discounts, and ecosystem rewards.',
      reviewSummary: 'Mode differentiates through AI x DeFi integration on the Superchain.'
    }
  },
  {
    id: 'taiko', name: 'Taiko', ticker: 'TAIKO', website: 'https://taiko.xyz',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-08-15', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/taikoxyz', 'https://discord.gg/taiko', '', 'https://taiko.xyz'),
    scores: s(78, 82, 82, 78, 75, 78, 80),
    riskFlags: [],
    verdict: 'Taiko is a based rollup with Ethereum-level sequencing security.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Taiko', 'Swap on Taiko DEXes', 'Provide liquidity', 'Use Taiko dApps', 'Bridge back'],
      '10 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Taiko is a based rollup - an L2 secured by Ethereum L1 proposers.',
      bullCase: 'Based sequencing innovation; Ethereum alignment; strong community',
      bearCase: 'Competing L2s with more features; adoption challenges',
      competitiveAnalysis: 'Unique based rollup architecture vs standard rollups.',
      marketOpportunity: 'Growing demand for Ethereum-aligned scaling solutions.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Taiko is a decentralized, Ethereum-equivalent ZK-rollup.',
      projectOverview: 'Taiko is a based rollup where Ethereum validators propose L2 blocks.',
      productDescription: 'EVM-identical ZK-rollup with Ethereum-level security guarantees.',
      ecosystemDescription: '50+ dApps across DeFi, NFTs, and infrastructure.',
      useCases: ['DeFi', 'NFTs', 'Scalable dApps'],
      teamInfo: 'Led by a team with deep Ethereum research background.',
      fundingInfo: 'Raised $37M from top investors.',
      investors: ['Sequoia China', 'Generative Ventures', 'IOSG'],
      tokenInfo: 'TAIKO for governance and protocol fees.',
      reviewSummary: 'Taiko\'s based rollup design offers unique security guarantees.'
    }
  },
  {
    id: 'zora', name: 'Zora', ticker: 'ZORA', website: 'https://zora.co',
    category: 'NFT', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-09-01', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/ourZORA', 'https://discord.gg/zora', '', 'https://zora.co'),
    scores: s(80, 82, 85, 78, 85, 80, 78),
    riskFlags: [],
    verdict: 'Zora is a creator-focused NFT platform and L2 network.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Create NFT on Zora', 'Collect NFTs from creators', 'Bridge ETH to Zora Network', 'Use Zora dApps'],
      '15 Minutes', '$5-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Zora is a creator-first NFT platform and OP Stack L2 network.',
      bullCase: 'Strong creator community; OP Stack; brand recognition',
      bearCase: 'NFT market downturn; competition from Blur, OpenSea',
      competitiveAnalysis: 'Competes with OpenSea, Blur, and other NFT marketplaces.',
      marketOpportunity: 'Creator economy and NFT market growing long-term.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Zora is a decentralized protocol for creating and trading NFTs.',
      projectOverview: 'Zora enables creators to mint, auction, and distribute NFTs with fair royalties.',
      productDescription: 'NFT marketplace and L2 network for digital art and collectibles.',
      ecosystemDescription: 'Thousands of creators, collectors, and developers building on Zora.',
      useCases: ['NFT creation', 'Art collecting', 'Creator monetization'],
      teamInfo: 'Founded by Jacob Horne, with team from Coinbase and leading NFT projects.',
      fundingInfo: 'Raised $60M from top investors.',
      investors: ['Kindred Ventures', 'Coinbase Ventures', 'Haun Ventures'],
      tokenInfo: 'ZORA for protocol governance.',
      reviewSummary: 'Zora is the leading creator-centric NFT platform.'
    }
  },
  {
    id: 'base', name: 'Base', ticker: 'BASE', website: 'https://base.org',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-08-01', estimatedReward: '$50-$2,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/BuildOnBase', 'https://discord.gg/base', '', 'https://base.org'),
    scores: s(82, 90, 88, 85, 88, 82, 85),
    riskFlags: [],
    verdict: 'Base is Coinbase\'s OP Stack L2 with massive user base potential.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Base', 'Use Aerodrome DEX', 'Use Base DeFi protocols', 'Provide liquidity', 'Use Base NFTs'],
      '10 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Base is a Coinbase-incubated OP Stack L2 with massive distribution.',
      bullCase: 'Coinbase distribution; Base ecosystem booming; Onchain Summer',
      bearCase: 'Governance concerns; centralization risk',
      competitiveAnalysis: 'Unique position with Coinbase integration vs other L2s.',
      marketOpportunity: 'Coinbase\'s 100M+ users onboarding to L2.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Base is a secure, low-cost, builder-friendly Ethereum L2 built on OP Stack.',
      projectOverview: 'Base aims to bring the next million builders and billion users onchain.',
      productDescription: 'EVM-equivalent L2 with low fees, fast transactions, and Coinbase integration.',
      ecosystemDescription: '200+ dApps including Aerodrome, Compound, Aave.',
      useCases: ['DeFi', 'NFTs', 'Social', 'Gaming'],
      teamInfo: 'Built by Coinbase, one of the largest crypto companies globally.',
      fundingInfo: 'Funded by Coinbase.',
      investors: ['Coinbase'],
      tokenInfo: 'BASE for governance (expected).',
      reviewSummary: 'Base leverages Coinbase\'s brand and distribution for massive adoption.'
    }
  },
  {
    id: 'blast', name: 'Blast', ticker: 'BLAST', website: 'https://blast.io',
    category: 'DeFi', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-06-15', estimatedReward: '$50-$1,500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/Blast_L2', 'https://discord.gg/blast', '', 'https://blast.io'),
    scores: s(78, 85, 82, 80, 82, 80, 82),
    riskFlags: ['Unclear Token Utility'],
    verdict: 'Blast is an L2 with native yield for ETH and stablecoins.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Blast', 'Use Blast DEXes', 'Provide liquidity', 'Blast Points accumulation', 'Use Blast dApps'],
      '10 Minutes', '$10-$100', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Blast is an L2 with native yield from ETH staking and RWA protocols.',
      bullCase: 'Native yield innovation; strong TVL growth; points system',
      bearCase: 'Competing L2s; yield sustainability questions',
      competitiveAnalysis: 'Unique native yield vs all other L2s.',
      marketOpportunity: 'User demand for yield-bearing L2 solutions.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Blast is an Ethereum L2 with native yield for ETH and stablecoins.',
      projectOverview: 'Blast automatically generates yield on bridged assets through L1 staking.',
      productDescription: 'L2 with automatic yield, low fees, and growing DeFi ecosystem.',
      ecosystemDescription: 'Major protocols: Blast DEX, Fragment, Juice Finance.',
      useCases: ['Yield generation', 'DeFi', 'Trading'],
      teamInfo: 'Founded by Pacman (Blur founder) with team from MIT and top crypto projects.',
      fundingInfo: 'Raised from Paradigm and others.',
      investors: ['Paradigm', 'Standard Crypto', 'eGirl Capital'],
      tokenInfo: 'BLAST for governance and yield distribution.',
      reviewSummary: 'Blast innovates with native yield but faces L2 competition.'
    }
  },
  {
    id: 'penumbra', name: 'Penumbra', ticker: 'PEN', website: 'https://penumbra.zone',
    category: 'Privacy', blockchain: 'Penumbra', status: 'active',
    launchDate: '2025-11-01', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/penumbrazone', 'https://discord.gg/penumbra', '', 'https://penumbra.zone'),
    scores: s(78, 75, 80, 72, 70, 78, 75),
    riskFlags: ['Anonymous Team', 'Niche Market'],
    verdict: 'Penumbra is a privacy-focused blockchain for shielded DeFi.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Download Penumbra app', 'Create shielded account', 'Bridge to Penumbra', 'Perform shielded swaps', 'Stake PEN'],
      '30 Minutes', '$10-$50', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Penumbra is a privacy-focused blockchain for shielded DeFi interactions.',
      bullCase: 'Privacy-first architecture; innovative shielded DEX; Cosmos IBC integration',
      bearCase: 'Privacy coin regulatory risk; niche market',
      competitiveAnalysis: 'Unique shielded DeFi vs Secret Network, Namada.',
      marketOpportunity: 'Growing demand for financial privacy in DeFi.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Penumbra is a privacy-preserving blockchain for DeFi. All transactions are fully shielded.',
      projectOverview: 'Penumbra uses zero-knowledge proofs to enable private trading, staking, and swapping.',
      productDescription: 'Shielded DEX with private swaps, LP provision, and staking.',
      ecosystemDescription: 'Part of Cosmos ecosystem with IBC interoperability.',
      useCases: ['Private DeFi', 'Shielded swapping', 'Private staking'],
      teamInfo: 'Core team from Zcash and blockchain research.',
      fundingInfo: 'Funded by grants and strategic investors.',
      investors: ['Zcash Foundation', 'Interchain Foundation'],
      tokenInfo: 'PEN for governance, staking, and privacy fees.',
      reviewSummary: 'Penumbra offers the most advanced privacy for DeFi transactions.'
    }
  },
  {
    id: 'celestia', name: 'Celestia', ticker: 'TIA', website: 'https://celestia.org',
    category: 'Infrastructure', blockchain: 'Celestia', status: 'active',
    launchDate: '2025-10-15', estimatedReward: '$50-$1,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/CelestiaOrg', 'https://discord.gg/celestia', '', 'https://celestia.org'),
    scores: s(85, 92, 88, 85, 80, 82, 82),
    riskFlags: [],
    verdict: 'Celestia is the first modular data availability network. Strong thesis.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to Celestia', 'Stake TIA with validator', 'Use Celestia-based rollups', 'Delegate to ecosystem'],
      '15 Minutes', '$20-$100', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Celestia is a modular data availability network that makes it easy to launch blockchains.',
      bullCase: 'Modular thesis pioneer; strong adoption; ecosystem growth',
      bearCase: 'Competing DA solutions (EigenDA, Avail); token dilution',
      competitiveAnalysis: 'First-mover in modular DA vs EigenDA, Avail, Near DA.',
      marketOpportunity: 'Modular blockchain market projected to be $100B+.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Celestia is the first modular blockchain network for data availability.',
      projectOverview: 'Celestia separates execution from consensus, enabling sovereign rollups.',
      productDescription: 'Data availability layer with Namespaced Merkle Trees for efficient verification.',
      ecosystemDescription: '20+ rollups including Eclipse, Movement, and Cevmos.',
      useCases: ['Data availability', 'Sovereign rollups', 'Modular blockchain deployment'],
      teamInfo: 'Founded by Mustafa Al-Bassam, Ismail Khoffi, John Adler.',
      fundingInfo: 'Raised $55M from top investors.',
      investors: ['Polychain Capital', 'Coinbase Ventures', 'Binance Labs'],
      tokenInfo: 'TIA for gas, staking, and governance.',
      reviewSummary: 'Celestia is the foundational layer of the modular blockchain ecosystem.'
    }
  },
  {
    id: 'dymension', name: 'Dymension', ticker: 'DYM', website: 'https://dymension.xyz',
    category: 'Infrastructure', blockchain: 'Dymension', status: 'active',
    launchDate: '2025-11-01', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/dymension', 'https://discord.gg/dymension', '', 'https://dymension.xyz'),
    scores: s(78, 82, 80, 78, 75, 78, 78),
    riskFlags: [],
    verdict: 'Dymension is a network of modular rollups called RollApps.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to Dymension', 'Use Dymension RollApps', 'Stake DYM', 'Provide liquidity'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Dymension is a network of easily deployable modular rollups called RollApps.',
      bullCase: 'Modular ecosystem; IBC-connected; easy RollApp deployment',
      bearCase: 'Early stage; RollApp adoption TBD',
      competitiveAnalysis: 'Competes with Celestia, Eclipse in modular space.',
      marketOpportunity: 'Growing demand for specialized application chains.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Dymension is a network of modular settlement layers for RollApps.',
      projectOverview: 'RollApps are specialized application-specific rollups secured by Dymension.',
      productDescription: 'Settlement and security layer for IBC-connected RollApps.',
      ecosystemDescription: 'Growing ecosystem of RollApps across DeFi, gaming, and social.',
      useCases: ['RollApp deployment', 'Cross-chain settlement', 'Modular infrastructure'],
      teamInfo: 'Team with Cosmos and IBC development experience.',
      fundingInfo: 'Raised from top investors.',
      investors: ['Polychain Capital', 'Placeholder', 'Stratos'],
      tokenInfo: 'DYM for governance, security, and gas.',
      reviewSummary: 'Dymension simplifies rollup deployment for developers.'
    }
  },
  {
    id: 'polyhedra', name: 'Polyhedra Network', ticker: 'ZKJ', website: 'https://polyhedra.network',
    category: 'Infrastructure', blockchain: 'Multi-Chain', status: 'active',
    launchDate: '2025-12-01', estimatedReward: '$30-$1,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/PolyhedraZK', 'https://discord.gg/polyhedra', '', 'https://polyhedra.network'),
    scores: s(80, 85, 82, 80, 75, 80, 80),
    riskFlags: [],
    verdict: 'Polyhedra builds ZK-proof infrastructure for interoperability.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Use zkBridge to transfer assets', 'Use Polyhedra dApps', 'Provide feedback', 'Join community'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Polyhedra Network builds ZK-proof infrastructure for cross-chain interoperability.',
      bullCase: 'Innovative zkBridge; strong team; multiple chain integrations',
      bearCase: 'Competing bridge solutions; ZK competition',
      competitiveAnalysis: 'Competes with LayerZero, Wormhole for cross-chain infrastructure.',
      marketOpportunity: 'Cross-chain infrastructure critical for multi-chain future.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Polyhedra Network uses zero-knowledge proofs for scalable cross-chain infrastructure.',
      projectOverview: 'Polyhedra\'s zkBridge provides trustless and efficient cross-chain communication.',
      productDescription: 'ZK-based infrastructure for asset transfer, data verification, and interop.',
      ecosystemDescription: 'Integrated with 20+ blockchains including Ethereum, BNB Chain, Polygon.',
      useCases: ['Cross-chain bridging', 'ZK-proof verification', 'Interoperability'],
      teamInfo: 'Led by PhDs in cryptography and distributed systems.',
      fundingInfo: 'Raised $25M from top investors.',
      investors: ['Polychain Capital', 'Binance Labs', 'Animoca Brands'],
      tokenInfo: 'ZKJ for governance and protocol fees.',
      reviewSummary: 'Polyhedra advances ZK technology for practical interoperability.'
    }
  },
  {
    id: 'initia', name: 'Initia', ticker: 'INIT', website: 'https://initia.xyz',
    category: 'Infrastructure', blockchain: 'Initia', status: 'active',
    launchDate: '2026-01-10', estimatedReward: '$50-$2,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/initia', 'https://discord.gg/initia', '', 'https://initia.xyz'),
    scores: s(82, 85, 80, 82, 78, 80, 82),
    riskFlags: ['Early Stage'],
    verdict: 'Initia is a modular L1 with integrated L2 app-specific rollup framework.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join Initia testnet', 'Run validator node', 'Deploy test app', 'Interact with ecosystem'],
      '1 Hour', '$0-$20', 'Hard'
    ),
    aiAnalysis: {
      summary: 'Initia is a modular L1 with an integrated framework for launching L2s.',
      bullCase: 'Binance-backed; innovative app-chain vision; strong team',
      bearCase: 'Early; complex architecture; execution risk',
      competitiveAnalysis: 'Unique L1+L2 integrated vision vs standalone L1s/L2s.',
      marketOpportunity: 'Growing demand for easy-to-launch app-specific chains.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'High', costRequired: 'Low', expectedROI: '2x-8x' }
    },
    about: {
      aboutProject: 'Initia is a modular L1 blockchain platform with interwoven L2 app-specific rollups.',
      projectOverview: 'Initia provides a complete stack for launching and securing application-specific L2s.',
      productDescription: 'Layer-1 with integrated OP rollup framework for L2 app-chains.',
      ecosystemDescription: 'Pre-launch ecosystem with multiple teams building L2s.',
      useCases: ['App-chain deployment', 'Modular DeFi', 'Gaming L2s'],
      teamInfo: 'Founded by team with Cosmos and L2 development experience.',
      fundingInfo: 'Raised $7.5M from Binance Labs and others.',
      investors: ['Binance Labs', 'Big Brain Holdings', 'Delphi Digital'],
      tokenInfo: 'INIT for governance, security, and gas.',
      reviewSummary: 'Initia simplifies L2 deployment with integrated L1 security.'
    }
  },
  {
    id: 'movement', name: 'Movement', ticker: 'MOVE', website: 'https://movementlabs.xyz',
    category: 'Infrastructure', blockchain: 'Movement', status: 'active',
    launchDate: '2026-01-15', estimatedReward: '$50-$1,500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/movementlabsxyz', 'https://discord.gg/movement', '', 'https://movementlabs.xyz'),
    scores: s(82, 85, 82, 82, 78, 80, 82),
    riskFlags: ['Early Stage'],
    verdict: 'Movement brings MoveVM to Ethereum ecosystem via L2.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Movement testnet', 'Deploy Move contracts', 'Use Move dApps', 'Provide feedback'],
      '30 Minutes', '$0-$20', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Movement brings MoveVM to Ethereum as a ZK-rollup L2.',
      bullCase: 'MoveVM + Ethereum liquidity; strong backing; Binance Labs',
      bearCase: 'Move adoption challenges; L2 competition',
      competitiveAnalysis: 'Unique Move on Ethereum vs native Move L1s (Sui, Aptos).',
      marketOpportunity: 'Bridging Move language advantages with Ethereum network effects.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Movement is a Move-based L2 bringing MoveVM execution to Ethereum.',
      projectOverview: 'Movement combines Move language security with Ethereum liquidity.',
      productDescription: 'Move-EVM L2 with parallel execution and formal verification benefits.',
      ecosystemDescription: 'Growing ecosystem with Move-native DeFi protocols.',
      useCases: ['Secure DeFi', 'Formally verified contracts', 'Cross-VM dApps'],
      teamInfo: 'Founded by team with Move and Ethereum development expertise.',
      fundingInfo: 'Raised from top investors.',
      investors: ['Binance Labs', 'Polychain Capital', 'Hack VC'],
      tokenInfo: 'MOVE for governance, gas, and staking.',
      reviewSummary: 'Movement bridges Move\'s safety with Ethereum\'s network effects.'
    }
  },
  {
    id: 'eclipse', name: 'Eclipse', ticker: 'ECL', website: 'https://eclipse.xyz',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'active',
    launchDate: '2026-01-20', estimatedReward: '$100-$3,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/EclipseFND', 'https://discord.gg/eclipse', '', 'https://eclipse.xyz'),
    scores: s(85, 88, 82, 85, 80, 82, 85),
    riskFlags: ['Early Stage'],
    verdict: 'Eclipse is a Solana VM L2 secured by Ethereum.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Eclipse testnet', 'Use Eclipse DEXes', 'Deploy programs', 'Provide liquidity'],
      '30 Minutes', '$10-$50', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Eclipse is a Solana Virtual Machine L2 secured by Ethereum.',
      bullCase: 'Best of Solana speed + Ethereum security; strong team; Polkadot backing',
      bearCase: 'Complex architecture; execution risk',
      competitiveAnalysis: 'Unique SVM + Ethereum L2 combination.',
      marketOpportunity: 'Bridging Solana and Ethereum ecosystems.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '2x-8x' }
    },
    about: {
      aboutProject: 'Eclipse is the first SVM L2 rollup secured by Ethereum.',
      projectOverview: 'Eclipse combines Solana\'s execution with Ethereum\'s security and Celestia\'s DA.',
      productDescription: 'SVM L2 enabling Solana-native dApps on Ethereum.',
      ecosystemDescription: 'Pre-launch ecosystem with SVM-native DeFi protocols.',
      useCases: ['High-speed DeFi', 'Solana-Ethereum bridging', 'SVM dApp deployment'],
      teamInfo: 'Founded by Neel Somani with team from top tech and crypto companies.',
      fundingInfo: 'Raised $65M from top investors.',
      investors: ['Polychain Capital', 'Polygon', 'Coinbase Ventures'],
      tokenInfo: 'ECL for governance and gas fees.',
      reviewSummary: 'Eclipse combines the best of Solana and Ethereum ecosystems.'
    }
  },
  {
    id: 'avail', name: 'Avail', ticker: 'AVAIL', website: 'https://availproject.org',
    category: 'Infrastructure', blockchain: 'Avail', status: 'active',
    launchDate: '2026-01-05', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/AvailProject', 'https://discord.gg/avail', '', 'https://availproject.org'),
    scores: s(80, 85, 82, 80, 75, 78, 80),
    riskFlags: [],
    verdict: 'Avail is a modular DA layer from Polygon team.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Stake AVAIL tokens', 'Use Avail DA for rollups', 'Run DA validator node', 'Build on Avail'],
      '20 Minutes', '$20-$100', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Avail is a modular data availability layer spun out from Polygon.',
      bullCase: 'Polygon team experience; growing DA demand; modular thesis',
      bearCase: 'DA competition (Celestia, EigenDA); late to market',
      competitiveAnalysis: 'Competes with Celestia, EigenDA, Near DA.',
      marketOpportunity: 'DA market critical for modular blockchain scaling.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Medium', costRequired: 'Medium', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Avail is a modular data availability and consensus layer.',
      projectOverview: 'Avail provides secure data availability for the modular blockchain ecosystem.',
      productDescription: 'DA layer with KZG commitments, fast finality, and easy validator set.',
      ecosystemDescription: 'Growing partner ecosystem with rollups integrating Avail for DA.',
      useCases: ['Data availability', 'Modular consensus', 'Validity proof settlement'],
      teamInfo: 'Led by Polygon co-founder Anurag Arjun.',
      fundingInfo: 'Raised $27M from top investors.',
      investors: ['Founders Fund', 'Dragonfly Capital', 'Coinbase Ventures'],
      tokenInfo: 'AVAIL for DA fees, staking, and governance.',
      reviewSummary: 'Avail addresses the critical DA need in modular blockchain architecture.'
    }
  },
  {
    id: 'puffer', name: 'Puffer Finance', ticker: 'PUFFER', website: 'https://puffer.fi',
    category: 'DeFi', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-12-15', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/puffer_finance', 'https://discord.gg/puffer', '', 'https://puffer.fi'),
    scores: s(78, 82, 80, 78, 75, 78, 80),
    riskFlags: [],
    verdict: 'Puffer Finance is a native liquid restaking protocol.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Deposit ETH into Puffer', 'Receive pufETH', 'Use pufETH in DeFi', 'Delegate to validators', 'Monitor rewards'],
      '15 Minutes', '$100-$1,000', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Puffer Finance is a native liquid restaking protocol on Ethereum.',
      bullCase: 'LRT narrative; EigenLayer integration; anti-slashing technology',
      bearCase: 'LRT competition; restaking risks',
      competitiveAnalysis: 'Competes with Lido, Rocket Pool, Swell in LST/LRT space.',
      marketOpportunity: 'Growing demand for liquid staking and restaking derivatives.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Medium', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Puffer Finance is a decentralized liquid restaking protocol on Ethereum.',
      projectOverview: 'Puffer uses native restaking and anti-slashing hardware to secure ETH deposits.',
      productDescription: 'Liquid restaking token (pufETH) that earns staking and restaking rewards.',
      ecosystemDescription: 'Integrated with EigenLayer AVSs and major DeFi protocols.',
      useCases: ['Liquid restaking', 'ETH yield optimization', 'AVS security'],
      teamInfo: 'Team with Ethereum research and distributed systems expertise.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Jump Crypto', 'Brevan Howard', 'ConsenSys'],
      tokenInfo: 'PUFFER for governance and fee sharing.',
      reviewSummary: 'Puffer offers competitive LRT yields with strong security guarantees.'
    }
  },
  {
    id: 'etherfi', name: 'Ether.fi', ticker: 'ETHFI', website: 'https://ether.fi',
    category: 'DeFi', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-11-15', estimatedReward: '$30-$1,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/ether_fi', 'https://discord.gg/etherfi', '', 'https://ether.fi'),
    scores: s(80, 85, 82, 80, 82, 80, 78),
    riskFlags: [],
    verdict: 'Ether.fi is a liquid restaking protocol with EigenLayer integration.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Deposit ETH into Ether.fi', 'Receive eETH', 'Use eETH in DeFi', 'Delegate to operators', 'Withdraw when ready'],
      '15 Minutes', '$100-$1,000', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Ether.fi is a non-custodial liquid restaking protocol on Ethereum.',
      bullCase: 'First-mover LRT; strong TVL growth; EigenLayer integration',
      bearCase: 'LRT competition; restaking risks',
      competitiveAnalysis: 'Leading LRT provider vs Puffer, Swell, Kelp.',
      marketOpportunity: 'LRT market projected to reach $50B+.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Medium', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Ether.fi is a non-custodial liquid restaking protocol.',
      projectOverview: 'Ether.fi enables users to retain control of their ETH while earning staking rewards.',
      productDescription: 'Liquid restaking token eETH with DeFi composability.',
      ecosystemDescription: 'Deep integration with EigenLayer AVSs and major DEXes.',
      useCases: ['Liquid restaking', 'ETH yield', 'DeFi collateral'],
      teamInfo: 'Led by Mike Silagadze with team from top DeFi projects.',
      fundingInfo: 'Raised $27M from top investors.',
      investors: ['Coinbase Ventures', 'Polychain Capital', 'North Island Ventures'],
      tokenInfo: 'ETHFI for governance and revenue sharing.',
      reviewSummary: 'Ether.fi is the leading liquid restaking protocol by TVL.'
    }
  },
  {
    id: 'swell', name: 'Swell', ticker: 'SWELL', website: 'https://swellnetwork.io',
    category: 'DeFi', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-10-15', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/swellnetwork', 'https://discord.gg/swell', '', 'https://swellnetwork.io'),
    scores: s(75, 80, 78, 75, 75, 76, 75),
    riskFlags: [],
    verdict: 'Swell is a liquid staking protocol with EigenLayer restaking.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Deposit ETH into Swell', 'Receive rswETH', 'Use rswETH in DeFi', 'Earn rewards'],
      '10 Minutes', '$50-$500', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Swell is a non-custodial liquid staking and restaking protocol.',
      bullCase: 'EigenLayer integration; growing ecosystem',
      bearCase: 'LRT competition; yield compression',
      competitiveAnalysis: 'Competes with Ether.fi, Puffer, Lido in liquid staking.',
      marketOpportunity: 'Growing demand for liquid staking derivatives.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Swell is a non-custodial liquid staking and restaking protocol.',
      projectOverview: 'Swell offers both liquid staking (swETH) and liquid restaking (rswETH).',
      productDescription: 'Multi-asset liquid staking platform with optimized yields.',
      ecosystemDescription: 'Integrated with major DeFi protocols across multiple chains.',
      useCases: ['Liquid staking', 'Restaking', 'Yield optimization'],
      teamInfo: 'Founder Daniel Dizon with team from leading DeFi projects.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Framework Ventures', 'IOSG Ventures', 'Apollo Capital'],
      tokenInfo: 'SWELL for governance and ecosystem rewards.',
      reviewSummary: 'Swell offers a competitive liquid staking product with strong tokenomics.'
    }
  },
  {
    id: 'ainn', name: 'Ainn', ticker: 'AINN', website: 'https://ainn.finance',
    category: 'DeFi', blockchain: 'Ethereum', status: 'active',
    launchDate: '2026-01-10', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/ainn_finance', 'https://discord.gg/ainn', '', 'https://ainn.finance'),
    scores: s(72, 75, 78, 75, 70, 75, 75),
    riskFlags: ['Early Stage', 'Anonymous Team'],
    verdict: 'Ainn is an AI-powered DeFi yield optimizer.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Connect wallet to Ainn', 'Deposit assets', 'Select yield strategy', 'Monitor AI optimization', 'Withdraw rewards'],
      '15 Minutes', '$50-$500', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Ainn uses AI agents to optimize DeFi yield strategies.',
      bullCase: 'AI x DeFi narrative; automated yield optimization',
      bearCase: 'Anonymous team; unproven AI model; competition',
      competitiveAnalysis: 'Competes with Yearn, Idle, and other yield optimizers.',
      marketOpportunity: 'Growing demand for automated DeFi yield optimization.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Ainn is an AI-powered DeFi platform for automated yield generation.',
      projectOverview: 'Ainn uses machine learning models to optimize yield strategies across DeFi.',
      productDescription: 'AI-driven yield optimizer with automated strategy execution.',
      ecosystemDescription: 'Integrated with major DEXes and lending protocols.',
      useCases: ['Automated yield', 'AI trading', 'Portfolio optimization'],
      teamInfo: 'Anonymous team with DeFi and ML expertise.',
      fundingInfo: 'Raised pre-seed from strategic investors.',
      investors: ['Private'],
      tokenInfo: 'AINN for governance and fee sharing.',
      reviewSummary: 'Ainn combines AI and DeFi but team anonymity increases risk.'
    }
  },
  {
    id: 'tenet', name: 'Tenet', ticker: 'TENET', website: 'https://tenet.org',
    category: 'Infrastructure', blockchain: 'Tenet', status: 'active',
    launchDate: '2025-09-15', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/TenetLabs', 'https://discord.gg/tenet', '', 'https://tenet.org'),
    scores: s(75, 78, 76, 74, 72, 74, 75),
    riskFlags: [],
    verdict: 'Tenet is an L1 with diversified staking and liquid staking hub.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to Tenet', 'Stake TENET', 'Provide LSD liquidity', 'Use Tenet dApps'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Tenet is an EVM L1 with diversified staking across multiple assets.',
      bullCase: 'Multi-asset staking; growing ecosystem',
      bearCase: 'L1 competition; liquidity fragmentation',
      competitiveAnalysis: 'Unique multi-asset staking vs single-asset L1s.',
      marketOpportunity: 'Growing demand for L1 diversification.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Tenet is an EVM-compatible L1 with diversified liquid staking.',
      projectOverview: 'Tenet enables staking with ETH, BTC, and other major assets.',
      productDescription: 'L1 blockchain with native multi-asset liquid staking.',
      ecosystemDescription: 'Growing DeFi ecosystem with native protocols.',
      useCases: ['Multi-asset staking', 'Liquid staking', 'DeFi'],
      teamInfo: 'Team with L1 and DeFi development expertise.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Private'],
      tokenInfo: 'TENET for gas, staking, and governance.',
      reviewSummary: 'Tenet differentiates through multi-asset staking capabilities.'
    }
  },
  {
    id: 'kamino', name: 'Kamino', ticker: 'KMNO', website: 'https://kamino.finance',
    category: 'DeFi', blockchain: 'Solana', status: 'active',
    launchDate: '2025-11-01', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/KaminoFinance', 'https://discord.gg/kamino', '', 'https://kamino.finance'),
    scores: s(78, 80, 82, 78, 76, 78, 78),
    riskFlags: [],
    verdict: 'Kamino is a leading lending and leverage protocol on Solana.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Connect Solana wallet', 'Deposit assets', 'Borrow or lend', 'Provide liquidity', 'Earn KMNO rewards'],
      '10 Minutes', '$10-$100', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Kamino is a Solana-native lending and automated leverage protocol.',
      bullCase: 'Solana ecosystem growth; innovative leverage products',
      bearCase: 'Competition from Marginfi, Solend',
      competitiveAnalysis: 'Competing with Marginfi, Solend, and Radium on Solana.',
      marketOpportunity: 'Growing Solana DeFi ecosystem demand.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Kamino is a Solana lending protocol with automated leverage strategies.',
      projectOverview: 'Kamino offers lending, borrowing, and multiply products for leveraged yield.',
      productDescription: 'Non-custodial lending market with automated position management.',
      ecosystemDescription: 'Integrated with Solana DeFi ecosystem.',
      useCases: ['Lending', 'Borrowing', 'Leveraged yield'],
      teamInfo: 'Anonymous team with proven DeFi track record.',
      fundingInfo: 'Backed by top Solana ecosystem investors.',
      investors: ['Jump Crypto', 'Coinbase Ventures'],
      tokenInfo: 'KMNO for governance and fee discounts.',
      reviewSummary: 'Kamino offers the best leverage product on Solana.'
    }
  },
  {
    id: 'parcl', name: 'Parcl', ticker: 'PRCL', website: 'https://parcl.com',
    category: 'DeFi', blockchain: 'Solana', status: 'active',
    launchDate: '2025-12-01', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/parcl', 'https://discord.gg/parcl', '', 'https://parcl.com'),
    scores: s(75, 78, 80, 76, 72, 76, 76),
    riskFlags: [],
    verdict: 'Parcl is a real estate index trading protocol on Solana.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Connect Solana wallet', 'Deposit USDC', 'Trade real estate indices', 'Provide liquidity'],
      '10 Minutes', '$20-$200', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Parcl enables trading of real estate price indices on Solana.',
      bullCase: 'Novel RWA product; growing demand for real estate exposure',
      bearCase: 'Niche product; liquidity dependency',
      competitiveAnalysis: 'First-mover in blockchain real estate indices.',
      marketOpportunity: 'Real estate market trillions - tokenized exposure growing.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Parcl is a decentralized platform for trading real estate indexes.',
      projectOverview: 'Parcl enables users to gain synthetic exposure to real estate markets.',
      productDescription: 'Real estate index trading with leverage, LP provision, and yield.',
      ecosystemDescription: 'Solana-based ecosystem with RWA focus.',
      useCases: ['Real estate trading', 'Hedging', 'Portfolio diversification'],
      teamInfo: 'Team with real estate and DeFi expertise.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Arrington Capital', 'Big Brain Holdings', 'Solana Ventures'],
      tokenInfo: 'PRCL for governance and fee sharing.',
      reviewSummary: 'Parcl brings real estate markets on-chain with novel indices.'
    }
  },
  {
    id: 'apex', name: 'ApeX Protocol', ticker: 'APEX', website: 'https://apex.exchange',
    category: 'DeFi', blockchain: 'Ethereum', status: 'active',
    launchDate: '2025-10-01', estimatedReward: '$20-$400', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/ApeX_Protocol', 'https://discord.gg/apex', 'https://t.me/apex', 'https://apex.exchange'),
    scores: s(75, 78, 80, 76, 72, 76, 75),
    riskFlags: [],
    verdict: 'ApeX is a decentralized perpetual DEX with social trading.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Connect wallet to ApeX', 'Deposit USDC', 'Trade perps with leverage', 'Copy trade top traders', 'Provide LP'],
      '15 Minutes', '$50-$500', 'Medium'
    ),
    aiAnalysis: {
      summary: 'ApeX is a non-custodial perp DEX with social and copy trading features.',
      bullCase: 'Social trading differentiator; growing perp DEX market',
      bearCase: 'Competition from dYdX, GMX; perp DEX saturation',
      competitiveAnalysis: 'Unique social trading vs GMX, dYdX, Synthetix.',
      marketOpportunity: 'Perp DEX market growing rapidly.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'ApeX is a decentralized perp DEX with integrated social trading features.',
      projectOverview: 'ApeX combines perp trading with copy trading and portfolio management.',
      productDescription: 'Non-custodial perp exchange with up to 50x leverage.',
      ecosystemDescription: 'Part of the broader DeFi ecosystem.',
      useCases: ['Perp trading', 'Copy trading', 'LP provision'],
      teamInfo: 'Team with trading platform and DeFi experience.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Private'],
      tokenInfo: 'APEX for governance and fee discounts.',
      reviewSummary: 'ApeX differentiates through social trading features.'
    }
  },
  {
    id: 'nibiru', name: 'Nibiru Chain', ticker: 'NIBI', website: 'https://nibiru.fi',
    category: 'Infrastructure', blockchain: 'Nibiru', status: 'active',
    launchDate: '2025-12-15', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/NibiruChain', 'https://discord.gg/nibiru', 'https://t.me/nibiru', 'https://nibiru.fi'),
    scores: s(78, 80, 80, 78, 75, 76, 78),
    riskFlags: [],
    verdict: 'Nibiru is a Cosmos L1 with integrated DeFi protocols.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to Nibiru', 'Stake NIBI', 'Use Nibi DEX and lending', 'Provide liquidity'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Nibiru is a Cosmos-based L1 with integrated DeFi dApps.',
      bullCase: 'All-in-one L1 + DeFi; Cosmos IBC; growing ecosystem',
      bearCase: 'L1 competition; Cosmos ecosystem challenges',
      competitiveAnalysis: 'Unique integrated model vs separate L1 + dApps.',
      marketOpportunity: 'Demand for user-friendly integrated L1s.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Nibiru Chain is a Cosmos L1 with native DeFi applications.',
      projectOverview: 'Nibiru combines L1 infrastructure with built-in DEX, lending, and perps.',
      productDescription: 'Smart contract platform with integrated DeFi protocols.',
      ecosystemDescription: 'IBC-connected with Cosmos ecosystem.',
      useCases: ['DeFi', 'Cross-chain trading', 'Staking'],
      teamInfo: 'Team with Cosmos and DeFi development expertise.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Private'],
      tokenInfo: 'NIBI for gas, governance, and staking.',
      reviewSummary: 'Nibiru offers an integrated DeFi experience on Cosmos.'
    }
  },
  {
    id: 'archway', name: 'Archway', ticker: 'ARCH', website: 'https://archway.io',
    category: 'Infrastructure', blockchain: 'Archway', status: 'active',
    launchDate: '2025-11-01', estimatedReward: '$20-$400', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/ArchwayNetwork', 'https://discord.gg/archway', '', 'https://archway.io'),
    scores: s(75, 78, 78, 76, 72, 74, 75),
    riskFlags: [],
    verdict: 'Archway rewards developers with protocol-level incentives.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to Archway', 'Deploy a smart contract', 'Earn developer rewards', 'Stake ARCH'],
      '20 Minutes', '$10-$50', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Archway is a Cosmos-based L1 that rewards dApp developers.',
      bullCase: 'Developer incentive alignment; Cosmos SDK; unique reward model',
      bearCase: 'L1 competition; developer adoption TBD',
      competitiveAnalysis: 'Unique developer rewards model vs other L1s.',
      marketOpportunity: 'Growing demand for developer-aligned L1s.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Archway is a Cosmos-based L1 that rewards developers from protocol revenue.',
      projectOverview: 'Developers earn a percentage of gas fees generated by their dApps.',
      productDescription: 'Smart contract platform with built-in developer incentives.',
      ecosystemDescription: 'IBC-connected with Cosmos ecosystem.',
      useCases: ['dApp development', 'DeFi', 'Web3 infrastructure'],
      teamInfo: 'Led by Griffin Anderson with Cosmos developer background.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Private'],
      tokenInfo: 'ARCH for gas, governance, and staking.',
      reviewSummary: 'Archway aligns developer and protocol incentives.'
    }
  },
  {
    id: 'neutron', name: 'Neutron', ticker: 'NTRN', website: 'https://neutron.org',
    category: 'Infrastructure', blockchain: 'Cosmos', status: 'active',
    launchDate: '2025-09-01', estimatedReward: '$20-$400', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/Neutron_org', 'https://discord.gg/neutron', '', 'https://neutron.org'),
    scores: s(78, 82, 80, 78, 75, 76, 76),
    riskFlags: [],
    verdict: 'Neutron is a CosmWasm L2 secured by Cosmos Hub.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to Neutron', 'Use Neutron DeFi dApps', 'Stake NTRN', 'Provide liquidity'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Neutron is a CosmWasm smart contract platform secured by Cosmos Hub.',
      bullCase: 'Cosmos Hub security; Interchain Security; CosmWasm ecosystem',
      bearCase: 'Cosmos ecosystem growth challenges',
      competitiveAnalysis: 'Unique Interchain Security model vs independent L1s.',
      marketOpportunity: 'Growing demand for ICS-secured app-chains.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Neutron is a consumer chain secured by Cosmos Hub via Interchain Security.',
      projectOverview: 'Neutron enables CosmWasm smart contracts with Hub-level security.',
      productDescription: 'Smart contract platform with IBC-native cross-chain interactions.',
      ecosystemDescription: 'Growing DeFi ecosystem with DEX and lending protocols.',
      useCases: ['Smart contracts', 'DeFi', 'Cross-chain dApps'],
      teamInfo: 'Team from Cosmos ecosystem with proven experience.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Private'],
      tokenInfo: 'NTRN for gas, governance, and security.',
      reviewSummary: 'Neutron benefits from Cosmos Hub security and IBC connectivity.'
    }
  },
  {
    id: 'saga', name: 'Saga', ticker: 'SAGA', website: 'https://saga.xyz',
    category: 'Infrastructure', blockchain: 'Saga', status: 'active',
    launchDate: '2025-11-15', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/Sagaxyz__', 'https://discord.gg/saga', '', 'https://saga.xyz'),
    scores: s(80, 85, 82, 80, 78, 80, 80),
    riskFlags: [],
    verdict: 'Saga is a protocol for deploying dedicated gaming L2s.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to Saga testnet', 'Deploy a chainlet', 'Test gaming dApps', 'Provide feedback'],
      '30 Minutes', '$0-$20', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Saga is a protocol for deploying dedicated gaming application-specific L2s.',
      bullCase: 'Gaming focus; strong investors; growing demand for game chains',
      bearCase: 'Gaming adoption slower than expected; L2 competition',
      competitiveAnalysis: 'Unique gaming-focused L2 deployment vs general L2s.',
      marketOpportunity: 'Gaming blockchain market projected to reach $30B+.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Saga is a protocol for deploying dedicated chainlets for gaming and entertainment.',
      projectOverview: 'Saga automates the deployment of application-specific L2s for games.',
      productDescription: 'Platform for deploying scalable, interoperable L2s for Web3 games.',
      ecosystemDescription: 'Growing gaming ecosystem with 50+ games building on Saga.',
      useCases: ['Game deployment', 'NFT infrastructure', 'In-game economies'],
      teamInfo: 'Led by Rebecca Liao with team from gaming and blockchain.',
      fundingInfo: 'Raised from top investors.',
      investors: ['Placeholder', 'Maven Capital', 'Longhash Ventures'],
      tokenInfo: 'SAGA for governance, security, and gas.',
      reviewSummary: 'Saga simplifies game blockchain deployment with chainlets.'
    }
  },
  {
    id: 'canto', name: 'Canto', ticker: 'CANTO', website: 'https://canto.io',
    category: 'DeFi', blockchain: 'Canto', status: 'active',
    launchDate: '2025-08-01', estimatedReward: '$20-$300', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/CantoPublic', 'https://discord.gg/canto', '', 'https://canto.io'),
    scores: s(72, 75, 76, 74, 72, 73, 72),
    riskFlags: [],
    verdict: 'Canto is a DeFi-focused L1 with free public infrastructure.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to Canto', 'Use Canto DEX and lending', 'Provide liquidity', 'Stake CANTO'],
      '10 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Canto is a DeFi-focused L1 with free public infrastructure for DeFi primitives.',
      bullCase: 'Free DeFi infrastructure; growing ecosystem',
      bearCase: 'L1 competition; slower growth',
      competitiveAnalysis: 'Unique free public infrastructure model.',
      marketOpportunity: 'Demand for low-cost DeFi infrastructure.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x' }
    },
    about: {
      aboutProject: 'Canto is a DeFi-focused L1 with free public infrastructure (DEX, lending, DAI).',
      projectOverview: 'Canto provides core DeFi primitives as free public goods.',
      productDescription: 'EVM-compatible L1 with built-in DEX and lending markets.',
      ecosystemDescription: 'Growing ecosystem of DeFi protocols and applications.',
      useCases: ['DeFi', 'Trading', 'Lending'],
      teamInfo: 'Run by community and core contributors.',
      fundingInfo: 'Community-driven without VC funding.',
      investors: ['Community'],
      tokenInfo: 'CANTO for gas, governance, and staking.',
      reviewSummary: 'Canto offers truly free DeFi primitives as public goods.'
    }
  },
  {
    id: 'pyth', name: 'Pyth Network', ticker: 'PYTH', website: 'https://pyth.network',
    category: 'Infrastructure', blockchain: 'Multi-Chain', status: 'active',
    launchDate: '2025-09-15', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/PythNetwork', 'https://discord.gg/pyth', '', 'https://pyth.network'),
    scores: s(80, 85, 85, 82, 78, 80, 78),
    riskFlags: [],
    verdict: 'Pyth is a leading oracle network providing real-time market data.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Use dApps integrated with Pyth', 'Provide data via Pyth publishers', 'Delegate PYTH'],
      '10 Minutes', '$0', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Pyth is a leading oracle network delivering real-time market data to blockchains.',
      bullCase: 'Dominant oracle across 50+ chains; strong data provider network',
      bearCase: 'Chainlink dominance; oracle competition',
      competitiveAnalysis: 'Direct competitor to Chainlink with focus on institutional-grade data.',
      marketOpportunity: 'Growing demand for low-latency price data across DeFi.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Pyth is a decentralized oracle network for real-world data on-chain.',
      projectOverview: 'Pyth aggregates price data from 90+ data providers across 50+ chains.',
      productDescription: 'Low-latency oracle for DeFi protocols requiring accurate market data.',
      ecosystemDescription: 'Integrated with 300+ dApps across 50+ blockchains.',
      useCases: ['DeFi oracles', 'Price feeds', 'Risk management'],
      teamInfo: 'Run by the Pyth Data Association with team from Jump Trading.',
      fundingInfo: 'Funded by Jump Trading Group.',
      investors: ['Jump Trading', 'Castle Island', 'Multicoin'],
      tokenInfo: 'PYTH for governance and publisher incentives.',
      reviewSummary: 'Pyth provides institutional-grade oracle infrastructure.'
    }
  },
  // ═══ UPCOMING (21) ════════════════════════════════════════════
  {
    id: 'story', name: 'Story Protocol', ticker: 'STORY', website: 'https://storyprotocol.xyz',
    category: 'Infrastructure', blockchain: 'Story', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$50-$2,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/StoryProtocol', 'https://discord.gg/story', '', 'https://storyprotocol.xyz'),
    scores: s(85, 88, 82, 85, 80, 82, 85),
    riskFlags: ['Early Stage'],
    verdict: 'Story Protocol enables IP tokenization and management on-chain.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join testnet', 'Register IP assets', 'Complete testnet tasks', 'Join Discord'],
      '30 Minutes', '$0-$10', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Story Protocol is a blockchain for registering and managing intellectual property.',
      bullCase: 'Novel IP tokenization; a16z-backed; strong team',
      bearCase: 'Niche use case; regulatory complexity',
      competitiveAnalysis: 'First-mover in blockchain IP management.',
      marketOpportunity: 'Global IP market worth trillions.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '3x-10x' }
    },
    about: {
      aboutProject: 'Story Protocol is a decentralized protocol for tokenizing and managing IP.',
      projectOverview: 'Story enables creators to register, license, and monetize IP on-chain.',
      productDescription: 'L1 blockchain optimized for IP registration and licensing.',
      ecosystemDescription: 'Pre-launch with IP-focused dApps.',
      useCases: ['IP registration', 'Licensing', 'Creator royalties'],
      teamInfo: 'Founded by SY Lee and Jason Zhao.',
      fundingInfo: 'Raised $140M from top investors.',
      investors: ['Andreessen Horowitz', 'Hashed', 'Samsung Next'],
      tokenInfo: 'STORY for governance and protocol fees.',
      reviewSummary: 'Story Protocol addresses the massive IP management market.'
    }
  },
  {
    id: 'swan', name: 'Swan Chain', ticker: 'SWAN', website: 'https://swanchain.io',
    category: 'Infrastructure', blockchain: 'Swan', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/swan_chain', 'https://discord.gg/swan', '', 'https://swanchain.io'),
    scores: s(75, 78, 78, 76, 72, 74, 75),
    riskFlags: ['Early Stage'],
    verdict: 'Swan Chain is a decentralized cloud computing marketplace.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join Discord', 'Follow Twitter', 'Test compute resources', 'Provide feedback'],
      '15 Minutes', '$0', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Swan Chain is a decentralized cloud computing platform for Web3.',
      bullCase: 'Growing demand for decentralized compute; strong backers',
      bearCase: 'Competition from Akash, Render; execution risk',
      competitiveAnalysis: 'Competes with Akash Network for decentralized compute.',
      marketOpportunity: 'Decentralized compute market growing with AI demand.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Swan Chain is a decentralized cloud computing marketplace.',
      projectOverview: 'Swan connects compute providers with AI and Web3 developers.',
      productDescription: 'Two-sided marketplace for decentralized computing resources.',
      ecosystemDescription: 'Pre-launch ecosystem with compute provider network.',
      useCases: ['AI compute', 'DePIN', 'Cloud computing'],
      teamInfo: 'Team with cloud computing and blockchain experience.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Private'],
      tokenInfo: 'SWAN for marketplace fees and governance.',
      reviewSummary: 'Swan Chain addresses the growing demand for decentralized AI compute.'
    }
  },
  {
    id: 'beraborrow', name: 'BeraBorrow', ticker: 'BRRR', website: 'https://beraborrow.xyz',
    category: 'DeFi', blockchain: 'Berachain', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/beraborrow', 'https://discord.gg/beraborrow', '', 'https://beraborrow.xyz'),
    scores: s(72, 75, 76, 74, 72, 74, 75),
    riskFlags: ['Early Stage', 'Depends on Berachain launch'],
    verdict: 'BeraBorrow is a lending protocol on Berachain.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['BeraBorrow testnet', 'Deposit assets', 'Borrow against deposits', 'Test liquidations'],
      '20 Minutes', '$0', 'Easy'
    ),
    aiAnalysis: {
      summary: 'BeraBorrow is a lending/borrowing protocol launching on Berachain.',
      bullCase: 'First-mover lending on Berachain; strong tokenomics',
      bearCase: 'Dependent on Berachain success; competitive lending space',
      competitiveAnalysis: 'Competes with Aave, Compound on Berachain L1.',
      marketOpportunity: 'Growing Berachain ecosystem needs DeFi infrastructure.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'BeraBorrow is the first lending protocol building on Berachain.',
      projectOverview: 'BeraBorrow enables users to deposit assets and borrow against them.',
      productDescription: 'Over-collateralized lending platform for Berachain ecosystem.',
      ecosystemDescription: 'Part of the Berachain DeFi ecosystem.',
      useCases: ['Lending', 'Borrowing', 'Yield farming'],
      teamInfo: 'Anonymous team with DeFi experience.',
      fundingInfo: 'Pre-launch.',
      investors: ['Private'],
      tokenInfo: 'BRRR for governance and fee sharing.',
      reviewSummary: 'BeraBorrow will be core infrastructure for Berachain DeFi.'
    }
  },
  {
    id: 'kintsu', name: 'Kintsu', ticker: 'KINTSU', website: 'https://kintsu.xyz',
    category: 'DeFi', blockchain: 'Monad', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/kintsuxyz', 'https://discord.gg/kintsu', '', 'https://kintsu.xyz'),
    scores: s(72, 75, 74, 72, 70, 72, 72),
    riskFlags: ['Early Stage', 'Depends on Monad launch'],
    verdict: 'Kintsu is a liquid staking protocol for Monad.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join testnet', 'Deposit test MON', 'Receive stMON', 'Deploy test dApps'],
      '20 Minutes', '$0', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Kintsu is a liquid staking protocol for Monad blockchain.',
      bullCase: 'First LST on Monad; first-mover advantage',
      bearCase: 'Dependent on Monad; competitive LST space',
      competitiveAnalysis: 'First liquid staking protocol on Monad L1.',
      marketOpportunity: 'Growing Monad ecosystem needs liquid staking.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Kintsu is a liquid staking protocol for the Monad blockchain.',
      projectOverview: 'Kintsu enables staking on Monad while maintaining liquidity.',
      productDescription: 'Liquid staking token (stMON) for Monad ecosystem.',
      ecosystemDescription: 'Part of Monad DeFi ecosystem.',
      useCases: ['Liquid staking', 'DeFi collateral', 'Yield'],
      teamInfo: 'Team with staking protocol experience.',
      fundingInfo: 'Pre-launch.',
      investors: ['Private'],
      tokenInfo: 'KINTSU for governance and fee sharing.',
      reviewSummary: 'Kintsu will be essential infrastructure for Monad DeFi.'
    }
  },
  {
    id: 'aethir', name: 'Aethir', ticker: 'ATH', website: 'https://aethir.com',
    category: 'DePIN', blockchain: 'Multi-Chain', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/AethirCloud', 'https://discord.gg/aethir', '', 'https://aethir.com'),
    scores: s(78, 82, 80, 80, 75, 78, 78),
    riskFlags: ['Early Stage'],
    verdict: 'Aethir is a decentralized cloud infrastructure for gaming and AI.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join testnet', 'Provide GPU compute', 'Run Aethir node', 'Join community'],
      '30 Minutes', '$50-$200', 'Hard'
    ),
    aiAnalysis: {
      summary: 'Aethir is a decentralized cloud computing platform for GPU resources.',
      bullCase: 'Growing demand for GPU compute; strong backers; DePIN narrative',
      bearCase: 'DePIN competition; hardware requirements for nodes',
      competitiveAnalysis: 'Competes with Render, Akash, and io.net for GPU compute.',
      marketOpportunity: 'Decentralized GPU market projected to grow 10x.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Hard', costRequired: 'Medium', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Aethir is a decentralized cloud infrastructure for gaming and AI.',
      projectOverview: 'Aethir connects GPU providers with enterprises and game developers.',
      productDescription: 'Distributed cloud computing network for rendering and AI.',
      ecosystemDescription: 'Growing ecosystem of game studios and AI companies.',
      useCases: ['Cloud gaming', 'AI rendering', 'GPU compute'],
      teamInfo: 'Led by Mark Rydon with enterprise infrastructure experience.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Hashed', 'Folius Ventures', 'Mirana Ventures'],
      tokenInfo: 'ATH for governance, staking, and marketplace fees.',
      reviewSummary: 'Aethir addresses the growing demand for decentralized GPU compute.'
    }
  },
  {
    id: 'hemi', name: 'Hemi', ticker: 'HEMI', website: 'https://hemi.xyz',
    category: 'Infrastructure', blockchain: 'Bitcoin', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/hemi_network', 'https://discord.gg/hemi', '', 'https://hemi.xyz'),
    scores: s(75, 78, 78, 76, 72, 74, 75),
    riskFlags: ['Early Stage'],
    verdict: 'Hemi is a modular L2 for Bitcoin with Ethereum compatibility.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join testnet', 'Bridge assets', 'Test dApps', 'Provide feedback'],
      '20 Minutes', '$0-$20', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Hemi is a modular L2 for Bitcoin bringing programmability to BTC.',
      bullCase: 'Bitcoin programmability; modular architecture; strong thesis',
      bearCase: 'Competition from other BTC L2s; early stage',
      competitiveAnalysis: 'Competes with Stacks, Rootstock, and other BTC L2s.',
      marketOpportunity: 'Unlocking $1T+ BTC for DeFi applications.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Hemi is a modular L2 network for Bitcoin with Ethereum compatibility.',
      projectOverview: 'Hemi enables smart contracts and DeFi on Bitcoin.',
      productDescription: 'Bitcoin-based L2 with EVM compatibility and Bitcoin security.',
      ecosystemDescription: 'Pre-launch with growing developer community.',
      useCases: ['BTC DeFi', 'Smart contracts', 'Cross-chain'],
      teamInfo: 'Team with Bitcoin and L2 expertise.',
      fundingInfo: 'Pre-launch.',
      investors: ['Private'],
      tokenInfo: 'HEMI for governance and gas fees.',
      reviewSummary: 'Hemi brings programmability to Bitcoin with modular L2 design.'
    }
  },
  {
    id: 'khalani', name: 'Khalani', ticker: 'KHAL', website: 'https://khalani.network',
    category: 'Infrastructure', blockchain: 'Multi-Chain', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/khalani_network', 'https://discord.gg/khalani', '', 'https://khalani.network'),
    scores: s(72, 75, 74, 72, 70, 72, 72),
    riskFlags: ['Early Stage', 'Anonymous Team'],
    verdict: 'Khalani is a intent-centric blockchain for UX-focused DeFi.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join testnet', 'Submit intents', 'Test solver network', 'Provide feedback'],
      '20 Minutes', '$0', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Khalani is an intent-centric blockchain focused on DeFi user experience.',
      bullCase: 'Intent-centric paradigm; solving UX problems; Solver architecture',
      bearCase: 'Unproven intent model; competition from Across, UniswapX',
      competitiveAnalysis: 'Unique intent-centric L1 vs intent-centric middleware.',
      marketOpportunity: 'Better DeFi UX addressing onboarding friction.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Khalani is an intent-centric blockchain designed for superior UX.',
      projectOverview: 'Users express intents rather than executing complex transactions.',
      productDescription: 'L1 blockchain with intent solving and aggregated settlement.',
      ecosystemDescription: 'Pre-launch with solver network forming.',
      useCases: ['DeFi', 'Cross-chain swaps', 'UX improvement'],
      teamInfo: 'Anonymous team with DeFi and intent research background.',
      fundingInfo: 'Pre-launch.',
      investors: ['Private'],
      tokenInfo: 'KHAL for governance and solver incentives.',
      reviewSummary: 'Khalani focuses on solving DeFi user experience with intents.'
    }
  },
  {
    id: 'reya', name: 'Reya Network', ticker: 'REYA', website: 'https://reya.network',
    category: 'DeFi', blockchain: 'Ethereum', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/reya_network', 'https://discord.gg/reya', '', 'https://reya.network'),
    scores: s(75, 78, 78, 76, 72, 74, 75),
    riskFlags: ['Early Stage'],
    verdict: 'Reya Network is a modular L2 for perp trading and DeFi.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Reya testnet', 'Test perp trading', 'Provide liquidity', 'Give feedback'],
      '20 Minutes', '$0-$20', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Reya Network is a modular L2 optimized for trading and DeFi.',
      bullCase: 'Trading-optimized L2; strong backers; perp DEX growth',
      bearCase: 'Competing perp L2s; execution risk',
      competitiveAnalysis: 'Unique trading-focused L2 vs general-purpose L2s.',
      marketOpportunity: 'Perpetual DEX volume growing rapidly.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Medium', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Reya Network is a modular L2 optimized for trading and liquidity.',
      projectOverview: 'Reya provides high-performance infrastructure for perp DEXes.',
      productDescription: 'L2 with optimized order book and matching engine.',
      ecosystemDescription: 'Pre-launch with trading-focused dApps.',
      useCases: ['Perp trading', 'DEX infrastructure', 'Liquidity'],
      teamInfo: 'Team with trading platform and L2 experience.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Coinbase Ventures', 'Polygon', 'Wintermute'],
      tokenInfo: 'REYA for governance and fee discounts.',
      reviewSummary: 'Reya brings CEX-level performance to on-chain trading.'
    }
  },
  {
    id: 'particle', name: 'Particle Network', ticker: 'PART', website: 'https://particle.network',
    category: 'Infrastructure', blockchain: 'Multi-Chain', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/ParticleNtwrk', 'https://discord.gg/particle', '', 'https://particle.network'),
    scores: s(78, 80, 80, 78, 75, 76, 78),
    riskFlags: ['Early Stage'],
    verdict: 'Particle is an L1 unifying liquidity and accounts across chains.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join testnet', 'Create universal account', 'Bridge assets', 'Test unified balance'],
      '20 Minutes', '$0-$20', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Particle Network is a modular L1 unifying liquidity and accounts across chains.',
      bullCase: 'Unified account abstraction; growing demand for chain abstraction',
      bearCase: 'Complex architecture; competing account abstraction solutions',
      competitiveAnalysis: 'Unique chain abstraction L1 vs middleware solutions.',
      marketOpportunity: 'Chain abstraction market critical for multi-chain UX.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Particle Network is a modular L1 providing chain abstraction.',
      projectOverview: 'Particle creates unified accounts and liquidity across all chains.',
      productDescription: 'Universal account L1 with cross-chain gas abstraction.',
      ecosystemDescription: 'Pre-launch with growing partner network.',
      useCases: ['Chain abstraction', 'Unified accounts', 'Cross-chain gas'],
      teamInfo: 'Founded by team with chain abstraction research background.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Polychain Capital', 'Binance Labs', 'Hack VC'],
      tokenInfo: 'PART for governance and network fees.',
      reviewSummary: 'Particle solves chain fragmentation with universal accounts.'
    }
  },
  {
    id: 'polygon_agglayer', name: 'Polygon AggLayer', ticker: 'POL', website: 'https://polygon.technology/agglayer',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$30-$1,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/0xPolygon', 'https://discord.gg/polygon', '', 'https://polygon.technology'),
    scores: s(80, 88, 85, 82, 80, 82, 80),
    riskFlags: [],
    verdict: 'Polygon AggLayer unifies ZK-rollups for seamless cross-chain UX.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Polygon zkEVM', 'Use AggLayer-connected dApps', 'Provide liquidity'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Polygon AggLayer is a unified liquidity layer for ZK-rollups.',
      bullCase: 'Polygon ecosystem; ZK tech; unifying L2 liquidity',
      bearCase: 'Competing aggregation solutions',
      competitiveAnalysis: 'Unique L2 aggregation vs Optimism Superchain, zkSync Hyperchain.',
      marketOpportunity: 'L2 fragmentation creating demand for unification.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'AggLayer is a decentralized protocol for unifying ZK-rollups.',
      projectOverview: 'AggLayer enables seamless cross-chain UX across Polygon ecosystem.',
      productDescription: 'ZK-based unifying layer for liquidity and state across L2s.',
      ecosystemDescription: 'Connected to Polygon zkEVM, Manta, Canto, and more.',
      useCases: ['Cross-chain swaps', 'Unified liquidity', 'ZK interoperability'],
      teamInfo: 'Built by Polygon Labs, led by Sandeep Nailwal.',
      fundingInfo: 'Funded by Polygon ecosystem.',
      investors: ['Polygon', 'Public'],
      tokenInfo: 'POL for gas, staking, and governance.',
      reviewSummary: 'AggLayer solves L2 fragmentation with ZK unification.'
    }
  },
  {
    id: 'aleo', name: 'Aleo', ticker: 'ALEO', website: 'https://aleo.org',
    category: 'Privacy', blockchain: 'Aleo', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/AleoHQ', 'https://discord.gg/aleo', 'https://t.me/aleo', 'https://aleo.org'),
    scores: s(80, 85, 82, 78, 75, 80, 78),
    riskFlags: [],
    verdict: 'Aleo is a privacy-focused L1 using ZK-proofs for private dApps.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join testnet', 'Run a prover node', 'Complete tasks', 'Provide feedback'],
      '1 Hour', '$0-$20', 'Hard'
    ),
    aiAnalysis: {
      summary: 'Aleo is a privacy-focused L1 blockchain with programmable ZK.',
      bullCase: 'Privacy-focused with ZK; strong team; a16z-backed',
      bearCase: 'Privacy coin regulatory risk; complex tech',
      competitiveAnalysis: 'Unique privacy L1 vs Zcash, Monero, Penumbra.',
      marketOpportunity: 'Growing demand for private smart contracts.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Hard', costRequired: 'Low', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Aleo is a privacy-first L1 blockchain using zero-knowledge proofs.',
      projectOverview: 'Aleo enables private, scalable, and cost-efficient dApps.',
      productDescription: 'ZK-native L1 with Leo programming language.',
      ecosystemDescription: 'Growing ecosystem of private DeFi and identity dApps.',
      useCases: ['Private DeFi', 'Identity', 'Privacy-preserving dApps'],
      teamInfo: 'Founded by Howard Wu and Michael Beller with ZK expertise.',
      fundingInfo: 'Raised $298M from top investors.',
      investors: ['Andreessen Horowitz', 'SoftBank', 'Coinbase Ventures'],
      tokenInfo: 'ALEO for gas, execution, and governance.',
      reviewSummary: 'Aleo brings programmable privacy to the blockchain.'
    }
  },
  {
    id: 'eigen_da', name: 'EigenDA', ticker: 'ED', website: 'https://eigenda.xyz',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/eigen_da', 'https://discord.gg/eigenda', '', 'https://eigenda.xyz'),
    scores: s(80, 85, 82, 80, 75, 78, 78),
    riskFlags: [],
    verdict: 'EigenDA is a data availability solution using EigenLayer restaking.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Restake ETH via EigenLayer to EigenDA', 'Run EigenDA node', 'Provide DA services'],
      '30 Minutes', '$100-$1,000', 'Hard'
    ),
    aiAnalysis: {
      summary: 'EigenDA is a data availability protocol secured by EigenLayer restaking.',
      bullCase: 'EigenLayer integration; scalable DA; strong backers',
      bearCase: 'Competition from Celestia, Avail',
      competitiveAnalysis: 'Competes with Celestia and Avail for DA market.',
      marketOpportunity: 'DA market critical for modular scaling.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Hard', costRequired: 'High', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'EigenDA is a hyperscale data availability solution on EigenLayer.',
      projectOverview: 'EigenDA provides high-throughput, low-cost DA for rollups.',
      productDescription: 'DA layer with 10 MB/s throughput using restaked ETH.',
      ecosystemDescription: 'Integrated with multiple rollups as first AVS.',
      useCases: ['Data availability', 'Rollup infrastructure', 'Modular DA'],
      teamInfo: 'Built by EigenLayer team.',
      fundingInfo: 'Part of EigenLayer ecosystem.',
      investors: ['Polychain', 'EigenLayer'],
      tokenInfo: 'EIGEN (shared with EigenLayer) for governance.',
      reviewSummary: 'EigenDA provides scalable DA secured by restaked ETH.'
    }
  },
  {
    id: 'symbiotic', name: 'Symbiotic', ticker: 'SYM', website: 'https://symbiotic.fi',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$30-$800', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/symbiotic_fi', 'https://discord.gg/symbiotic', '', 'https://symbiotic.fi'),
    scores: s(80, 85, 82, 80, 75, 78, 80),
    riskFlags: ['Early Stage'],
    verdict: 'Symbiotic is a permissionless restaking protocol competing with EigenLayer.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Deposit ETH/collateral', 'Delegate to operators', 'Secure networks', 'Earn rewards'],
      '15 Minutes', '$100-$1,000', 'Medium'
    ),
    aiAnalysis: {
      summary: 'Symbiotic is a permissionless restaking protocol for shared security.',
      bullCase: 'Permissionless; multi-asset collateral; Paradigm-backed',
      bearCase: 'Competition from EigenLayer; restaking risks',
      competitiveAnalysis: 'Direct competitor to EigenLayer with permissionless design.',
      marketOpportunity: 'Restaking market projected to grow significantly.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Medium', costRequired: 'Medium', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'Symbiotic is a permissionless restaking protocol for shared network security.',
      projectOverview: 'Symbiotic enables any asset to be used as restaked collateral.',
      productDescription: 'Permissionless restaking with multi-asset support and modular design.',
      ecosystemDescription: 'Growing ecosystem of networks securing via Symbiotic.',
      useCases: ['Restaking', 'Shared security', 'Multi-asset collateral'],
      teamInfo: 'Team with DeFi and restaking expertise.',
      fundingInfo: 'Backed by Paradigm.',
      investors: ['Paradigm', 'CyberFund'],
      tokenInfo: 'SYM for governance and protocol fees.',
      reviewSummary: 'Symbiotic offers a permissionless alternative to EigenLayer.'
    }
  },
  {
    id: 'karak', name: 'Karak', ticker: 'KARAK', website: 'https://karak.network',
    category: 'Infrastructure', blockchain: 'Multi-Chain', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/karak_network', 'https://discord.gg/karak', '', 'https://karak.network'),
    scores: s(75, 78, 76, 75, 72, 74, 75),
    riskFlags: ['Early Stage'],
    verdict: 'Karak is a multi-chain restaking platform.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Deposit assets across chains', 'Delegate to operators', 'Earn rewards'],
      '15 Minutes', '$50-$500', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Karak is a multi-chain restaking platform supporting various assets.',
      bullCase: 'Multi-chain restaking; strong backers; growing TVL',
      bearCase: 'Restaking competition; security risks',
      competitiveAnalysis: 'Competes with EigenLayer, Symbiotic for restaking.',
      marketOpportunity: 'Multi-chain restaking market expanding.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Easy', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Karak is a multi-chain restaking platform for shared security.',
      projectOverview: 'Karak enables restaking across multiple blockchains.',
      productDescription: 'Multi-chain restaking with flexible asset support.',
      ecosystemDescription: 'Growing operator and AVS network.',
      useCases: ['Restaking', 'Multi-chain security', 'Yield'],
      teamInfo: 'Team with DeFi and cross-chain expertise.',
      fundingInfo: 'Raised from top investors.',
      investors: ['Polychain', 'Framework Ventures', 'Coinbase'],
      tokenInfo: 'KARAK for governance and staking.',
      reviewSummary: 'Karak expands restaking across multiple chains.'
    }
  },
  {
    id: 'opensea', name: 'OpenSea', ticker: 'SEA', website: 'https://opensea.io',
    category: 'NFT', blockchain: 'Multi-Chain', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$50-$2,000', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/opensea', '', '', 'https://opensea.io'),
    scores: s(82, 88, 85, 82, 85, 82, 82),
    riskFlags: [],
    verdict: 'OpenSea is the largest NFT marketplace exploring token launch.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Trade NFTs on OpenSea', 'Create NFT collections', 'Use OpenSea features', 'Maintain activity'],
      '30 Minutes', '$20-$200', 'Easy'
    ),
    aiAnalysis: {
      summary: 'OpenSea is the world\'s largest NFT marketplace with potential token launch.',
      bullCase: 'Dominant NFT marketplace; brand recognition; user base',
      bearCase: 'NFT market slowdown; competition from Blur',
      competitiveAnalysis: 'Leading NFT marketplace vs Blur, Rarible, LooksRare.',
      marketOpportunity: 'NFT market projected to recover and grow long-term.',
      airdropAttractiveness: { rewardPotential: 'High', effortRequired: 'Easy', costRequired: 'Medium', expectedROI: '2x-5x' }
    },
    about: {
      aboutProject: 'OpenSea is the largest NFT marketplace for digital collectibles.',
      projectOverview: 'OpenSea enables creation, trading, and discovery of NFTs across chains.',
      productDescription: 'Multi-chain NFT marketplace with advanced trading tools.',
      ecosystemDescription: 'Integrated with Ethereum, Polygon, Solana, and more.',
      useCases: ['NFT trading', 'Digital art', 'Collectibles'],
      teamInfo: 'Founded by Devin Finzer and Alex Atallah.',
      fundingInfo: 'Raised $423M at $13.3B valuation.',
      investors: ['Andreessen Horowitz', 'Paradigm', 'Coinbase'],
      tokenInfo: 'SEA for governance and platform fees.',
      reviewSummary: 'OpenSea is the most established brand in the NFT space.'
    }
  },
  {
    id: 'linea_surge', name: 'Linea Surge', ticker: 'LXP', website: 'https://linea.build/surge',
    category: 'DeFi', blockchain: 'Ethereum', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$20-$500', rewardType: 'Points → Token',
    socialLinks: slots('https://x.com/LineaBuild', 'https://discord.gg/linea', '', 'https://linea.build'),
    scores: s(78, 82, 80, 78, 75, 76, 78),
    riskFlags: [],
    verdict: 'Linea Surge rewards users for DeFi activity on Linea L2.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Linea', 'Provide liquidity on Linea', 'Trade on Linea DEXes', 'Accumulate LXP'],
      '15 Minutes', '$10-$100', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Linea Surge is a loyalty program rewarding DeFi engagement on Linea.',
      bullCase: 'Linea growth; LXP-to-token potential; ConsenSys backing',
      bearCase: 'Point system dilution; timeline uncertainty',
      competitiveAnalysis: 'Points program vs Blast, Mode, and other L2 points.',
      marketOpportunity: 'Driving DeFi adoption on Linea L2.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Linea Surge is Linea\'s points-based loyalty program for DeFi users.',
      projectOverview: 'Users earn LXP points for using Linea DeFi protocols.',
      productDescription: 'Points accumulation through lending, trading, and LP provision.',
      ecosystemDescription: 'Part of Linea L2 ecosystem with ConsenSys backing.',
      useCases: ['DeFi incentives', 'Points earning', 'L2 adoption'],
      teamInfo: 'Part of ConsenSys / Linea team.',
      fundingInfo: 'Funded by ConsenSys.',
      investors: ['ConsenSys'],
      tokenInfo: 'LXP convertible to future token.',
      reviewSummary: 'Linea Surge incentivizes DeFi adoption on ConsenSys L2.'
    }
  },
  {
    id: 'scroll_sessions', name: 'Scroll Sessions', ticker: 'SCR', website: 'https://scroll.io/sessions',
    category: 'DeFi', blockchain: 'Ethereum', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$20-$500', rewardType: 'Points → Token',
    socialLinks: slots('https://x.com/Scroll_ZKP', 'https://discord.gg/scroll', '', 'https://scroll.io'),
    scores: s(78, 82, 80, 78, 75, 76, 78),
    riskFlags: [],
    verdict: 'Scroll Sessions rewards users for activity on Scroll L2.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge ETH to Scroll', 'Use Scroll dApps', 'Accumulate marks', 'Provide liquidity'],
      '15 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Scroll Sessions is a loyalty program incentivizing Scroll L2 usage.',
      bullCase: 'Scroll growth; marks-to-token potential; ZK technology',
      bearCase: 'Points dilution; timeline uncertainty',
      competitiveAnalysis: 'Points program vs Linea Surge, Blast points.',
      marketOpportunity: 'Driving DeFi adoption on Scroll L2.',
      airdropAttractiveness: { rewardPotential: 'Medium', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Scroll Sessions rewards users for engaging with the Scroll L2 ecosystem.',
      projectOverview: 'Users earn marks through DeFi activity on Scroll.',
      productDescription: 'Points system for L2 loyalty with future token conversion.',
      ecosystemDescription: 'Part of Scroll ZK-rollup ecosystem.',
      useCases: ['DeFi incentives', 'L2 engagement', 'Points earning'],
      teamInfo: 'Part of Scroll team.',
      fundingInfo: 'Funded by Scroll ecosystem.',
      investors: ['Polychain', 'Bain Capital'],
      tokenInfo: 'Marks convertible to SCR.',
      reviewSummary: 'Scroll Sessions drives engagement on the Scroll ZK-rollup.'
    }
  },
  {
    id: 'kinto', name: 'Kinto', ticker: 'KINTO', website: 'https://kinto.xyz',
    category: 'DeFi', blockchain: 'Ethereum', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/kinto_xyz', 'https://discord.gg/kinto', '', 'https://kinto.xyz'),
    scores: s(75, 78, 76, 74, 72, 74, 74),
    riskFlags: ['Early Stage'],
    verdict: 'Kinto is an L2 with integrated KYC for compliance-friendly DeFi.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Complete KYC on Kinto', 'Bridge assets', 'Use Kinto dApps', 'Provide liquidity'],
      '20 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Kinto is an L2 with built-in KYC for regulatory-compliant DeFi.',
      bullCase: 'KYC-compliant DeFi; institutional adoption; regulatory clarity',
      bearCase: 'Crypto ethos of anonymity; KYC friction',
      competitiveAnalysis: 'Unique KYC-integrated L2 vs permissionless L2s.',
      marketOpportunity: 'Institutional DeFi requiring compliance.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'Kinto is a KYC-integrated L2 for compliant DeFi access.',
      projectOverview: 'Kinto enables institutions to participate in DeFi with KYC compliance.',
      productDescription: 'EVM L2 with embedded KYC and insurance for users.',
      ecosystemDescription: 'Growing DeFi ecosystem with institutional focus.',
      useCases: ['Compliant DeFi', 'Institutional DeFi', 'Regulated finance'],
      teamInfo: 'Team with regulatory and DeFi expertise.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Blockchain Capital', 'Variant'],
      tokenInfo: 'KINTO for governance and fee discounts.',
      reviewSummary: 'Kinto bridges DeFi and regulatory compliance for institutions.'
    }
  },
  {
    id: 'fibrous', name: 'Fibrous', ticker: 'FIB', website: 'https://fibrous.finance',
    category: 'DeFi', blockchain: 'StarkNet', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$20-$400', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/fibrous_finance', 'https://discord.gg/fibrous', '', 'https://fibrous.finance'),
    scores: s(72, 74, 74, 72, 70, 72, 72),
    riskFlags: ['Early Stage', 'Small Team'],
    verdict: 'Fibrous is a yield aggregator on StarkNet.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Bridge to StarkNet', 'Use Fibrous aggregator', 'Optimize yields'],
      '10 Minutes', '$10-$50', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Fibrous is a yield aggregator and optimizer on StarkNet.',
      bullCase: 'StarkNet DeFi growth; yield optimization demand',
      bearCase: 'Dependent on StarkNet adoption; competition',
      competitiveAnalysis: 'Yield aggregator on StarkNet vs Yearn on Ethereum.',
      marketOpportunity: 'Growing StarkNet ecosystem needs DeFi infrastructure.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Fibrous is a DeFi yield aggregator on StarkNet.',
      projectOverview: 'Fibrous optimizes yields across StarkNet DeFi protocols.',
      productDescription: 'Automated yield farming platform with strategy optimization.',
      ecosystemDescription: 'Part of StarkNet DeFi ecosystem.',
      useCases: ['Yield farming', 'DeFi aggregation', 'Auto-compounding'],
      teamInfo: 'Small team with DeFi and StarkNet expertise.',
      fundingInfo: 'Pre-launch.',
      investors: ['Private'],
      tokenInfo: 'FIB for governance and fee sharing.',
      reviewSummary: 'Fibrous simplifies yield farming on StarkNet.'
    }
  },
  {
    id: 'elixir', name: 'Elixir', ticker: 'ELX', website: 'https://elixir.finance',
    category: 'DeFi', blockchain: 'Multi-Chain', status: 'upcoming',
    launchDate: '2026-Q1', estimatedReward: '$20-$500', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/elixir', 'https://discord.gg/elixir', '', 'https://elixir.finance'),
    scores: s(75, 78, 76, 75, 72, 74, 75),
    riskFlags: ['Early Stage'],
    verdict: 'Elixir is a DEX market-making protocol for perp LPs.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Deposit USDC into Elixir', 'Select market-making strategy', 'Earn yields'],
      '10 Minutes', '$50-$500', 'Easy'
    ),
    aiAnalysis: {
      summary: 'Elixir is a decentralized market-making protocol for DEXes.',
      bullCase: 'Solves DEX liquidity problem; growing perp DEX market',
      bearCase: 'Market-making risk; competition',
      competitiveAnalysis: 'Unique market-making protocol vs traditional LPs.',
      marketOpportunity: 'DEX liquidity market growing with perp DEX adoption.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Medium', expectedROI: '1x-2x' }
    },
    about: {
      aboutProject: 'Elixir is a decentralized market-making protocol for DEXes.',
      projectOverview: 'Elixir enables users to provide market-making liquidity.',
      productDescription: 'Automated market-making vaults with optimized strategies.',
      ecosystemDescription: 'Integrated with major perp DEXes.',
      useCases: ['Market making', 'DEX liquidity', 'Yield generation'],
      teamInfo: 'Team with market-making and DeFi expertise.',
      fundingInfo: 'Raised from strategic investors.',
      investors: ['Hack VC', 'Arrington Capital'],
      tokenInfo: 'ELX for governance and fee sharing.',
      reviewSummary: 'Elixir democratizes market-making for DeFi.'
    }
  },
  {
    id: 'zerobase', name: 'ZeroBase', ticker: 'ZB', website: 'https://zerobase.xyz',
    category: 'Infrastructure', blockchain: 'Ethereum', status: 'upcoming',
    launchDate: '2026-Q2', estimatedReward: '$20-$400', rewardType: 'Token Airdrop',
    socialLinks: slots('https://x.com/zerobase_xyz', 'https://discord.gg/zerobase', '', 'https://zerobase.xyz'),
    scores: s(72, 74, 74, 72, 70, 72, 72),
    riskFlags: ['Early Stage', 'Anonymous Team'],
    verdict: 'ZeroBase is a ZK-based cross-chain bridge.',
    source: 'airdrops.io',
    participationGuide: pGuide(
      ['Join testnet', 'Test bridge transfers', 'Provide feedback'],
      '15 Minutes', '$0', 'Easy'
    ),
    aiAnalysis: {
      summary: 'ZeroBase is a zero-knowledge proof-based cross-chain bridge.',
      bullCase: 'ZK-bridge technology; growing demand for secure bridges',
      bearCase: 'Bridge competition; security concerns',
      competitiveAnalysis: 'ZK-based bridge vs LayerZero, Wormhole.',
      marketOpportunity: 'Cross-chain bridge market expanding with multi-chain growth.',
      airdropAttractiveness: { rewardPotential: 'Low', effortRequired: 'Low', costRequired: 'Low', expectedROI: '1x-3x' }
    },
    about: {
      aboutProject: 'ZeroBase uses ZK-proofs for secure cross-chain bridging.',
      projectOverview: 'ZeroBase enables trustless asset transfers between chains.',
      productDescription: 'ZK-powered bridge with minimal trust assumptions.',
      ecosystemDescription: 'Pre-launch with multi-chain support planned.',
      useCases: ['Cross-chain bridging', 'ZK verification', 'Interoperability'],
      teamInfo: 'Anonymous team with ZK research expertise.',
      fundingInfo: 'Pre-launch.',
      investors: ['Private'],
      tokenInfo: 'ZB for governance and bridge fees.',
      reviewSummary: 'ZeroBase uses ZK technology for secure bridging.'
    }
  }
];
