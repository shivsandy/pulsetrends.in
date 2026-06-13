import { readFileSync, writeFileSync, copyFileSync, existsSync, readdirSync, mkdirSync, statSync } from 'node:fs';
import { resolve, dirname } from 'node:path';

const SITE_ORIGIN = 'https://pulsetrends.in';

const STATIC_ROUTES = [
  { path: '/', priority: '1.0', changefreq: 'daily' },
  { path: '/ipo-analysis', priority: '0.9', changefreq: 'daily' },
  { path: '/airdrops', priority: '0.9', changefreq: 'daily' },
  { path: '/news', priority: '0.9', changefreq: 'hourly' },
  { path: '/about', priority: '0.5', changefreq: 'monthly' },
  { path: '/contact', priority: '0.4', changefreq: 'monthly' },
  { path: '/privacy-policy', priority: '0.3', changefreq: 'yearly' },
  { path: '/terms', priority: '0.3', changefreq: 'yearly' },
  { path: '/cookies', priority: '0.3', changefreq: 'yearly' },
  { path: '/learn', priority: '0.7', changefreq: 'weekly' },
  { path: '/learn/what-is-cryptocurrency', priority: '0.8', changefreq: 'monthly' },
  { path: '/learn/what-is-bitcoin', priority: '0.8', changefreq: 'monthly' },
  { path: '/learn/what-is-ethereum', priority: '0.8', changefreq: 'monthly' },
  { path: '/learn/what-is-ipo', priority: '0.8', changefreq: 'monthly' },
  { path: '/learn/how-to-buy-cryptocurrency-in-india', priority: '0.8', changefreq: 'monthly' },
  { path: '/learn/how-to-apply-for-ipo', priority: '0.8', changefreq: 'monthly' },
  { path: '/author/shiva-sandeep', priority: '0.6', changefreq: 'weekly' },
];

function slugify(s) {
  return s.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

function extractStocksFromTs(tsPath) {
  if (!existsSync(tsPath)) return [];
  const src = readFileSync(tsPath, 'utf8');
  const match = src.match(/export\s+const\s+ipoStocks\s*:\s*IPOStock\[\]\s*=\s*(\[[\s\S]*?\n\];)/);
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

function extractArticlesFromTs(tsPath) {
  if (!existsSync(tsPath)) return [];
  const src = readFileSync(tsPath, 'utf8');
  const match = src.match(/export\s+const\s+newsArticles\s*:\s*NewsArticle\[\]\s*=\s*(\[[\s\S]*?\n\];)/);
  if (!match) return [];
  return safeEvalArr(match[1]);
}

function extractAirdropsFromTs(tsPath) {
  if (!existsSync(tsPath)) return [];
  const src = readFileSync(tsPath, 'utf8');
  const match = src.match(/export\s+const\s+airdropProjects\s*:\s*AirdropProject\[\]\s*=\s*(\[[\s\S]*?\n\];)/);
  if (!match) return [];
  return safeEvalArr(match[1], AIRDROP_SCORES_HELPER);
}

function safeEvalArr(arrLiteral, helpers = '') {
  const cleaned = arrLiteral
    .replace(/;\s*$/, '')
    .replace(/\s+as\s+(const|[A-Za-z_$][\w$]*(\[\])?)/g, '')
    .replace(/:\s*IPOStock\[\]/g, '')
    .replace(/:\s*CryptoProject\[\]/g, '')
    .replace(/:\s*NewsArticle\[\]/g, '')
    .replace(/:\s*AirdropProject\[\]/g, '');
  try {
    const parsed = Function(`"use strict";${helpers} return (${cleaned});`)();
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    console.warn('[postbuild] parse error:', e.message);
    return [];
  }
}

// Helper: airdrop scores function (needed by airdropData.ts)
const AIRDROP_SCORES_HELPER = `
  function s(t,i,p,m,c,tk,a) {
    var o = Math.round(t*0.20 + i*0.15 + p*0.20 + m*0.15 + c*0.10 + tk*0.10 + a*0.10);
    return { team:t, investors:i, product:p, market:m, community:c, token:tk, airdrop:a, overall:o };
  }
`;

function buildDynamicRoutes() {
  const routes = [];
  for (const stock of extractStocksFromTs(resolve('src/data/ipoData.ts'))) {
    const slug = `${slugify(stock.company)}-${stock.id}`;
    routes.push({ path: `/ipo-analysis/${slug}`, priority: '0.7', changefreq: 'daily' });
  }
  // Airdrops from airdropData.ts (primary source, new pipeline)
  for (const project of extractAirdropsFromTs(resolve('src/data/airdropData.ts'))) {
    const slug = `${slugify(project.name)}-${project.id}`;
    routes.push({ path: `/airdrops/${slug}`, priority: '0.6', changefreq: 'daily' });
  }
  // Also include airdrops from cryptoData.ts (legacy) for backwards compatibility
  for (const project of extractProjectsFromTs(resolve('src/data/cryptoData.ts'))) {
    if (project.category !== 'airdrop') continue;
    const slug = `${slugify(project.name)}-${project.id}`;
    routes.push({ path: `/airdrops/${slug}`, priority: '0.6', changefreq: 'daily' });
  }
  for (const article of extractArticlesFromTs(resolve('src/data/newsData.ts'))) {
    const slug = `${slugify(article.headline)}-${article.id}`;
    routes.push({ path: `/news/${slug}`, priority: '0.6', changefreq: 'weekly' });
  }
  return routes;
}

function buildSitemap(routes) {
  const today = new Date().toISOString().split('T')[0];
  const urls = routes
    .map(
      (r) =>
        `  <url>\n    <loc>${SITE_ORIGIN}${r.path}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>${r.changefreq}</changefreq>\n    <priority>${r.priority}</priority>\n  </url>`,
    )
    .join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`;
}

function buildNewsSitemap() {
  const articles = extractArticlesFromTs(resolve('src/data/newsData.ts'));
  const today = new Date().toISOString().split('T')[0];
  const urls = articles
    .map((a) => {
      const slug = `${slugify(a.headline)}-${a.id}`;
      const pubDate = a.publishedAt ? a.publishedAt.split('T')[0] : today;
      const keywords = [a.primaryKeyword, ...(a.secondaryKeywords || []), ...(a.tags || [])]
        .filter(Boolean)
        .slice(0, 10)
        .join(', ');
      return `  <url>\n    <loc>${SITE_ORIGIN}/news/${slug}</loc>\n    <lastmod>${pubDate}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.6</priority>\n    <news:news>\n      <news:publication>\n        <news:name>PulseTrends</news:name>\n        <news:language>en</news:language>\n      </news:publication>\n      <news:publication_date>${pubDate}</news:publication_date>\n      <news:title>${a.headline.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')}</news:title>\n      <news:keywords>${keywords.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')}</news:keywords>\n    </news:news>\n  </url>`;
    })
    .join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n${urls}\n</urlset>\n`;
}

function buildRobots() {
  return `User-agent: *
Allow: /

Disallow: /admin/
Disallow: /api/
Disallow: /staging/

Sitemap: ${SITE_ORIGIN}/sitemap.xml
Sitemap: ${SITE_ORIGIN}/news-sitemap.xml
`;
}

function buildHeaders() {
  return `/*
  strict-transport-security: max-age=63072000; includeSubDomains; preload
  x-content-type-options: nosniff
  x-frame-options: DENY
  referrer-policy: strict-origin-when-cross-origin
  permissions-policy: camera=(), microphone=(), geolocation=(), interest-cohort=(), payment=(), usb=(), magnetometer=(), gyroscope=()
  content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://pagead2.googlesyndication.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' https://images.unsplash.com https://*.unsplash.com https://www.google-analytics.com https://www.googletagmanager.com https://pagead2.googlesyndication.com https://googleads.g.doubleclick.net data: blob:; connect-src 'self' https://api.unsplash.com https://www.google-analytics.com https://www.googletagmanager.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
`;
}

async function main() {
  const distDir = resolve('dist');
  if (!existsSync(distDir)) {
    console.error('[postbuild] dist/ not found, run vite build first');
    process.exit(1);
  }

  const publicDir = resolve('public');
  const assetsDistDir = resolve(distDir, 'assets');

  // Copy public/ assets (e.g., favicon, og-image) into dist/ for deployment
  if (existsSync(publicDir)) {
    const publicEntries = readdirSync(publicDir, { withFileTypes: true });
    for (const entry of publicEntries) {
      const srcPath = resolve(publicDir, entry.name);
      const destPath = resolve(distDir, entry.name);
      if (!entry.isDirectory() && !existsSync(destPath)) {
        copyFileSync(srcPath, destPath);
        console.log(`[postbuild] Copied public/${entry.name} to dist/`);
      }
    }
  }

  // Copy root-level files needed for GitHub Pages (CNAME, .nojekyll)
  const rootFiles = ['CNAME', '.nojekyll'];
  const projectRoot = resolve(distDir, '..');
  for (const f of rootFiles) {
    const srcPath = resolve(projectRoot, f);
    const destPath = resolve(distDir, f);
    if (existsSync(srcPath) && !existsSync(destPath)) {
      copyFileSync(srcPath, destPath);
      console.log(`[postbuild] Copied ${f} to dist/`);
    }
  }

  // Copy ipoComprehensiveAnalysis.json for runtime fetch (avoids 34MB bundle)
  const analysisSrc = resolve(projectRoot, 'src/data/ipoComprehensiveAnalysis.json');
  const analysisDestDir = resolve(distDir, 'data');
  if (existsSync(analysisSrc)) {
    if (!existsSync(analysisDestDir)) mkdirSync(analysisDestDir, { recursive: true });
    copyFileSync(analysisSrc, resolve(analysisDestDir, 'ipoComprehensiveAnalysis.json'));
    const size = (statSync(analysisSrc).size / 1024 / 1024).toFixed(1);
    console.log(`[postbuild] Copied analysis data (${size}MB) to dist/data/`);
  }

  // Generate static HTML pages for all routes (fixes 404 & adds meta tags)
  console.log('[postbuild] Generating static HTML pages...');
  const { generateStaticPages } = await import('./generate-static-pages.mjs');
  generateStaticPages(distDir);

  // Generate all routes for sitemap
  const allRoutes = [...STATIC_ROUTES, ...buildDynamicRoutes()];
  
  // Generate sitemap.xml
  const sitemap = buildSitemap(allRoutes);
  writeFileSync(resolve(distDir, 'sitemap.xml'), sitemap, 'utf8');
  console.log(`[postbuild] Wrote dist/sitemap.xml (${allRoutes.length} URLs)`);

  // Generate news-sitemap.xml for Google News
  const newsSitemap = buildNewsSitemap();
  writeFileSync(resolve(distDir, 'news-sitemap.xml'), newsSitemap, 'utf8');
  console.log(`[postbuild] Wrote dist/news-sitemap.xml (${allRoutes.filter(r => r.path.startsWith('/news/')).length} news URLs)`);

  // Generate robots.txt
  const robots = buildRobots();
  writeFileSync(resolve(distDir, 'robots.txt'), robots, 'utf8');
  console.log('[postbuild] Wrote dist/robots.txt');

  // Generate _headers for security headers (GitHub Pages format)
  const headers = buildHeaders();
  writeFileSync(resolve(distDir, '_headers'), headers, 'utf8');
  console.log('[postbuild] Wrote dist/_headers (security headers)');

  // Also copy to 404.html directory for GitHub Pages SPA fallback coverage
  // This ensures security headers apply even on 404 fallback paths

  // Generate .well-known/security.txt
  const securityWellKnownDir = resolve(distDir, '.well-known');
  if (!existsSync(securityWellKnownDir)) {
    mkdirSync(securityWellKnownDir, { recursive: true });
  }
  const securityTxt = `# Security Disclosure Policy\n# PulseTrends (https://pulsetrends.in)\n\nContact: mailto:pulsetrendsin@gmail.com\nPreferred-Languages: en, hi\nPolicy: https://pulsetrends.in/.well-known/security.txt\nExpires: 2027-06-02T00:00:00.000Z\nCanonical: https://pulsetrends.in/.well-known/security.txt\n`;
  writeFileSync(resolve(securityWellKnownDir, 'security.txt'), securityTxt, 'utf8');
  console.log('[postbuild] Wrote dist/.well-known/security.txt');
}

main();
