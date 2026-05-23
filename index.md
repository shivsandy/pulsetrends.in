---
layout: default
title: Home
---

<div class="hero">
  <h1>Trending Insights, Delivered Daily</h1>
  <p>Expert analysis on AI, technology, politics, finance, weather, and more — curated and published every day.</p>
  <div class="hero-categories">
    <span class="category-badge">AI</span>
    <span class="category-badge">Technology</span>
    <span class="category-badge">Politics</span>
    <span class="category-badge">Finance</span>
    <span class="category-badge">Weather</span>
    <span class="category-badge">Business</span>
  </div>
</div>

<div class="container">
  <h2 class="section-title">Latest Articles</h2>

  <div class="post-grid">
    {% for post in site.posts limit:18 %}
    <article class="post-card">
      <a href="{{ post.url | relative_url }}">
        {% if post.image %}
        <img src="{{ post.image }}" alt="{{ post.title }}" class="post-card-img" loading="lazy">
        {% else %}
        <div class="post-card-img" style="background: linear-gradient(135deg, #2563eb, #7c3aed);"></div>
        {% endif %}
        <div class="post-card-body">
          {% if post.tags.size > 0 %}
          <div class="post-card-tags">
            {% for tag in post.tags limit:3 %}
            <span class="post-card-tag">{{ tag }}</span>
            {% endfor %}
          </div>
          {% endif %}
          <h3>{{ post.title }}</h3>
          <p>{{ post.excerpt | strip_html | truncatewords: 25 }}</p>
          <span class="read-more">Read More &rarr;</span>
        </div>
      </a>
    </article>
    {% endfor %}
  </div>
</div>
