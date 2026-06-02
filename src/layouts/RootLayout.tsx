import { Outlet, ScrollRestoration, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Ticker from '../components/Ticker';
import Footer from '../components/Footer';
import CookieConsent from '../components/CookieConsent';

export default function RootLayout() {
  const location = useLocation();
  const isHome = location.pathname === '/';
  return (
    <div className="min-h-screen bg-surface-0 flex flex-col">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:px-3 focus:py-2 focus:bg-brand focus:text-white focus:rounded-md focus:text-[13px] focus:font-medium"
      >
        Skip to main content
      </a>
      <Header />
      {!isHome && <Ticker />}
      <main id="main-content" className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full">
        <Outlet />
      </main>
      <Footer />
      <CookieConsent />
      <ScrollRestoration />
    </div>
  );
}
