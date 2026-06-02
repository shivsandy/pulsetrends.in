import { readFileSync, writeFileSync, copyFileSync, existsSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';

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
    console.warn('[postbuild] parse error:', e.message);
    return [];
  }
}

function buildDynamicRoutes() {
  const routes = [];
  for (const stock of extractStocksFromTs(resolve('src/data/ipoData.ts'))) {
    const slug = `${slugify(stock.company)}-${stock.id}`;
    routes.push({ path: `/ipo-analysis/${slug}`, priority: '0.7', changefreq: 'daily' });
  }
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
  return `User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\nDisallow: /staging/\n\nSitemap: ${SITE_ORIGIN}/sitemap.xml\nSitemap: ${SITE_ORIGIN}/news-sitemap.xml\n`;
}

function main() {
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
        console.log(`[postbuild] Copied ${entry.name} to dist/`);
      }
    }
  }

  // Copy assets/ to dist/assets for the deploy step (already built by Vite)
  if (existsSync(assetsDistDir)) {
    console.log('[postbuild] Assets directory found, ensuring all assets are in place');
  }

  // SPA fallback: copy index.html to 404.html for GitHub Pages
  const indexPath = resolve(distDir, 'index.html');
  if (existsSync(indexPath)) {
    copyFileSync(indexPath, resolve(distDir, '404.html'));
    console.log('[postbuild] Wrote dist/404.html (SPA fallback)');
  }

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
}

main();
