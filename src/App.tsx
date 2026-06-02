import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import RootLayout from './layouts/RootLayout';
import HomePage from './pages/HomePage';

const IPOAnalysisPage = lazy(() => import('./pages/IPOAnalysisPage'));
const IPODetailPage = lazy(() => import('./pages/IPODetailPage'));
const AirdropsPage = lazy(() => import('./pages/AirdropsPage'));
const NewsPage = lazy(() => import('./pages/NewsPage'));
const NewsDetailPage = lazy(() => import('./pages/NewsDetailPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'));
const TermsPage = lazy(() => import('./pages/TermsPage'));
const CookiesPage = lazy(() => import('./pages/CookiesPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-5 h-5 rounded-full border-2 border-brand border-t-transparent animate-spin" />
          <p className="text-[13px] text-surface-600">Loading...</p>
        </div>
      </div>
    }>
      {children}
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'ipo-analysis', element: <SuspenseWrapper><IPOAnalysisPage /></SuspenseWrapper> },
      { path: 'ipo-analysis/:slug', element: <SuspenseWrapper><IPODetailPage /></SuspenseWrapper> },
      { path: 'airdrops', element: <SuspenseWrapper><AirdropsPage /></SuspenseWrapper> },
      { path: 'airdrops/:slug', element: <SuspenseWrapper><AirdropsPage /></SuspenseWrapper> },
      { path: 'news', element: <SuspenseWrapper><NewsPage /></SuspenseWrapper> },
      { path: 'news/:slug', element: <SuspenseWrapper><NewsDetailPage /></SuspenseWrapper> },
      { path: 'about', element: <SuspenseWrapper><AboutPage /></SuspenseWrapper> },
      { path: 'contact', element: <SuspenseWrapper><ContactPage /></SuspenseWrapper> },
      { path: 'privacy-policy', element: <SuspenseWrapper><PrivacyPolicyPage /></SuspenseWrapper> },
      { path: 'terms', element: <SuspenseWrapper><TermsPage /></SuspenseWrapper> },
      { path: 'cookies', element: <SuspenseWrapper><CookiesPage /></SuspenseWrapper> },
      { path: '*', element: <SuspenseWrapper><NotFoundPage /></SuspenseWrapper> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
