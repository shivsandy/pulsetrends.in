import { Mail } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';

export default function ContactPage() {
  return (
    <>
      <PageSeo
        meta={ROUTES.contact}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Contact', path: '/contact' },
        ]}
      />
      <div className="max-w-3xl mx-auto page-content animate-fade-in">
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Contact' }]} />
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-brand-muted flex items-center justify-center">
            <Mail className="w-5 h-5 text-brand" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-white">Contact Us</h1>
            <p className="text-[13px] text-surface-600">Get in touch with the PulseTrends team</p>
          </div>
        </div>
        <p>We'd love to hear from you. Whether you have a question about our analysis, want to report a bug, suggest a feature, or explore partnership opportunities — we're here to help.</p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6">
          {[
            { icon: Mail, title: 'Email', desc: 'General inquiries, feedback & support', addr: 'pulsetrendsin@gmail.com' },
          ].map((c) => (
            <div key={c.title} className="bg-surface-100 border border-surface-300/60 rounded-lg p-4 text-center">
              <div className="w-10 h-10 rounded-lg bg-brand-muted flex items-center justify-center mx-auto mb-3">
                <c.icon className="w-5 h-5 text-brand" />
              </div>
              <h3 className="text-[14px] font-semibold text-surface-white mb-1">{c.title}</h3>
              <p className="text-[12px] text-surface-700 mb-2">{c.desc}</p>
              <a href={`mailto:${c.addr}`} className="text-[13px] text-brand hover:text-brand-light transition-colors">{c.addr}</a>
            </div>
          ))}
        </div>

        <h2>Response Time</h2>
        <p>We aim to respond to all inquiries within 24-48 hours during business days. For urgent issues, please mention [URGENT] in your subject line and we'll prioritise your message.</p>

        <h2>Partnerships</h2>
        <p>Interested in partnering with PulseTrends? We're open to collaborations with media outlets, data providers, research firms, and blockchain projects. Reach out to us at pulsetrendsin@gmail.com with details about your proposal.</p>
      </div>
    </>
  );
}
