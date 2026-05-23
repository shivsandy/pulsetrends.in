---
layout: default
title: Home
---

# {{ site.tagline }}

Welcome to **{{ site.title }}**. We provide expert insights on the latest trending topics across finance, technology, business, health, and more.

<div class="post-grid">
  {% for post in site.posts limit:12 %}
  <article class="post-card">
    <a href="{{ post.url | relative_url }}">
      {% if post.image %}
      <img src="{{ post.image }}" alt="{{ post.title }}" loading="lazy">
      {% endif %}
      <h3>{{ post.title }}</h3>
      <p>{{ post.excerpt | strip_html | truncatewords: 30 }}</p>
      <span class="read-more">Read More &rarr;</span>
    </a>
  </article>
  {% endfor %}
</div>
