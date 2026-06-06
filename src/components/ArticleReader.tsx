import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  CalendarDays,
  Clock,
  ExternalLink,
  Lightbulb,
  ListChecks,
  Quote,
  Target,
} from 'lucide-react';
import Badge from './Badge';
import { newsArticles, type NewsArticle } from '../data/newsData';
import { slugify } from '../seo/config';

type AiTab = 'bull' | 'bear' | 'neutral';
type ArticleImage = NewsArticle['images'][number];

const impactConfig: Record<string, 'danger' | 'warning' | 'info'> = {
  high: 'danger',
  medium: 'warning',
  low: 'info',
};

const FALLBACK_IMAGE: ArticleImage = {
  url: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1400&q=80',
  alt: 'Market data on a digital screen',
  attribution: 'Photo via Unsplash',
  category: 'markets',
};

function getHeroImage(article: NewsArticle): ArticleImage {
  const valid = (article.images || []).filter((i) => i && i.url);
  if (valid.length > 0) return valid[0];
  return FALLBACK_IMAGE;
}

function getReadingTime(article: NewsArticle): number {
  const text = [
    article.executiveSummary,
    article.marketBackground,
    article.detailedAnalysis,
    article.expertInsights,
    article.outlook,
    article.conclusion,
  ].join(' ');
  return Math.max(3, Math.ceil(text.split(/\s+/).filter(Boolean).length / 220));
}

export function getArticleSlug(article: NewsArticle): string {
  return `${slugify(article.headline)}-${article.id}`;
}

export function findArticleBySlug(slug: string): NewsArticle | undefined {
  return newsArticles.find((a) => getArticleSlug(a) === slug);
}

interface ArticleReaderProps {
  article: NewsArticle;
}

export default function ArticleReader({ article }: ArticleReaderProps) {
  const navigate = useNavigate();
  const [aiTab, setAiTab] = useState<AiTab>('bull');
  const heroImage = getHeroImage(article);
  const ai = article.aiAnalysis;
  const financialMetrics = article.financialMetrics;

  return (
    <article className="animate-fade-in max-w-6xl mx-auto">
      <button
        type="button"
        onClick={() => navigate('/news')}
        className="mb-4 inline-flex items-center gap-2 text-[13px] text-surface-700 hover:text-surface-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to news
      </button>

      <div className="overflow-hidden rounded-xl border border-surface-300/60 bg-surface-100">
        {heroImage?.url && (
          <div className="relative h-72 sm:h-[420px] overflow-hidden">
            <img
              src={heroImage.url}
              alt={heroImage.alt || article.headline}
              width={1400}
              height={788}
              decoding="async"
              className="h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-surface-100 via-surface-100/30 to-transparent" />
            {heroImage.attribution && (
              <span className="absolute bottom-3 right-3 rounded bg-surface-100/85 px-2 py-0.5 text-[10px] text-surface-700">
                {heroImage.attribution}
              </span>
            )}
          </div>
        )}

        <div className="px-5 pb-7 pt-5 sm:px-8">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <Badge variant="default" size="sm">{article.category || 'markets'}</Badge>
            <Badge variant={impactConfig[article.impact] || 'info'} size="sm">
              {article.impact || 'medium'} impact
            </Badge>
            <span className="inline-flex items-center gap-1 text-[12px] text-surface-600">
              <CalendarDays className="h-3.5 w-3.5" />
              {article.publishedAt ? new Date(article.publishedAt).toLocaleDateString() : 'Latest'}
            </span>
            <span className="text-[12px] text-surface-600 inline-flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" /> {getReadingTime(article)} min read
            </span>
          </div>

          {/* Author */}
          <div className="mt-4 flex items-center gap-3">
            <img
              src="/author-avatar.jpg"
              alt="Shiva Sandeep"
              width={40}
              height={40}
              className="w-10 h-10 rounded-full object-cover border-2 border-surface-300"
            />
            <div>
              <p className="text-[13px] font-semibold text-surface-white">
                {article.author || 'Shiva Sandeep'}
              </p>
              <div className="flex items-center gap-2 text-[11px] text-surface-600">
                <span>Analyst</span>
                {article.telegram && (
                  <a
                    href={`https://t.me/${article.telegram}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sky-400 hover:text-sky-300 transition-colors"
                  >
                    <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                    </svg>
                    @{article.telegram}
                  </a>
                )}
              </div>
            </div>
          </div>

          <h1 className="max-w-4xl text-3xl font-bold leading-tight tracking-tight text-surface-white sm:text-[42px]">
            {article.headline}
          </h1>
          {article.subheadline && (
            <p className="mt-3 max-w-3xl text-[16px] leading-relaxed text-surface-700">
              {article.subheadline}
            </p>
          )}

          {(article.relatedCoins?.length > 0 || article.relatedStocks?.length > 0) && (
            <div className="mt-4 flex flex-wrap items-center gap-1.5">
              <span className="mr-1 text-[11px] uppercase tracking-wider text-surface-600">Related</span>
              {[...(article.relatedCoins || []), ...(article.relatedStocks || [])].map((item) => (
                <span key={item} className="rounded border border-surface-300/60 bg-surface-200 px-2 py-0.5 font-mono text-[11px] text-surface-800">
                  {item}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div className="space-y-6">
          {article.keyHighlights?.length > 0 && (
            <section className="rounded-lg border border-surface-300/50 bg-surface-100 p-5">
              <h2 className="mb-3 text-[15px] font-bold text-surface-white">Key Takeaways</h2>
              <div className="grid gap-2 sm:grid-cols-2">
                {article.keyHighlights.slice(0, 6).map((item, index) => (
                  <div key={index} className="flex items-start gap-2 rounded-md bg-surface-200/45 p-3">
                    <ListChecks className="mt-0.5 h-4 w-4 shrink-0 text-brand-light" />
                    <p className="text-[13px] leading-relaxed text-surface-800">{item}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="space-y-5 rounded-lg border border-surface-300/50 bg-surface-100 p-5 sm:p-6">
            {article.executiveSummary && (
              <div>
                <h2 className="mb-2 text-xl font-bold text-surface-white">Summary</h2>
                <p className="text-[15px] leading-8 text-surface-800">{article.executiveSummary}</p>
              </div>
            )}
            {article.marketBackground && (
              <div>
                <h2 className="mb-2 text-xl font-bold text-surface-white">Market Context</h2>
                <p className="text-[15px] leading-8 text-surface-800">{article.marketBackground}</p>
              </div>
            )}
            {article.detailedAnalysis && (
              <div>
                <h2 className="mb-2 text-xl font-bold text-surface-white">Analysis</h2>
                <p className="text-[15px] leading-8 text-surface-800">{article.detailedAnalysis}</p>
              </div>
            )}
            {article.expertInsights && (
              <div className="rounded-lg border-l-4 border-brand bg-surface-200/35 p-4">
                <Quote className="mb-2 h-4 w-4 text-brand-light" />
                <p className="text-[14px] italic leading-7 text-surface-800">{article.expertInsights}</p>
              </div>
            )}
          </section>

          {financialMetrics && financialMetrics.headers.length > 0 && (
            <section className="rounded-lg border border-surface-300/50 bg-surface-100 p-5">
              <h2 className="mb-3 flex items-center gap-2 text-xl font-bold text-surface-white">
                <BarChart3 className="h-5 w-5 text-brand-light" />
                {financialMetrics.tableCaption || 'Market Metrics'}
              </h2>
              <div className="overflow-x-auto rounded-lg border border-surface-300/40">
                <table className="w-full text-[13px]">
                  <thead>
                    <tr className="bg-surface-200/70">
                      {financialMetrics.headers.map((header) => (
                        <th key={header} className="border-b border-surface-300/40 px-3 py-2 text-left font-semibold text-surface-900">{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {financialMetrics.rows.map((row, rowIndex) => (
                      <tr key={rowIndex} className="border-b border-surface-300/20 last:border-0">
                        {row.map((cell, cellIndex) => (
                          <td key={cellIndex} className="px-3 py-2 text-surface-800">{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <section className="grid gap-4 sm:grid-cols-2">
            {article.risks?.length > 0 && (
              <div className="rounded-lg border border-danger-border/40 bg-danger-muted/30 p-4">
                <h2 className="mb-2 flex items-center gap-2 text-[15px] font-bold text-danger">
                  <AlertTriangle className="h-4 w-4" />
                  Risks
                </h2>
                <ul className="space-y-2">
                  {article.risks.map((risk, index) => (
                    <li key={index} className="text-[13px] leading-relaxed text-surface-800">{risk}</li>
                  ))}
                </ul>
              </div>
            )}
            {article.opportunities?.length > 0 && (
              <div className="rounded-lg border border-success-border/40 bg-success-muted/30 p-4">
                <h2 className="mb-2 flex items-center gap-2 text-[15px] font-bold text-success">
                  <Lightbulb className="h-4 w-4" />
                  Opportunities
                </h2>
                <ul className="space-y-2">
                  {article.opportunities.map((item, index) => (
                    <li key={index} className="text-[13px] leading-relaxed text-surface-800">{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          {ai && (
            <section className="rounded-lg border border-surface-300/50 bg-surface-100 p-5">
              <h2 className="mb-3 flex items-center gap-2 text-xl font-bold text-surface-white">
                <Target className="h-5 w-5 text-brand-light" />
                Investment Lens
              </h2>
              <div className="mb-3 flex gap-1" role="tablist" aria-label="Investment lens">
                {(['bull', 'bear', 'neutral'] as AiTab[]).map((tab) => (
                  <button
                    type="button"
                    key={tab}
                    role="tab"
                    aria-selected={aiTab === tab}
                    onClick={() => setAiTab(tab)}
                    className={`rounded-md px-3 py-1.5 text-[12px] font-medium capitalize transition-all ${
                      aiTab === tab
                        ? tab === 'bull' ? 'bg-success text-white' : tab === 'bear' ? 'bg-danger text-white' : 'bg-surface-400 text-white'
                        : 'bg-surface-200 text-surface-600 hover:text-surface-800'
                    }`}
                  >
                    {tab === 'bull' ? 'Bull Case' : tab === 'bear' ? 'Bear Case' : 'Neutral'}
                  </button>
                ))}
              </div>
              <p className="text-[14px] leading-7 text-surface-800">
                {aiTab === 'bull' ? ai.bullCase : aiTab === 'bear' ? ai.bearCase : ai.neutralCase}
              </p>
              {ai.probabilityWeightedOutlook && (
                <p className="mt-3 border-t border-surface-300/40 pt-3 text-[13px] text-surface-700">
                  <span className="font-semibold text-surface-900">Outlook:</span> {ai.probabilityWeightedOutlook}
                </p>
              )}
            </section>
          )}

          {(article.outlook || article.conclusion) && (
            <section className="rounded-lg border border-surface-300/50 bg-surface-100 p-5">
              {article.outlook && <p className="mb-4 text-[15px] leading-8 text-surface-800">{article.outlook}</p>}
              {article.conclusion && <p className="text-[15px] leading-8 text-surface-800">{article.conclusion}</p>}
            </section>
          )}

          {article.sourcesReferenced?.length > 0 && (
            <section className="border-t border-surface-300/50 pt-4">
              <h2 className="mb-2 text-[13px] font-semibold uppercase tracking-wider text-surface-600">Sources Referenced</h2>
              <ul className="space-y-1">
                {article.sourcesReferenced.map((source, index) => (
                  <li key={index} className="flex items-start gap-1.5 text-[12px] text-surface-600">
                    <ExternalLink className="mt-0.5 h-3 w-3 shrink-0" />
                    {source}
                  </li>
                ))}
              </ul>
              <p className="mt-4 text-[11px] italic leading-relaxed text-surface-500">
                This PulseTrends story is AI-assisted and based on cited source material. It is informational content, not financial advice.
              </p>
            </section>
          )}
        </div>

        <aside className="space-y-3">
          <h2 className="text-[13px] font-semibold uppercase tracking-wider text-surface-600">More Stories</h2>
          {newsArticles
            .filter((a) => a.id !== article.id)
            .slice(0, 4)
            .map((item) => {
              const image = getHeroImage(item);
              return (
                <Link
                  key={item.id}
                  to={`/news/${getArticleSlug(item)}`}
                  className="group flex w-full gap-3 rounded-lg border border-surface-300/50 bg-surface-100 p-2 text-left transition-colors hover:border-surface-500"
                >
                  <img
                    src={image.url}
                    alt={image.alt || item.headline}
                    width={80}
                    height={64}
                    loading="lazy"
                    decoding="async"
                    className="h-16 w-20 shrink-0 rounded-md object-cover"
                  />
                  <div>
                    <p className="text-[11px] uppercase tracking-wider text-surface-600">{item.category || 'markets'}</p>
                    <p className="line-clamp-3 text-[12px] font-semibold leading-snug text-surface-900 group-hover:text-brand-light">{item.headline}</p>
                  </div>
                </Link>
              );
            })}
        </aside>
      </div>
    </article>
  );
}
