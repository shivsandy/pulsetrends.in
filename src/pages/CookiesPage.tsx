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

        <p>This Cookie Policy explains what cookies are, how PulseTrends ("we", "our", or "us") uses them, and the choices available to users regarding cookies.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>What Are Cookies?</h2>
        <p>Cookies are small text files that websites store on your device when you visit them. Cookies help websites function properly, remember user preferences, improve performance, and provide insights about how visitors use a website.</p>
        <p>Cookies may be either:</p>
        <ul>
          <li><strong>Session cookies</strong>, which expire when you close your browser.</li>
          <li><strong>Persistent cookies</strong>, which remain on your device until they expire or are deleted.</li>
        </ul>

        <hr className="border-surface-300/40 my-6" />

        <h2>Cookies We Currently Use</h2>
        <p>At present, PulseTrends uses only limited cookies necessary for the operation of the Service.</p>

        <h3>Essential Cookies</h3>
        <p>These cookies are required for basic website functionality and cannot be disabled through our systems.</p>

        <div className="overflow-x-auto my-4">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="bg-surface-200/50">
                <th className="text-left px-4 py-2.5 font-semibold text-surface-white border-b border-surface-300/40">Cookie</th>
                <th className="text-left px-4 py-2.5 font-semibold text-surface-white border-b border-surface-300/40">Purpose</th>
                <th className="text-left px-4 py-2.5 font-semibold text-surface-white border-b border-surface-300/40">Duration</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-surface-300/20">
                <td className="px-4 py-2.5 font-mono text-[12px] text-surface-white">cookie-consent</td>
                <td className="px-4 py-2.5 text-surface-800">Stores your cookie preference selection</td>
                <td className="px-4 py-2.5 text-surface-800">Up to 7 days</td>
              </tr>
            </tbody>
          </table>
        </div>

        <p>Without these cookies, certain features of the Service may not function correctly.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Future Use of Analytics or Advertising Cookies</h2>
        <p>As PulseTrends evolves, we may introduce analytics, advertising, or other optional cookies to improve the Service and support its operation.</p>
        <p>If such cookies are introduced:</p>
        <ul>
          <li>This Cookie Policy will be updated accordingly.</li>
          <li>Where required by applicable law, users will be given the opportunity to provide consent before such cookies are activated.</li>
        </ul>

        <hr className="border-surface-300/40 my-6" />

        <h2>Third-Party Content</h2>
        <p>Some content displayed on the Service may be provided by third-party services.</p>
        <p>Examples may include:</p>
        <ul>
          <li>Images</li>
          <li>Embedded content</li>
          <li>Videos</li>
          <li>Social media content</li>
          <li>Advertising content</li>
        </ul>
        <p>These third parties may place cookies or similar technologies on your device when their content is loaded.</p>
        <p>We do not control third-party cookies and encourage users to review the privacy and cookie policies of those providers.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Managing Cookies</h2>
        <p>Most web browsers allow you to:</p>
        <ul>
          <li>View stored cookies</li>
          <li>Delete existing cookies</li>
          <li>Block certain cookies</li>
          <li>Block all cookies</li>
          <li>Receive notifications when cookies are being set</li>
        </ul>
        <p>Instructions vary by browser, but settings are generally available within your browser's Privacy or Security settings.</p>
        <p>Please note that disabling essential cookies may affect the functionality of the Service.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Your Consent</h2>
        <p>Where required by law, we will request your consent before using non-essential cookies.</p>
        <p>You may withdraw or modify your cookie preferences at any time by adjusting your browser settings or using any cookie preference tools that may be made available on the Service.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Changes to This Cookie Policy</h2>
        <p>We may update this Cookie Policy from time to time.</p>
        <p>Any changes will be posted on this page together with an updated "Last updated" date.</p>
        <p>Continued use of the Service after changes become effective constitutes acceptance of the updated Cookie Policy.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Contact</h2>
        <p>For questions regarding this Cookie Policy or our use of cookies, contact:</p>
        <p>
          <strong>Email:</strong>{' '}
          <a href="mailto:pulsetrendsin@gmail.com" className="text-brand hover:text-brand-light transition-colors">
            pulsetrendsin@gmail.com
          </a>
        </p>
      </div>
    </>
  );
}
