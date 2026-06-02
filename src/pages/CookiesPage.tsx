import { Cookie } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';

export default function CookiesPage() {
  return (
    <>
      <PageSeo
        meta={ROUTES.cookies}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Cookie Policy', path: '/cookies' },
        ]}
      />
      <div className="max-w-3xl mx-auto page-content animate-fade-in">
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Cookie Policy' }]} />
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-brand-muted flex items-center justify-center">
            <Cookie className="w-5 h-5 text-brand" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-white">Cookie Policy</h1>
            <p className="text-[13px] text-surface-600">Last updated: 1 June 2026</p>
          </div>
        </div>
        <p>This Cookie Policy explains what cookies are, how PulseTrends uses them, and how you can control them.</p>

        <h2>What Are Cookies?</h2>
        <p>Cookies are small text files placed in your browser by websites you visit. They are widely used to make sites work more efficiently and to provide information to site owners.</p>

        <h2>Cookies We Use</h2>
        <p>PulseTrends uses only <strong>strictly necessary first-party cookies</strong>:</p>
        <ul>
          <li><strong>cookie-consent</strong> — remembers your cookie consent choice (Accept / Decline). Duration: 1 year.</li>
        </ul>
        <p>We do <strong>not</strong> use:</p>
        <ul>
          <li>Advertising or remarketing cookies</li>
          <li>Cross-site tracking cookies</li>
          <li>Third-party analytics that profile you across sites</li>
        </ul>

        <h2>Third-Party Cookies</h2>
        <p>Some content on our pages (e.g., article images) is loaded from third-party services such as Unsplash. These providers may set their own cookies when their content is loaded in your browser. We do not control these cookies. Refer to their privacy policies:</p>
        <ul>
          <li><a href="https://unsplash.com/privacy" target="_blank" rel="noopener noreferrer">Unsplash Privacy Policy</a></li>
        </ul>

        <h2>Managing Cookies</h2>
        <p>You can control or delete cookies through your browser settings. Most browsers also allow you to refuse all cookies or indicate when a cookie is being sent. Note that disabling essential cookies may affect site functionality.</p>

        <h2>Your Consent</h2>
        <p>By clicking "Accept" on the cookie banner, you consent to our use of strictly necessary cookies as described above. You can change your choice at any time by clearing your browser's storage for this site.</p>

        <h2>Contact</h2>
        <p>For questions about our use of cookies, email us at <a href="mailto:privacy@pulsetrends.in">privacy@pulsetrends.in</a>.</p>
      </div>
    </>
  );
}
