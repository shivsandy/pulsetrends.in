/**
 * generate-report.mjs
 * Generates a professional Microsoft Word (.docx) audit report for pulsetrends.in
 */

import {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, WidthType, BorderStyle,
  PageNumber, Footer, Header, PageBreak, TableOfContents,
  LevelFormat, TabStopPosition, TabStopType, convertInchesToTwip,
  ShadingType, ImageRun
} from 'docx';
import { writeFileSync, existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

// ── Date ──────────────────────────────────────────────────────────
const AUDIT_DATE = 'June 2, 2026';
const SITE_URL = 'https://pulsetrends.in';
const SITE_NAME = 'PulseTrends';

// ── Color palette ──────────────────────────────────────────────────
const COLORS = {
  brand: 'E01A4F',
  darkBg: '1A1A1E',
  lightBg: 'F5F5F7',
  white: 'FFFFFF',
  black: '000000',
  gray: '71717A',
  darkText: '1A1A1E',
  success: '10B981',
  warning: 'F59E0B',
  danger: 'EF4444',
  info: '06B6D4',
  green: '22C55E',
  red: 'EF4444',
};

// ── Score data ─────────────────────────────────────────────────────
const SCORES = {
  technicalSeo: 82,
  onPageSeo: 85,
  contentQuality: 55,
  ux: 68,
  mobileOptimization: 75,
  eeat: 60,
  authorityTrust: 45,
  security: 55,
  overallSeo: 72,
  adsenseProbability: 38,
  organicGrowthPotential: 55,
  revenuePotential: 4.5,
  overallHealth: 65,
};

// ── Helper functions ───────────────────────────────────────────────
function headerCell(text, width) {
  return new TableCell({
    children: [new Paragraph({
      children: [new TextRun({ text, bold: true, color: COLORS.white, size: 18 })],
      alignment: AlignmentType.CENTER,
      spacing: { before: 40, after: 40 },
    })],
    width: { size: width, type: WidthType.PERCENTAGE },
    shading: { fill: COLORS.darkBg, type: ShadingType.SOLID },
  });
}

function dataCell(text, width, opts = {}) {
  const runs = [];
  if (opts.bold) {
    runs.push(new TextRun({ text: String(text), bold: true, size: 18, color: opts.color || COLORS.darkText }));
  } else {
    runs.push(new TextRun({ text: String(text), size: 18, color: opts.color || COLORS.darkText }));
  }
  return new TableCell({
    children: [new Paragraph({
      children: runs,
      alignment: opts.align || AlignmentType.LEFT,
      spacing: { before: 30, after: 30 },
    })],
    width: { size: width, type: WidthType.PERCENTAGE },
    shading: opts.shading ? { fill: opts.shading, type: ShadingType.SOLID } : undefined,
  });
}

function dataRow(cells, widths, alt = false) {
  return new TableRow({
    children: cells.map((c, i) => {
      const isEvenRow = i % 2 === 0;
      return dataCell(c, widths[i], {
        align: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
        shading: alt ? COLORS.lightBg : undefined,
      });
    }),
    ...(alt ? { shading: { fill: COLORS.lightBg, type: ShadingType.SOLID } } : {}),
  });
}

function makeTable(headers, rows, widths) {
  return new Table({
    rows: [
      new TableRow({ children: headers.map((h, i) => headerCell(h, widths[i])) }),
      ...rows.map((row, idx) => dataRow(row, widths, idx % 2 === 1)),
    ],
    width: { size: 100, type: WidthType.PERCENTAGE },
  });
}

function heading(level, text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, size: level === 1 ? 36 : level === 2 ? 30 : 24, color: COLORS.darkText })],
    heading: level === 1 ? HeadingLevel.HEADING_1 : level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3,
    spacing: { before: level === 1 ? 400 : 300, after: 200 },
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, size: opts.size || 20, color: opts.color || COLORS.darkText, ...(opts.bold ? { bold: true } : {}) })],
    spacing: { before: 60, after: 60 },
    alignment: opts.align || AlignmentType.LEFT,
  });
}

function spacer() {
  return new Paragraph({ spacing: { before: 100, after: 100 }, children: [] });
}

function scoreBar(score, label) {
  const barColor = score >= 80 ? COLORS.green : score >= 60 ? COLORS.warning : COLORS.red;
  const barLen = Math.round(score / 10);
  const bar = '█'.repeat(barLen) + '░'.repeat(10 - barLen);
  return para(`${label}: ${score}/100  ${bar}`, { size: 20 });
}

// ── Build Document ─────────────────────────────────────────────────

async function buildReport() {
  const doc = new Document({
    title: `Complete Website Audit Report - ${SITE_NAME}`,
    description: `Professional SEO, AdSense, UX, Security & Revenue Audit for ${SITE_URL}`,
    creator: 'PulseTrends Audit Engine',
    styles: {
      default: {
        document: {
          run: { font: 'Calibri', size: 20, color: COLORS.darkText },
          paragraph: { spacing: { after: 120 } },
        },
      },
    },
    sections: [
      // ═══════════════════ COVER PAGE ═══════════════════
      {
        children: [
          spacer(), spacer(), spacer(), spacer(), spacer(),
          new Paragraph({
            children: [new TextRun({ text: 'COMPLETE WEBSITE AUDIT REPORT', bold: true, size: 52, color: COLORS.brand })],
            alignment: AlignmentType.CENTER,
          }),
          spacer(),
          new Paragraph({
            children: [new TextRun({ text: SITE_URL, size: 36, color: COLORS.gray })],
            alignment: AlignmentType.CENTER,
          }),
          spacer(),
          new Paragraph({
            children: [new TextRun({ text: 'SEO  ·  ADSENSE  ·  UX  ·  SECURITY  ·  REVENUE', size: 24, color: COLORS.gray })],
            alignment: AlignmentType.CENTER,
          }),
          spacer(), spacer(), spacer(), spacer(), spacer(), spacer(),
          new Paragraph({
            children: [new TextRun({ text: `Audit Date: ${AUDIT_DATE}`, size: 22, color: COLORS.gray })],
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({
            children: [new TextRun({ text: 'Prepared for: PulseTrends Management', size: 22, color: COLORS.gray })],
            alignment: AlignmentType.CENTER,
          }),
          new Paragraph({
            children: [new TextRun({ text: 'CONFIDENTIAL', size: 20, bold: true, color: COLORS.brand })],
            alignment: AlignmentType.CENTER,
          }),
        ],
      },

      // ═══════════════════ TABLE OF CONTENTS ═══════════════════
      {
        children: [
          new Paragraph({ children: [new TextRun({ text: 'TABLE OF CONTENTS', bold: true, size: 36, color: COLORS.darkText })], spacing: { before: 400, after: 300 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 1: Full Website Crawl', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 2: Technical SEO Audit', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 3: Mobile SEO Audit', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 4: On-Page SEO Audit', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 5: Content Quality Analysis', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 6: E-E-A-T Audit', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 7: User Experience (UX) Audit', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 8: Google AdSense Approval Analysis', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 9: SEO Scorecard', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 10: Revenue Optimization', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 11: Security Audit', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 12: Competitor Benchmarking', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 13: Top 20 Recommendations', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Section 14: Executive Summary & Action Plan', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Master Findings Table', size: 22 })], spacing: { before: 100, after: 60 } }),
          new Paragraph({ children: [new TextRun({ text: 'Final Scores', size: 22 })], spacing: { before: 100, after: 60 } }),
        ],
      },

      // ═══════════════════ SECTION 1: CRAWL ═══════════════════
      {
        children: [
          heading(1, 'Section 1: Full Website Crawl'),
          para('A complete crawl of pulsetrends.in was performed on June 2, 2026. The site is a React SPA hosted on GitHub Pages with static HTML prerendering for all routes.'),
          spacer(),
          heading(2, 'Crawl Statistics'),
          makeTable(
            ['Metric', 'Value'],
            [
              ['Total URLs Discovered', '164'],
              ['Total Indexable URLs', '163'],
              ['Total Non-Indexable URLs', '1 (/404)'],
              ['Total Internal Links', '210+'],
              ['Total External Links', '12'],
              ['Total Images', '12 (Unsplash CDN)'],
              ['Total Redirects', '0 (all direct 200)'],
              ['Total Static Pages', '155'],
              ['Total Categories', '4 (IPO, Airdrops, News, Pages)'],
              ['Total Dynamic Routes', '146 (85 IPOs + 4 News + 41 Airdrops)'],
              ['Sitemap URLs', '154'],
              ['News Sitemap URLs', '4'],
            ],
            [50, 50]
          ),
          spacer(),
          heading(2, 'Page Status Summary'),
          makeTable(
            ['URL', 'Status', 'Size', 'Load Time'],
            [
              ['/ (Homepage)', '200 OK', '3.8 KB', '0.049s'],
              ['/ipo-analysis/', '200 OK', '3.4 KB', '0.049s'],
              ['/news/', '200 OK', '3.3 KB', '0.053s'],
              ['/airdrops/', '200 OK', '3.3 KB', '0.049s'],
              ['/about/', '200 OK', '3.3 KB', '0.034s'],
              ['/contact/', '200 OK', '3.0 KB', '0.036s'],
              ['/privacy-policy/', '200 OK', '3.1 KB', '0.050s'],
              ['/terms/', '200 OK', '3.0 KB', '0.052s'],
              ['/cookies/', '200 OK', '3.0 KB', '0.041s'],
              ['/ipo-analysis/* (85 IPOs)', '200 OK', '~3.4 KB', '~0.05s'],
              ['/news/* (4 articles)', '200 OK', '~3.3 KB', '~0.05s'],
              ['/airdrops/* (41 airdrops)', '200 OK', '~3.3 KB', '~0.05s'],
            ],
            [55, 15, 15, 15]
          ),
        ],
      },

      // ═══════════════════ SECTION 2: TECHNICAL SEO ═══════════════════
      {
        children: [
          heading(1, 'Section 2: Technical SEO Audit'),
          heading(2, 'Crawlability'),
          makeTable(
            ['Factor', 'Status', 'Notes'],
            [
              ['robots.txt', '✅ Present', 'Allows all crawlers, disallows /admin, /api/, /staging/'],
              ['XML Sitemap', '✅ Present', '154 URLs in sitemap.xml + 4 news URLs in news-sitemap.xml'],
              ['SPA Fallback', '✅ Fixed', 'All subpages now return HTTP 200 via static HTML prerendering'],
              ['Orphan Pages', '✅ None', 'All pages linked in navigation, sitemap, and footer'],
              ['Crawl Budget', '✅ Optimized', '~3KB per page, fast CDN delivery via GitHub Pages'],
            ],
            [20, 15, 65]
          ),
          spacer(),
          heading(2, 'Indexability'),
          makeTable(
            ['Factor', 'Status', 'Notes'],
            [
              ['Index Status', '✅ All pages indexable', 'All pages return index,follow (except /404)'],
              ['Canonical Tags', '✅ Present', 'Each page has self-referencing canonical URL'],
              ['Noindex Pages', '1 (/404)', 'Properly set to noindex,nofollow'],
              ['Duplicate Content', '✅ None detected', 'Unique content per page'],
              ['Pagination', 'N/A', 'No pagination implemented'],
            ],
            [20, 20, 60]
          ),
          spacer(),
          heading(2, 'URL Structure'),
          makeTable(
            ['Factor', 'Rating', 'Notes'],
            [
              ['URL Length', '✅ Good', 'Short, descriptive slugs (e.g., /ipo-analysis/flipkart-44)'],
              ['Keyword Usage', '✅ Good', 'URLs contain company names and section paths'],
              ['Slug Optimization', '⚠️ Fair', 'Slugs use hyphens but include IDs (e.g., -44)'],
              ['Dynamic Parameters', '✅ None', 'Clean static URLs throughout'],
              ['Trailing Slash', '✅ Consistent', 'All URLs end with /'],
            ],
            [20, 15, 65]
          ),
          spacer(),
          heading(2, 'HTTP Status Analysis'),
          makeTable(
            ['Issue', 'Count', 'Notes'],
            [
              ['404 Errors', '0', 'All pages now return 200'],
              ['Soft 404 Errors', '0', 'No soft 404s detected'],
              ['500 Errors', '0', 'Server responds correctly'],
              ['Broken Internal Links', '0', 'All navigation links verified'],
              ['Redirect Chains', '0', 'No chain of redirects'],
              ['301 Redirects', '0 (direct)', 'Non-trailing-slash → trailing-slash (expected)'],
            ],
            [30, 15, 55]
          ),
          spacer(),
          heading(2, 'Core Web Vitals (Estimated)'),
          para('Note: Exact Core Web Vitals require field data from Google Search Console / PageSpeed Insights. Estimates based on page structure:'),
          makeTable(
            ['Metric', 'Desktop Estimate', 'Mobile Estimate', 'Status'],
            [
              ['LCP (Largest Contentful Paint)', '< 1.5s', '< 2.5s', '⚠️ Needs testing'],
              ['INP (Interaction to Next Paint)', '< 100ms', '< 150ms', '✅ Good (SPA)'],
              ['CLS (Cumulative Layout Shift)', '< 0.05', '< 0.05', '✅ Good'],
            ],
            [30, 20, 20, 30]
          ),
          spacer(),
          heading(2, 'Performance Audit'),
          makeTable(
            ['Issue', 'Severity', 'Affected URLs', 'Recommendation'],
            [
              ['JS Bundle 428KB', '⚠️ High', 'All pages', 'Code-split main bundle, lazy-load heavy dependencies'],
              ['No WebP images', '⚠️ Medium', 'All image pages', 'Use <picture> with WebP sources for Unsplash images'],
              ['Render-blocking CSS', '✅ OK', 'None', 'CSS is critical-path inlined via Vite'],
              ['No CDN for fonts', '⚠️ Low', 'All pages', 'Self-host Inter font instead of Google Fonts CDN'],
              ['No service worker', '⚠️ Low', 'All pages', 'Add service worker for offline cache and faster repeat loads'],
              ['No preload for hero images', '⚠️ Medium', 'News articles', 'Add <link rel="preload"> for above-fold images'],
            ],
            [25, 15, 20, 40]
          ),
        ],
      },

      // ═══════════════════ SECTION 3: MOBILE ═══════════════════
      {
        children: [
          heading(1, 'Section 3: Mobile SEO Audit'),
          para('The site uses a responsive design with Tailwind CSS and passes basic mobile usability checks.'),
          spacer(),
          makeTable(
            ['Factor', 'Rating', 'Notes'],
            [
              ['Mobile Responsiveness', '✅ Good', 'Fluid layout with responsive breakpoints'],
              ['Touch Elements', '✅ Good', 'Buttons and links have adequate touch targets'],
              ['Mobile Navigation', '✅ Good', 'Hamburger menu on mobile, sticky header'],
              ['Mobile Layout Stability', '✅ Good', 'No CLS issues detected'],
              ['Viewport Configuration', '✅ Present', 'viewport-fit=cover meta tag'],
              ['Font Sizing', '✅ Good', 'Readable text sizes on mobile'],
              ['Mobile Page Speed', '⚠️ Fair', '428KB JS bundle impacts mobile load times'],
            ],
            [25, 15, 60]
          ),
          spacer(),
          heading(2, 'Mobile SEO Score', { size: 24 }),
          scoreBar(SCORES.mobileOptimization, 'Mobile Optimization'),
        ],
      },

      // ═══════════════════ SECTION 4: ON-PAGE SEO ═══════════════════
      {
        children: [
          heading(1, 'Section 4: On-Page SEO Audit'),
          heading(2, 'Meta Tags'),
          makeTable(
            ['Page', 'Title', 'Meta Description', 'Status'],
            [
              ['Homepage', 'PulseTrends — IPO, Crypto & Market Intelligence', 'AI-powered intelligence for IPOs...', '✅ Optimal'],
              ['/ipo-analysis/', 'IPO Analysis - Latest IPO Reviews & Insights | PulseTrends', 'In-depth IPO analysis with...', '✅ Optimal'],
              ['/news/', 'Market News - Stock Market & Crypto Updates | PulseTrends', 'AI-analyzed market news with...', '✅ Optimal'],
              ['/airdrops/', 'Crypto Airdrops - Latest Free Token Opportunities | PulseTrends', 'Track active and upcoming crypto...', '✅ Optimal'],
              ['/about/', 'About Us - PulseTrends | IPO & Crypto Intelligence', 'PulseTrends is a financial...', '✅ Optimal'],
              ['/contact/', 'Contact Us - PulseTrends', 'Get in touch with the PulseTrends...', '✅ Optimal'],
              ['/privacy-policy/', 'Privacy Policy - PulseTrends', 'PulseTrends privacy policy...', '✅ Optimal'],
              ['/terms/', 'Terms & Conditions - PulseTrends', 'Terms and conditions governing...', '✅ Optimal'],
              ['/cookies/', 'Cookie Policy - PulseTrends', 'PulseTrends cookie policy...', '✅ Optimal'],
              ['IPO Detail pages', 'Company Name IPO Analysis | PulseTrends', 'Dynamic per-IPO description', '✅ Good'],
              ['News Detail pages', 'Headline | PulseTrends', 'Dynamic per-article description', '✅ Good'],
            ],
            [22, 30, 30, 18]
          ),
          spacer(),
          heading(2, 'Schema Markup Audit'),
          makeTable(
            ['Schema Type', 'Present', 'Pages'],
            [
              ['WebSite', '✅', 'All pages'],
              ['Organization', '✅', 'All pages'],
              ['WebPage', '✅', 'All pages'],
              ['BreadcrumbList', '✅', 'All pages'],
              ['NewsArticle', '✅', 'News detail pages (4)'],
              ['Product', '✅', 'IPO & Airdrop detail pages'],
              ['SearchAction', '✅', 'Homepage'],
              ['FAQPage', '❌', 'Not implemented'],
              ['Person (Author)', '✅', 'News articles & About page'],
            ],
            [30, 15, 55]
          ),
          spacer(),
          heading(2, 'Open Graph & Twitter Cards'),
          para('All pages have complete Open Graph tags (og:title, og:description, og:url, og:type, og:image, og:locale) and Twitter Card tags (summary_large_image).'),
          spacer(),
          heading(2, 'Heading Structure'),
          para('Heading hierarchy is implemented correctly in the React components: H1 → H2 → H3. Each page has a single H1 tag. Headings are rendered client-side via JavaScript.'),
          spacer(),
          heading(2, 'Image SEO'),
          para('Images are loaded from Unsplash CDN with alt text attributes. Alt text is somewhat generic ("a pile of gold bitcoins sitting on top of each other") and could be more descriptive for SEO.'),
        ],
      },

      // ═══════════════════ SECTION 5: CONTENT QUALITY ═══════════════════
      {
        children: [
          heading(1, 'Section 5: Content Quality Analysis'),
          para('Content quality is the weakest area for this site. The site has significant volume (85+ IPO analyses, 4 news articles, 41 airdrop analyses) but quality concerns around originality and depth.'),
          spacer(),
          heading(2, 'Content Inventory'),
          makeTable(
            ['Section', 'Page Count', 'Avg. Word Count', 'Quality Score'],
            [
              ['IPO Analysis (list)', '1', '~200', '60/100'],
              ['IPO Detail pages', '85+', '~800-1500', '55/100'],
              ['News Articles', '4', '~1500-2500', '70/100'],
              ['Airdrops (list)', '1', '~150', '50/100'],
              ['Airdrop Detail', '41', '~300-500', '55/100'],
              ['Policy Pages', '5', '~500-1000', '85/100'],
              ['About / Contact', '2', '~300-500', '75/100'],
            ],
            [25, 15, 20, 15]
          ),
          spacer(),
          heading(2, 'AI Content Detection'),
          para('Several content patterns suggest AI-assisted generation:'),
          para('• Formulaic structure: "Bullish Factors / Bearish Factors / Risk Analysis" sections appear in all news articles', { size: 20 }),
          para('• Repetitive phrasing across IPO analyses', { size: 20 }),
          para('• Lack of original quotes, interviews, or first-hand research', { size: 20 }),
          para('• Generic descriptions that lack specific, unique insights', { size: 20 }),
          spacer(),
          heading(2, 'Readability Analysis'),
          para('Content uses complex financial terminology which may be challenging for general audiences. Flesch Reading Ease score is estimated at 40-50 (College level). News articles are better structured with key takeaways, but IPO analyses are very dense.'),
          spacer(),
          heading(2, 'Content Gap Analysis'),
          para('Recommended new content categories:'),
          para('• IPO vs Listed Performance analysis (tracking IPOs post-listing)', { size: 20 }),
          para('• Weekly/Monthly Market Roundup articles', { size: 20 }),
          para('• How-To guides for IPO investing and airdrop participation', { size: 20 }),
          para('• Glossary of financial terms for beginners', { size: 20 }),
          para('• Company-specific deep-dive series with original analysis', { size: 20 }),
        ],
      },

      // ═══════════════════ SECTION 6: E-E-A-T ═══════════════════
      {
        children: [
          heading(1, 'Section 6: E-E-A-T Audit'),
          makeTable(
            ['Factor', 'Score', 'Notes'],
            [
              ['Experience', '45/100', 'Limited first-hand trading/investing experience shown'],
              ['Expertise', '55/100', 'Editor named (Shiva Sandeep) but credentials not detailed'],
              ['Authoritativeness', '40/100', 'New site, limited backlinks, no industry recognition'],
              ['Trustworthiness', '60/100', 'Policy pages present, contact info available'],
            ],
            [25, 15, 60]
          ),
          spacer(),
          heading(2, 'E-E-A-T Score'),
          scoreBar(SCORES.eeat, 'E-E-A-T'),
          spacer(),
          para('Improvements made: Named editor with bio on About page, editorial standards documented, corrections policy added. Still needs: detailed author credentials, external recognition/citations, and more transparent content sourcing.'),
        ],
      },

      // ═══════════════════ SECTION 7: UX ═══════════════════
      {
        children: [
          heading(1, 'Section 7: User Experience (UX) Audit'),
          makeTable(
            ['Factor', 'Rating', 'Notes'],
            [
              ['Navigation', '✅ Good', 'Sticky header, clear menu, breadcrumbs on subpages'],
              ['Footer Navigation', '✅ Good', 'All pages linked in organized footer'],
              ['Search Functionality', '❌ Missing', 'No search bar — users cannot find specific content'],
              ['Accessibility', '⚠️ Fair', 'Skip-to-content link present, but no ARIA landmarks'],
              ['Color Contrast', '✅ Good', 'High contrast dark theme, WCAG AA compliant'],
              ['Keyboard Navigation', '⚠️ Fair', 'Basic keyboard support works but not fully audited'],
              ['Print Styles', '❌ Missing', 'No print CSS — pages will not print well'],
              ['Loading States', '✅ Good', 'Skeleton/spinner shown during lazy loading'],
              ['Mobile Navigation', '✅ Good', 'Responsive hamburger menu'],
            ],
            [25, 15, 60]
          ),
          spacer(),
          heading(2, 'UX Score'),
          scoreBar(SCORES.ux, 'User Experience'),
        ],
      },

      // ═══════════════════ SECTION 8: ADSENSE ═══════════════════
      {
        children: [
          heading(1, 'Section 8: Google AdSense Approval Analysis'),
          para('This section evaluates pulsetrends.in against current Google AdSense approval standards as of June 2026.'),
          spacer(),
          makeTable(
            ['Factor', 'Status', 'Score'],
            [
              ['Content Quality', '⚠️ Needs Improvement', '40/100'],
              ['Content Volume', '✅ Sufficient', '75/100'],
              ['Originality', '⚠️ AI-generated patterns detected', '35/100'],
              ['Privacy Policy', '✅ Present & comprehensive', '90/100'],
              ['About Us', '✅ Present with named editor', '80/100'],
              ['Contact Page', '✅ Present with email', '80/100'],
              ['Terms & Conditions', '✅ Present & thorough', '90/100'],
              ['Cookie Policy', '✅ Present & compliant', '85/100'],
              ['Site Navigation', '✅ Good', '75/100'],
              ['Professional Design', '✅ Excellent dark theme', '85/100'],
              ['Traffic Readiness', '⚠️ No visible traffic data', '30/100'],
              ['Copyright Notice', '✅ Present in footer', '70/100'],
            ],
            [30, 40, 30]
          ),
          spacer(),
          heading(2, 'AdSense Approval Probability'),
          para(`AdSense Approval Probability: ${SCORES.adsenseProbability}% — HIGH REJECTION RISK`, { bold: true, color: COLORS.red }),
          spacer(),
          heading(2, 'Exact Reasons for Rejection Risk'),
          para('1. Content appears AI-generated — formulaic structures, lack of original research, no cited experts or interviews', { size: 20 }),
          para('2. Insufficient E-E-A-T signals — author credentials not verified, no external recognition', { size: 20 }),
          para('3. Thin content on IPO pages — many listings have minimal unique analysis', { size: 20 }),
          para('4. No visible traffic — cannot demonstrate existing user engagement', { size: 20 }),
          para('5. Financial niche — high scrutiny category requiring expert-level content', { size: 20 }),
          spacer(),
          heading(2, 'Exact Fixes Required Before Applying'),
          para('1. Rewrite all article content with natural, original narrative — remove template structures', { size: 20 }),
          para('2. Add author credentials (degrees, certifications, professional experience) to each byline', { size: 20 }),
          para('3. Include original research, data analysis, quotes from industry experts', { size: 20 }),
          para('4. Build traffic through SEO and social media before applying', { size: 20 }),
          para('5. Add disclaimers to all financial analysis pages', { size: 20 }),
        ],
      },

      // ═══════════════════ SECTION 9: SEO SCORECARD ═══════════════════
      {
        children: [
          heading(1, 'Section 9: SEO Scorecard'),
          spacer(),
          scoreBar(SCORES.technicalSeo, 'Technical SEO'),
          scoreBar(SCORES.onPageSeo, 'On-Page SEO'),
          scoreBar(SCORES.contentQuality, 'Content Quality'),
          scoreBar(SCORES.ux, 'User Experience (UX)'),
          scoreBar(SCORES.mobileOptimization, 'Mobile Optimization'),
          scoreBar(SCORES.eeat, 'E-E-A-T'),
          scoreBar(SCORES.authorityTrust, 'Authority & Trust'),
          scoreBar(SCORES.security, 'Security'),
          spacer(),
          heading(2, 'Overall SEO Score'),
          scoreBar(SCORES.overallSeo, 'Overall SEO'),
          spacer(),
          makeTable(
            ['Metric', 'Estimated Value'],
            [
              ['Google Ranking Potential', 'Low-Medium (niche queries only)'],
              ['Organic Traffic Potential', 'Low (1,000-5,000 monthly visitors max at current state)'],
              ['Competitive Strength', 'Weak — needs differentiation and authority building'],
              ['Growth Opportunity', 'Medium — niche is growing but competitive'],
            ],
            [40, 60]
          ),
        ],
      },

      // ═══════════════════ SECTION 10: REVENUE ═══════════════════
      {
        children: [
          heading(1, 'Section 10: Revenue Optimization'),
          heading(2, 'AdSense Revenue Potential'),
          makeTable(
            ['Metric', 'Estimate'],
            [
              ['Estimated RPM (Page Revenue per 1K Views)', '$1-3 (financial niche)'],
              ['Ad Placement Opportunities', 'Below article content, sidebar, between sections'],
              ['Revenue Growth Potential', 'Medium — traffic-dependent'],
            ],
            [40, 60]
          ),
          spacer(),
          heading(2, 'Affiliate Marketing Opportunities'),
          para('Recommended affiliate programs for this niche:'),
          para('• Brokerage platforms (Zerodha, Groww, Angel Broking) for IPO investors', { size: 20 }),
          para('• Crypto exchanges (Coinbase, Binance) for airdrop/crypto audience', { size: 20 }),
          para('• Financial data tools (TradingView, Screener.in)', { size: 20 }),
          para('• Online broker introductory offers', { size: 20 }),
          spacer(),
          heading(2, 'Revenue Potential Score'),
          scoreBar(Math.round(SCORES.revenuePotential * 10), 'Revenue Potential'),
        ],
      },

      // ═══════════════════ SECTION 11: SECURITY ═══════════════════
      {
        children: [
          heading(1, 'Section 11: Security Audit'),
          makeTable(
            ['Security Issue', 'Risk Level', 'Recommendation'],
            [
              ['Missing CSP header', '⚠️ High', 'Implement Content-Security-Policy header via GitHub Pages _headers or switch to Cloudflare'],
              ['Missing X-Frame-Options', '⚠️ Medium', 'Add DENY value — clickjacking risk'],
              ['Missing X-Content-Type-Options', '⚠️ Medium', 'Add nosniff value — MIME sniffing risk'],
              ['Missing Referrer-Policy', '⚠️ Low', 'Add strict-origin-when-cross-origin'],
              ['HSTS present (but low max-age)', '⚠️ Low', 'Increase max-age to 63072000 for preload'],
              ['CORS wide open (*)', '⚠️ Low', 'Restrict to specific origins if needed'],
              ['No directory listing', '✅ Secure', 'Not exposed'],
              ['security.txt present', '✅ Good', 'Properly configured'],
              ['SSL/HTTPS', '✅ Good', 'Valid certificate via GitHub Pages'],
              ['Server info disclosure', '⚠️ Low', 'Server: GitHub.com header visible'],
            ],
            [32, 15, 53]
          ),
          spacer(),
          heading(2, 'Security Score'),
          scoreBar(SCORES.security, 'Security'),
        ],
      },

      // ═══════════════════ SECTION 12: COMPETITOR ═══════════════════
      {
        children: [
          heading(1, 'Section 12: Competitor Benchmarking'),
          para('The site competes in the Indian financial content space. Key competitors include:'),
          spacer(),
          makeTable(
            ['Competitor', 'Content', 'SEO', 'E-E-A-T', 'Monetization'],
            [
              ['Chittorgarh.com', 'Strong', 'Excellent', 'Medium', 'AdSense + Affiliate'],
              ['IPOWatch.in', 'Medium', 'Good', 'Low', 'AdSense'],
              ['Investobull.com', 'Medium', 'Good', 'Medium', 'AdSense + Affiliate'],
              ['PulseTrends', 'Medium', 'Improving', 'Low-Medium', 'Early stage'],
            ],
            [25, 20, 20, 20, 15]
          ),
          spacer(),
          heading(2, 'Competitive Gaps'),
          para('• Lack of IPO performance tracking data (GMP, listing gains history)', { size: 20 }),
          para('• No user reviews or community engagement features', { size: 20 }),
          para('• Lower content depth compared to established competitors', { size: 20 }),
          para('• No mobile app or newsletter', { size: 20 }),
        ],
      },

      // ═══════════════════ SECTION 13: RECOMMENDATIONS ═══════════════════
      {
        children: [
          heading(1, 'Section 13: Top 20 Recommendations'),
          spacer(),
          heading(2, 'Top 10 SEO Improvements'),
          para('1. Rewrite article content with original, human-written analysis (highest impact)', { size: 20 }),
          para('2. Build high-quality backlinks through guest posting and partnerships', { size: 20 }),
          para('3. Implement FAQ schema on news articles for rich results', { size: 20 }),
          para('4. Reduce JS bundle size from 428KB (code-split, tree-shake, lazy-load)', { size: 20 }),
          para('5. Add search functionality for better user engagement and internal linking', { size: 20 }),
          para('6. Implement weekly/monthly market roundup content series', { size: 20 }),
          para('7. Add author detail pages with credentials and article lists', { size: 20 }),
          para('8. Create pillar pages for IPO analysis and airdrop guides', { size: 20 }),
          para('9. Optimize images with WebP format and descriptive alt text', { size: 20 }),
          para('10. Add internal linking between related IPO and news articles', { size: 20 }),
          spacer(),
          heading(2, 'Top 10 Technical Fixes'),
          para('1. Implement CSP header (fixes security gap)', { size: 20 }),
          para('2. Add X-Frame-Options DENY header', { size: 20 }),
          para('3. Add X-Content-Type-Options nosniff header', { size: 20 }),
          para('4. Add service worker for caching and offline support', { size: 20 }),
          para('5. Self-host fonts to reduce external DNS lookups', { size: 20 }),
          para('6. Add preload for hero images on news articles', { size: 20 }),
          para('7. Implement print CSS styles', { size: 20 }),
          para('8. Add RSS/Atom feed for content syndication', { size: 20 }),
          para('9. Add 301 redirects from non-www to www (or vice versa)', { size: 20 }),
          para('10. Submit to Google Search Console and Bing Webmaster Tools', { size: 20 }),
        ],
      },

      // ═══════════════════ SECTION 14: EXECUTIVE ═══════════════════
      {
        children: [
          heading(1, 'Section 14: Executive Summary & Action Plan'),
          heading(2, 'Executive Summary'),
          para('PulseTrends.in is a newly redesigned financial intelligence platform focused on IPOs, crypto airdrops, and market news. The site has made significant progress in technical SEO by implementing static HTML prerendering, proper meta tags, structured data, and comprehensive schema markup. All pages now return HTTP 200 with complete metadata.'),
          spacer(),
          para('However, the site faces critical challenges in content quality (AI-generation patterns), authority/E-E-A-T signals, and AdSense approval readiness. The financial niche is highly competitive and requires expert-level content that demonstrates original research and human expertise.'),
          spacer(),
          heading(2, 'Critical Issues'),
          para('1. Content reads as AI-generated — template structures and formulaic language throughout', { bold: true, size: 20 }),
          para('2. Insufficient E-E-A-T — author credentials not detailed, no external validation', { bold: true, size: 20 }),
          para('3. Security headers missing — CSP, X-Frame-Options, X-Content-Type-Options not served', { bold: true, size: 20 }),
          para('4. No search functionality — users cannot find specific content easily', { bold: true, size: 20 }),
          spacer(),
          heading(2, '30-Day Action Plan'),
          para('Week 1: Rewrite all 4 news articles with original narrative — remove template structures', { size: 20 }),
          para('Week 1: Implement CSP, X-Frame-Options, X-Content-Type-Options headers', { size: 20 }),
          para('Week 2: Add author detail page with full credentials and experience', { size: 20 }),
          para('Week 2: Add search functionality (Fuse.js client-side search)', { size: 20 }),
          para('Week 3: Create 2-3 pillar content pieces (IPO guide, airdrop guide)', { size: 20 }),
          para('Week 3: Submit to Google Search Console and Bing Webmaster Tools', { size: 20 }),
          para('Week 4: Build 3-5 backlinks through guest posting', { size: 20 }),
          spacer(),
          heading(2, '60-Day Action Plan'),
          para('30-day items + implement WebP images, add FAQ schema, create weekly market roundup series, optimize JS bundle, add RSS feed, set up social media profiles and content promotion', { size: 20 }),
          spacer(),
          heading(2, '90-Day Action Plan'),
          para('60-day items + launch weekly newsletter, build affiliate content strategy, reach 50+ pages of high-quality original content, apply for AdSense after content rewrite', { size: 20 }),
        ],
      },

      // ═══════════════════ MASTER FINDINGS TABLE ═══════════════════
      {
        children: [
          heading(1, 'Master Findings Table'),
          spacer(),
          makeTable(
            ['Issue', 'Severity', 'Affected URL', 'Impact', 'Fix', 'SEO Gain', 'AdSense Impact'],
            [
              ['AI-generated content patterns', 'Critical', 'All content pages', 'Zero AdSense approval, low trust', 'Rewrite with original narrative', 'High', 'Critical'],
              ['Missing security headers', 'High', 'All pages', 'Security risk, lower trust', 'Add CSP, X-Frame-Options, etc.', 'Low', 'Medium'],
              ['No search functionality', 'Medium', 'All pages', 'Poor UX, reduced engagement', 'Add Fuse.js search', 'Medium', 'Low'],
              ['Large JS bundle (428KB)', 'Medium', 'All pages', 'Slow load on slow connections', 'Code-split and tree-shake', 'Medium', 'Low'],
              ['No FAQ schema', 'Low', 'News articles', 'Missed rich results', 'Add FAQPage schema', 'Medium', 'Low'],
              ['No RSS feed', 'Low', 'All pages', 'Missed syndication', 'Add /feed.xml', 'Low', 'Low'],
              ['Generic image alt text', 'Medium', 'News/Articles', 'Poor image SEO', 'Write descriptive alt text', 'Medium', 'Low'],
              ['No service worker', 'Low', 'All pages', 'No offline capability', 'Add service worker', 'Low', 'Low'],
            ],
            [22, 12, 18, 20, 22, 12, 14]
          ),
        ],
      },

      // ═══════════════════ FINAL SCORES ═══════════════════
      {
        children: [
          heading(1, 'Final Scores Summary'),
          spacer(),
          scoreBar(SCORES.overallHealth, 'Overall Website Health'),
          scoreBar(SCORES.technicalSeo, 'Technical SEO'),
          scoreBar(SCORES.onPageSeo, 'On-Page SEO'),
          scoreBar(SCORES.contentQuality, 'Content Quality'),
          scoreBar(SCORES.ux, 'User Experience'),
          scoreBar(SCORES.eeat, 'E-E-A-T'),
          scoreBar(SCORES.security, 'Security'),
          scoreBar(SCORES.mobileOptimization, 'Mobile Optimization'),
          scoreBar(SCORES.overallSeo, 'Overall SEO'),
          spacer(),
          makeTable(
            ['Metric', 'Value'],
            [
              ['Overall Website Health Score', `${SCORES.overallHealth}/100`],
              ['Technical SEO Score', `${SCORES.technicalSeo}/100`],
              ['On-Page SEO Score', `${SCORES.onPageSeo}/100`],
              ['Content Quality Score', `${SCORES.contentQuality}/100`],
              ['UX Score', `${SCORES.ux}/100`],
              ['E-E-A-T Score', `${SCORES.eeat}/100`],
              ['Security Score', `${SCORES.security}/100`],
              ['Mobile Score', `${SCORES.mobileOptimization}/100`],
              ['Overall SEO Score', `${SCORES.overallSeo}/100`],
              ['AdSense Approval Probability', `${SCORES.adsenseProbability}%`],
              ['Organic Growth Potential', `${SCORES.organicGrowthPotential}%`],
              ['Revenue Potential Score', `${SCORES.revenuePotential}/10`],
            ],
            [40, 60]
          ),
          spacer(),
          new Paragraph({
            children: [new TextRun({ text: '— End of Report —', size: 24, color: COLORS.gray, italics: true })],
            alignment: AlignmentType.CENTER,
            spacing: { before: 400 },
          }),
          new Paragraph({
            children: [new TextRun({ text: `Generated on ${AUDIT_DATE} for ${SITE_URL}`, size: 18, color: COLORS.gray })],
            alignment: AlignmentType.CENTER,
          }),
        ],
      },
    ],
  });

  // Generate document
  const buffer = await Packer.toBuffer(doc);
  const outputPath = resolve('pulse.docx');
  writeFileSync(outputPath, buffer);
  console.log(`[report] Generated ${outputPath} (${(buffer.length / 1024).toFixed(1)} KB)`);
}

buildReport().catch(console.error);
