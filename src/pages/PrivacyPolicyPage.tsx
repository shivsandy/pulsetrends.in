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

        <p>PulseTrends ("we", "our", or "us") operates the website <strong>pulsetrends.in</strong> (the "Service"). This Privacy Policy explains what information we collect, how we use it, and the choices available to users regarding their information.</p>

        <div className="bg-surface-100 border border-surface-300/60 rounded-lg p-4 my-6">
          <h2 className="text-[15px] font-bold text-surface-white mt-0">Data Controller</h2>
          <p className="text-[13px] text-surface-800 mt-1">PulseTrends is the data controller responsible for personal information collected through the Service.</p>
          <p className="text-[13px] text-surface-800 mt-2">
            <strong>Contact:</strong><br />
            Email: <a href="mailto:pulsetrendsin@gmail.com" className="text-brand hover:text-brand-light">pulsetrendsin@gmail.com</a>
          </p>
        </div>

        <hr className="border-surface-300/40 my-6" />

        <h2>Information We Collect</h2>
        <p>We collect only the limited information necessary to operate and improve the Service.</p>

        <h3>Usage Data</h3>
        <p>We may collect anonymous or aggregated information about how visitors use the Service, including:</p>
        <ul>
          <li>Pages visited</li>
          <li>Referring websites</li>
          <li>Device and browser information</li>
          <li>Country or general geographic region</li>
          <li>Site performance and usage statistics</li>
        </ul>
        <p>This information is used solely for analytics and service improvement purposes.</p>

        <h3>Cookies</h3>
        <p>We use first-party cookies that are necessary for basic website functionality, including remembering cookie consent preferences and user settings.</p>
        <p>We do <strong>not</strong> use advertising cookies or cross-site tracking cookies.</p>

        <h3>Information You Voluntarily Provide</h3>
        <p>If you contact us by email or otherwise communicate with us, we may collect the information you choose to provide, including your name, email address, and the contents of your message.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>How We Use Information</h2>
        <p>We use information we collect to:</p>
        <ul>
          <li>Operate, maintain, and improve the Service</li>
          <li>Monitor website performance and usage trends</li>
          <li>Respond to inquiries and communications</li>
          <li>Protect the security and integrity of the Service</li>
          <li>Detect and prevent misuse or abuse</li>
          <li>Comply with legal obligations and enforce our policies</li>
        </ul>

        <hr className="border-surface-300/40 my-6" />

        <h2>Legal Bases for Processing</h2>
        <p>Where applicable, we process personal information on the following legal bases:</p>
        <ul>
          <li><strong>Legitimate interests</strong> in operating, securing, maintaining, and improving the Service</li>
          <li><strong>Consent</strong>, where you voluntarily provide information or consent is otherwise required</li>
          <li><strong>Legal obligations</strong>, where processing is necessary to comply with applicable laws and regulations</li>
        </ul>

        <hr className="border-surface-300/40 my-6" />

        <h2>Cookies</h2>
        <p>Cookies are small text files stored on your device.</p>
        <p>We use cookies only where necessary to:</p>
        <ul>
          <li>Remember your cookie preferences</li>
          <li>Maintain essential website functionality</li>
          <li>Improve user experience</li>
        </ul>
        <p>You can control or delete cookies through your browser settings. Disabling certain cookies may affect website functionality.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Third-Party Services</h2>
        <p>We rely on third-party providers to operate the Service. These providers may receive limited technical information as necessary to provide their services.</p>
        <p>Current providers include:</p>
        <ul>
          <li><strong>GitHub Pages</strong> — website hosting</li>
          <li><strong>Unsplash</strong> — article imagery and content delivery</li>
        </ul>
        <p>Each provider maintains its own privacy practices and policies.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Third-Party Links</h2>
        <p>The Service may contain links to third-party websites, services, or resources.</p>
        <p>We are not responsible for the privacy practices, content, or security of third-party websites. Users should review the privacy policies of any external websites they visit.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Data Sharing</h2>
        <p>We do <strong>not</strong> sell, rent, trade, or otherwise disclose personal information to advertising networks, data brokers, or other third parties for marketing purposes.</p>
        <p>We may disclose information only when:</p>
        <ul>
          <li>Required by law or legal process</li>
          <li>Necessary to protect our rights, users, or the public</li>
          <li>Required to investigate fraud, abuse, or security issues</li>
        </ul>

        <hr className="border-surface-300/40 my-6" />

        <h2>International Data Transfers</h2>
        <p>Some third-party service providers may process information in countries outside your country of residence.</p>
        <p>Where such transfers occur, we rely on the safeguards, security measures, and privacy commitments implemented by those providers.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Data Retention</h2>
        <p>We retain information only for as long as necessary to fulfill the purposes described in this Privacy Policy.</p>
        <p>Examples include:</p>
        <ul>
          <li>Analytics data may be retained in aggregated or anonymized form</li>
          <li>Email correspondence may be retained as necessary to respond to inquiries and maintain records</li>
          <li>Cookie preference data may remain until it expires or is deleted from your browser</li>
        </ul>
        <p>When information is no longer needed, we take reasonable steps to delete or anonymize it.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Data Security</h2>
        <p>We implement reasonable technical and organizational safeguards designed to protect information under our control from unauthorized access, disclosure, alteration, or destruction.</p>
        <p>However, no method of transmission over the Internet or electronic storage is completely secure. Accordingly, we cannot guarantee absolute security.</p>
        <p>If a data breach occurs affecting personal information, we will take actions required under applicable law.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Children's Privacy</h2>
        <p>The Service is not intended for children.</p>
        <p>We do not knowingly collect personal information from children in violation of applicable law. If you believe a child has provided personal information to us, please contact us so we can take appropriate action.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Your Rights</h2>
        <p>Depending on your jurisdiction and applicable law, you may have the right to:</p>
        <ul>
          <li>Request access to personal information we hold about you</li>
          <li>Request correction of inaccurate or incomplete information</li>
          <li>Request deletion of personal information</li>
          <li>Request restriction of certain processing activities</li>
          <li>Object to certain processing activities</li>
          <li>Withdraw consent where processing is based on consent</li>
          <li>Lodge a complaint with an appropriate regulatory authority</li>
        </ul>
        <p>To exercise any of these rights, contact us at:</p>
        <p><strong>Email:</strong> <a href="mailto:pulsetrendsin@gmail.com" className="text-brand hover:text-brand-light">pulsetrendsin@gmail.com</a></p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Indian Privacy Rights</h2>
        <p>Where applicable, individuals may exercise rights available under the <strong>Digital Personal Data Protection Act, 2023 (India)</strong> and other applicable laws by contacting us at <a href="mailto:pulsetrendsin@gmail.com" className="text-brand hover:text-brand-light">pulsetrendsin@gmail.com</a>.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Do Not Track Signals</h2>
        <p>Some web browsers provide a "Do Not Track" feature.</p>
        <p>Because there is currently no universally accepted standard for responding to such signals, the Service may not respond to Do Not Track requests.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Changes to This Privacy Policy</h2>
        <p>We may update this Privacy Policy from time to time.</p>
        <p>Any updates will be posted on this page with a revised "Last updated" date. Continued use of the Service after changes become effective constitutes acceptance of the updated Privacy Policy.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Governing Law</h2>
        <p>This Privacy Policy shall be governed by and interpreted in accordance with the laws of India, without regard to conflict of law principles.</p>

        <hr className="border-surface-300/40 my-6" />

        <h2>Contact</h2>
        <p>For privacy-related questions, requests, or concerns, contact:</p>
        <p><strong>Email:</strong> <a href="mailto:pulsetrendsin@gmail.com" className="text-brand hover:text-brand-light">pulsetrendsin@gmail.com</a></p>
      </div>
    </>
  );
}
