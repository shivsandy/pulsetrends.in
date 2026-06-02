import { Activity, TrendingUp, Brain, BarChart3 } from 'lucide-react';
import PageSeo from '../components/PageSeo';
import Breadcrumbs from '../components/Breadcrumbs';
import { ROUTES } from '../seo/routes';

export default function AboutPage() {
  return (
    <>
      <PageSeo
        meta={ROUTES.about}
        breadcrumbs={[
          { name: 'Home', path: '/' },
          { name: 'About', path: '/about' },
        ]}
      />
      <div className="max-w-3xl mx-auto page-content animate-fade-in">
        <Breadcrumbs items={[{ name: 'Home', path: '/' }, { name: 'About' }]} />
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-brand-muted flex items-center justify-center">
            <Activity className="w-5 h-5 text-brand" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-white">About PulseTrends</h1>
            <p className="text-[13px] text-surface-600">IPO & Crypto Intelligence Platform</p>
          </div>
        </div>
        <p>PulseTrends is a financial intelligence platform focused on IPOs, cryptocurrency airdrops, and market-moving news. Our goal is to help investors and market participants navigate complex information through structured research, AI-assisted analysis, and clear explanations.</p>

        <h2>Our Mission</h2>
        <p>Modern financial markets generate enormous amounts of information every day. Investors often struggle to separate meaningful signals from noise.</p>
        <p>PulseTrends was created to make market research more accessible by combining data aggregation, analytical frameworks, and artificial intelligence to deliver concise insights that help users understand opportunities, risks, and market developments more efficiently.</p>

        <h2>What We Offer</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-4">
          {[
            { icon: TrendingUp, title: 'IPO Intelligence', desc: 'Analysis of upcoming IPOs, including company overviews, business models, financial highlights, risk factors, valuation considerations, and AI-assisted scoring frameworks.' },
            { icon: Activity, title: 'Airdrop Radar', desc: 'Coverage of cryptocurrency airdrops, including eligibility requirements, participation guides, estimated rewards, project background, and risk assessments.' },
            { icon: Brain, title: 'AI News Analysis', desc: 'Summaries and analysis of significant market events, crypto developments, and industry news, enhanced with sentiment analysis and potential market impact assessments.' },
            { icon: BarChart3, title: 'Risk Metrics', desc: 'Structured risk evaluation frameworks that consider financial, operational, market, and technical factors to help users better understand potential risks.' },
          ].map((f) => (
            <div key={f.title} className="bg-surface-100 border border-surface-300/60 rounded-lg p-4">
              <f.icon className="w-5 h-5 text-brand mb-2" />
              <h3 className="text-[14px] font-semibold text-surface-white mb-1">{f.title}</h3>
              <p className="text-[13px] text-surface-700 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>

        <h2>Our Technology</h2>
        <p>PulseTrends uses modern AI and data-processing technologies to assist with research, summarization, and analytical workflows.</p>
        <p>Our platform incorporates multiple AI models, market data sources, public information, and analytical methodologies to generate research outputs and scoring frameworks. AI-generated content may be reviewed, refined, or supplemented with additional research before publication.</p>

        <h2>Our Approach</h2>
        <p>We believe effective market research should be:</p>
        <ul>
          <li><strong>Transparent</strong> — Methodologies, assumptions, and limitations should be clearly disclosed whenever possible.</li>
          <li><strong>Accessible</strong> — High-quality financial information should be understandable to both new and experienced investors.</li>
          <li><strong>Evidence-Based</strong> — Analysis should be grounded in publicly available information and verifiable data.</li>
          <li><strong>Independent</strong> — Editorial decisions should not be influenced by compensation from covered projects or companies.</li>
        </ul>

        <h2>Important Disclaimer</h2>
        <p>PulseTrends provides information, research, commentary, and analytical content for educational and informational purposes only.</p>
        <p>Nothing published on this platform constitutes financial advice, investment advice, legal advice, tax advice, or a recommendation to buy, sell, or hold any security, cryptocurrency, or other financial asset.</p>
        <p>Financial markets involve risk, including the possible loss of capital. Users should conduct their own research and, where appropriate, consult qualified professional advisers before making investment decisions.</p>
        <p>While we strive for accuracy, we do not guarantee the completeness, accuracy, or timeliness of any information published on the platform.</p>
      </div>
    </>
  );
}
