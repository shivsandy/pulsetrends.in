import { Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, Coins, Newspaper, BookOpen, HelpCircle } from 'lucide-react';
import PageSeo from '../../components/PageSeo';
import Breadcrumbs from '../../components/Breadcrumbs';
import { SITE } from '../../seo/config';
import { faqPageSchema } from '../../seo/schema';
import { TOPIC_CONFIGS, type TopicConfig } from './topicsConfig';

export default function PillarPage({ config }: { config: TopicConfig }) {
  const path = `/learn/${config.slug}`;

  return (
    <>
      <PageSeo
        meta={{
          path,
          title: config.title,
          description: config.description,
          keywords: config.keywords,
          ogType: config.ogType,
          ogImage: `${SITE.origin}/og-default.png`,
          schema: {
            '@context': 'https://schema.org',
            '@graph': [
              {
                '@type': 'Article',
                headline: config.title,
                description: config.description,
                datePublished: '2026-06-07',
                dateModified: '2026-06-07',
                author: {
                  '@type': 'Person',
                  name: 'Shiva Sandeep',
                  url: `${SITE.origin}/author/shiva-sandeep`,
                },
                publisher: {
                  '@type': 'Organization',
                  name: SITE.name,
                  logo: { '@type': 'ImageObject', url: `${SITE.origin}/og-default.png` },
                },
                mainEntityOfPage: { '@type': 'WebPage', '@id': `${SITE.origin}${path}` },
              },
              ...(config.faqs.length > 0 ? [faqPageSchema(config.faqs)] : []),
            ],
          },
        }}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Learn', path: '/learn' },
          { name: config.title, path },
        ]}
      />

      <article className="max-w-4xl mx-auto animate-fade-in" itemScope itemType="https://schema.org/Article">
        <Breadcrumbs items={[
          { name: 'Home', path: '/' },
          { name: 'Learn', path: '/learn' },
          { name: config.title },
        ]} />

        <Link to="/learn" className="mb-4 inline-flex items-center gap-2 text-[13px] text-surface-700 hover:text-surface-white transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Guides
        </Link>

        <header className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-brand-muted border border-brand-border text-[11px] font-semibold text-brand-light uppercase tracking-wider">Guide</span>
            <span className="text-[11px] text-surface-600">Updated June 2026</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-surface-white tracking-tight leading-tight">
            {config.h1}
          </h1>
          <p className="text-[15px] text-surface-700 mt-3 max-w-3xl leading-relaxed">
            {config.description}
          </p>
          <div className="flex flex-wrap items-center gap-4 mt-4 text-[12px] text-surface-600">
            <span className="inline-flex items-center gap-1"><BookOpen className="w-3.5 h-3.5" /> {config.sections.length} sections</span>
            <span className="inline-flex items-center gap-1"><HelpCircle className="w-3.5 h-3.5" /> {config.faqs.length} FAQs</span>
            <span className="inline-flex items-center gap-1"><Coins className="w-3.5 h-3.5" /> Educational</span>
          </div>
        </header>

        <div className="space-y-8">
          {config.sections.map((section, i) => (
            <section key={i} className="scroll-mt-20" id={`section-${i + 1}`}>
              <h2 className="text-xl font-bold text-surface-white mb-3 tracking-tight">{section.h2}</h2>
              <p className="text-[14px] text-surface-800 leading-relaxed">{section.content}</p>
            </section>
          ))}
        </div>

        <hr className="border-surface-300/40 my-10" />

        <section className="mb-10">
          <h2 className="text-xl font-bold text-surface-white mb-5">Frequently Asked Questions</h2>
          <div className="space-y-3" itemScope itemType="https://schema.org/FAQPage">
            {config.faqs.map((faq, i) => (
              <details key={i} className="bg-surface-100 border border-surface-300/60 rounded-lg overflow-hidden group" itemScope itemType="https://schema.org/Question">
                <summary className="px-4 py-3.5 cursor-pointer text-[14px] font-semibold text-surface-white hover:bg-surface-200/50 transition-colors list-none flex items-center justify-between">
                  <span itemProp="name">{faq.q}</span>
                  <HelpCircle className="w-4 h-4 text-surface-600 shrink-0 ml-2 group-open:rotate-180 transition-transform" />
                </summary>
                <div className="px-4 pb-4" itemProp="acceptedAnswer" itemScope itemType="https://schema.org/Answer">
                  <p className="text-[13px] text-surface-700 leading-relaxed" itemProp="text">{faq.a}</p>
                </div>
              </details>
            ))}
          </div>
        </section>

        <div className="bg-surface-100 border border-surface-300/60 rounded-xl p-6 mb-10">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-brand-light" />
            <h3 className="text-[15px] font-bold text-surface-white">Related Analysis on PulseTrends</h3>
          </div>
          <p className="text-[13px] text-surface-700 mb-4">
            Explore in-depth analysis, real-time prices, and AI-powered insights on PulseTrends.
          </p>
          <div className="flex flex-wrap gap-2">
            <Link to="/ipo-analysis" className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-surface-200 border border-surface-300/60 text-[12px] font-medium text-surface-700 hover:text-surface-white hover:bg-surface-300 transition-colors">
              <TrendingUp className="w-3.5 h-3.5" /> IPO Analysis
            </Link>
            <Link to="/airdrops" className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-surface-200 border border-surface-300/60 text-[12px] font-medium text-surface-700 hover:text-surface-white hover:bg-surface-300 transition-colors">
              <Coins className="w-3.5 h-3.5" /> Crypto Airdrops
            </Link>
            <Link to="/news" className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-surface-200 border border-surface-300/60 text-[12px] font-medium text-surface-700 hover:text-surface-white hover:bg-surface-300 transition-colors">
              <Newspaper className="w-3.5 h-3.5" /> Market News
            </Link>
          </div>
        </div>

        <div className="text-[12px] text-surface-600 border-t border-surface-300/40 pt-6">
          <p><strong>Disclaimer:</strong> This article is for educational and informational purposes only and does not constitute financial advice. Cryptocurrency and IPO investments carry significant risk. Always conduct your own research and consult a qualified financial advisor before making investment decisions.</p>
          <p className="mt-2"><strong>Author:</strong> <Link to="/author/shiva-sandeep" className="text-brand hover:text-brand-light">Shiva Sandeep</Link>, Software Analyst at PulseTrends. Edited by the PulseTrends editorial team.</p>
        </div>
      </article>
    </>
  );
}
