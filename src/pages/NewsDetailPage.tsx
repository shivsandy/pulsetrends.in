import { Link, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import ArticleReader, { findArticleBySlug } from '../components/ArticleReader';
import { canonical } from '../seo/config';
import { newsArticleSchema } from '../seo/schema';
import { newsArticles } from '../data/newsData';

export default function NewsDetailPage() {
  const { slug = '' } = useParams();
  const article = findArticleBySlug(slug);

  if (!article) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center">
        <PageSeo
          meta={{
            path: `/news/${slug}`,
            title: 'Article Not Found | PulseTrends',
            description: 'The article you are looking for does not exist.',
            noindex: true,
            ogType: 'website',
          }}
        />
        <h1 className="text-2xl font-bold text-surface-white">Article Not Found</h1>
        <p className="text-surface-600 mt-2">The article you are looking for does not exist or has been removed.</p>
        <Link to="/news" className="inline-flex items-center gap-2 mt-6 text-brand hover:text-brand-light">
          <ArrowLeft className="w-4 h-4" /> Back to News
        </Link>
      </div>
    );
  }

  const path = `/news/${slug}`;
  const description = (article.subheadline || article.metaDescription || article.executiveSummary || '').slice(0, 160);
  const heroImage = article.images?.find((i) => i && i.url);
  const articleSchema = newsArticleSchema({
    id: article.id,
    headline: article.headline,
    description,
    publishedAt: article.publishedAt,
    image: heroImage?.url,
    urlPath: path,
  });
  // Build related-articles JSON-LD ItemList for richer SERP
  const relatedList = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    itemListElement: newsArticles.slice(0, 10).map((a, idx) => ({
      '@type': 'ListItem',
      position: idx + 1,
      url: canonical(`/news/${a.id}-${a.id}`),
      name: a.headline,
    })),
  };

  return (
    <>
      <PageSeo
        meta={{
          path,
          title: `${article.headline} | PulseTrends`,
          description,
          ogType: 'article',
          ogImage: heroImage?.url,
          schema: [articleSchema, relatedList],
        }}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'News', path: '/news' },
          { name: article.headline, path: `/news/${slug}` },
        ]}
      />
      <ArticleReader article={article} />
    </>
  );
}
