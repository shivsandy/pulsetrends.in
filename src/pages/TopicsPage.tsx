import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import PillarPage from './topics/PillarPage';
import { TOPIC_CONFIGS } from './topics/topicsConfig';

export default function TopicsPage() {
  const { slug = '' } = useParams();
  const config = TOPIC_CONFIGS[slug];

  if (!config) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center">
        <PageSeo
          meta={{
            path: `/learn/${slug}`,
            title: 'Guide Not Found | PulseTrends',
            description: 'The guide you are looking for does not exist.',
            noindex: true,
            ogType: 'website',
          }}
        />
        <h1 className="text-2xl font-bold text-surface-white">Guide Not Found</h1>
        <p className="text-surface-600 mt-2">The guide you are looking for is not available.</p>
        <Link to="/learn" className="inline-flex items-center gap-2 mt-6 text-brand hover:text-brand-light">
          <ArrowLeft className="w-4 h-4" /> Browse All Guides
        </Link>
      </div>
    );
  }

  return <PillarPage config={config} />;
}
