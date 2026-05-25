---
layout: default
title: Home
---

{% assign posts = site.posts %}

<h1 class="sr-only">{{ site.title }}</h1>

{% if posts.size > 0 %}
{% assign primary = posts.first %}
{% assign secondary1 = posts[1] %}
{% assign secondary2 = posts[2] %}

<div class="home-three-col">

  <div class="home-col-left">
    <article class="hero-card">
      <a href="{{ primary.url | relative_url }}">
        <div class="hero-img-wrap">
          {% if primary.image %}
          <img src="{{ primary.image }}&auto=format" alt="{{ primary.title }}" class="hero-img" width="1200" height="675" loading="eager" fetchpriority="high">
          {% else %}
          <div class="hero-img-placeholder" style="background: linear-gradient(135deg, #1a1a2e, #e01a4f);"></div>
          {% endif %}
        </div>
        <div class="hero-content">
          {% if primary.tags.size > 0 %}
          <span class="hero-tag">{{ primary.tags.first }}</span>
          {% endif %}
          <h2 class="hero-title">{{ primary.title }}</h2>
          <p class="hero-desc">{{ primary.excerpt | strip_html | truncatewords: 30 }}</p>
          <span class="hero-meta">{{ primary.date | date: "%B %d, %Y" }}</span>
        </div>
      </a>
    </article>
  </div>

  <div class="home-col-center">
    <div class="side-stack">
      <div class="side-card">
        <a href="{{ secondary1.url | relative_url }}">
          <div class="side-img-wrap">
            {% if secondary1.image %}
            <img src="{{ secondary1.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format" alt="{{ secondary1.title }}" width="400" height="267" loading="lazy" decoding="async">
            {% else %}
            <div class="side-img-placeholder" style="background: linear-gradient(135deg, #16213e, #e01a4f);"></div>
            {% endif %}
          </div>
          <div class="side-body">
            {% if secondary1.tags.size > 0 %}
            <span class="cat-tag">{{ secondary1.tags.first }}</span>
            {% endif %}
            <h3>{{ secondary1.title }}</h3>
            <span class="meta">{{ secondary1.date | date: "%B %d, %Y" }}</span>
          </div>
        </a>
      </div>
      <div class="side-card">
        <a href="{{ secondary2.url | relative_url }}">
          <div class="side-img-wrap">
            {% if secondary2.image %}
            <img src="{{ secondary2.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format" alt="{{ secondary2.title }}" width="400" height="267" loading="lazy" decoding="async">
            {% else %}
            <div class="side-img-placeholder" style="background: linear-gradient(135deg, #16213e, #e01a4f);"></div>
            {% endif %}
          </div>
          <div class="side-body">
            {% if secondary2.tags.size > 0 %}
            <span class="cat-tag">{{ secondary2.tags.first }}</span>
            {% endif %}
            <h3>{{ secondary2.title }}</h3>
            <span class="meta">{{ secondary2.date | date: "%B %d, %Y" }}</span>
          </div>
        </a>
      </div>
    </div>

    <h2 class="section-title" id="latestSection" style="scroll-margin-top:70px">Latest Articles</h2>

    <div class="post-grid" id="postGrid">
      {% for post in posts offset:4 limit:24 %}
      <article class="post-card">
        <a href="{{ post.url | relative_url }}">
          <div class="card-img-wrap">
            {% if post.image %}
            <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format" alt="{{ post.title }}" class="post-card-img" width="400" height="267" loading="lazy" decoding="async">
            {% else %}
            <div class="post-card-img" style="background: linear-gradient(135deg, #16213e, #e01a4f);"></div>
            {% endif %}
          </div>
          <div class="post-card-body">
            {% if post.tags.size > 0 %}
            <span class="cat-tag">{{ post.tags.first }}</span>
            {% endif %}
            <h3>{{ post.title }}</h3>
            <p>{{ post.excerpt | strip_html | truncatewords: 22 }}</p>
            <span class="meta">{{ post.date | date: "%B %d, %Y" }}</span>
          </div>
        </a>
      </article>
      {% endfor %}
    </div>

    <div class="pagination" id="pagination"></div>
  </div>

  <div class="home-col-right">
    <div class="ipo-widget">
      <div class="ipo-widget-header">
        <span class="ipo-widget-icon">📈</span>
        <h3>IPO Dashboard</h3>
      </div>
      <div class="ipo-widget-body">
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Upcoming IPOs</span>
          <span class="ipo-stat-badge status-upcoming">—</span>
        </a>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Open IPOs</span>
          <span class="ipo-stat-badge status-open">—</span>
        </a>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Closing Soon</span>
          <span class="ipo-stat-badge status-closing">—</span>
        </a>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Recently Listed</span>
          <span class="ipo-stat-badge status-listed">—</span>
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
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Price Band</span>
          <span class="ipo-stat-badge">Check →</span>
        </a>
        <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-stat">
          <span class="ipo-stat-label">Listing Date</span>
          <span class="ipo-stat-badge">Check →</span>
        </a>
      </div>
      <a href="{{ '/ipodashboard/' | relative_url }}" class="ipo-widget-cta">View All IPOs →</a>
    </div>
  </div>

</div>

{% elsif posts.size == 0 %}
<div class="page-content">
  <h1>Welcome to PulseTrends</h1>
  <p>Your daily source for trending insights across AI, technology, politics, finance, weather, and business. Articles are generated fresh every day — check back soon for the latest content!</p>
</div>
{% endif %}
