import { Shield } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';

export default function PrivacyPolicyPage() {
  return (
    <>
      <PageSeo
        meta={ROUTES.privacy}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Privacy Policy', path: '/privacy-policy' },
        ]}
      />
      <div className="max-w-3xl mx-auto page-content animate-fade-in">
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Privacy Policy' }]} />
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-brand-muted flex items-center justify-center">
            <Shield className="w-5 h-5 text-brand" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-white">Privacy Policy</h1>
            <p className="text-[13px] text-surface-600">Last updated: 1 June 2026</p>
          </div>
        </div>
        <p>This Privacy Policy describes how PulseTrends ("we", "our", "us") collects, uses, and protects your information when you visit pulsetrends.in (the "Service").</p>

        <h2>Information We Collect</h2>
        <p>We collect minimal information necessary to operate the Service:</p>
        <ul>
          <li><strong>Usage data</strong> — anonymous analytics such as pages visited, referrer, device type, and country (via privacy-respecting analytics).</li>
          <li><strong>Cookies</strong> — small text files stored in your browser to remember your preferences (e.g., cookie consent state).</li>
          <li><strong>Voluntary submissions</strong> — any information you voluntarily provide when contacting us via email.</li>
        </ul>

        <h2>How We Use Information</h2>
        <p>We use the limited information we collect to:</p>
        <ul>
          <li>Operate, maintain, and improve the Service.</li>
          <li>Understand aggregated usage patterns to improve content and UX.</li>
          <li>Respond to your direct inquiries when you contact us.</li>
          <li>Comply with applicable legal obligations.</li>
        </ul>

        <h2>Cookies</h2>
        <p>We use only first-party cookies for essential site functionality (such as remembering your cookie preferences). We do not use advertising cookies or cross-site tracking cookies. See our <a href="/cookies">Cookie Policy</a> for details.</p>

        <h2>Third-Party Services</h2>
        <p>We use the following third-party services to operate the Service. Each provider has its own privacy practices:</p>
        <ul>
          <li><strong>GitHub Pages</strong> — static site hosting.</li>
          <li><strong>Unsplash</strong> — article imagery (images are loaded directly from Unsplash's CDN).</li>
        </ul>

        <h2>Data Sharing</h2>
        <p>We do not sell, rent, or trade your personal information. We do not share data with advertising networks or data brokers.</p>

        <h2>Data Security</h2>
        <p>We implement reasonable technical and organisational safeguards to protect any data we hold. However, no method of transmission over the internet or electronic storage is 100% secure, and we cannot guarantee absolute security.</p>

        <h2>Children's Privacy</h2>
        <p>Our Service is not directed to children under the age of 13, and we do not knowingly collect personal information from children.</p>

        <h2>Your Rights</h2>
        <p>Depending on your jurisdiction, you may have rights to access, correct, or delete any personal data we hold about you. To exercise these rights, contact us at pulsetrendsin@gmail.com.</p>

        <h2>Changes to This Policy</h2>
        <p>We may update this Privacy Policy from time to time. We will post the updated version on this page with a revised "Last updated" date. Continued use of the Service after changes constitutes acceptance of the revised policy.</p>

        <h2>Contact</h2>
        <p>For privacy-related questions, email us at <a href="mailto:pulsetrendsin@gmail.com">pulsetrendsin@gmail.com</a>.</p>
      </div>
    </>
  );
}
