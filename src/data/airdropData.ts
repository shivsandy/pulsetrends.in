// ──────────────────────────────────────────────────────────────
// Airdrop Intelligence Platform — Auto-generated from scraped data
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

export type AirdropStatus = "active" | "upcoming" | "ended";
export type Difficulty = "Easy" | "Medium" | "Hard";

export interface AirdropProject {
  id: string;
  name: string;
  ticker: string;
  website: string;
  category: string;
  blockchain: string;
  status: AirdropStatus;
  launchDate?: string;
  estimatedReward: string;
  rewardType: string;
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

export function calculateOverall(scores: Omit<AirdropScores, "overall">): number {
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
  if (overall >= 90) return "Exceptional";
  if (overall >= 80) return "Strong";
  if (overall >= 70) return "Good";
  if (overall >= 60) return "Speculative";
  return "Avoid";
}

export function ratingColor(overall: number): string {
  if (overall >= 90) return "text-emerald-400";
  if (overall >= 80) return "text-green-400";
  if (overall >= 70) return "text-yellow-400";
  if (overall >= 60) return "text-orange-400";
  return "text-red-400";
}

function s(t: number, i: number, p: number, m: number, c: number, tk: number, a: number): AirdropScores {
  return { team: t, investors: i, product: p, market: m, community: c, token: tk, airdrop: a, overall: calculateOverall({ team: t, investors: i, product: p, market: m, community: c, token: tk, airdrop: a }) };
}

export const airdropProjects: AirdropProject[] = [
  {
    id: "polymarket",
    name: "Polymarket",
    ticker: "POLYMA",
    website: "https://airdrops.io/polymarket/",
    category: "airdrop",
    blockchain: "Ethereum",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/i/broadcasts/1DXxyWLbaBvGM", discord: "https://discord.gg/hGYPGru", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/polymarket/" },
    scores: s(93, 98, 98, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "Polymarket is an active airdrop opportunity on Ethereum.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Focus on market categories you know: crypto, sports, politics, economics", "Spread activity across different categories rather than concentrating in one niche", "Reinvest winnings into new markets to maintain consistent on-chain activity", "PolyGun has launched a Telegram bot for copy-trading on Polymarket where users can generate a wallet, fund it with SOL, USDC, or USDC.e (available on Binance or via Rhino.fi bridge), and earn referral rewards of 25% from direct referrals, 5% from second-tier, and 3% from third-tier referrals.", "Deposit USDC via Ethereum mainnet to Ember Protocol’s Polymarket vault. The vault is designed to maximize user earnings, adopting high-risk strategies that could also result in higher drawdowns.", "Polyinsights and Polyagent – both provide AI-generated insights and leaderboards to identify profitable traders", "Polymarket Analytics – analyze data on all Polymarket traders, markets, positions and tradesTrack deposits and withdrawals — with filters by win rate, PnL and other factors. Perfect for spotting potential insiders who deposit large sums into empty wallets just before key events.X Connect — follow trades of influential Twitter accounts", "Track deposits and withdrawals — with filters by win rate, PnL and other factors. Perfect for spotting potential insiders who deposit large sums into empty wallets just before key events."],
      estimatedTime: "30 Minutes",
      estimatedCost: "s for active market makers",
      difficulty: "Hard" as const,
    },
  },
  {
    id: "solpump",
    name: "SolPump",
    ticker: "SOLPUM",
    website: "https://airdrops.io/solpump/",
    category: "airdrop",
    blockchain: "Solana",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/solpumpcom/status/1967664691460878433", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/solpump/" },
    scores: s(95, 98, 98, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "SolPump is an active airdrop opportunity on Solana.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Visit the SolPump Platform", "Connect Your Solana Wallet", "Acquire SOL TokensEnsure you have sufficient SOL in your wallet for betting and transaction feesYou can purchase SOL directly from Binance or use Rhino Bridge", "Ensure you have sufficient SOL in your wallet for betting and transaction fees", "You can purchase SOL directly from Binance or use Rhino Bridge", "Complete Initial SetupConnect your social media accounts as promptedThis step can provide up to 10 SOL in bonus rewards", "Connect your social media accounts as prompted", "This step can provide up to 10 SOL in bonus rewards"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Low Overview Website: solpump",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "dreamcash",
    name: "Dreamcash",
    ticker: "DREAMC",
    website: "https://airdrops.io/dreamcash/",
    category: "airdrop",
    blockchain: "Hyperliquid",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Dreamcash&url=https%3A%2F%2Fairdrops.io%2Fdreamcash%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/dreamcash/" },
    scores: s(91, 98, 98, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "Dreamcash is an active airdrop opportunity on Hyperliquid.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["USA500-USDT: S&P 500 index, up to 20x leverage", "TSLA-USDT: Tesla, up to 20x leverage", "NVDA-USDT: Nvidia, up to 20x leverage", "Mobile volume scores at 1x", "Web app and Treadfi volume score at 0.5x.", "Trades made on the Hyperliquid frontend earn no XP."],
      estimatedTime: "30 Minutes",
      estimatedCost: "-free",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "acebet",
    name: "Acebet",
    ticker: "ACEBET",
    website: "https://airdrops.io/acebet/",
    category: "airdrop",
    blockchain: "243°",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Acebet&url=https%3A%2F%2Fairdrops.io%2Facebet%2F", discord: "https://discord.gg/28aGta357F", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/acebet/" },
    scores: s(98, 98, 98, 98, 97, 98, 98),
    riskFlags: [],
    verdict: "Acebet is an active airdrop opportunity on 243°.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Visit Acebet.com and click “Sign Up” in the top-right corner", "Register using your email address and create a secure password (or use Google/Steam login)", "Verify your email address before depositing or playing", "Click the “Claim Your Free $1” button at the top of the website", "Choose your desired deposit bonus amount (up to 50% match)", "Make your first deposit to activate the bonus"],
      estimatedTime: "30 Minutes",
      estimatedCost: "",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "ink",
    name: "Ink",
    ticker: "INK",
    website: "https://airdrops.io/ink-chain/",
    category: "airdrop",
    blockchain: "Own",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Ink&url=https%3A%2F%2Fairdrops.io%2Fink-chain%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/ink-chain/" },
    scores: s(93, 98, 98, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "Ink is an active airdrop opportunity on Own.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Deposit cash (2x points)", "Reactivation bonus (3x points)", "Set price alerts (Bonus boost)"],
      estimatedTime: "30 Minutes",
      estimatedCost: "-free",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "base",
    name: "Base",
    ticker: "BASE",
    website: "https://airdrops.io/base/",
    category: "airdrop",
    blockchain: "Base",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/base/status/1967602096360063341", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/base/" },
    scores: s(90, 98, 98, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "Base is an active airdrop opportunity on Base.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["for decentralized applications, DeFi protocols, NFTs, and payments. Base integrates directly with Coinbase’s platform, providing users seamless access to onchain activities through the Base App and web interfaces. The network supports a growing ecosystem of DeFi protocols like Aerodrome and Uniswap, social applications, and NFT platforms including Zora and OpenSea. Base recently announced plans to explore launching a network token with potential timing between Q2", "Q4 2026, though specific tokenomics remain unconfirmed. Coinbase operates the network and supports ecosystem projects through programs like the Base Ecosystem Fund and Coinbase Ventures. Base’s main value proposition centers on empowering builders and users to create, trade, and earn onchain with Coinbase", "level security and integration. The network currently runs active incentive programs including Builder Rewards at talent.app . Ongoing Base Airdrop Details Base has not confirmed a token airdrop. However, the network announced it’s beginning to explore launching a network token with potential deployment between Q2", "Q4 2026. Users who actively engage with Base ecosystem applications, bridge assets, and contribute to network activity may position themselves for potential rewards if a token launches. Key Parameters: Token Status: Unconfirmed, exploring launch in Q2", "Q4 2026 Airdrop Allocation: Not announced Eligibility Criteria: Likely based on ecosystem participation and transaction activity Positioning for potential Base rewards involves regular interaction with Base mainnet applications, bridging ETH from Ethereum, swapping tokens on decentralized exchanges, providing liquidity to DeFi protocols, and minting NFTs."],
      estimatedTime: "30 Minutes",
      estimatedCost: ", fast transactions for decentralized applications, DeFi protocols, NFTs, and payments",
      difficulty: "Hard" as const,
    },
  },
  {
    id: "hyperliquid",
    name: "Hyperliquid",
    ticker: "HYPERL",
    website: "https://airdrops.io/hyperliquid/",
    category: "airdrop",
    blockchain: "Arbitrum",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/hypurr_co/status/1873677850752233913", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/hyperliquid/" },
    scores: s(96, 98, 96, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "Hyperliquid is an active airdrop opportunity on Arbitrum.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Create your accountVisit Hyperliquid and connect your wallet — this referral link gives you an instant 4% discount on all trading feesComplete account setup and accept the terms of service", "Visit Hyperliquid and connect your wallet — this referral link gives you an instant 4% discount on all trading fees", "Complete account setup and accept the terms of service", "Fund your accountGet USDC from Binance or bridge from any chain to Arbitrum via Rhino BridgeDeposit the bridged USDC into your Hyperliquid account", "Get USDC from Binance or bridge from any chain to Arbitrum via Rhino Bridge", "Deposit the bridged USDC into your Hyperliquid account", "Access spot marketsGo to “Trade” → “Select instrument” → choose “Spot” from the dropdown", "Go to “Trade” → “Select instrument” → choose “Spot” from the dropdown"],
      estimatedTime: "30 Minutes",
      estimatedCost: "averaging works well for larger positions given price volatility Complete the staking process Go to “Staking” → transfer HYPE from spot balance to staking balance → click “Stake Tokens” Consider delegating to HypurrCollective validator for added benefits: Earn Nansen points alongside staking rewards Access to exclusive ecosystem airdrops Track record of 5 successful airdrops since staking launch What staking pays HYPE token rewards from network inflation USDC rewards from platform trading fees Eligibility for ecosystem project airdrops Governance participation in protocol decisions For higher yield, liquid staking protocols like Kinetiq and LoopedHYPE let you stake HYPE, receive an LST, then deploy that LST into HyperEVM DEX liquidity pools — stacking staking APR, LP APR, and protocol points at the same time",
      difficulty: "Hard" as const,
    },
  },
  {
    id: "liquidiction",
    name: "Liquidiction",
    ticker: "LIQUID",
    website: "https://airdrops.io/liquidiction/",
    category: "airdrop",
    blockchain: "Hyperliquid",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Liquidiction&url=https%3A%2F%2Fairdrops.io%2Fliquidiction%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/liquidiction/" },
    scores: s(98, 98, 98, 97, 98, 98, 98),
    riskFlags: [],
    verdict: "Liquidiction is an active airdrop opportunity on Hyperliquid.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Hypurr", "HypioHL", "TinyHypercats", "PiPonHL", "Whal3s, Atlanteans, and Eternal Whal3s"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Medium Overview Website: liquidiction",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "dustswap",
    name: "Dustswap",
    ticker: "DUSTSW",
    website: "https://airdrops.io/dustswap/",
    category: "airdrop",
    blockchain: "Base",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Dustswap&url=https%3A%2F%2Fairdrops.io%2Fdustswap%2F", discord: "https://discord.gg/dustswap", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/dustswap/" },
    scores: s(98, 97, 98, 98, 97, 98, 98),
    riskFlags: [],
    verdict: "Dustswap is an active airdrop opportunity on Base.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Join the Dustswap Discord", "Follow @DustswapOnBase on X", "Post about Dustswap on X and mention @DustswapOnBase", "Share your post link in the #claim_early_user channel"],
      estimatedTime: "30 Minutes",
      estimatedCost: "nothing",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "fast",
    name: "Fast",
    ticker: "FAST",
    website: "https://airdrops.io/fast/",
    category: "airdrop",
    blockchain: "Own",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/Pi_Squared_Pi2", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/fast/" },
    scores: s(98, 97, 98, 98, 97, 98, 98),
    riskFlags: [],
    verdict: "Fast is an active airdrop opportunity on Own.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["T-shirts", "Headphones", "Electronics", "Anything else you’d normally shop for", "Old points migrate to the new portal", "Migrated balances get a 1.1x multiplier", "That’s a 10% bonus on everything you already earned, from day one", "Go to work.fast.xyz"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Free Overview Website: fast",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "dac",
    name: "DAC",
    ticker: "DAC",
    website: "https://airdrops.io/dac/",
    category: "airdrop",
    blockchain: "Own",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/dac_chain", discord: "https://discord.gg/gb9PjJzzK3", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/dac/" },
    scores: s(98, 98, 98, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "DAC is an active airdrop opportunity on Own.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Burn: Trade 1 DACC for a flat 1,000 QE. Immediate, predictable payout.", "Stake: Lock DACC to earn a passive share of QE from every future burn across the network. Slower start, higher upside if burn volume grows."],
      estimatedTime: "30 Minutes",
      estimatedCost: "s will be",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "grass",
    name: "Grass",
    ticker: "GRASS",
    website: "https://airdrops.io/grass/",
    category: "airdrop",
    blockchain: "Solana",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/grass/status/1942651181417030106", discord: "https://discord.gg/8NxzRj9ayN", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/grass/" },
    scores: s(92, 98, 97, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "Grass is an active airdrop opportunity on Solana.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Visit the Grass Website and RegisterCreate an account with email and passwordClick the “Connect” button", "Create an account with email and password", "Click the “Connect” button", "Install Required ComponentsDownload the Grass Desktop App", "Download the Grass Desktop App", "Complete VerificationVerify your email addressConnect your Solana wallet (Phantom or Solflare recommended)", "Verify your email address", "Connect your Solana wallet (Phantom or Solflare recommended)"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Free Overview Website: app",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "saturn_credit",
    name: "Saturn Credit",
    ticker: "SC",
    website: "https://airdrops.io/saturn-credit/",
    category: "airdrop",
    blockchain: "Ethereum",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Saturn%20Credit&url=https%3A%2F%2Fairdrops.io%2Fsaturn-credit%2F", discord: "https://discord.gg/A8MdmCwha2", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/saturn-credit/" },
    scores: s(98, 98, 98, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "Saturn Credit is an active airdrop opportunity on Ethereum.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Curve LP: Provide liquidity in the USDC/USDat pool (20x) or USDC/sUSDat pool (18x). Single-sided and two-sided positions both qualify.", "Pendle YT positions: Buy yt-USDat (30x) or yt-sUSDat (10x) on Pendle for the highest multipliers. Yield tokens decay to zero at maturity, so factor that into sizing.", "Pendle LP: Provide liquidity to Pendle’s USDat (15x), sUSDat (5x), srUSDat (7.5x), or jrUSDat (5x) pools.", "Strata tranches: Hold srUSDat (1x) or jrUSDat (3x) for tranche-based exposure.", "Morpho lending: Supply sUSDat as collateral via the Flowdesk strategy (2x) or lend AUSD (1x)."],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Medium Overview Website: saturn",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "kinetiq",
    name: "Kinetiq",
    ticker: "KINETI",
    website: "https://airdrops.io/kinetiq/",
    category: "airdrop",
    blockchain: "Hyperliquid",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Kinetiq&url=https%3A%2F%2Fairdrops.io%2Fkinetiq%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/kinetiq/" },
    scores: s(91, 98, 98, 98, 98, 98, 98),
    riskFlags: [],
    verdict: "Kinetiq is an active airdrop opportunity on Hyperliquid.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Download the Markets iOS app", "Deposit fiat or crypto (you can purchase USDC directly from Binance)", "Start trading and accrue XP through trades, daily check-in streaks, referrals, level progression, and gaining followers", "Watch for weekly competition announcements and surprise reward drops", "Acquire USDC from Binance", "Visit Markets and connect your wallet", "Click “Deposit”, select “Transfer Crypto”, choose USDC and your preferred network", "Copy the Markets deposit address and use it when withdrawing USDC from Binance"],
      estimatedTime: "30 Minutes",
      estimatedCost: "",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "monetrix",
    name: "Monetrix",
    ticker: "MONETR",
    website: "https://airdrops.io/monetrix/",
    category: "airdrop",
    blockchain: "Hyperliquid",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Monetrix&url=https%3A%2F%2Fairdrops.io%2Fmonetrix%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/monetrix/" },
    scores: s(67, 77, 72, 81, 86, 90, 96),
    riskFlags: [],
    verdict: "Monetrix is an active airdrop opportunity on Hyperliquid.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Complete the Genesis Signal tasks", "Open the Monetrix Genesis page and deposit USDC (you can purchase USDC directly from Binance or bridge using Rhino.fi bridge)", "Keep your deposit active, since both deposit size and duration build your Genesis weight", "Daily GEMs: 330,000 GEMs distributed each day, shared across depositors on a time-weighted and size-weighted basis", "Genesis SBTs: Tiered, non-transferable credentials based on GEMs Rank and deposit size; deposits held over 3 days qualify for size-tiered SBTs", "Mainnet priority: Genesis depositors get first access at mainnet launch and can claim USDM, redeemable 1:1 for USDC through the protocol redemption flow", "Subscribe to the Monetrix Announcements channel on Telegram", "Join the official Monetrix Discord server"],
      estimatedTime: "30 Minutes",
      estimatedCost: "s nothing but a few minutes and a wallet signature",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "hlos",
    name: "HLOS",
    ticker: "HLOS",
    website: "https://airdrops.io/hlos/",
    category: "airdrop",
    blockchain: "HyperEVM",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=HLOS&url=https%3A%2F%2Fairdrops.io%2Fhlos%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/hlos/" },
    scores: s(65, 66, 72, 76, 69, 80, 90),
    riskFlags: [],
    verdict: "HLOS is an active airdrop opportunity on HyperEVM.",
    source: "airdrops.io",
    participationGuide: {
      steps: [". Consider locking points for boosts. Saved and locked points can earn boosts on future activity. If you do not need to redeem for HYPE right away, locking can raise your effective rate. Keep gas funded. Running out of HYPE mid", "task interrupts farming. A small reserve keeps your activity uninterrupted across trading and staking. Frequently Asked Questions When will the HLOS airdrop happen? HLOS has not announced a TGE date or confirmed a token airdrop. The team has referenced future redemption and a possible token launch, but no timeline has been set. Is the HLOS airdrop free to farm? Farming HLOS Points requires USDC and HYPE to trade and stake inside the OS, so there is some capital cost. There are no fees to install the app itself, but on", "chain activity needs funds and gas. How are HLOS Points distributed? HLOS Points are earned through app usage, trading, and staking integrated apps over the 28", "week campaign. Points appear in your OS Card. Conclusion HLOS rewards users who actively trade, stake, and use DeFi apps inside its operating system on HyperEVM. With the HLOS Points campaign live and a possible token launch referenced by the team, early and consistent activity is the way to build a meaningful points balance before any redemption opens. Join points campaign You\'re interested in more projects that do not have any token yet and could potentially airdrop a governance token to early users in the future? Then check out our list of potential retroactive airdrops to not miss out on the next DeFi airdrop! Share Copy link X Telegram Report an issue Report an Issue Help us keep listings accurate Airdrop is expired Links are broken Other issue Please note that these are only notifications. We can\'t reply. If you have any question you would like to receive an answer please send us an email to [email protected] . Difficulty Medium Cost to Farm Medium Overview Website: hlos.app Ticker: HLOS X (Formerly Twitter): Telegram Group: X Follow us to never miss any airdrop again! Airdrop Newsletter Email Airdrops.io is a free aggregator. We don\'t run the listed airdrops. Read our safety guide before connecting any wallet. Explore Home Latest Airdrops Hot Airdrops Retroactive DeFi Airdrops Confirmed Airdrops Blog FAQ Calendar Airdrop Alert Contact us / Submit Airdrop Donate ETH 0xE718325723E43430DcdE5167bbD65fa8fFFFA769 BTC 3LoM7rYkDhFepPKukiDLiMbHguNbCSwyap Newsletter Email © 2026 airdrops.io Telegram Twitter Facebook Stay safe"],
      estimatedTime: "30 Minutes",
      estimatedCost: ". There are no fees to install the app itself, but on-chain activity needs funds and gas",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "predikt",
    name: "Predikt",
    ticker: "PREDIK",
    website: "https://airdrops.io/predikt/",
    category: "airdrop",
    blockchain: "Solana",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Predikt&url=https%3A%2F%2Fairdrops.io%2Fpredikt%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/predikt/" },
    scores: s(65, 66, 72, 76, 69, 80, 90),
    riskFlags: [],
    verdict: "Predikt is an active airdrop opportunity on Solana.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["data without risking meaningful capital. Frequently Asked Questions Is the Predikt Airdrop Confirmed? No, Predikt has not confirmed a token or formal airdrop. The team has publicly mentioned early tester benefits and an active referral campaign. Do I Need to Spend Money to Participate? Joining the waitlist and sharing your referral link are free. Testing the beta requires SOL for transactions, so a small amount of Solana is needed to actually place bets and generate meaningful activity. When Will the Predikt Token Launch? A TGE date has not been announced. Predikt is still in beta, and any token launch would typically follow a stable public release. Joining the waitlist and testing the beta is the current way to position for potential future rewards. Conclusion Predikt is one of the earlier protocols building infrastructure for prediction markets rather than launching another standalone venue. With the waitlist live, referral rewards active, and the team confirming early tester benefits, the cost of positioning is low: a Solana wallet, a small amount of SOL, and a few test bets on the beta. Join Waitlist You\'re interested in more projects that do not have any token yet and could potentially airdrop a governance token to early users in the future? Then check out our list of potential retroactive airdrops to not miss out on the next DeFi airdrop! More Airdrops to Farm SHIFT Ongoing Solana View Guide → okbet Ongoing Solana View Guide → isometric Ongoing Solana View Guide → Solstice Ongoing Solana View Guide → Phoenix Ongoing Solana View Guide → ForeGate Ongoing Solana View Guide → Share Copy link X Telegram Report an issue Report an Issue Help us keep listings accurate Airdrop is expired Links are broken Other issue Please note that these are only notifications. We can\'t reply. If you have any question you would like to receive an answer please send us an email to [email protected] . Difficulty Medium Cost to Farm Low Overview Website: predikt.gg X (Formerly Twitter): Telegram Group: X Follow us to never miss any airdrop again! Airdrop Newsletter Email Airdrops.io is a free aggregator. We don\'t run the listed airdrops. Read our safety guide before connecting any wallet. Explore Home Latest Airdrops Hot Airdrops Retroactive DeFi Airdrops Confirmed Airdrops Blog FAQ Calendar Airdrop Alert Contact us / Submit Airdrop Donate ETH 0xE718325723E43430DcdE5167bbD65fa8fFFFA769 BTC 3LoM7rYkDhFepPKukiDLiMbHguNbCSwyap Newsletter Email © 2026 airdrops.io Telegram Twitter Facebook Stay safe"],
      estimatedTime: "30 Minutes",
      estimatedCost: "of positioning is low: a Solana wallet, a small amount of SOL, and a few test bets on the beta",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "vibe_trading",
    name: "Vibe Trading",
    ticker: "VT",
    website: "https://airdrops.io/vibe-trading/",
    category: "airdrop",
    blockchain: "Hyperliquid",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Vibe%20Trading&url=https%3A%2F%2Fairdrops.io%2Fvibe-trading%2F", discord: "https://discord.gg/vibetrading", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/vibe-trading/" },
    scores: s(63, 70, 65, 72, 75, 74, 86),
    riskFlags: [],
    verdict: "Vibe Trading is an active airdrop opportunity on Hyperliquid.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["on Vibe can graduate to HIP", "3, Hyperliquid’s framework for native order", "book perpetuals, giving long", "tail tokens a path to deeper liquidity. The platform is in beta with a QuantStamp audit pending. Ongoing Confirmed Vibe Trading Airdrop Details Vibe Trading has confirmed a $VIBE token with a points", "based pre", "TGE program. Three separate streams accrue points: trading volume on the platform, referring active wallets, and community participation. Allocations, ratios, and TGE timing have not been disclosed, so the exact value of each point remains speculative. Points reset at 00:00 UTC each day and are tracked across all three programs simultaneously, so users can farm every stream in parallel. Referrers earn through two channels: a commission paid instantly in USDC from the aggregated 30", "day volume of their referred traders, plus pre", "TGE points based on the number of daily active referred wallets."],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Medium Overview Website: vibe",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "limitless_prediction_markets",
    name: "Limitless Prediction Markets",
    ticker: "LPM",
    website: "https://airdrops.io/limitless-prediction-markets/",
    category: "airdrop",
    blockchain: "Base",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Limitless%20Prediction%20Markets&url=https%3A%2F%2Fairdrops.io%2Flimitless-prediction-markets%2F", discord: "https://discord.gg/UQtv7h5ZFE", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/limitless-prediction-markets/" },
    scores: s(30, 33, 37, 37, 39, 51, 54),
    riskFlags: ["Low Buzz"],
    verdict: "Limitless Prediction Markets is an active airdrop opportunity on Base.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Team Captains running teams in the Prophet Challenge", "High-volume traders with a consistent track record", "Developers building tools, integrations, or mini-apps on Limitless Ground", "Early users who backed the platform from the start", "Active X supporters who regularly share Limitless content", "Visit the Limitless claim page", "Check your eligibility and claim your allocation", "Visit the claim page for Wallchain Quackers"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm High Overview Website: limitless",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "ondo_perps",
    name: "Ondo Perps",
    ticker: "OP",
    website: "https://airdrops.io/ondo-perps/",
    category: "airdrop",
    blockchain: "Ethereum",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Ondo%20Perps&url=https%3A%2F%2Fairdrops.io%2Fondo-perps%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/ondo-perps/" },
    scores: s(30, 41, 32, 39, 35, 40, 51),
    riskFlags: ["Low Buzz"],
    verdict: "Ondo Perps is an active airdrop opportunity on Ethereum.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Ondo Perps Actions: Join waitlist", "trade perps"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Medium Overview Website: ondoperps",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "catena",
    name: "Catena",
    ticker: "CATENA",
    website: "https://airdrops.io/catena/",
    category: "airdrop",
    blockchain: "Own",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/oakhcft/status/2057116661350551998", discord: "https://discord.gg/catenacommunity", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/catena/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "Catena is an active airdrop opportunity on Own.",
    source: "airdrops.io",
    participationGuide: {
      steps: [". You can also check back for new features, agent capabilities, and program phases. Consistent activity is what most points", "based systems end up rewarding, so treat this as an ongoing task rather than a one", "time signup. Frequently Asked Questions Has Catena confirmed an airdrop? No. Catena has not announced a token, points system, or airdrop, and the team has warned that any token using the Catena name is fake. Joining the waitlist is a way to position early, but no rewards are confirmed at this stage. Is joining the Catena waitlist free? Yes. Signing up for the waitlist and applying for Private Access costs nothing. There are no deposits, gas fees, or purchases involved. Anyone with an email address can join, and developers can apply for build access at no cost. When is the Catena token launch? There is no Catena token and no TGE date. The company has stated it has not launched a token. Any launch would be announced through Catena’s official channels first, so a firm date cannot be given yet. Conclusion Catena is building regulated banking infrastructure for AI agents, and its funding and backers give it real credibility. There is no confirmed airdrop, no token, and no points program, so participation here is about positioning rather than claiming. Joining the waitlist and applying for Private Access costs nothing. Join Waitlist You\'re interested in more projects that do not have any token yet and could potentially airdrop a governance token to early users in the future? Then check out our list of potential retroactive airdrops to not miss out on the next DeFi airdrop! Requirements Email Share Copy link X Telegram Report an issue Report an Issue Help us keep listings accurate Airdrop is expired Links are broken Other issue Please note that these are only notifications. We can\'t reply. If you have any question you would like to receive an answer please send us an email to [email protected] . Funding $48M Difficulty Beginner Cost to Farm Free Overview Website: catena.com X (Formerly Twitter): Discord Chat: Blog: X Follow us to never miss any airdrop again! Airdrop Newsletter Email Airdrops.io is a free aggregator. We don\'t run the listed airdrops. Read our safety guide before connecting any wallet. Explore Home Latest Airdrops Hot Airdrops Retroactive DeFi Airdrops Confirmed Airdrops Blog FAQ Calendar Airdrop Alert Contact us / Submit Airdrop Donate ETH 0xE718325723E43430DcdE5167bbD65fa8fFFFA769 BTC 3LoM7rYkDhFepPKukiDLiMbHguNbCSwyap Newsletter Email © 2026 airdrops.io Telegram Twitter Facebook Stay safe"],
      estimatedTime: "30 Minutes",
      estimatedCost: "s nothing, which makes it a low-effort way to register as an early user if the team ever introduces rewards",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "ceitnot",
    name: "Ceitnot",
    ticker: "CEITNO",
    website: "https://airdrops.io/ceitnot/",
    category: "airdrop",
    blockchain: "Arbitrum",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/ceitnotdefi", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/ceitnot/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "Ceitnot is an active airdrop opportunity on Arbitrum.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Select your collateral asset (e.g., mock ETH)", "Deposit collateral into a vault", "Mint (borrow) $ceitUSD against it", "Twitter/X", "Telegram", "LinkedIn"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Free Overview Website: ceitnot",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "minotaurus",
    name: "Minotaurus",
    ticker: "MINOTA",
    website: "https://airdrops.io/minotaurus/",
    category: "airdrop",
    blockchain: "BSC",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/minotaurus_io", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/minotaurus/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "Minotaurus is an active airdrop opportunity on BSC.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["500 USDT spent = 10 extra tickets", "5,000 USDT spent = 100 extra tickets", "1st Place: 50,000 USDT worth of $MTAUR", "2nd Place: 20,000 USDT worth of $MTAUR", "3rd Place: 10,000 USDT worth of $MTAUR", "4th Place: 5,000 USDT worth of $MTAUR", "5th Place: 4,000 USDT worth of $MTAUR", "6th Place: 3,000 USDT worth of $MTAUR"],
      estimatedTime: "30 Minutes",
      estimatedCost: "",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "coinex",
    name: "CoinEx",
    ticker: "COINEX",
    website: "https://airdrops.io/coinex/",
    category: "airdrop",
    blockchain: "Ongoing",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=CoinEx&url=https%3A%2F%2Fairdrops.io%2Fcoinex%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/coinex/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "CoinEx is an active airdrop opportunity on Ongoing.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Deposit at least 20 USDT to unlock the 50 USDT futures trial fund", "Deposit at least 30 USDT to unlock the 50 USDT fee cashback"],
      estimatedTime: "30 Minutes",
      estimatedCost: ", but qualifying for the full 300 USDT requires depositing and trading real funds",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "domination_finance",
    name: "Domination Finance",
    ticker: "DF",
    website: "https://airdrops.io/domination-finance/",
    category: "airdrop",
    blockchain: "Base",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Domination%20Finance&url=https%3A%2F%2Fairdrops.io%2Fdomination-finance%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/domination-finance/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "Domination Finance is an active airdrop opportunity on Base.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Native USDC", "A few dollars of ETH for gas. Each trade requires roughly 0.00003 ETH for oracle price verification, so a small balance covers hundreds of actions", "The vault is non-custodial but exposed to LP-side risk if trader PnL skews against the pool", "Withdrawals depend on vault liquidity at exit", "$dfUSDC balances show up on DeBank and other portfolio trackers", "$BTCDOM: Bitcoin’s share of total crypto market cap", "$ETHDOM: Ethereum’s share", "$USDTDOM: Tether’s share, useful for expressing views on risk-off flows"],
      estimatedTime: "30 Minutes",
      estimatedCost: "less actions that the team explicitly built UI for tend to matter",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "rabbithole",
    name: "RabbitHole",
    ticker: "RABBIT",
    website: "https://airdrops.io/rabbithole/",
    category: "airdrop",
    blockchain: "Own",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=RabbitHole&url=https%3A%2F%2Fairdrops.io%2Frabbithole%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/rabbithole/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "RabbitHole is an active airdrop opportunity on Own.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["right now. RabbitHole has raised roughly $21.6 million across two rounds: a $3.6 million seed in 2021 and an $18 million Series A in 2022. Backers include Electric Capital, which led the seed, along with Greylock, ParaFi Capital, and Framework Ventures. Ongoing RabbitHole Airdrop Details RabbitHole has not launched a token, and a RabbitHole token airdrop is unconfirmed. The platform is in its waitlist stage, with Hold", "Earn reward campaigns still to come. Securing waitlist access now positions you to join reward campaigns from the start, and an early activity record could matter if RabbitHole later rewards its first users retroactively. Key Parameters: Distribution Method : Hold", "Earn campaigns (planned) with Bronze", "Diamond tiers, daily check", "ins, lottery drops, and milestone bonuses Rewards Paid In : USDC and partner assets Current Stage : Waitlist open; campaigns not yet live"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Free Overview Website: rabbithole",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "okbet",
    name: "okbet",
    ticker: "OKBET",
    website: "https://airdrops.io/okbet/",
    category: "airdrop",
    blockchain: "Solana",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=okbet&url=https%3A%2F%2Fairdrops.io%2Fokbet%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/okbet/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "okbet is an active airdrop opportunity on Solana.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Polymarket event markets", "Kalshi regulated contracts", "Limitless short-duration markets", "Opinion-based markets", "Hyperliquid perpetuals"],
      estimatedTime: "30 Minutes",
      estimatedCost: "of entry is mostly your trading activity, with $OK holdings and referrals layered on top",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "popdex",
    name: "PopDEX",
    ticker: "POPDEX",
    website: "https://airdrops.io/popdex/",
    category: "airdrop",
    blockchain: "Own",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/popdex_/status/2057733271568716055", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/popdex/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "PopDEX is an active airdrop opportunity on Own.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Stay genuinely active in the community.", "Get Discord role You\'re interested in more projects that do not have any token yet and could potentially airdrop a governance token to early users in the future?"],
      estimatedTime: "30 Minutes",
      estimatedCost: "nothing beyond your time",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "litvm",
    name: "LitVM",
    ticker: "LITVM",
    website: "https://airdrops.io/litvm/",
    category: "airdrop",
    blockchain: "Arbitrum",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=LitVM&url=https%3A%2F%2Fairdrops.io%2Flitvm%2F", discord: "https://discord.gg/fwCxnEXTWd", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/litvm/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "LitVM is an active airdrop opportunity on Arbitrum.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["are fine. The goal is breadth of activity across the ecosystem. Step 6: Deploy a Token Visit Lester Labs , connect your wallet, and create a token. It’s a one", "time interaction, but deploying a contract adds a different type of on", "chain activity to your history. Step 7: Participate in the LiteForge Pioneer Campaign on Arkada Visit the campaign page , connect your wallet, and work through the available quests to accumulate LitPT points within the LiteForge ecosystem. Tips for Maximizing Your LitVM Allocation Come back regularly. One session won’t be enough. In retroactive distributions, what usually matters is building a history of interactions across dApps over several weeks. Using them every day or almost every day is better than just one long session. Cover all the dApps. Bridge, predict, lend, and deploy. It’s safer to have a wider range of activities across the whole ecosystem than to focus on just one protocol. Frequently Asked Questions Is the LitVM Airdrop Confirmed? No, LitVM has not said anything about a token, a ticker, or a date for distribution. The project has said that 51% of the final supply will go to the community, but nothing else has been set in stone. Do I Need Real LTC or ETH to Participate? No. You can get zkLTC for free from the faucet and use it on the LiteForge testnet. You don’t have to pay anything to take part—no bridging or buying is needed. What Activities Are Most Likely to Count? Using multiple dApps consistently over time is the safest way to do things like bridge transactions, lending, prediction markets, and deploying contracts. Over the course of weeks, volume and frequency matter more than one big interaction. Conclusion LitVM has not confirmed an airdrop, but the 51% community allocation and Charlie Lee’s support make it worth the time investment, especially since the testnet is free to use. Get on the LiteForge testnet right now, check out all the dApps that are available, and come back to see how the project grows. Join testnet You\'re interested in more projects that do not have any token yet and could potentially airdrop a governance token to early users in the future? Then check out our list of potential retroactive airdrops to not miss out on the next DeFi airdrop! More Airdrops to Farm Ceitnot Ongoing Arbitrum View Guide → Otomato Ongoing Arbitrum, Base View Guide → Variational Ongoing Arbitrum View Guide → Hibachi Ongoing Arbitrum, Base View Guide → Hyperliquid Ongoing Own chain, Arbitrum View Guide → GMX Ongoing Arbitrum, MegaETH View Guide → Share Copy link X Telegram Report an issue Report an Issue Help us keep listings accurate Airdrop is expired Links are broken Other issue Please note that these are only notifications. We can\'t reply. If you have any question you would like to receive an answer please send us an email to [email protected] . Difficulty Beginner Cost to Farm Free Overview Website: litvm.com Whitepaper: View Whitepaper Documentation: Visit now X (Formerly Twitter): Telegram Channel: Discord Chat: Blog: X Follow us to never miss any airdrop again! Airdrop Newsletter Email Airdrops.io is a free aggregator. We don\'t run the listed airdrops. Read our safety guide before connecting any wallet. Explore Home Latest Airdrops Hot Airdrops Retroactive DeFi Airdrops Confirmed Airdrops Blog FAQ Calendar Airdrop Alert Contact us / Submit Airdrop Donate ETH 0xE718325723E43430DcdE5167bbD65fa8fFFFA769 BTC 3LoM7rYkDhFepPKukiDLiMbHguNbCSwyap Newsletter Email © 2026 airdrops.io Telegram Twitter Facebook Stay safe"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Free Overview Website: litvm",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "valantis",
    name: "Valantis",
    ticker: "VALANT",
    website: "https://airdrops.io/valantis/",
    category: "airdrop",
    blockchain: "Hyperliquid",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Valantis&url=https%3A%2F%2Fairdrops.io%2Fvalantis%2F", discord: "https://discord.gg/jK2E6GPRFz", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/valantis/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "Valantis is an active airdrop opportunity on Hyperliquid.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["The program ran for six months, distributing 260M points weekly", "65M Genesis Points were allocated to Genesis Badge holders", "34.41M of those Genesis Points went unclaimed by users who didn’t return to participate", "The surplus ~34M points will be dropped exclusively to Valantis Prime Trading activity once public access opens", "Prime Trading is currently early access only — no points are earned until it’s open to all users, giving every trader a final chance to earn", "Existing Points holders and Genesis Badge users get priority access during the early access period"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm High Overview Website: valantis",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "xstocks",
    name: "xStocks",
    ticker: "XSTOCK",
    website: "https://airdrops.io/xstocks/",
    category: "airdrop",
    blockchain: "Solana",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=xStocks&url=https%3A%2F%2Fairdrops.io%2Fxstocks%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/xstocks/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "xStocks is an active airdrop opportunity on Solana.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Analyst — 10,000+ xPoints", "Associate — 50,000+ xPoints", "VP — 100,000+ xPoints", "Director — 500,000+ xPoints", "MD — 1,000,000+ xPoints"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Medium Overview Website: xstocks",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "dscvr",
    name: "DSCVR",
    ticker: "DSCVR",
    website: "https://airdrops.io/dscvr/",
    category: "airdrop",
    blockchain: "Solana",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=DSCVR&url=https%3A%2F%2Fairdrops.io%2Fdscvr%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/dscvr/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "DSCVR is an active airdrop opportunity on Solana.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Log in to your DSCVR account at the Airdrop Hub", "Review your eligibility status once your account is verified", "Connect your EVM wallet and sign the message to bind it to your account", "Open the DSCVR platform, click login, and connect a Phantom or Solflare wallet holding SOL for transaction fees. You can purchase SOL directly from Binance or bridge using the Rhino.fi bridge.", "Set up your profile with a username and picture, using NFT verification if you held an eligible NFT.", "Browse the available portals and join communities that matched your interests, including any NFT-gated ones you qualified for.", "Claim your daily streak reward, publish posts and comments, engage with other users’ content, and enter community contests to accumulate points.", "Maintaining consistent daily activity to build your streak"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Free Overview Website: dscvr",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "shift_protocol",
    name: "SHIFT Protocol",
    ticker: "SP",
    website: "https://airdrops.io/shift-protocol/",
    category: "airdrop",
    blockchain: "StarkNet",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/ethos_network", discord: "https://discord.gg/3bxdmZY5SS", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/shift-protocol/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "SHIFT Protocol is an active airdrop opportunity on StarkNet.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Buy USDC on Binance and withdraw it to your wallet", "Bridge assets to Base with Rhino Bridge if your funds sit on another chain", "1x Lighter S3 Points, distributed on release", "1.3x to 2x Hibachi Points (base plus a minimum 30% bonus)", "Deposit early: Points programs typically reward early participants, and depositing sooner means more time accumulating both points and yield", "Maintain larger deposits: Points are generally calculated based on the amount deposited, so larger positions earn proportionally more", "Utilize the referral program: Share your referral code to earn 5% of points generated by referred addresses", "Monitor for new vaults: Shift plans to expand to additional chains and protocols in Q4, which may offer new point-earning opportunities"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Medium Overview Website: shiftprotocol",
      difficulty: "Easy" as const,
    },
  },
  {
    id: "megaeth",
    name: "MegaETH",
    ticker: "MEGAET",
    website: "https://airdrops.io/megaeth/",
    category: "airdrop",
    blockchain: "Ethereum",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=MegaETH&url=https%3A%2F%2Fairdrops.io%2Fmegaeth%2F", discord: "https://discord.gg/megaeth", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/megaeth/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "MegaETH is an active airdrop opportunity on Ethereum.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Bridge: Transfer ETH from another chain using the built-in Bridge on Rabbithole", "Fund directly: Deposit from a CEX, your bank, or via card through the Fund option on Rabbithole", "Live Now: Apps ready to use today", "Coming Soon: Upcoming launches to watch", "Marching Forward: Projects in earlier development stages", "Select the wallet that will receive your rewards", "Subscribe with your email to get reward release updates", "Visit the MegaETH Terminal and connect your wallet and X account"],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Free Overview Website: megaeth",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "bulk",
    name: "BULK",
    ticker: "BULK",
    website: "https://airdrops.io/bulk/",
    category: "airdrop",
    blockchain: "Solana",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/kdotcrypto/status/2057770145561694238", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/bulk/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "BULK is an active airdrop opportunity on Solana.",
    source: "airdrops.io",
  },
  {
    id: "satsuma",
    name: "Satsuma",
    ticker: "SATSUM",
    website: "https://airdrops.io/satsuma/",
    category: "airdrop",
    blockchain: "Citrea",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://x.com/intent/tweet?text=Satsuma&url=https%3A%2F%2Fairdrops.io%2Fsatsuma%2F", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/satsuma/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "Satsuma is an active airdrop opportunity on Citrea.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Check your allocation on the Satsuma airdrop page (eligibility only shows for now; claims open at TGE on June 4).", "At TGE, connect your eligible wallet and choose one of two claim formats:veSUMA: unlocks linearly over 30 days, block by block. While locked, vote on gauges and earn weekly rebases; after unlock, hold, stake, or exit to SUMA.S33 (liquid): skip the 30-day wait and receive tradeable S33 instantly. Auto-compounds with the ratio growing each epoch, and can be used to LP, trade, or lend across protocols.", "veSUMA: unlocks linearly over 30 days, block by block. While locked, vote on gauges and earn weekly rebases; after unlock, hold, stake, or exit to SUMA.", "S33 (liquid): skip the 30-day wait and receive tradeable S33 instantly. Auto-compounds with the ratio growing each epoch, and can be used to LP, trade, or lend across protocols.", "Complete your claim before deciding on a format, as each path has different liquidity and reward trade-offs."],
      estimatedTime: "30 Minutes",
      estimatedCost: "to Farm Free Overview Website: satsuma",
      difficulty: "Medium" as const,
    },
  },
  {
    id: "how_to_get_free_crypto_airdrops",
    name: "How to get free crypto airdrops?",
    ticker: "HTGFCA",
    website: "https://airdrops.io/latest/",
    category: "airdrop",
    blockchain: "Ethereum",
    status: "active" as const,
    estimatedReward: "",
    rewardType: "Token Airdrop",
    socialLinks: { twitter: "https://twitter.com/airdrops_io", discord: "", telegram: "https://airdrops.io/telegram/", website: "https://airdrops.io/latest/" },
    scores: s(37, 32, 36, 43, 35, 41, 52),
    riskFlags: ["Low Buzz"],
    verdict: "How to get free crypto airdrops? is an active airdrop opportunity on Ethereum.",
    source: "airdrops.io",
    participationGuide: {
      steps: ["Install App, Trade & Stake for Points CLAIM AIRDROP Ongoing Catena Actions: Join waitlist CLAIM AIRDROP 62° Ongoing Predikt Actions: Join waitlist CLAIM AIRDROP 61° Ongoing Confirmed Vibe Trading Actions: Earn points and refer users CLAIM AIRDROP Ongoing Ceitnot Actions: Join testnet CLAIM AIRDROP Ongoing Minotaurus Actions: Earn tickets to enter $100k giveaway CLAIM AIRDROP Sponsored Ongoing CoinEx Actions: Deposit and trade to earn CLAIM AIRDROP 137° Ongoing Confirmed Dustswap Actions: Complete quests, claim Discord role & refer friends CLAIM AIRDROP Ongoing Domination Finance Actions: Deposit and earn CLAIM AIRDROP Ongoing RabbitHole Actions: Join waitlist CLAIM AIRDROP Ongoing okbet Actions: Invite friends and complete quests CLAIM AIRDROP Ongoing PopDEX Actions: Get Discord role CLAIM AIRDROP 22° Ongoing Confirmed Ondo Perps Actions: Join waitlist & trade perps CLAIM AIRDROP Ongoing isometric Actions: Sign up & Make Testnet Trades CLAIM AIRDROP Ongoing Confirmed Poly Helper Actions: Use browser extension to Get Daily Reward, Predict, Complete Social Tasks and Refer CLAIM AIRDROP Ongoing Phoenix Actions: Trade Perps and Refer Friends CLAIM AIRDROP Ongoing Beep Actions: Deploy AI agents CLAIM AIRDROP Ongoing Confirmed Kash Actions: Join testnet and make free predictions CLAIM AIRDROP X Follow us to never miss any airdrop again! Airdrop Newsletter Email Airdrops.io is a free aggregator. We don\'t run the listed airdrops. Read our safety guide before connecting any wallet. Explore Home Latest Airdrops Hot Airdrops Retroactive DeFi Airdrops Confirmed Airdrops Blog FAQ Calendar Airdrop Alert Contact us / Submit Airdrop Donate ETH 0xE718325723E43430DcdE5167bbD65fa8fFFFA769 BTC 3LoM7rYkDhFepPKukiDLiMbHguNbCSwyap Newsletter Email © 2026 airdrops.io Telegram Twitter Facebook Stay safe"],
      estimatedTime: "30 Minutes",
      estimatedCost: "",
      difficulty: "Medium" as const,
    },
  },
];
