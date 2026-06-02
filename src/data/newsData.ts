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

export interface FaqItem {
  question: string;
  answer: string;
}

export interface IndexingNotes {
  primaryKeyword: string;
  searchIntent: string;
  category: string;
  tags: string[];
  entityCoverage: string[];
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
  frequentlyAskedQuestions?: FaqItem[];
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
  indexingNotes?: IndexingNotes;
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

export const newsArticles: NewsArticle[] = [];
