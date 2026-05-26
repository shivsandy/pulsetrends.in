---
layout: default
title: Home
description: "PulseTrends — AI, Crypto, Stocks & Daily Trending News. Expert analysis on technology, cryptocurrency, politics, finance, weather, and business."
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

<div class="home-three-col">

  <!-- LEFT COLUMN: 10 Compact Horizontal Cards -->
  <aside class="home-col-left">
    {% assign left_posts = posts | slice: 0, 10 %}
    {% for post in left_posts %}
    <article class="left-card">
      <a href="{{ post.url | relative_url }}">
        <div class="left-card-img">
          {% if post.image %}
          <img src="{{ post.image | replace: 'w=1200', 'w=200' | replace: 'w=800', 'w=200' }}&auto=format&q=35" alt="{{ post.title }}" width="200" height="200" loading="lazy" decoding="async" fetchpriority="low">
          {% else %}
          <div class="img-fallback"><span class="fallback-icon"></span></div>
          {% endif %}
        </div>
        <div class="left-card-body">
          {% if post.tags.size > 0 %}<span class="cat-tag">{{ post.tags.first }}</span>{% endif %}
          <h3>{{ post.title | truncate: 50 }}</h3>
          <span class="excerpt">{{ post.excerpt | strip_html | truncatewords: 12 }}</span>
          <span class="meta">{{ post.date | date: "%b %d, %Y" }}</span>
        </div>
      </a>
    </article>
    {% endfor %}
  </aside>

  <!-- CENTER COLUMN -->
  <main class="home-col-center">

    <!-- HERO: Featured Article -->
    {% assign hero_post = posts.first %}
    {% if hero_post %}
    <article class="hero-card">
      <a href="{{ hero_post.url | relative_url }}">
        {% if hero_post.image %}
        <img src="{{ hero_post.image }}&auto=format&q=60" alt="{{ hero_post.title }}" class="hero-card-img" width="1200" height="675" loading="eager" fetchpriority="high" itemprop="image">
        {% endif %}
        <div class="section-card-body">
          {% if hero_post.tags.size > 0 %}<span class="cat-tag">{{ hero_post.tags.first }}</span>{% endif %}
          <h3 class="hero-title">{{ hero_post.title }}</h3>
          <span class="excerpt">{{ hero_post.excerpt | strip_html | truncatewords: 25 }}</span>
          <span class="meta">{{ hero_post.date | date: "%B %d, %Y" }}</span>
        </div>
      </a>
    </article>
    {% endif %}

    <!-- LATEST ARTICLES -->
    {% assign latest_posts = posts | slice: 1, 16 %}
    <section class="content-section">
      <h2>Latest Articles</h2>
      <div class="section-grid" id="latestGrid">
        {% for post in latest_posts %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=50" alt="{{ post.title }}" width="400" height="250" loading="lazy" decoding="async" fetchpriority="low">
              {% else %}
              <div class="img-fallback"><span class="fallback-icon"></span></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              {% if post.tags.size > 0 %}<span class="cat-tag">{{ post.tags.first }}</span>{% endif %}
              <h3>{{ post.title }}</h3>
              <span class="excerpt">{{ post.excerpt | strip_html | truncatewords: 12 }}</span>
              <span class="meta">{{ post.date | date: "%b %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
      <div class="pagination" id="latestPagination"></div>
    </section>

    <!-- TRENDING -->
    {% assign trending_posts = posts | slice: 0, 4 %}
    <section class="content-section">
      <h2>Trending</h2>
      <div class="section-grid">
        {% for post in trending_posts %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=50" alt="{{ post.title }}" width="400" height="250" loading="lazy" decoding="async" fetchpriority="low">
              {% else %}
              <div class="img-fallback"><span class="fallback-icon"></span></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              {% if post.tags.size > 0 %}<span class="cat-tag">{{ post.tags.first }}</span>{% endif %}
              <h3>{{ post.title }}</h3>
              <span class="excerpt">{{ post.excerpt | strip_html | truncatewords: 12 }}</span>
              <span class="meta">{{ post.date | date: "%b %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
    </section>

    <!-- TECH NEWS -->
    {% if tech_posts.size > 0 %}
    <section class="content-section">
      <h2>Tech News</h2>
      <div class="section-grid">
        {% for post in tech_posts limit:8 %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=50" alt="{{ post.title }}" width="400" height="250" loading="lazy" decoding="async" fetchpriority="low">
              {% else %}
              <div class="img-fallback"><span class="fallback-icon"></span></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              <span class="cat-tag">Tech</span>
              <h3>{{ post.title }}</h3>
              <span class="meta">{{ post.date | date: "%b %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
    </section>
    {% endif %}

    <!-- MARKETS & FINANCE -->
    {% if market_posts.size > 0 %}
    <section class="content-section">
      <h2>Markets & Finance</h2>
      <div class="section-grid">
        {% for post in market_posts limit:8 %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=50" alt="{{ post.title }}" width="400" height="250" loading="lazy" decoding="async" fetchpriority="low">
              {% else %}
              <div class="img-fallback"><span class="fallback-icon"></span></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              {% if post.tags.size > 0 %}<span class="cat-tag">{{ post.tags.first }}</span>{% endif %}
              <h3>{{ post.title }}</h3>
              <span class="meta">{{ post.date | date: "%b %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
    </section>
    {% endif %}

    <!-- IPO NEWS -->
    {% if ipo_posts.size > 0 %}
    <section class="content-section">
      <h2>IPO News</h2>
      <div class="section-grid">
        {% for post in ipo_posts limit:8 %}
        <article class="section-card">
          <a href="{{ post.url | relative_url }}">
            <div class="section-card-img">
              {% if post.image %}
              <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}&auto=format&q=50" alt="{{ post.title }}" width="400" height="250" loading="lazy" decoding="async" fetchpriority="low">
              {% else %}
              <div class="img-fallback"><span class="fallback-icon"></span></div>
              {% endif %}
            </div>
            <div class="section-card-body">
              <span class="cat-tag">IPO</span>
              <h3>{{ post.title }}</h3>
              <span class="meta">{{ post.date | date: "%b %d, %Y" }}</span>
            </div>
          </a>
        </article>
        {% endfor %}
      </div>
    </section>
    {% endif %}

  </main>

  <!-- RIGHT COLUMN: 8 IPO Stock Cards -->
  <aside class="home-col-right">
    <div class="ipo-section-title">IPO Stocks Watchlist</div>
    <div class="ipo-stock-list" id="ipoStockList"></div>
    <a href="/ipodashboard/" class="ipo-view-more" title="View complete IPO dashboard" aria-label="View full IPO dashboard">View More &rarr;</a>
  </aside>

</div>

{% elsif posts.size == 0 %}
<div class="page-content">
  <h1>Welcome to PulseTrends</h1>
  <p>Your daily source for trending insights across AI, technology, politics, finance, weather, and business. Articles are generated fresh every day — check back soon for the latest content!</p>
</div>
{% endif %}
