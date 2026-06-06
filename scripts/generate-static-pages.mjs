/**
 * generate-static-pages.mjs
 * 
 * Runs after `vite build`. Reads the built SPA shell (dist/index.html),
 * extracts the CSS/JS asset references, then writes a static HTML file
 * for EVERY route with proper meta tags, Open Graph, Twitter Cards,
 * canonical URLs, and JSON-LD structured data so crawlers see
 * complete metadata without executing JavaScript.
 *
 * This fixes HTTP-404-on-subpages because each route now has a real
 * physical .html file (or directory with index.html) on disk.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

// ── Config ────────────────────────────────────────────────────────
const SITE_ORIGIN = 'https://pulsetrends.in';
const SITE_NAME = 'PulseTrends';
const SITE_TAGLINE = 'IPO, Crypto & Market Intelligence';
const SITE_DESC = 'AI-powered intelligence for IPOs, crypto airdrops, and market-moving news. Deep analysis, risk metrics, and actionable insights for modern investors.';
const LOCALE = 'en_IN';
const DEFAULT_OG_IMAGE = `${SITE_ORIGIN}/og-default.png`;

// ═══════════════════════════════════════════════════════════════════
//  Shared data extraction helpers (identical approach to postbuild.mjs)
// ═══════════════════════════════════════════════════════════════════

function safeEvalArr(arrLiteral) {
  const cleaned = arrLiteral
    .replace(/;\s*$/, '')
    .replace(/\s+as\s+(const|[A-Za-z_$][\w$]*(\[\])?)/g, '')
    .replace(/:\s*IPOStock\[\]/g, '')
    .replace(/:\s*CryptoProject\[\]/g, '')
    .replace(/:\s*NewsArticle\[\]/g, '');
  try {
    const parsed = Function(`"use strict";return (${cleaned});`)();
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    console.warn('[generate-static-pages] parse error:', e.message);
    return [];
  }
}

function extractStocksFromTs(tsPath) {
  if (!existsSync(tsPath)) return [];
  const src = readFileSync(tsPath, 'utf8');
  const match = src.match(/export\s+const\s+ipoStocks\s*:\s*IPOStock\[\]\s*=\s*(\[[\s\S]*?\n\];)/);
  if (!match) return [];
  return safeEvalArr(match[1]);
}

function extractNewsFromTs(tsPath) {
  if (!existsSync(tsPath)) return [];
  const src = readFileSync(tsPath, 'utf8');
  const match = src.match(/export\s+const\s+newsArticles\s*:\s*NewsArticle\[\]\s*=\s*(\[[\s\S]*?\n\];)/);
  if (!match) return [];
  return safeEvalArr(match[1]);
}

function extractProjectsFromTs(tsPath) {
  if (!existsSync(tsPath)) return [];
  const src = readFileSync(tsPath, 'utf8');
  const match = src.match(/export\s+const\s+cryptoProjects\s*:\s*CryptoProject\[\]\s*=\s*(\[[\s\S]*?\n\];)/);
  if (!match) return [];
  return safeEvalArr(match[1]);
}

// ═══════════════════════════════════════════════════════════════════
//  Helpers
// ═══════════════════════════════════════════════════════════════════

function slugify(input) {
  return (input || '')
    .toString()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80);
}

function canonical(path) {
  const clean = path.startsWith('/') ? path : `/${path}`;
  const trimmed = clean.length > 1 && clean.endsWith('/') ? clean.slice(0, -1) : clean;
  return `${SITE_ORIGIN}${trimmed}`;
}

function escapeHtml(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function truncate(str, max = 160) {
  if (!str) return '';
  return str.length > max ? str.slice(0, max - 3) + '...' : str;
}

// ═══════════════════════════════════════════════════════════════════
//  Schema builders
// ═══════════════════════════════════════════════════════════════════

function buildBreadcrumb(items) {
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

function buildWebPageSchema(title, desc, path) {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    '@id': canonical(path),
    url: canonical(path),
    name: title,
    description: desc,
    isPartOf: { '@id': `${SITE_ORIGIN}/#website` },
    publisher: { '@id': `${SITE_ORIGIN}/#organization` },
    inLanguage: 'en-IN',
  };
}

// ═══════════════════════════════════════════════════════════════════
//  HTML template builder
// ═══════════════════════════════════════════════════════════════════

function buildHtml({
  title,
  description,
  path,
  ogImage = DEFAULT_OG_IMAGE,
  ogType = 'website',
  noindex = false,
  schemas = [],
  breadcrumbs = [],
  stylesheetHref,
  jsSrc,
  modulepreloadLinks = [],
  redirectTo,
}) {
  if (redirectTo) {
    const redirectUrl = redirectTo.startsWith('http') ? redirectTo : `${SITE_ORIGIN}${redirectTo}`;
    return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="noindex,nofollow" />
    <meta http-equiv="refresh" content="0; url=${redirectUrl}" />
    <title>Redirecting... | ${SITE_NAME}</title>
    <link rel="canonical" href="${redirectUrl}" />
  </head>
  <body>
    <p>Redirecting to <a href="${redirectUrl}">${redirectUrl}</a>...</p>
    <script>window.location.replace("${redirectUrl}");</script>
  </body>
</html>`;
  }
  const url = canonical(path);
  const robots = noindex ? 'noindex,nofollow' : 'index,follow,max-image-preview:large';

  const allSchemas = [...schemas];
  if (breadcrumbs.length > 0) {
    allSchemas.push(buildBreadcrumb(breadcrumbs));
  }
  allSchemas.push(buildWebPageSchema(title, description, path));

  const schemaJson = JSON.stringify({
    '@context': 'https://schema.org',
    '@graph': allSchemas,
  }, null, 2);

  const preloadHtml = modulepreloadLinks.join('\n    ');

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
    <meta name="theme-color" content="#050505" />
    <meta name="color-scheme" content="dark" />
    <meta name="author" content="PulseTrends" />
    <meta name="robots" content="${robots}" />

    <title>${escapeHtml(title)}</title>
    <meta name="description" content="${escapeHtml(truncate(description, 160))}" />
    <link rel="canonical" href="${url}" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="apple-touch-icon" href="/favicon.svg" />
    <link rel="preconnect" href="https://images.unsplash.com" />

    ${preloadHtml ? `    ${preloadHtml}` : ''}

    <!-- Open Graph -->
    <meta property="og:site_name" content="${SITE_NAME}" />
    <meta property="og:title" content="${escapeHtml(title)}" />
    <meta property="og:description" content="${escapeHtml(truncate(description, 200))}" />
    <meta property="og:url" content="${url}" />
    <meta property="og:type" content="${ogType}" />
    <meta property="og:image" content="${ogImage}" />
    <meta property="og:locale" content="${LOCALE}" />

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="${escapeHtml(title)}" />
    <meta name="twitter:description" content="${escapeHtml(truncate(description, 200))}" />
    <meta name="twitter:image" content="${ogImage}" />

    <!-- Schema.org -->
    <script type="application/ld+json">
${schemaJson}
    </script>

    ${stylesheetHref ? `<link rel="stylesheet" href="${stylesheetHref}" />` : ''}
  </head>
  <body>
    <div id="root"></div>
    ${jsSrc ? `<script type="module" crossorigin src="${jsSrc}"></script>` : ''}
  </body>
</html>`;
}

// ═══════════════════════════════════════════════════════════════════
//  Main generator — called by postbuild.mjs
// ═══════════════════════════════════════════════════════════════════

export function generateStaticPages(distDir) {
  if (!existsSync(distDir)) {
    console.error('[generate-static-pages] dist/ not found at', distDir);
    process.exit(1);
  }

  // 1. Read the built index.html to extract CSS/JS/modulepreload references
  const builtIndexPath = resolve(distDir, 'index.html');
  if (!existsSync(builtIndexPath)) {
    console.error('[generate-static-pages] dist/index.html not found');
    return;
  }
  const builtHtml = readFileSync(builtIndexPath, 'utf8');

  const cssMatch = builtHtml.match(/<link rel="stylesheet"[^>]*href="([^"]+)"[^>]*\/?>/);
  const stylesheetHref = cssMatch ? cssMatch[1] : null;

  const jsMatch = builtHtml.match(/<script type="module"[^>]*src="([^"]+)"[^>]*><\/script>/);
  const jsSrc = jsMatch ? jsMatch[1] : null;

  const modulepreloads = [];
  const mpRegex = /<link rel="modulepreload"[^>]*\/?>/g;
  let mpMatch;
  while ((mpMatch = mpRegex.exec(builtHtml)) !== null) {
    modulepreloads.push(mpMatch[0]);
  }

  console.log('[generate-static-pages] CSS:', stylesheetHref);
  console.log('[generate-static-pages] JS:', jsSrc);
  console.log('[generate-static-pages] Modulepreloads:', modulepreloads.length);

  // 2. Extract data using robust safeEvalArr (same as postbuild.mjs)
  const srcDir = resolve(distDir, '..', 'src', 'data');
  const ipoStocks = extractStocksFromTs(resolve(srcDir, 'ipoData.ts'));
  const newsArticles = extractNewsFromTs(resolve(srcDir, 'newsData.ts'));
  const allProjects = extractProjectsFromTs(resolve(srcDir, 'cryptoData.ts'));
  const airdrops = allProjects.filter((p) => p.category === 'airdrop');

  console.log(`[generate-static-pages] Found ${ipoStocks.length} IPOs, ${newsArticles.length} news articles, ${airdrops.length} airdrops`);

  // 3. Build all routes
  const routes = [];

  // Homepage
  routes.push({
    path: '/',
    title: `${SITE_NAME} — ${SITE_TAGLINE}`,
    description: SITE_DESC,
    ogType: 'website',
    schemas: [
      {
        '@type': 'WebSite',
        '@id': `${SITE_ORIGIN}/#website`,
        url: SITE_ORIGIN,
        name: SITE_NAME,
        description: SITE_DESC,
        inLanguage: 'en-IN',
        potentialAction: {
          '@type': 'SearchAction',
          target: `${SITE_ORIGIN}/?q={search_term_string}`,
          'query-input': 'required name=search_term_string',
        },
      },
      {
        '@type': 'Organization',
        '@id': `${SITE_ORIGIN}/#organization`,
        name: SITE_NAME,
        url: SITE_ORIGIN,
        logo: { '@type': 'ImageObject', url: DEFAULT_OG_IMAGE },
        sameAs: ['https://twitter.com/pulsetrends'],
      },
    ],
  });

  // Static pages
  const staticPageDefs = [
    { path: '/ipo-analysis', title: `IPO Analysis - Latest IPO Reviews & Insights | ${SITE_NAME}`, desc: 'In-depth IPO analysis with company overviews, financial snapshots, AI scoring, and risk assessment for upcoming Indian and global IPOs.', breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'IPO Analysis', path: '/ipo-analysis' }] },
    { path: '/airdrops', title: `Crypto Airdrops - Latest Free Token Opportunities | ${SITE_NAME}`, desc: 'Track active and upcoming crypto airdrops. Eligibility guides, estimated values, farming strategies, and AI conviction scores.', breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Airdrops', path: '/airdrops' }] },
    { path: '/news', title: `Market News - Stock Market & Crypto Updates | ${SITE_NAME}`, desc: 'AI-analyzed market news with sentiment, impact scoring, bull/bear cases, and actionable insights for crypto and equity markets.', breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'News', path: '/news' }] },
    { path: '/about', title: `About Us - ${SITE_NAME} | IPO & Crypto Intelligence`, desc: `${SITE_NAME} is a financial intelligence platform delivering AI-powered analysis of IPOs, crypto airdrops, and market-moving news.`, breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'About', path: '/about' }] },
    { path: '/contact', title: `Contact Us - ${SITE_NAME}`, desc: `Get in touch with the ${SITE_NAME} team. For inquiries, feedback, support, or partnerships.`, breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Contact', path: '/contact' }] },
    { path: '/privacy-policy', title: `Privacy Policy - ${SITE_NAME}`, desc: `${SITE_NAME} privacy policy. How we collect, use, and protect your personal data.`, breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Privacy Policy', path: '/privacy-policy' }] },
    { path: '/terms', title: `Terms & Conditions - ${SITE_NAME}`, desc: `Terms and conditions governing your use of ${SITE_NAME}. Please read carefully.`, breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Terms & Conditions', path: '/terms' }] },
    { path: '/cookies', title: `Cookie Policy - ${SITE_NAME}`, desc: `${SITE_NAME} cookie policy. What cookies we use, why, and how to control them.`, breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Cookie Policy', path: '/cookies' }] },
  ];

  for (const p of staticPageDefs) {
    routes.push({ path: p.path, title: p.title, description: p.desc, ogType: 'website', breadcrumbs: p.breadcrumbs });
  }

  // IPO detail pages
  for (const stock of ipoStocks) {
    const stockSlug = `${slugify(stock.company)}-${stock.id}`;
    const stockPath = `/ipo-analysis/${stockSlug}`;
    routes.push({
      path: stockPath,
      title: `${stock.company} IPO Analysis | ${SITE_NAME}`,
      description: truncate(`${stock.company} IPO analysis with AI scoring (${stock.aiScores?.overall || ''}/100), risk assessment, and financial insights. ${stock.description || ''}`, 160),
      ogType: 'article',
      breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'IPO Analysis', path: '/ipo-analysis' }, { name: stock.company, path: stockPath }],
      schemas: [{
        '@type': 'Product',
        name: `${stock.company} IPO`,
        description: `${stock.company} IPO analysis with AI-powered scoring.`,
        url: canonical(stockPath),
        category: 'IPO',
      }],
    });
  }

  // News detail pages
  for (const article of newsArticles) {
    const articleSlug = `${slugify(article.headline)}-${article.id}`;
    const articlePath = `/news/${articleSlug}`;
    const pubDate = article.publishedAt ? article.publishedAt.split('T')[0] : new Date().toISOString().split('T')[0];
    routes.push({
      path: articlePath,
      title: `${article.headline} | ${SITE_NAME}`,
      description: article.metaDescription || article.headline,
      ogType: 'article',
      breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'News', path: '/news' }, { name: article.headline, path: articlePath }],
      schemas: [{
        '@type': 'NewsArticle',
        headline: article.headline,
        description: article.metaDescription || article.headline,
        datePublished: pubDate,
        dateModified: pubDate,
        author: { '@type': 'Person', name: 'Shiva Sandeep', url: SITE_ORIGIN },
        publisher: { '@type': 'Organization', name: SITE_NAME, logo: { '@type': 'ImageObject', url: DEFAULT_OG_IMAGE } },
        mainEntityOfPage: { '@type': 'WebPage', '@id': canonical(articlePath) },
      }],
    });
  }

  // Airdrop detail pages
  for (const airdrop of airdrops) {
    const airdropSlug = `${slugify(airdrop.name)}-${airdrop.id}`;
    const airdropPath = `/airdrops/${airdropSlug}`;
    routes.push({
      path: airdropPath,
      title: `${airdrop.name} Airdrop | ${SITE_NAME}`,
      description: truncate(airdrop.description || `${airdrop.name} crypto airdrop analysis.`, 160),
      ogType: 'website',
      breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Airdrops', path: '/airdrops' }, { name: airdrop.name, path: airdropPath }],
      schemas: [{
        '@type': 'Product',
        name: `${airdrop.name} Airdrop`,
        description: airdrop.description || `${airdrop.name} airdrop analysis.`,
        url: canonical(airdropPath),
        category: 'Airdrop',
      }],
    });
  }

  // Redirects for old/removed URLs
  const redirectRoutes = [
    '/east-texas-politics-mayoral-candidates-discuss-vision-for-tyler-ahead-of-runoff',
  ];

  for (const oldPath of redirectRoutes) {
    routes.push({
      path: oldPath,
      title: 'Redirecting...',
      description: 'This page has moved.',
      noindex: true,
      redirectTo: '/news',
    });
  }

  // 404 page
  routes.push({
    path: '/404',
    title: `Page Not Found | ${SITE_NAME}`,
    description: 'The page you are looking for does not exist.',
    noindex: true,
  });

  // 4. Generate HTML files
  let generated = 0;
  for (const route of routes) {
    const html = buildHtml({
      title: route.title,
      description: route.description || SITE_DESC,
      path: route.path,
      ogImage: DEFAULT_OG_IMAGE,
      ogType: route.ogType || 'website',
      noindex: route.noindex || false,
      schemas: route.schemas || [],
      breadcrumbs: route.breadcrumbs || [],
      stylesheetHref,
      jsSrc,
      modulepreloadLinks: modulepreloads,
      redirectTo: route.redirectTo,
    });

    let outputDir, outputFile;
    if (route.path === '/') {
      outputDir = distDir;
      outputFile = resolve(distDir, 'index.html');
    } else if (route.path === '/404') {
      outputDir = distDir;
      outputFile = resolve(distDir, '404.html');
    } else {
      const relativePath = route.path.replace(/^\//, '');
      outputDir = resolve(distDir, relativePath);
      outputFile = resolve(outputDir, 'index.html');
    }

    if (!existsSync(outputDir)) {
      mkdirSync(outputDir, { recursive: true });
    }
    writeFileSync(outputFile, html, 'utf8');
    generated++;
  }

  console.log(`[generate-static-pages] Generated ${generated} static HTML pages`);
  return generated;
}

// Run directly
const distDir = resolve('dist');
generateStaticPages(distDir);
