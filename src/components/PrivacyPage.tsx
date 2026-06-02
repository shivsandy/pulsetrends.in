import { Shield } from 'lucide-react';

export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto page-content animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-brand-muted flex items-center justify-center">
          <Shield className="w-5 h-5 text-brand" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-surface-white">Privacy Policy</h1>
          <p className="text-[13px] text-surface-600">Last updated: 2 June 2026</p>
        </div>
      </div>

      <h2>Introduction</h2>
      <p>PulseTrends ("we", "our", "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our platform.</p>

      <h2>Information We Collect</h2>
      <p><strong>Personal Data:</strong> We may collect personally identifiable information such as your name and email address when you contact us or subscribe to our newsletter.</p>
      <p><strong>Usage Data:</strong> We automatically collect certain information when you visit our platform, including your IP address, browser type, operating system, referring URLs, and pages viewed.</p>
      <p><strong>Cookies:</strong> We use cookies and similar tracking technologies to enhance your experience. You can control cookie preferences through our cookie settings.</p>

      <h2>How We Use Your Information</h2>
      <ul>
        <li>To provide, operate, and maintain our platform</li>
        <li>To improve, personalise, and expand our services</li>
        <li>To communicate with you, including for customer support</li>
        <li>To analyse usage patterns and optimise user experience</li>
        <li>To detect, prevent, and address technical issues</li>
      </ul>

      <h2>Data Sharing</h2>
      <p>We do not sell your personal information. We may share data with trusted third-party service providers who assist us in operating our platform (e.g., hosting, analytics), subject to confidentiality agreements.</p>

      <h2>Data Security</h2>
      <p>We implement industry-standard security measures including encryption, access controls, and regular security audits. However, no method of transmission over the Internet is 100% secure.</p>

      <h2>Your Rights</h2>
      <p>You have the right to access, correct, or delete your personal data. You may also object to or restrict certain processing activities. To exercise these rights, contact us at privacy@pulsetrends.in.</p>

      <h2>Changes to This Policy</h2>
      <p>We may update this Privacy Policy periodically. Changes will be posted on this page with an updated effective date. We encourage you to review this policy regularly.</p>

      <h2>Contact</h2>
      <p>For questions about this Privacy Policy, contact us at privacy@pulsetrends.in.</p>
    </div>
  );
}
