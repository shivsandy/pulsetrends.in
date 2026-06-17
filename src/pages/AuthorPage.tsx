import { useParams, Link } from 'react-router-dom';
import { Mail, Send, ArrowLeft, BookOpen, TrendingUp, Coins, Newspaper, ExternalLink, Trophy, Film, Monitor, BarChart3, AlertTriangle, Globe } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { SITE, canonical } from '../seo/config';
import { personSchema } from '../seo/schema';
import { newsArticles, type NewsArticle } from '../data/newsData';
import { getArticleSlug } from '../components/ArticleReader';

const AUTHORS: Record<string, {
  name: string; role: string; bio: string; avatar: string;
  telegram: string; twitter: string; email: string;
  credentials: string[];
  expertise: string[];
}> = {
  'shiva-sandeep': {
    name: 'Shiva Sandeep',
    role: 'Software Analyst',
    bio: 'Software Analyst covering cryptocurrency markets, IPO analysis, and financial technology. Provides AI-powered market intelligence and data-driven investment research at PulseTrends.',
    avatar: '/author-avatar.jpg',
    telegram: 'its_terabyte',
    twitter: 'pulsetrends',
    email: 'pulsetrendsin@gmail.com',
    credentials: [
      'Software Analysis & Engineering',
      'Cryptocurrency Market Research',
      'Financial Data Analysis',
      'AI-Powered Investment Intelligence',
    ],
    expertise: ['Cryptocurrency', 'IPO Analysis', 'Market Research', 'Financial Technology', 'Data Analysis'],
  },
};

export default function AuthorPage() {
  const { slug = 'shiva-sandeep' } = useParams();
  const author = AUTHORS[slug];

  if (!author) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center">
        <PageSeo meta={{
          path: `/author/${slug}`,
          title: 'Author Not Found | PulseTrends',
          description: 'The author profile you are looking for does not exist.',
          noindex: true,
          ogType: 'profile',
        }} />
        <h1 className="text-2xl font-bold text-surface-white">Author Not Found</h1>
        <p className="text-surface-600 mt-2">The author you are looking for does not exist.</p>
        <Link to="/" className="inline-flex items-center gap-2 mt-6 text-brand hover:text-brand-light">
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </Link>
      </div>
    );
  }

  const path = `/author/${slug}`;
  const authorArticles = newsArticles.filter((a) => a.author === author.name || !a.author);
  const schema = personSchema(author.name, canonical(path), author.role, author.bio);

  return (
    <>
      <PageSeo
        meta={{
          path,
          title: `${author.name} — Author Profile | PulseTrends`,
          description: `${author.name} is a ${author.role.toLowerCase()} at PulseTrends. ${author.bio.slice(0, 120)}`,
          ogType: 'profile',
          ogImage: `${SITE.origin}/author-avatar.jpg`,
          schema: { '@context': 'https://schema.org', '@graph': [schema] },
          keywords: `${author.name}, ${author.role}, PulseTrends, ${author.expertise.join(', ')}`,
        }}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Authors', path: '/author' },
          { name: author.name, path: `/author/${slug}` },
        ]}
      />

      <div className="max-w-4xl mx-auto animate-fade-in">
        <Breadcrumbs items={[
          { name: 'Home', path: '/' },
          { name: 'Authors', path: '/author' },
          { name: author.name },
        ]} />

        <div className="bg-surface-100 border border-surface-300/60 rounded-xl p-6 mb-8">
          <div className="flex flex-col sm:flex-row items-start gap-5">
            <div className="w-20 h-20 rounded-full bg-surface-300 border-2 border-surface-400 overflow-hidden shrink-0 flex items-center justify-center">
              <img
                src={author.avatar}
                alt={author.name}
                width={80}
                height={80}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                  (e.target as HTMLImageElement).parentElement!.innerHTML = '<svg class="w-8 h-8 text-surface-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
                }}
              />
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-surface-white">{author.name}</h1>
              <p className="text-[13px] text-brand-light font-medium mt-0.5">{author.role}</p>
              <p className="text-[13px] text-surface-700 mt-2 leading-relaxed">{author.bio}</p>

              <div className="flex flex-wrap items-center gap-3 mt-4">
                <a
                  href={`https://t.me/${author.telegram}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-sky-500/10 border border-sky-500/30 text-[12px] font-medium text-sky-400 hover:bg-sky-500/20 transition-colors"
                >
                  <Send className="w-3.5 h-3.5" />
                  @{author.telegram}
                </a>
                <a
                  href={`https://twitter.com/${author.twitter}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-surface-200 border border-surface-300/60 text-[12px] font-medium text-surface-700 hover:text-surface-white transition-colors"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  @{author.twitter}
                </a>
                <a
                  href={`mailto:${author.email}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-surface-200 border border-surface-300/60 text-[12px] font-medium text-surface-700 hover:text-surface-white transition-colors"
                >
                  <Mail className="w-3.5 h-3.5" />
                  Email
                </a>
              </div>
            </div>
          </div>
        </div>

        {author.credentials.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-bold text-surface-white mb-3">Credentials & Expertise</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {author.credentials.map((c, i) => (
                <div key={i} className="bg-surface-100 border border-surface-300/60 rounded-lg px-4 py-3">
                  <p className="text-[13px] text-surface-800">{c}</p>
                </div>
              ))}
            </div>
            <div className="flex flex-wrap gap-1.5 mt-3">
              {author.expertise.map((e, i) => (
                <span key={i} className="px-2.5 py-1 rounded-md bg-brand-muted border border-brand-border text-[11px] font-medium text-brand-light">
                  {e}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-surface-300/40 pt-8">
          <h2 className="text-lg font-bold text-surface-white mb-4">
            <BookOpen className="w-4 h-4 inline mr-2 text-brand-light" />
            Articles by {author.name}
          </h2>

          {authorArticles.length === 0 ? (
            <p className="text-[13px] text-surface-600">No articles published yet.</p>
          ) : (
            <div className="space-y-3">
              {authorArticles.map((article) => (
                <AuthorArticleCard key={article.id} article={article} />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function AuthorArticleCard({ article }: { article: NewsArticle }) {
  const slug = getArticleSlug(article);
  const categoryIcon = article.category === 'crypto' ? <Coins className="w-3.5 h-3.5" /> :
    article.category === 'ipo' ? <TrendingUp className="w-3.5 h-3.5" /> :
    article.category === 'sports' ? <Trophy className="w-3.5 h-3.5" /> :
    article.category === 'entertainment' ? <Film className="w-3.5 h-3.5" /> :
    article.category === 'technology' ? <Monitor className="w-3.5 h-3.5" /> :
    article.category === 'economy' ? <BarChart3 className="w-3.5 h-3.5" /> :
    article.category === 'breaking' ? <AlertTriangle className="w-3.5 h-3.5" /> :
    article.category === 'trending' ? <Globe className="w-3.5 h-3.5" /> :
    <Newspaper className="w-3.5 h-3.5" />;

  return (
    <Link
      to={`/news/${slug}`}
      className="block bg-surface-100 border border-surface-300/60 rounded-lg p-4 hover:border-surface-500 transition-all duration-200"
    >
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-surface-200 border border-surface-300/60 flex items-center justify-center shrink-0 mt-0.5">
          {categoryIcon}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-[14px] font-semibold text-surface-white leading-snug">{article.headline}</h3>
          {article.subheadline && (
            <p className="text-[12px] text-surface-700 mt-0.5 line-clamp-2">{article.subheadline}</p>
          )}
          <div className="flex items-center gap-3 mt-2 text-[11px] text-surface-600">
            <span className="capitalize">{article.category}</span>
            {article.publishedAt && (
              <span>{new Date(article.publishedAt).toLocaleDateString()}</span>
            )}
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium uppercase ${
              article.sentiment === 'bullish' ? 'bg-success-muted text-success' :
              article.sentiment === 'bearish' ? 'bg-danger-muted text-danger' :
              'bg-surface-200 text-surface-600'
            }`}>
              {article.sentiment}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
