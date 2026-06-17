import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import CookieModal from './CookieModal';

const COOKIE_NAME = 'pulsetrends_cookie_consent';
const SEVEN_DAYS_SECONDS = 7 * 24 * 60 * 60;

interface CookiePrefs {
  consent: boolean;
  analytics: boolean;
  marketing: boolean;
}

function setGAConsent(enabled: boolean) {
  if (typeof window === 'undefined' || !window.gtag) return;
  window.gtag('consent', 'update', {
    analytics_storage: enabled ? 'granted' : 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
  });
}

/**
 * Read a cookie by name. Returns null if not found or unparseable.
 */
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${encodeURIComponent(name)}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

/**
 * Set a cookie with the given name, value, and attributes.
 * 7-day expiry via max-age, scoped to entire site.
 */
function setCookie(name: string, value: string): void {
  const encodedName = encodeURIComponent(name);
  const encodedValue = encodeURIComponent(value);
  const isSecure = window.location.protocol === 'https:';
  document.cookie = [
    `${encodedName}=${encodedValue}`,
    `max-age=${SEVEN_DAYS_SECONDS}`,
    'path=/',
    'SameSite=Lax',
    isSecure ? 'Secure' : '',
  ]
    .filter(Boolean)
    .join('; ');
}

/** Parse stored JSON from the cookie. Returns null if missing or expired. */
function loadConsent(): CookiePrefs | null {
  try {
    const raw = getCookie(COOKIE_NAME);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as CookiePrefs & { timestamp?: number };
    // Basic shape check
    if (typeof parsed.consent !== 'boolean') return null;
    return { consent: parsed.consent, analytics: parsed.analytics, marketing: parsed.marketing };
  } catch {
    return null;
  }
}

/** Persist consent preferences as a cookie with a 7-day max-age. */
function saveConsent(consent: boolean, analytics: boolean, marketing: boolean): void {
  try {
    const payload = JSON.stringify({ consent, analytics, marketing });
    setCookie(COOKIE_NAME, payload);
  } catch {
    // cookie may be unavailable
  }
}

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const existing = loadConsent();
    if (!existing) {
      setVisible(true);
      setGAConsent(false);
    } else {
      setGAConsent(existing.analytics);
    }
    setLoaded(true);
  }, []);

  const accept = () => {
    saveConsent(true, true, true);
    setGAConsent(true);
    setVisible(false);
  };

  const decline = () => {
    saveConsent(false, false, false);
    setGAConsent(false);
    setVisible(false);
  };

  const customiseDone = (analytics: boolean, marketing: boolean) => {
    saveConsent(true, analytics, marketing);
    setGAConsent(analytics);
    setModalOpen(false);
    setVisible(false);
  };

  // Don't flash the banner before checking the cookie
  if (!loaded || !visible) return null;

  return (
    <>
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-surface-100 border-t border-surface-300/60 p-4 animate-slide-up">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex-1">
            <p className="text-[13px] text-surface-800 leading-relaxed">
              We use cookies and similar technologies to enhance your experience, analyze traffic, and deliver personalised content. 
              By clicking "Accept", you consent to our use of cookies. Read our{' '}
              <button onClick={() => setModalOpen(true)} className="text-brand hover:text-brand-light underline">Cookie Policy</button>.
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => { setModalOpen(true); }}
              className="px-3 py-1.5 rounded-md text-[12px] font-medium text-surface-800 hover:text-surface-white bg-surface-300 hover:bg-surface-400 transition-colors"
            >
              Customise
            </button>
            <button
              onClick={decline}
              className="px-3 py-1.5 rounded-md text-[12px] font-medium text-surface-800 hover:text-surface-white bg-surface-300 hover:bg-surface-400 transition-colors"
            >
              Decline
            </button>
            <button
              onClick={accept}
              className="px-4 py-1.5 rounded-md text-[12px] font-medium text-white bg-brand hover:bg-brand-light transition-colors"
            >
              Accept
            </button>
            <button
              onClick={decline}
              className="p-1.5 text-surface-600 hover:text-surface-white rounded-md hover:bg-surface-300 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      {modalOpen && (
        <CookieModal
          onClose={() => setModalOpen(false)}
          onDone={customiseDone}
        />
      )}
    </>
  );
}
