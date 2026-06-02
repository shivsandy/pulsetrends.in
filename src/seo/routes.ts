import { SITE, canonical } from './config';

export type JsonLd = Record<string, unknown> | Record<string, unknown>[];

export interface PageMeta {
  path: string;
  title: string;
  description: string;
  ogType?: 'website' | 'article' | 'profile';
  ogImage?: string;
  noindex?: boolean;
  schema?: JsonLd;
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
      'In-depth IPO analysis with company overviews, financial snapshots, AI scoring, and risk assessment for upcoming Indian and global IPOs.',
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  airdrops: {
    path: '/airdrops',
    title: `Crypto Airdrops - Latest Free Token Opportunities | ${SITE.name}`,
    description:
      'Track active and upcoming crypto airdrops. Eligibility guides, estimated values, farming strategies, and AI conviction scores.',
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  news: {
    path: '/news',
    title: `Market News - Stock Market & Crypto Updates | ${SITE.name}`,
    description:
      'AI-analyzed market news with sentiment, impact scoring, bull/bear cases, and actionable insights for crypto and equity markets.',
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  about: {
    path: '/about',
    title: `About Us - ${SITE.name} | IPO & Crypto Intelligence`,
    description: `${SITE.name} is a financial intelligence platform delivering AI-powered analysis of IPOs, crypto airdrops, and market-moving news.`,
    ogType: 'website',
    ogImage: DEFAULT_OG,
  },
  contact: {
    path: '/contact',
    title: `Contact Us - ${SITE.name}`,
    description: `Get in touch with the ${SITE.name} team. For inquiries, feedback, support, or partnerships.`,
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
    return {
      path: clean,
      title: `IPO Analysis | ${SITE.name}`,
      description:
        'Detailed IPO analysis: company overview, financial snapshot, AI scoring, and risk assessment.',
      ogType: 'article',
      ogImage: DEFAULT_OG,
    };
  }
  if (clean === '/airdrops') return ROUTES.airdrops;
  if (clean.startsWith('/airdrops/')) {
    return {
      path: clean,
      title: `Crypto Airdrop | ${SITE.name}`,
      description:
        'Crypto airdrop details: eligibility, estimated value, farming guide, and risk assessment.',
      ogType: 'article',
      ogImage: DEFAULT_OG,
    };
  }
  if (clean === '/news') return ROUTES.news;
  if (clean.startsWith('/news/')) {
    return {
      path: clean,
      title: `Market News Article | ${SITE.name}`,
      description: 'AI-analyzed market news with sentiment and impact scoring.',
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
