---
layout: default
title: Home
---

{% assign posts = site.posts %}
{% assign tech_posts = site.posts | where_exp: "p", "p.tags contains 'tech'" %}
{% assign stocks_posts = site.posts | where_exp: "p", "p.tags contains 'stocks'" %}
{% assign finance_posts = site.posts | where_exp: "p", "p.tags contains 'finance'" %}
{% assign crypto_posts = site.posts | where_exp: "p", "p.tags contains 'crypto'" %}
{% assign market_posts = stocks_posts | concat: finance_posts | concat: crypto_posts %}
{% assign ipo_posts = site.posts | where_exp: "p", "p.tags contains 'ipos'" %}

<h1 class="sr-only">{{ site.title }}</h1>

{% if posts.size > 0 %}

<div class="home-four-col">

  <!-- LEFT COLUMN: Recent Articles (8-10 mixed posts) -->
  <aside class="home-col-left">
    {% assign recent_limit = 5 %}
    {% for post in posts limit:5 %}
    <article class="left-card">
      <a href="{{ post.url | relative_url }}">
        <div class="left-card-img">
          {% if post.image %}
          <img src="{{ post.image | replace: 'w=1200', 'w=200' | replace: 'w=800', 'w=200' }}&auto=format&q=50" alt="{{ post.title }}" width="200" height="150" loading="lazy" decoding="async" sizes="(max-width: 768px) 100vw, 200px">
          {% else %}
          <div style="background: linear-gradient(135deg, #16213e, #e01a4f); width: 100%; height: 100%;"></div>
          {% endif %}
        </div>
        <div class="left-card-body">
          {% if post.tags.size > 0 %}
          <span class="cat-tag">{{ post.tags.first }}</span>
          {% endif %}
          <h3>{{ post.title | truncate: 50 }}</h3>
          <span class="meta">{{ post.date | date: "%b %d" }}</span>
        </div>
      </a>
    </article>
    {% endfor %}
    
    {% assign shuffled = site.posts | slice: 5, 20 | shuffle | slice: 0, 5 %}
    {% for post in shuffled %}
    <article class="left-card">
      <a href="{{ post.url | relative_url }}">
        <div class="left-card-img">
          {% if post.image %}
          <img src="{{ post.image | replace: 'w=1200', 'w=200' | replace: 'w=800', 'w=200' }}&auto=format&q=50" alt="{{ post.title }}" width="200" height="150" loading="lazy" decoding="async" sizes="(max-width: 768px) 100vw, 200px">
          {% else %}
          <div style="background: linear-gradient(135deg, #16213e, #e01a4f); width: 100%; height: 100%;"></div>
          {% endif %}
        </div>
        <div class="left-card-body">
          {% if post.tags.size > 0 %}
          <span class="cat-tag">{{ post.tags.first }}</span>
          {% endif %}
          <h3>{{ post.title | truncate: 50 }}</h3>
          <span class="meta">{{ post.date | date: "%b %d" }}</span>
        </div>
      </a>
    </article>
    {% endfor %}
  </aside>

  <!-- CENTER MAIN COLUMN: Hero + Latest + Sections -->
  <main class="home-col-center-main">

    <!-- HERO FEATURED ARTICLE -->
    {% assign primary = posts.first %}
    {% if primary %}
    <article class="hero-card" style="margin-bottom: 32px;">
      <a href="{{ primary.url | relative_url }}">
        <div class="hero-img-wrap">
          {% if primary.image %}
          <img src="{{ primary.image }}&auto=format&q=75" alt="{{ primary.title }}" class="hero-img" width="1200" height="675" loading="eager" fetchpriority="high" sizes="(max-width: 768px) 100vw, (max-width: 1200px) 75vw, 50vw">
          {% else %}
          <div class="hero-img-placeholder" style="background: linear-gradient(135deg, #1a1a2e, #e01a4f);"></div>
          {% endif %}
        </div>
        <div class="hero-content">
          {% if primary.tags.size > 0 %}
          <span class="hero-tag">{{ primary.tags.first }}</span>
          {% endif %}
          <h2 class="hero-title">{{ primary.title }}</h2>
          <p class="hero-desc">{{ primary.excerpt | strip_html | truncatewords: 35 }}</p>
          <span class="hero-meta">{{ primary.date | date: "%B %d, %Y" }}</span>
        </div>
      </a>
    </article>
    {% endif %}

    <!-- LATEST ARTICLES SECTION -->
    {% assign latest_posts = posts | slice: 1, 24 %}
    <section class="content-section">
      <h2>Latest Articles</h2>
      <div class="section-grid" id="latestGrid">
        {% for post in latest_posts %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=75" alt="{{ post.title }}" width="400" height="267" loading="lazy" decoding="async" sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 400px">
              {% else %}
              <div style="background: linear-gradient(135deg, #16213e, #e01a4f); width: 100%; height: 100%;"></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              {% if post.tags.size > 0 %}
              <span class="cat-tag">{{ post.tags.first }}</span>
              {% endif %}
              <h3>{{ post.title }}</h3>
              <p style="font-size: 0.8em; color: var(--text-light); flex: 1;">{{ post.excerpt | strip_html | truncatewords: 15 }}</p>
              <span class="meta">{{ post.date | date: "%B %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
      <div class="pagination" id="latestPagination"></div>
    </section>

    <!-- TRENDING SECTION -->
    {% assign trending_posts = posts | slice: 0, 4 %}
    <section class="content-section">
      <h2>🔥 Trending Now</h2>
      <div class="section-grid">
        {% for post in trending_posts %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=75" alt="{{ post.title }}" width="400" height="267" loading="lazy" decoding="async" sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 400px">
              {% else %}
              <div style="background: linear-gradient(135deg, #16213e, #e01a4f); width: 100%; height: 100%;"></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              {% if post.tags.size > 0 %}
              <span class="cat-tag">{{ post.tags.first }}</span>
              {% endif %}
              <h3>{{ post.title }}</h3>
              <span class="meta">{{ post.date | date: "%B %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
    </section>

    <!-- TECH NEWS SECTION -->
    {% if tech_posts.size > 0 %}
    <section class="content-section">
      <h2>💻 Tech News</h2>
      <div class="section-grid" id="techGrid">
        {% for post in tech_posts limit:8 %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=75" alt="{{ post.title }}" width="400" height="267" loading="lazy" decoding="async" sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 400px">
              {% else %}
              <div style="background: linear-gradient(135deg, #16213e, #e01a4f); width: 100%; height: 100%;"></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              <span class="cat-tag">Tech</span>
              <h3>{{ post.title }}</h3>
              <span class="meta">{{ post.date | date: "%B %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
      <div class="pagination" id="techPagination"></div>
    </section>
    {% endif %}

    <!-- MARKETS & FINANCE SECTION -->
    {% if market_posts.size > 0 %}
    <section class="content-section">
      <h2>📈 Markets & Finance</h2>
      <div class="section-grid" id="marketsGrid">
        {% for post in market_posts limit:8 %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=75" alt="{{ post.title }}" width="400" height="267" loading="lazy" decoding="async" sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 400px">
              {% else %}
              <div style="background: linear-gradient(135deg, #16213e, #e01a4f); width: 100%; height: 100%;"></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              {% if post.tags.size > 0 %}
              <span class="cat-tag">{{ post.tags.first }}</span>
              {% endif %}
              <h3>{{ post.title }}</h3>
              <span class="meta">{{ post.date | date: "%B %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
      <div class="pagination" id="marketsPagination"></div>
    </section>
    {% endif %}

    <!-- IPO NEWS SECTION -->
    {% if ipo_posts.size > 0 %}
    <section class="content-section">
      <h2>🚀 IPO News</h2>
      <div class="section-grid" id="ipoGrid">
        {% for post in ipo_posts limit:8 %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=75" alt="{{ post.title }}" width="400" height="267" loading="lazy" decoding="async" sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 400px">
              {% else %}
              <div style="background: linear-gradient(135deg, #16213e, #e01a4f); width: 100%; height: 100%;"></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              <span class="cat-tag">IPO</span>
              <h3>{{ post.title }}</h3>
              <span class="meta">{{ post.date | date: "%B %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
      <div class="pagination" id="ipoPagination"></div>
    </section>
    {% endif %}

  </main>

  <!-- CENTER-RIGHT COLUMN: Secondary Grid (optional) -->
  <aside class="home-col-center-right" style="display: none;"></aside>

  <!-- RIGHT COLUMN: IPO Dashboard (sticky) -->
  <aside class="home-col-right">
    <div class="ipo-widget">
      <div class="ipo-widget-header">
        <span class="ipo-widget-icon">📈</span>
        <h3>IPO Dashboard</h3>
      </div>
      <div class="ipo-widget-body">
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Upcoming IPOs</span>
          <span class="ipo-stat-badge status-upcoming" id="upcomingBadge">—</span>
        </a>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Open IPOs</span>
          <span class="ipo-stat-badge status-open" id="openBadge">—</span>
        </a>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Closing Soon</span>
          <span class="ipo-stat-badge status-closing" id="closingBadge">—</span>
        </a>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Recently Listed</span>
          <span class="ipo-stat-badge status-listed" id="listedBadge">—</span>
        </a>
        <div class="ipo-divider"></div>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">IPO GMP</span>
          <span class="ipo-stat-badge">View →</span>
        </a>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">IPO Status</span>
          <span class="ipo-stat-badge">Check →</span>
        </a>
      </div>
      <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-widget-cta">View All IPOs →</a>
    </div>

    <!-- IPO CARDS BELOW WIDGET -->
    <div class="ipo-cards-container" id="ipoCardsContainer"></div>
  </aside>

</div>

{% elsif posts.size == 0 %}
<div class="page-content">
  <h1>Welcome to PulseTrends</h1>
  <p>Your daily source for trending insights across AI, technology, politics, finance, weather, and business. Articles are generated fresh every day — check back soon for the latest content!</p>
</div>
{% endif %}
