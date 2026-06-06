import { SITE, canonical } from './config';
import type { PageMeta } from './routes';

export interface PageSeoProps {
  meta: PageMeta;
  breadcrumbs?: { name: string; path: string }[];
  imageOverride?: string;
}

const ORG_ID = `${SITE.origin}/#organization`;
const WEBSITE_ID = `${SITE.origin}/#website`;

function buildBreadcrumbSchema(items: { name: string; path: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, idx) => ({
      '@type': 'ListItem',
      position: idx + 1,
      name: item.name,
      item: canonical(item.path),
    })),
  };
}

function buildWebPageSchema(meta: PageMeta) {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    '@id': canonical(meta.path),
    url: canonical(meta.path),
    name: meta.title,
    description: meta.description,
    isPartOf: { '@id': WEBSITE_ID },
    publisher: { '@id': ORG_ID },
    inLanguage: 'en-IN',
  };
}

export function buildFullSchema(meta: PageMeta, breadcrumbs?: { name: string; path: string }[]) {
  const nodes: Record<string, unknown>[] = [buildWebPageSchema(meta)];
  if (meta.schema) {
    const s = meta.schema;
    if (Array.isArray(s)) nodes.push(...(s as Record<string, unknown>[]));
    else nodes.push(s);
  }
  if (breadcrumbs && breadcrumbs.length > 0) nodes.push(buildBreadcrumbSchema(breadcrumbs));
  return {
    '@context': 'https://schema.org',
    '@graph': nodes,
  };
}

export function newsArticleSchema(article: {
  id: string;
  headline: string;
  description: string;
  publishedAt: string;
  image?: string;
  author?: string;
  urlPath: string;
  category?: string;
  tags?: string[];
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'NewsArticle',
    headline: article.headline,
    description: article.description,
    datePublished: article.publishedAt,
    dateModified: article.publishedAt,
    articleSection: article.category || 'Market News',
    keywords: (article.tags || []).join(', '),
    author: {
      '@type': 'Person',
      name: article.author || 'Shiva Sandeep',
      url: `https://twitter.com/pulsetrends`,
    },
    publisher: {
      '@type': 'Organization',
      name: SITE.name,
      logo: { '@type': 'ImageObject', url: `${SITE.origin}/og-default.png` },
    },
    mainEntityOfPage: { '@type': 'WebPage', '@id': canonical(article.urlPath) },
    image: article.image ? [canonical(article.image)] : [`${SITE.origin}/og-default.png`],
  };
}

export function personSchema(name: string, url: string, jobTitle?: string, description?: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name,
    url,
    jobTitle: jobTitle || 'Editor',
    description: description || `${name} is an editor at ${SITE.name}.`,
    sameAs: [`https://twitter.com/pulsetrends`],
  };
}

export function faqPageSchema(questions: { question: string; answer: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: questions.map((q) => ({
      '@type': 'Question',
      name: q.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: q.answer,
      },
    })),
  };
}

export function financialProductSchema(product: {
  name: string;
  description: string;
  urlPath: string;
  category?: string;
  identifier?: string;
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FinancialProduct',
    name: product.name,
    description: product.description,
    url: canonical(product.urlPath),
    category: product.category,
    provider: { '@type': 'Organization', name: SITE.name, url: SITE.origin },
    identifier: product.identifier,
  };
}
