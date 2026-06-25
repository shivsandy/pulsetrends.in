import { useEffect, useRef } from 'react';
import { Outlet, ScrollRestoration, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import CookieConsent from '../components/CookieConsent';
import { initGA, trackPageView, initScrollTracking, initTimeOnPage, resetTrackingForNewPage, setupOutboundLinkTracking } from '../lib/analytics';

// Global search event to allow opening search from anywhere
const SEARCH_OPEN_EVENT = 'pulsetrends:open-search';

export function triggerSearchOpen() {
  window.dispatchEvent(new CustomEvent(SEARCH_OPEN_EVENT));
}

export default function RootLayout() {
  const location = useLocation();
  const isHome = location.pathname === '/';
  const prevPath = useRef(location.pathname);

  // Initialize GA4 once
  useEffect(() => {
    initGA();
    setupOutboundLinkTracking();
    initScrollTracking();
    initTimeOnPage();
  }, []);

  // Track page views on route change (SPA navigation)
  useEffect(() => {
    if (prevPath.current !== location.pathname) {
      resetTrackingForNewPage();
      prevPath.current = location.pathname;
    }
    trackPageView(location.pathname, document.title);
    initScrollTracking();
    initTimeOnPage();
  }, [location.pathname]);

  // Ctrl+K / Cmd+K keyboard shortcut for search
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        triggerSearchOpen();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return (
    <div className="min-h-screen bg-surface-0 flex flex-col">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:px-3 focus:py-2 focus:bg-brand focus:text-white focus:rounded-md focus:text-[13px] focus:font-medium"
      >
        Skip to main content
      </a>
      <Header />
      <main id="main-content" className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex-1 w-full">
        <Outlet />
      </main>
      <Footer />
      <CookieConsent />
      <ScrollRestoration />
    </div>
  );
}
