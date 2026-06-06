const GA_MEASUREMENT_ID = 'G-SC8VSW3D32';

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void;
    dataLayer: unknown[];
  }
}

function gtag(...args: unknown[]) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag(...args);
  }
}

export function initGA() {
  if (typeof window === 'undefined') return;
  const existing = document.querySelector(`script[src*="${GA_MEASUREMENT_ID}"]`);
  if (existing) return;

  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', GA_MEASUREMENT_ID, {
    send_page_view: false,
    anonymize_ip: true,
  });
}

export function trackPageView(path: string, title?: string) {
  gtag('event', 'page_view', {
    page_path: path,
    page_title: title || document.title,
    page_location: window.location.href,
    send_to: GA_MEASUREMENT_ID,
  });
}

export function trackEvent(action: string, params?: Record<string, unknown>) {
  gtag('event', action, params);
}

export function trackSearch(query: string) {
  if (!query.trim()) return;
  trackEvent('search', { search_term: query });
}

export function trackOutboundLink(url: string, linkText?: string) {
  trackEvent('click', {
    event_category: 'outbound',
    event_label: url,
    link_text: linkText || '',
    transport_type: 'beacon',
  });
}

export function trackCTA(ctaName: string, location?: string) {
  trackEvent('cta_click', {
    cta_name: ctaName,
    cta_location: location || 'unknown',
  });
}

export function trackDownload(fileName: string, fileType?: string) {
  trackEvent('file_download', {
    file_name: fileName,
    file_type: fileType || 'unknown',
  });
}

export function trackContactSubmission(method: string) {
  trackEvent('contact_submission', {
    contact_method: method,
  });
}

export function trackNewsletterSignup(location?: string) {
  trackEvent('newsletter_signup', {
    signup_location: location || 'unknown',
  });
}

export function trackError(errorType: string, errorMessage?: string) {
  trackEvent('error', {
    error_type: errorType,
    error_message: errorMessage || '',
    non_interaction: true,
  });
}

const SCROLL_DEPTHS = [25, 50, 75, 100];
let trackedDepths = new Set<number>();
let scrollListenerAttached = false;

export function initScrollTracking() {
  if (typeof window === 'undefined' || scrollListenerAttached) return;
  scrollListenerAttached = true;
  trackedDepths = new Set();

  const handler = () => {
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollHeight <= 0) return;
    const scrolled = (window.scrollY / scrollHeight) * 100;

    for (const depth of SCROLL_DEPTHS) {
      if (scrolled >= depth && !trackedDepths.has(depth)) {
        trackedDepths.add(depth);
        trackEvent('scroll_depth', {
          scroll_depth: depth,
          page_path: window.location.pathname,
          non_interaction: true,
        });
      }
    }
  };

  window.addEventListener('scroll', handler, { passive: true });
}

const TIME_ON_PAGE_INTERVAL = 30000;
let topTimer: ReturnType<typeof setInterval> | null = null;
let topSeconds = 0;

export function initTimeOnPage() {
  if (typeof window === 'undefined' || topTimer) return;
  topSeconds = 0;
  topTimer = setInterval(() => {
    topSeconds += 30;
    if (topSeconds >= 60) {
      trackEvent('time_on_page', {
        seconds: topSeconds,
        page_path: window.location.pathname,
        non_interaction: true,
      });
    }
  }, TIME_ON_PAGE_INTERVAL);
}

export function resetTrackingForNewPage() {
  if (topTimer) {
    clearInterval(topTimer);
    topTimer = null;
  }
  topSeconds = 0;
  trackedDepths = new Set();
}

export function setupOutboundLinkTracking() {
  if (typeof document === 'undefined') return;
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const link = target.closest<HTMLAnchorElement>('a');
    if (!link || !link.href) return;

    const isInternal = link.href.startsWith(window.location.origin) ||
      link.href.startsWith('/') ||
      !link.href.startsWith('http');

    if (!isInternal) {
      trackOutboundLink(link.href, link.textContent || link.getAttribute('aria-label') || '');
    }
  }, { passive: true });
}
