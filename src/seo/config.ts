export const SITE = {
  name: 'PulseTrends',
  shortName: 'PulseTrends',
  domain: 'pulsetrends.in',
  origin: 'https://pulsetrends.in',
  twitter: '@pulsetrends',
  description:
    'AI-powered intelligence for IPOs, crypto airdrops, and market-moving news. Deep analysis, risk metrics, and actionable insights for modern investors.',
  tagline: 'IPO, Crypto & Market Intelligence',
  locale: 'en_IN',
} as const;

export function canonical(path: string): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  const trimmed = clean.length > 1 && clean.endsWith('/') ? clean.slice(0, -1) : clean;
  return `${SITE.origin}${trimmed}`;
}

export function slugify(input: string): string {
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
