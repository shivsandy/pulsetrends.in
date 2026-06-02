import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';
import PageSeo from '../components/PageSeo';

export default function NotFoundPage() {
  return (
    <>
      <PageSeo
        meta={{
          path: '/404',
          title: 'Page Not Found | PulseTrends',
          description: 'The page you are looking for does not exist.',
          noindex: true,
          ogType: 'website',
        }}
      />
      <div className="max-w-xl mx-auto py-20 text-center animate-fade-in">
        <p className="text-[12px] uppercase tracking-wider font-semibold text-brand-light mb-3">404</p>
        <h1 className="text-3xl font-bold text-surface-white mb-3">Page Not Found</h1>
        <p className="text-[14px] text-surface-700 leading-relaxed mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-brand text-white hover:bg-brand-light transition-colors text-[14px] font-medium"
        >
          <Home className="w-4 h-4" />
          Back to Home
        </Link>
        <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
          <Link to="/ipo-analysis" className="bg-surface-100 border border-surface-300/60 rounded-lg p-4 hover:border-surface-500 transition-colors">
            <p className="text-[11px] text-surface-600 uppercase tracking-wider">IPO Analysis</p>
            <p className="text-[14px] font-semibold text-surface-white mt-1">Browse IPOs →</p>
          </Link>
          <Link to="/airdrops" className="bg-surface-100 border border-surface-300/60 rounded-lg p-4 hover:border-surface-500 transition-colors">
            <p className="text-[11px] text-surface-600 uppercase tracking-wider">Airdrops</p>
            <p className="text-[14px] font-semibold text-surface-white mt-1">Track airdrops →</p>
          </Link>
          <Link to="/news" className="bg-surface-100 border border-surface-300/60 rounded-lg p-4 hover:border-surface-500 transition-colors">
            <p className="text-[11px] text-surface-600 uppercase tracking-wider">News</p>
            <p className="text-[14px] font-semibold text-surface-white mt-1">Read news →</p>
          </Link>
        </div>
      </div>
    </>
  );
}
