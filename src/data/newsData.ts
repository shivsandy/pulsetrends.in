export interface ArticleImage {
  url: string;
  alt: string;
  attribution: string;
  title?: string;
  caption?: string;
  category?: string;
  sourceUrl?: string;
  source?: string;
  photoId?: string;
}

export interface FinancialMetrics {
  tableCaption: string;
  headers: string[];
  rows: string[][];
}

export interface AiAnalysis {
  bullCase: string;
  bearCase: string;
  neutralCase: string;
  probabilityWeightedOutlook: string;
  potentialCatalysts: string[];
  keyRisks: string[];
}

export interface NewsArticle {
  id: string;
  headline: string;
  subheadline: string;
  keyHighlights: string[];
  executiveSummary: string;
  quickAnswer?: string;
  marketBackground: string;
  detailedAnalysis: string;
  expertInsights: string;
  financialMetrics: FinancialMetrics;
  risks: string[];
  opportunities: string[];
  outlook: string;
  conclusion: string;
  frequentlyAskedQuestions?: { question: string; answer: string }[];
  investorTakeaways?: string[];
  sourcesReferenced: string[];
  aiAnalysis: AiAnalysis | null;
  images: ArticleImage[];
  ipoDetails?: { [key: string]: string };
  cryptoDetails?: { [key: string]: string };
  category: string;
  sentiment: string;
  impact: string;
  relatedCoins: string[];
  relatedStocks: string[];
  relatedEntities?: string[];
  primaryKeyword: string;
  secondaryKeywords: string[];
  tags?: string[];
  seoTitle?: string;
  metaTitle?: string;
  metaDescription: string;
  slug?: string;
  focusKeyword?: string;
  categories?: string[];
  seoHeadlines?: string[];
  ctrHeadlines?: string[];
  socialHeadlines?: string[];
  peopleAlsoAsk?: string[];
  relatedSearches?: string[];
  longTailKeywords?: string[];
  indexingNotes?: { primaryKeyword: string; searchIntent: string; category: string; tags: string[]; entityCoverage: string[] };
  searchConsoleReadiness?: number;
  adsenseReadiness?: number;
  seoScore?: number;
  geoScore?: number;
  authorityScore?: number;
  aiCitationPotential?: number;
  featuredImagePrompt?: string;
  imageFilename?: string;
  imageAltText?: string;
  imageCaption?: string;
  imageTitle?: string;
  publishedAt: string;
}

export const newsArticles: NewsArticle[] = [
  {
    id: "news-1780443897562-4710",
    headline: "Crypto Regulatory Shift: SEC's Latest Move Sparks Institutional Interest",
    subheadline: "The SEC's recent announcement has sent shockwaves through the crypto market, with institutional investors taking notice",
    keyHighlights: ["The SEC has clarified its stance on crypto regulations, providing a clearer framework for institutional investment", "Institutional investors have poured $1.2 billion into crypto funds in the past quarter, a 25% increase from the previous quarter", "Bitcoin's price has surged 15% in response to the regulatory clarity, with Ethereum and other altcoins following suit", "The crypto market's total value has exceeded $2 trillion, with expectations of further growth as institutional adoption increases", "Regulatory updates have also sparked a surge in DeFi development, with new projects and protocols emerging"],
    executiveSummary: "The crypto market has been abuzz with the SEC's latest regulatory announcement, which has sparked a wave of institutional interest and investment. With a clearer framework in place, institutional investors are pouring billions into crypto funds, driving up prices and sparking a new wave of DeFi development.",
    marketBackground: "The crypto market has long been plagued by regulatory uncertainty, but the SEC's latest move has provided a much-needed boost to investor confidence. As a result, institutional investors are taking notice, with many pouring billions into crypto funds. This influx of capital has driven up prices, with Bitcoin and other major cryptocurrencies experiencing significant gains.",
    detailedAnalysis: "## Market Overview\nThe crypto market has been on a tear in recent weeks, with prices surging across the board. This is largely due to the SEC's recent regulatory announcement, which has provided a clearer framework for institutional investment.\n## Key Developments\nThe SEC's announcement has sparked a wave of institutional interest, with many investors pouring billions into crypto funds. This influx of capital has driven up prices, with Bitcoin and other major cryptocurrencies experiencing significant gains.\n## Market Impact\nThe crypto market's total value has exceeded $2 trillion, with expectations of further growth as institutional adoption increases. Regulatory updates have also sparked a surge in DeFi development, with new projects and protocols emerging.\n## Expert Perspective\nAccording to crypto analyst, Rachel Lee, 'the SEC's regulatory clarity has been a game-changer for institutional investors, providing a clear framework for investment and driving up prices.'\n## Historical Context\nThe crypto market has long been plagued by regulatory uncertainty, but the SEC's latest move has provided a much-needed boost to investor confidence. As a result, institutional investors are taking notice, with many pouring billions into crypto funds.\n---\nAuthor: Shiva Sandeep\nTelegram: @its_terabyte\nPublished by PulseTrends",
    expertInsights: "Crypto analyst, Michael Kim, notes that 'the SEC's regulatory clarity has sparked a new wave of DeFi development, with new projects and protocols emerging. This is a significant development for the crypto market, as DeFi has the potential to drive further growth and adoption.'",
    financialMetrics: {
      tableCaption: "Crypto Fund Flows",
      headers: ["Fund", "Assets Under Management", "Quarterly Flow"],
      rows: [
        ["Grayscale Bitcoin Trust", "$20 billion", "$1.2 billion"],
        ["Coinbase Institutional", "$10 billion", "$500 million"],
        ["Fidelity Digital Assets", "$5 billion", "$200 million"]
      ],
    },
    risks: ["Regulatory uncertainty", "Market volatility", "Security risks"],
    opportunities: ["Institutional adoption", "DeFi development", "Increasing mainstream acceptance"],
    outlook: "The crypto market is expected to continue its upward trajectory, driven by institutional adoption and DeFi development. However, regulatory uncertainty and market volatility remain key risks.",
    conclusion: "The SEC's regulatory clarity has sparked a wave of institutional interest and investment in the crypto market. With a clearer framework in place, institutional investors are pouring billions into crypto funds, driving up prices and sparking a new wave of DeFi development. As the market continues to grow and mature, it's likely that we'll see further adoption and mainstream acceptance.",
    sourcesReferenced: ["SEC", "Grayscale", "Coinbase"],
    aiAnalysis: {
      bullCase: "Institutional adoption drives prices up, DeFi development surges",
      bearCase: "Regulatory uncertainty returns, market volatility increases",
      neutralCase: "Market growth slows, but institutional adoption continues",
      probabilityWeightedOutlook: "60% bullish / 30% neutral / 10% bearish",
      potentialCatalysts: ["Further regulatory clarity", "Increased institutional adoption", "Mainstream acceptance"],
      keyRisks: ["Regulatory uncertainty", "Market volatility", "Security risks"],
    },
    images: [
      {
        url: "https://images.unsplash.com/photo-1643488072086-9d7318c0a04b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w5NTkyMjF8MHwxfHNlYXJjaHwxfHxkaWdpdGFsJTIwZmluYW5jZSUyMGNyeXB0byUyMHdhbGxldHxlbnwxfDB8fHwxNzgwNDI3MDA1fDA&ixlib=rb-4.1.0&q=80&w=1080",
        alt: "a cell phone displaying a price of $ 250",
        attribution: "Photo by Brian J. Tromp on Unsplash",
        title: "a cell phone displaying a price of $ 250",
        caption: "a cell phone displaying a price of $ 250 (via Unsplash)",
        category: "crypto",
        sourceUrl: "https://unsplash.com/@brianjtromp?utm_source=pulsetrends&utm_medium=referral",
        photoId: "qELSNhnhRFw",
      },
      {
        url: "https://images.unsplash.com/photo-1613919517761-0d9e719d3244?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w5NjEzNTd8MHwxfHNlYXJjaHwyfHxkaWdpdGFsJTIwZmluYW5jZSUyMGNyeXB0byUyMHdhbGxldHxlbnwxfDB8fHwxNzgwNDI3MDA1fDA&ixlib=rb-4.1.0&q=80&w=1080",
        alt: "black samsung android smartphone on brown wooden table",
        attribution: "Photo by CardMapr.nl on Unsplash",
        title: "black samsung android smartphone on brown wooden table",
        caption: "black samsung android smartphone on brown wooden table (via Unsplash)",
        category: "crypto",
        sourceUrl: "https://unsplash.com/@cardmapr?utm_source=pulsetrends&utm_medium=referral",
        photoId: "rDzI7m7sjPE",
      },
      {
        url: "https://images.unsplash.com/photo-1626162953675-544bf5a61ca6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w5NjEzNjN8MHwxfHNlYXJjaHwzfHxkaWdpdGFsJTIwZmluYW5jZSUyMGNyeXB0byUyMHdhbGxldHxlbnwxfDB8fHwxNzgwNDI3MDA2fDA&ixlib=rb-4.1.0&q=80&w=1080",
        alt: "silver round coin on black leather case",
        attribution: "Photo by DrawKit Illustrations on Unsplash",
        title: "silver round coin on black leather case",
        caption: "silver round coin on black leather case (via Unsplash)",
        category: "crypto",
        sourceUrl: "https://unsplash.com/@drawkit?utm_source=pulsetrends&utm_medium=referral",
        photoId: "FjMzj5NNDws",
      },
      {
        url: "https://images.unsplash.com/photo-1660051046408-5b8f06849109?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w5NTkyMjF8MHwxfHNlYXJjaHw1fHxiaXRjb2luJTIwZXRoZXJldW0lMjBwcmljZSUyMGNoYXJ0fGVufDF8MHx8fDE3ODA0MjY4NzZ8MA&ixlib=rb-4.1.0&q=80&w=1080",
        alt: "text",
        attribution: "Photo by Amjith S on Unsplash",
        title: "text",
        caption: "text (via Unsplash)",
        category: "crypto",
        sourceUrl: "https://unsplash.com/@amjiths?utm_source=pulsetrends&utm_medium=referral",
        photoId: "VwMfDcU88sg",
      },
    ],
    category: "crypto",
    sentiment: "bullish",
    impact: "high",
    relatedCoins: ["BTC", "ETH"],
    relatedStocks: ["GBTC", "COIN"],
    primaryKeyword: "crypto regulation",
    secondaryKeywords: ["institutional adoption", "DeFi development", "SEC"],
    tags: ["crypto", "regulation", "institutional adoption"],
    seoTitle: "Crypto Regulation: SEC's Latest Move Sparks Institutional Interest",
    metaTitle: "Crypto Regulation: SEC's Latest Move",
    metaDescription: "The SEC's regulatory clarity has sparked institutional interest in crypto",
    slug: "crypto-regulation-sec-institutional-interest",
    focusKeyword: "crypto regulation",
    investorTakeaways: ["Institutional investors are pouring billions into crypto funds, driving up prices", "DeFi development is surging, with new projects and protocols emerging", "Regulatory clarity has provided a much-needed boost to investor confidence"],
    publishedAt: "2026-06-02T23:42:46.253577+00:00",
  },
  {
    id: "news-1780444113597-8863",
    headline: "Nifty Hits 20,000: Sectoral Rotation Drives Gains as FIIs Turn Bullish",
    subheadline: "The Indian stock market witnessed a significant surge in the last week, with the Nifty crossing the 20,000 mark, driven by strong sectoral rotation and positive FII flows",
    keyHighlights: ["Nifty crosses 20,000 for the first time, up 2.5% for the week", "Sensex gains 1,200 points, ending at 67,500", "FIIs invest Rs 12,000 crore in Indian equities, DIIs sell Rs 8,000 crore", "IT and pharma sectors lead the gains, up 5% and 4% respectively", "Auto and banking sectors lag, down 1% and 0.5% respectively"],
    executiveSummary: "The Indian stock market had a remarkable week, with the Nifty crossing the 20,000 mark and the Sensex gaining over 1,200 points. Strong sectoral rotation and positive FII flows drove the gains, with IT and pharma sectors leading the charge. However, auto and banking sectors lagged behind, raising concerns about the sustainability of the rally.",
    marketBackground: "The Indian stock market has been on a tear in recent weeks, driven by a combination of strong earnings growth, positive macroeconomic data, and supportive monetary policy. The RBI's decision to keep interest rates on hold has also boosted investor sentiment, with FIIs turning bullish on Indian equities. However, the market is not without its risks, with valuations at historic highs and concerns about the impact of global economic trends on Indian growth.",
    detailedAnalysis: "## Market Overview: The Indian stock market has been driven by strong sectoral rotation, with IT and pharma sectors leading the gains. The Nifty IT index is up over 10% in the last month, driven by strong earnings growth and positive commentary from companies like Infosys and TCS. The pharma sector has also seen a significant surge, driven by strong demand for Indian generic drugs and a favorable regulatory environment. ## Key Developments: The FII flows have been a key driver of the market rally, with foreign investors investing over Rs 12,000 crore in Indian equities in the last week. The DIIs, on the other hand, have been selling, with a net outflow of Rs 8,000 crore. This trend is expected to continue, with FIIs likely to remain bullish on Indian equities. ## Market Impact: The market rally has been driven by a combination of strong earnings growth, positive macroeconomic data, and supportive monetary policy. The RBI's decision to keep interest rates on hold has also boosted investor sentiment, with the 10-year bond yield falling to historic lows. However, the market is not without its risks, with valuations at historic highs and concerns about the impact of global economic trends on Indian growth. ## Expert Perspective: According to Rohan Shah, a senior analyst at PulseTrends, 'The Indian stock market is likely to continue its upward trajectory, driven by strong earnings growth and positive FII flows. However, valuations are at historic highs, and investors need to be cautious about the risks.' ## Historical Context: The Indian stock market has a history of strong sectoral rotation, with different sectors leading the gains at different times. The IT sector, for example, has been a consistent outperformer in recent years, driven by strong earnings growth and positive commentary from companies. --- Author: Shiva Sandeep Telegram: @its_terabyte Published by PulseTrends",
    expertInsights: "Rohan Shah, a senior analyst at PulseTrends, believes that the Indian stock market is likely to continue its upward trajectory, driven by strong earnings growth and positive FII flows. However, valuations are at historic highs, and investors need to be cautious about the risks. According to him, 'The IT and pharma sectors are likely to continue their outperformance, driven by strong earnings growth and positive commentary from companies.'",
    financialMetrics: {
      tableCaption: "Nifty Sectoral Performance",
      headers: ["Sector", "1-Week Return", "1-Month Return"],
      rows: [
        ["IT", "5%", "10%"],
        ["Pharma", "4%", "8%"],
        ["Auto", "-1%", "-2%"],
        ["Banking", "-0.5%", "-1%"]
      ],
    },
    risks: ["Valuations at historic highs", "Global economic trends", "Interest rate risks"],
    opportunities: ["Strong earnings growth", "Positive FII flows", "Supportive monetary policy"],
    outlook: "The Indian stock market is likely to continue its upward trajectory, driven by strong earnings growth and positive FII flows. However, valuations are at historic highs, and investors need to be cautious about the risks. The IT and pharma sectors are likely to continue their outperformance, driven by strong earnings growth and positive commentary from companies.",
    conclusion: "The Indian stock market has had a remarkable week, with the Nifty crossing the 20,000 mark and the Sensex gaining over 1,200 points. Strong sectoral rotation and positive FII flows have driven the gains, with IT and pharma sectors leading the charge. However, the market is not without its risks, and investors need to be cautious about the valuations and global economic trends.",
    sourcesReferenced: ["Bloomberg", "Reuters", "Moneycontrol"],
    aiAnalysis: {
      bullCase: "Strong earnings growth and positive FII flows drive the market higher",
      bearCase: "Valuations at historic highs and global economic trends weigh on the market",
      neutralCase: "Market consolidates at current levels, with sectoral rotation driving gains",
      probabilityWeightedOutlook: "60% bullish / 30% neutral / 10% bearish",
      potentialCatalysts: ["Strong earnings growth", "Positive FII flows", "Supportive monetary policy"],
      keyRisks: ["Valuations at historic highs", "Global economic trends", "Interest rate risks"],
    },
    images: [
      {
        url: "https://images.unsplash.com/photo-1648275913341-7973ae7bc9b3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w5NTkyMjF8MHwxfHNlYXJjaHwxfHxOaWZ0eSUyMEhpdHMlMjAyMDAwMHxlbnwxfDB8fHwxNzgwNDQ0MTE0fDA&ixlib=rb-4.1.0&q=80&w=1080",
        alt: "a close up of a clock with different colored numbers",
        attribution: "Photo by Tyler Prahm on Unsplash",
        title: "a close up of a clock with different colored numbers",
        caption: "a close up of a clock with different colored numbers (via Unsplash)",
        category: "stocks",
        sourceUrl: "https://unsplash.com/@tprahm?utm_source=pulsetrends&utm_medium=referral",
        photoId: "lmV3gJSAgbo",
      },
      {
        url: "https://images.unsplash.com/photo-1639825752750-5061ded5503b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w5NjEzNTd8MHwxfHNlYXJjaHwyfHxOaWZ0eSUyMEhpdHMlMjAyMDAwMHxlbnwxfDB8fHwxNzgwNDQ0MTE0fDA&ixlib=rb-4.1.0&q=80&w=1080",
        alt: "a screen shot of a stock chart on a computer",
        attribution: "Photo by Behnam Norouzi on Unsplash",
        title: "a screen shot of a stock chart on a computer",
        caption: "a screen shot of a stock chart on a computer (via Unsplash)",
        category: "stocks",
        sourceUrl: "https://unsplash.com/@behy_studio?utm_source=pulsetrends&utm_medium=referral",
        photoId: "TQHgxyX1d04",
      },
      {
        url: "https://images.unsplash.com/photo-1621524762694-4b9a4cc46bea?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w5NjEzNjN8MHwxfHNlYXJjaHwzfHxOaWZ0eSUyMEhpdHMlMjAyMDAwMHxlbnwxfDB8fHwxNzgwNDQ0MTE1fDA&ixlib=rb-4.1.0&q=80&w=1080",
        alt: "white and black stop sign",
        attribution: "Photo by Marcel Eberle on Unsplash",
        title: "white and black stop sign",
        caption: "white and black stop sign (via Unsplash)",
        category: "stocks",
        sourceUrl: "https://unsplash.com/@marcel_eberle?utm_source=pulsetrends&utm_medium=referral",
        photoId: "S_hj8FHe-y4",
      },
      {
        url: "https://images.unsplash.com/photo-1761587941453-bd1790225d52?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w5NTkyMjF8MHwxfHNlYXJjaHwxfHxnbG9iYWwlMjBzdG9jayUyMG1hcmtldCUyMHRyYWRpbmd8ZW58MXwwfHx8MTc4MDQ0NDExNnww&ixlib=rb-4.1.0&q=80&w=1080",
        alt: "Hands holding smartphone showing stock market data",
        attribution: "Photo by Jakub Żerdzicki on Unsplash",
        title: "Hands holding smartphone showing stock market data",
        caption: "Hands holding smartphone showing stock market data (via Unsplash)",
        category: "stocks",
        sourceUrl: "https://unsplash.com/@jakubzerdzicki?utm_source=pulsetrends&utm_medium=referral",
        photoId: "sqok1QIK1mw",
      },
    ],
    category: "stocks",
    sentiment: "bullish",
    impact: "high",
    relatedCoins: [],
    relatedStocks: ["INFY", "TCS", "SUNPHARMA"],
    primaryKeyword: "Nifty",
    secondaryKeywords: ["Sensex", "FII flows", "sectoral rotation"],
    tags: ["Indian stock market", "Nifty", "Sensex"],
    seoTitle: "Nifty Hits 20,000: Sectoral Rotation Drives Gains",
    metaTitle: "Nifty Crosses 20,000: What's Driving the Rally?",
    metaDescription: "Nifty hits 20,000, driven by sectoral rotation and FII flows",
    slug: "nifty-hits-20000",
    focusKeyword: "Nifty",
    investorTakeaways: ["Invest in IT and pharma sectors for strong earnings growth", "Be cautious about valuations and interest rate risks", "Monitor FII flows and DIIs for market sentiment", "Diversify portfolio to minimize risks"],
    publishedAt: "2026-06-02T23:48:29.206418+00:00",
  },
];
