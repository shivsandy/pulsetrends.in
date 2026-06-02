import { useState } from 'react';
import { X } from 'lucide-react';
import CookieModal from './CookieModal';

export default function CookieConsent() {
  const [visible, setVisible] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  if (!visible) return null;

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
              onClick={() => setVisible(false)}
              className="px-3 py-1.5 rounded-md text-[12px] font-medium text-surface-800 hover:text-surface-white bg-surface-300 hover:bg-surface-400 transition-colors"
            >
              Decline
            </button>
            <button
              onClick={() => setVisible(false)}
              className="px-4 py-1.5 rounded-md text-[12px] font-medium text-white bg-brand hover:bg-brand-light transition-colors"
            >
              Accept
            </button>
            <button
              onClick={() => setVisible(false)}
              className="p-1.5 text-surface-600 hover:text-surface-white rounded-md hover:bg-surface-300 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      {modalOpen && <CookieModal onClose={() => setModalOpen(false)} onDone={() => { setModalOpen(false); setVisible(false); }} />}
    </>
  );
}
