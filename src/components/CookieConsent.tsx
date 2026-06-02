import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import CookieModal from './CookieModal';

const STORAGE_KEY = 'pulsetrends_cookie_consent';

interface CookiePrefs {
  consent: boolean;
  analytics: boolean;
  marketing: boolean;
  timestamp: number;
}

function loadConsent(): CookiePrefs | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as CookiePrefs;
    // Check if consent is older than 1 year
    const oneYear = 365 * 24 * 60 * 60 * 1000;
    if (Date.now() - parsed.timestamp > oneYear) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function saveConsent(consent: boolean, analytics: boolean, marketing: boolean) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      consent,
      analytics,
      marketing,
      timestamp: Date.now(),
    }));
  } catch {
    // localStorage may be unavailable
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
    }
    setLoaded(true);
  }, []);

  const accept = () => {
    saveConsent(true, true, true);
    setVisible(false);
  };

  const decline = () => {
    saveConsent(false, false, false);
    setVisible(false);
  };

  const customiseDone = (analytics: boolean, marketing: boolean) => {
    saveConsent(true, analytics, marketing);
    setModalOpen(false);
    setVisible(false);
  };

  // Don't flash the banner before checking localStorage
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
