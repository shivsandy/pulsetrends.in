---
layout: default
title: Home
---

{% assign posts = site.posts %}

{% if posts.size > 0 %}
{% assign featured = posts.first %}
<article class="featured-post">
  <a href="{{ featured.url | relative_url }}">
    {% if featured.image %}
    <img src="{{ featured.image }}" alt="{{ featured.title }}" class="featured-post-img" loading="lazy">
    {% else %}
    <div class="featured-post-img" style="background: linear-gradient(135deg, #1a1a2e, #e74c3c);"></div>
    {% endif %}
    <div class="featured-post-body">
      {% if featured.tags.size > 0 %}
      <span class="cat-tag">{{ featured.tags.first }}</span>
      {% endif %}
      <h2>{{ featured.title }}</h2>
      <p>{{ featured.excerpt | strip_html | truncatewords: 40 }}</p>
      <span class="meta">{{ featured.date | date: "%B %d, %Y" }}</span>
    </div>
  </a>
</article>
{% endif %}

<h2 class="section-title">Latest Articles</h2>

<div class="post-grid">
  {% for post in posts offset:1 limit:10 %}
  <article class="post-card">
    <a href="{{ post.url | relative_url }}">
      {% if post.image %}
      <img src="{{ post.image }}" alt="{{ post.title }}" class="post-card-img" loading="lazy">
      {% else %}
      <div class="post-card-img" style="background: linear-gradient(135deg, #16213e, #e74c3c);"></div>
      {% endif %}
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
<div class="page-content">
  <h1>Welcome to PulseTrends</h1>
  <p>Your daily source for trending insights across AI, technology, politics, finance, weather, and business. Articles are generated fresh every day — check back soon for the latest content!</p>
</div>
{% endif %}
