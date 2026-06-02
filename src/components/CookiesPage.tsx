import { Cookie } from 'lucide-react';

export default function CookiesPage() {
  return (
    <div className="max-w-3xl mx-auto page-content animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-brand-muted flex items-center justify-center">
          <Cookie className="w-5 h-5 text-brand" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-surface-white">Cookie Policy</h1>
          <p className="text-[13px] text-surface-600">Last updated: 2 June 2026</p>
        </div>
      </div>

      <h2>What Are Cookies</h2>
      <p>Cookies are small text files stored on your device when you visit a website. They help us remember your preferences, understand how you use our platform, and improve your experience.</p>

      <h2>How We Use Cookies</h2>
      <p>We use cookies for the following purposes:</p>
      <ul>
        <li><strong>Necessary:</strong> Essential for the website to function properly. These cannot be disabled.</li>
        <li><strong>Analytics:</strong> Help us understand how visitors interact with our site, which pages are most popular, and how users navigate through the platform.</li>
        <li><strong>Marketing:</strong> Used to deliver relevant advertisements and measure the effectiveness of our marketing campaigns.</li>
      </ul>

      <h2>Types of Cookies We Use</h2>
      <p><strong>Session Cookies:</strong> Temporary cookies that expire when you close your browser. Used for basic functionality.</p>
      <p><strong>Persistent Cookies:</strong> Remain on your device for a set period or until deleted. Used to remember your preferences.</p>
      <p><strong>Third-Party Cookies:</strong> Set by services we use (e.g., analytics providers) to collect anonymous usage data.</p>

      <h2>Managing Cookies</h2>
      <p>You can control cookie preferences through our cookie consent banner or by adjusting your browser settings. Note that disabling certain cookies may affect the functionality of our platform.</p>
      <p>Most browsers allow you to:</p>
      <ul>
        <li>View cookies stored on your device</li>
        <li>Block cookies from specific sites</li>
        <li>Clear all cookies when closing your browser</li>
        <li>Enable private browsing modes</li>
      </ul>

      <h2>Changes to This Policy</h2>
      <p>We may update this Cookie Policy periodically. Changes will be posted on this page with an updated effective date.</p>

      <h2>Contact</h2>
      <p>For questions about our use of cookies, contact us at privacy@pulsetrends.in.</p>
    </div>
  );
}
