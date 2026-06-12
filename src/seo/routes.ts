import { SITE, canonical } from './config';
import type { IPOStock } from '../data/ipoData';

export type JsonLd = Record<string, unknown> | Record<string, unknown>[];

export interface PageMeta {
  path: string;
  title: string;
  description: string;
  ogType?: 'website' | 'article' | 'profile';
  ogImage?: string;
  noindex?: boolean;
  schema?: JsonLd;
  keywords?: string;
}

const DEFAULT_OG = `${SITE.origin}/og-default.png`;

export const ROUTES: Record<string, PageMeta> = {
  home: {
    path: '/',
    title: `${SITE.name} — ${SITE.tagline}`,
    description: SITE.description,
    ogType: 'website',
    ogImage: DEFAULT_OG,
    schema: {
      '@context': 'https://schema.org',
      '@graph': [
        {
          '@type': 'WebSite',
          '@id': `${SITE.origin}/#website`,
          url: SITE.origin,
          name: SITE.name,
          description: SITE.description,
          inLanguage: 'en-IN',
          potentialAction: {
            '@type': 'SearchAction',
            target: `${SITE.origin}/?q={search_term_string}`,
            'query-input': 'required name=search_term_string',
          },
        },
        {
          '@type': 'Organization',
          '@id': `${SITE.origin}/#organization`,
          name: SITE.name,
          url: SITE.origin,
          logo: {
            '@type': 'ImageObject',
            url: `${SITE.origin}/og-default.png`,
          },
          sameAs: [
            `https://twitter.com/${SITE.twitter.replace('@', '')}`,
          ],
        },
      ],
    },
  },
  ipoAnalysis: {
    path: '/ipo-analysis',
    title: `IPO Analysis - Latest IPO Reviews & Insights | ${SITE.name}`,
    description:
      'Looking for the best upcoming IPOs to invest in? In-depth IPO analysis with company overviews, financial snapshots, AI scoring, and risk assessment for Indian and global IPOs.',
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  airdrops: {
    path: '/airdrops',
    title: `Crypto Airdrops - Latest Free Token Opportunities | ${SITE.name}`,
    description:
      'Want free crypto tokens? Track active and upcoming airdrops with eligibility guides, estimated values, farming strategies, and AI conviction scores.',
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  news: {
    path: '/news',
    title: `Market News - Stock Market & Crypto Updates | ${SITE.name}`,
    description:
      'What\'s moving the markets today? AI-analyzed crypto, IPO, and stock market news with sentiment analysis, impact scoring, and actionable insights.',
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  about: {
    path: '/about',
    title: `About Us - ${SITE.name} | IPO & Crypto Intelligence`,
    description: `${SITE.name} delivers AI-powered financial intelligence — IPO analysis, crypto airdrop tracking, and market-moving news for modern investors.`,
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  contact: {
    path: '/contact',
    title: `Contact Us - ${SITE.name}`,
    description: `Have questions or feedback? Contact the ${SITE.name} team for inquiries, support, or partnership opportunities.`,
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  privacy: {
    path: '/privacy-policy',
    title: `Privacy Policy - ${SITE.name}`,
    description: `${SITE.name} privacy policy. How we collect, use, and protect your personal data.`,
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  terms: {
    path: '/terms',
    title: `Terms & Conditions - ${SITE.name}`,
    description: `Terms and conditions governing your use of ${SITE.name}. Please read carefully.`,
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  cookies: {
    path: '/cookies',
    title: `Cookie Policy - ${SITE.name}`,
    description: `${SITE.name} cookie policy. What cookies we use, why, and how to control them.`,
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
};

export function getMetaForPath(pathname: string): PageMeta {
  const clean = pathname.length > 1 && pathname.endsWith('/') ? pathname.slice(0, -1) : pathname;
  if (clean === '/' || clean === '') return ROUTES.home;
  if (clean === '/ipo-analysis') return ROUTES.ipoAnalysis;
  if (clean.startsWith('/ipo-analysis/')) {
    const ipoName = clean.replace('/ipo-analysis/', '').split('-').slice(0, -1).join(' ').replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    return {
      path: clean,
      title: ipoName ? `${ipoName} IPO Analysis | ${SITE.name}` : `IPO Analysis | ${SITE.name}`,
      description: ipoName
        ? `Should you invest in ${ipoName} IPO? Comprehensive 21-section research with financials, valuation, SWOT analysis, risk assessment, and AI-powered investment verdict.`
        : 'Detailed IPO analysis: company overview, financial snapshot, AI scoring, and risk assessment.',
      ogType: 'article',
      ogImage: DEFAULT_OG,
    };
  }
  if (clean === '/airdrops') return ROUTES.airdrops;
  if (clean.startsWith('/airdrops/')) {
    const projectName = clean.replace('/airdrops/', '').split('-').slice(0, -1).join(' ').replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    return {
      path: clean,
      title: projectName ? `${projectName} Airdrop Guide | ${SITE.name}` : `Crypto Airdrops | ${SITE.name}`,
      description: projectName
        ? `How to get the ${projectName} airdrop? Complete guide: eligibility criteria, estimated value, step-by-step farming instructions, and risk assessment.`
        : 'Crypto airdrop details: eligibility, estimated value, farming guide, and risk assessment.',
      ogType: 'article',
      ogImage: DEFAULT_OG,
    };
  }
  if (clean === '/news') return ROUTES.news;
  if (clean.startsWith('/news/')) {
    const headline = clean.replace('/news/', '').split('-').slice(0, -1).join(' ').replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    return {
      path: clean,
      title: headline ? `${headline} | ${SITE.name}` : `Market News | ${SITE.name}`,
      description: headline
        ? `${headline} — AI-analyzed market impact. Get sentiment analysis, bull/bear cases, and actionable crypto and equity market insights.`
        : 'AI-analyzed market news with sentiment and impact scoring.',
      ogType: 'article',
      ogImage: DEFAULT_OG,
    };
  }
  if (clean === '/about') return ROUTES.about;
  if (clean === '/contact') return ROUTES.contact;
  if (clean === '/privacy-policy') return ROUTES.privacy;
  if (clean === '/terms') return ROUTES.terms;
  if (clean === '/cookies') return ROUTES.cookies;
  return {
    path: clean,
    title: `Page Not Found | ${SITE.name}`,
    description: 'The page you are looking for does not exist.',
    ogType: 'website',
    ogImage: DEFAULT_OG,
    noindex: true,
  };
}

export function absoluteUrl(pathOrUrl: string): string {
  if (pathOrUrl.startsWith('http')) return pathOrUrl;
  return canonical(pathOrUrl);
}
