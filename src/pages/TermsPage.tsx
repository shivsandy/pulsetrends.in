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
        <p>By accessing or using <strong>pulsetrends.in</strong> (the "Service"), you agree to be bound by these Terms & Conditions. If you do not agree with any part of these Terms, you must not use the Service.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>1. Acceptance of Terms</h2>
        <p>These Terms & Conditions govern your access to and use of the Service. By accessing, browsing, or using the Service, you acknowledge that you have read, understood, and agreed to these Terms.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>2. Eligibility</h2>
        <p>You must be at least 18 years old or the age of majority in your jurisdiction to use the Service.</p>
        <p>By using the Service, you represent and warrant that you satisfy this requirement.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>3. Informational and Educational Purposes Only</h2>
        <p>The content published on PulseTrends is provided solely for informational and educational purposes.</p>
        <p>Nothing on the Service constitutes:</p>
        <ul>
          <li>Financial advice</li>
          <li>Investment advice</li>
          <li>Trading advice</li>
          <li>Tax advice</li>
          <li>Legal advice</li>
          <li>Accounting advice</li>
          <li>Any other professional advice</li>
        </ul>
        <p>Users should not rely on the Service as a substitute for independent research or professional consultation.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>4. No Investment Recommendations</h2>
        <p>PulseTrends does not recommend, endorse, or promote the purchase, sale, or holding of any security, cryptocurrency, token, financial instrument, or investment product.</p>
        <p>Any ratings, scores, rankings, verdicts, sentiment analyses, conviction scores, forecasts, or risk assessments are generated using analytical frameworks and AI-assisted methodologies and should not be interpreted as personalised investment recommendations.</p>
        <p>Before making any financial decision, users should conduct independent research and consult a qualified professional adviser where appropriate.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>5. AI-Generated Content Disclaimer</h2>
        <p>Certain content published on the Service may be generated, assisted, summarized, or enhanced using artificial intelligence systems.</p>
        <p>AI-generated outputs may:</p>
        <ul>
          <li>Contain inaccuracies</li>
          <li>Contain omissions</li>
          <li>Reflect outdated information</li>
          <li>Misinterpret source material</li>
          <li>Produce incorrect conclusions</li>
        </ul>
        <p>Users are responsible for independently verifying all information before relying on it.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>6. Market Risk Warning</h2>
        <p>Investing in securities, cryptocurrencies, digital assets, IPOs, and related financial products involves significant risk.</p>
        <p>Past performance does not guarantee future results.</p>
        <p>Market conditions can change rapidly, and investments may lose value, including the loss of your entire invested capital.</p>
        <p>You acknowledge that any investment decisions are made solely at your own risk.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>7. No Fiduciary Relationship</h2>
        <p>Your use of the Service does not create any fiduciary, advisory, brokerage, agency, partnership, employment, or professional-client relationship between you and PulseTrends.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>8. Accuracy of Information</h2>
        <p>We strive to provide accurate and timely information but make no representations, warranties, or guarantees regarding:</p>
        <ul>
          <li>Accuracy</li>
          <li>Completeness</li>
          <li>Reliability</li>
          <li>Timeliness</li>
          <li>Availability</li>
          <li>Suitability</li>
        </ul>
        <p>Information may contain errors, omissions, delays, or inaccuracies.</p>
        <p>You are solely responsible for verifying information before acting upon it.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>9. Third-Party Content and Links</h2>
        <p>The Service may contain links to third-party websites, applications, social media platforms, news sources, or other external resources.</p>
        <p>PulseTrends does not control, endorse, or assume responsibility for any third-party content, products, services, or practices.</p>
        <p>Your interactions with third-party websites are governed by their own terms and policies.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>10. Intellectual Property</h2>
        <p>Unless otherwise stated, all original content, software, branding, logos, designs, text, graphics, analysis, and other materials on the Service are owned by PulseTrends or its licensors and are protected by applicable intellectual property laws.</p>
        <p>You may not:</p>
        <ul>
          <li>Reproduce</li>
          <li>Republish</li>
          <li>Modify</li>
          <li>Distribute</li>
          <li>Sell</li>
          <li>License</li>
          <li>Create derivative works</li>
        </ul>
        <p>without prior written permission.</p>
        <p>Reasonable quotations with proper attribution for non-commercial or journalistic purposes are permitted.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>11. Copyright Complaints</h2>
        <p>If you believe content on the Service infringes your intellectual property rights, please contact us with:</p>
        <ul>
          <li>Identification of the copyrighted work</li>
          <li>Identification of the allegedly infringing content</li>
          <li>Your contact information</li>
          <li>A statement of good-faith belief regarding the alleged infringement</li>
        </ul>
        <p>We will review and respond to valid notices as appropriate.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>12. User Conduct</h2>
        <p>You agree not to:</p>
        <ul>
          <li>Violate any applicable laws or regulations</li>
          <li>Attempt unauthorized access to systems or infrastructure</li>
          <li>Interfere with the operation or security of the Service</li>
          <li>Use automated tools to scrape or harvest content in a manner that impacts Service performance</li>
          <li>Distribute malware, malicious code, or harmful content</li>
          <li>Use the Service to harass, abuse, or harm others</li>
          <li>Misrepresent your identity or affiliations</li>
        </ul>

        <hr className="border-surface-300/40 my-6" />

        <h2>13. Service Availability</h2>
        <p>We do not guarantee uninterrupted, secure, or error-free operation of the Service.</p>
        <p>The Service may be modified, suspended, restricted, or discontinued at any time without prior notice.</p>
        <p>We are not liable for any loss resulting from service interruptions or downtime.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>14. Termination of Access</h2>
        <p>We reserve the right to suspend, restrict, or terminate access to the Service at any time, with or without notice, for conduct that we believe violates these Terms or may harm the Service, its users, or third parties.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>15. Limitation of Liability</h2>
        <p>To the fullest extent permitted by applicable law, PulseTrends, its owners, operators, contributors, affiliates, contractors, and licensors shall not be liable for any:</p>
        <ul>
          <li>Direct damages</li>
          <li>Indirect damages</li>
          <li>Incidental damages</li>
          <li>Special damages</li>
          <li>Consequential damages</li>
          <li>Punitive damages</li>
        </ul>
        <p>including but not limited to:</p>
        <ul>
          <li>Financial losses</li>
          <li>Trading losses</li>
          <li>Investment losses</li>
          <li>Loss of profits</li>
          <li>Loss of revenue</li>
          <li>Loss of data</li>
          <li>Loss of goodwill</li>
          <li>Business interruption</li>
        </ul>
        <p>arising out of or related to your use of, inability to use, or reliance upon the Service.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>16. Indemnification</h2>
        <p>You agree to indemnify, defend, and hold harmless PulseTrends and its operators from any claims, liabilities, damages, losses, expenses, or legal fees arising from:</p>
        <ul>
          <li>Your use of the Service</li>
          <li>Your violation of these Terms</li>
          <li>Your violation of any applicable law</li>
          <li>Your infringement of any third-party rights</li>
        </ul>

        <hr className="border-surface-300/40 my-6" />

        <h2>17. Changes to These Terms</h2>
        <p>We may update these Terms & Conditions at any time.</p>
        <p>Updated versions will be posted on this page with a revised "Last updated" date.</p>
        <p>Continued use of the Service following publication of updated Terms constitutes acceptance of the revised Terms.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>18. Governing Law</h2>
        <p>These Terms shall be governed by and construed in accordance with the laws of India.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>19. Dispute Resolution</h2>
        <p>Any dispute arising from or relating to these Terms or the Service shall be subject to the exclusive jurisdiction of the courts located in Bengaluru, Karnataka, India.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>20. Contact</h2>
        <p>For questions regarding these Terms & Conditions, contact:</p>
        <p><strong>Email:</strong> <a href="mailto:pulsetrendsin@gmail.com" className="text-brand hover:text-brand-light">pulsetrendsin@gmail.com</a></p>
      </div>
    </>
  );
}
