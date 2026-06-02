import { FileText } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';

export default function TermsPage() {
  return (
    <>
      <PageSeo
        meta={ROUTES.terms}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'Terms & Conditions', path: '/terms' },
        ]}
      />
      <div className="max-w-3xl mx-auto page-content animate-fade-in">
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'Terms & Conditions' }]} />
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-brand-muted flex items-center justify-center">
            <FileText className="w-5 h-5 text-brand" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-white">Terms & Conditions</h1>
            <p className="text-[13px] text-surface-600">Last updated: 1 June 2026</p>
          </div>
        </div>
        <p>By accessing or using pulsetrends.in (the "Service"), you agree to be bound by these Terms & Conditions. If you disagree with any part, please do not use the Service.</p>

        <h2>1. Informational Purposes Only</h2>
        <p>The content on PulseTrends is provided for general informational and educational purposes only. It does <strong>not</strong> constitute financial advice, investment advice, trading advice, or any other form of professional advice. The platform does not recommend buying, selling, or holding any specific security, cryptocurrency, or other asset.</p>

        <h2>2. No Investment Recommendations</h2>
        <p>Any AI-generated scores, verdicts, sentiment analyses, or risk assessments are algorithmic outputs based on available data and model assumptions. They are <strong>not</strong> personalised recommendations and should <strong>not</strong> be relied upon as the sole basis for any investment decision. Always conduct your own research and consult a SEBI-registered investment advisor (in India) or equivalent qualified professional in your jurisdiction.</p>

        <h2>3. Accuracy of Information</h2>
        <p>We strive for accuracy but make no warranties, express or implied, about the completeness, accuracy, reliability, or suitability of the information on this Service. Market data, IPO details, airdrop information, and news content may be delayed, incomplete, or contain errors. Verify all information independently before acting on it.</p>

        <h2>4. Third-Party Content and Links</h2>
        <p>The Service may contain links to third-party websites, news sources, social media, or other resources. We are not responsible for the content, accuracy, or practices of any third-party site. Access them at your own risk.</p>

        <h2>5. Intellectual Property</h2>
        <p>All original content, design, code, and branding on PulseTrends is the property of PulseTrends or its licensors. You may not reproduce, distribute, modify, or create derivative works without prior written consent. Brief quotations for non-commercial, attributed use (e.g., journalism) are welcome.</p>

        <h2>6. User Conduct</h2>
        <p>You agree not to:</p>
        <ul>
          <li>Use the Service for any unlawful purpose or in violation of any applicable laws.</li>
          <li>Attempt to gain unauthorised access to any portion of the Service or related systems.</li>
          <li>Scrape, crawl, or otherwise extract data at a rate that interferes with the Service's operation.</li>
          <li>Use the Service to harass, abuse, or harm others.</li>
        </ul>

        <h2>7. Limitation of Liability</h2>
        <p>To the maximum extent permitted by law, PulseTrends and its operators shall not be liable for any indirect, incidental, special, consequential, or punitive damages — including loss of profits, data, or goodwill — arising from your use of the Service.</p>

        <h2>8. Changes to These Terms</h2>
        <p>We may revise these Terms at any time. The updated version will be posted on this page with a revised "Last updated" date. Continued use of the Service after changes constitutes acceptance of the revised terms.</p>

        <h2>9. Governing Law</h2>
        <p>These Terms are governed by the laws of India. Any disputes shall be subject to the exclusive jurisdiction of the courts in Bengaluru, India.</p>

        <h2>10. Contact</h2>
        <p>For questions about these Terms, contact us at <a href="mailto:legal@pulsetrends.in">legal@pulsetrends.in</a>.</p>
      </div>
    </>
  );
}
