---
layout: default
title: Home
---

{% assign posts = site.posts %}

{% if posts.size > 0 %}
{% assign featured = posts.first %}
<div class="hero-featured reveal">
  <a href="{{ featured.url | relative_url }}">
    <div class="hero-img-wrap">
      {% if featured.image %}
      <img src="{{ featured.image }}" alt="{{ featured.title }}" class="hero-featured-img" loading="lazy">
      {% else %}
      <div class="hero-featured-img" style="background: linear-gradient(135deg, #1a1a2e, #e74c3c);"></div>
      {% endif %}
    </div>
    <div class="hero-featured-body">
      {% if featured.tags.size > 0 %}
      <span class="cat-tag">{{ featured.tags.first }}</span>
      {% endif %}
      <h2>{{ featured.title }}</h2>
      <p>{{ featured.excerpt | strip_html | truncatewords: 40 }}</p>
      <span class="meta">{{ featured.date | date: "%B %d, %Y" }}</span>
    </div>
  </a>
</div>
{% endif %}

<h2 class="section-title">Latest Articles</h2>

<div class="post-grid">
  {% for post in posts offset:1 limit:10 %}
  <article class="post-card reveal" style="transition-delay: var(--card-delay, 0s)">
    <a href="{{ post.url | relative_url }}">
      <div class="card-img-wrap">
        {% if post.image %}
        <img src="{{ post.image }}" alt="{{ post.title }}" class="post-card-img" loading="lazy">
        {% else %}
        <div class="post-card-img" style="background: linear-gradient(135deg, #16213e, #e74c3c);"></div>
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

{% if posts.size == 0 %}
<div class="page-content reveal">
  <h1>Welcome to PulseTrends</h1>
  <p>Your daily source for trending insights across AI, technology, politics, finance, weather, and business. Articles are generated fresh every day — check back soon for the latest content!</p>
</div>
{% endif %}
