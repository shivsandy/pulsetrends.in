import { useState } from 'react';
import { X, Shield } from 'lucide-react';

interface CookieModalProps {
  onClose: () => void;
  onDone: (analytics: boolean, marketing: boolean) => void;
}

export default function CookieModal({ onClose, onDone }: CookieModalProps) {
  const [prefs, setPrefs] = useState({
    necessary: true,
    analytics: false,
    marketing: false,
  });

  const toggle = (key: keyof typeof prefs) => {
    if (key === 'necessary') return;
    setPrefs(p => ({ ...p, [key]: !p[key] }));
  };

  const items = [
    { key: 'necessary' as const, label: 'Necessary', desc: 'Essential for the website to function. Cannot be disabled.', locked: true },
    { key: 'analytics' as const, label: 'Analytics', desc: 'Help us understand how visitors interact with our site.', locked: false },
    { key: 'marketing' as const, label: 'Marketing', desc: 'Used to deliver relevant advertisements and track effectiveness.', locked: false },
  ];

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-surface-100 border border-surface-300/60 rounded-xl w-full max-w-md shadow-2xl animate-fade-in">
        <div className="flex items-center justify-between p-5 border-b border-surface-300/60">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-muted flex items-center justify-center">
              <Shield className="w-4 h-4 text-brand" />
            </div>
            <h2 className="font-semibold text-surface-white text-[15px]">Cookie Preferences</h2>
          </div>
          <button onClick={onClose} className="p-1 text-surface-600 hover:text-surface-white rounded-md hover:bg-surface-300 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {items.map(item => (
            <div key={item.key} className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <p className="text-[13px] font-medium text-surface-white">{item.label}</p>
                <p className="text-[12px] text-surface-700 mt-0.5">{item.desc}</p>
              </div>
              <button
                onClick={() => toggle(item.key)}
                disabled={item.locked}
                className={`relative w-9 h-5 rounded-full transition-colors shrink-0 mt-0.5 ${
                  prefs[item.key] ? 'bg-brand' : 'bg-surface-400'
                } ${item.locked ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                  prefs[item.key] ? 'translate-x-4' : 'translate-x-0'
                }`} />
              </button>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-end gap-2 p-5 border-t border-surface-300/60">
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded-md text-[12px] font-medium text-surface-800 hover:text-surface-white bg-surface-300 hover:bg-surface-400 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onDone(prefs.analytics, prefs.marketing)}
            className="px-4 py-1.5 rounded-md text-[12px] font-medium text-white bg-brand hover:bg-brand-light transition-colors"
          >
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
}
