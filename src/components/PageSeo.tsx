import { SITE, canonical } from '../seo/config';
import type { PageMeta } from '../seo/routes';
import { buildFullSchema } from '../seo/schema';

interface PageSeoProps {
  meta: PageMeta;
  breadcrumbs?: { name: string; path: string }[];
  imageOverride?: string;
}

export default function PageSeo({ meta, breadcrumbs, imageOverride }: PageSeoProps) {
  const url = canonical(meta.path);
  const ogImage = imageOverride || meta.ogImage || `${SITE.origin}/og-default.png`;
  const robots = meta.noindex ? 'noindex,nofollow' : 'index,follow,max-image-preview:large';
  const schemaJson = JSON.stringify(buildFullSchema(meta, breadcrumbs));
  return (
    <>
      <title>{meta.title}</title>
      <meta name="description" content={meta.description} />
      {meta.keywords && <meta name="keywords" content={meta.keywords} />}
      <meta name="robots" content={robots} />
      <link rel="canonical" href={url} />
      <meta property="og:site_name" content={SITE.name} />
      <meta property="og:title" content={meta.title} />
      <meta property="og:description" content={meta.description} />
      <meta property="og:url" content={url} />
      <meta property="og:type" content={meta.ogType || 'website'} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:locale" content="en_IN" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={meta.title} />
      <meta name="twitter:description" content={meta.description} />
      <meta name="twitter:image" content={ogImage} />
      <script type="application/ld+json">{schemaJson}</script>
    </>
  );
}
