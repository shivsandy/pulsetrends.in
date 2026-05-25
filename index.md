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
<div class="template-grid-tall">
  <div class="display-card large primary">
    <a href="{{ primary.url | relative_url }}">
      <div class="dc-img-wrap">
        {% if primary.image %}
        <img src="{{ primary.image }}" alt="{{ primary.title }}" class="dc-img" loading="eager" fetchpriority="high">
        {% else %}
        <div class="dc-img" style="background: linear-gradient(135deg, #1a1a2e, #e01a4f);"></div>
        {% endif %}
        <div class="dc-img-overlay"></div>
      </div>
      <div class="dc-content">
        {% if primary.tags.size > 0 %}
        <span class="cat-tag">{{ primary.tags.first }}</span>
        {% endif %}
        <h2>{{ primary.title }}</h2>
        <p>{{ primary.excerpt | strip_html | truncatewords: 30 }}</p>
        <span class="meta">{{ primary.date | date: "%B %d, %Y" }}</span>
      </div>
    </a>
  </div>

  <div class="right-stack">
    <div class="display-card large secondary">
      <a href="{{ secondary1.url | relative_url }}">
        <div class="dc-img-wrap">
          {% if secondary1.image %}
          <img src="{{ secondary1.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}" alt="{{ secondary1.title }}" class="dc-img" loading="lazy" decoding="async">
          {% else %}
          <div class="dc-img" style="background: linear-gradient(135deg, #16213e, #e01a4f);"></div>
          {% endif %}
        </div>
        <div class="dc-content">
          {% if secondary1.tags.size > 0 %}
          <span class="cat-tag">{{ secondary1.tags.first }}</span>
          {% endif %}
          <h3>{{ secondary1.title }}</h3>
          <span class="meta">{{ secondary1.date | date: "%B %d, %Y" }}</span>
        </div>
      </a>
    </div>

    <div class="display-card large secondary">
      <a href="{{ secondary2.url | relative_url }}">
        <div class="dc-img-wrap">
          {% if secondary2.image %}
          <img src="{{ secondary2.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}" alt="{{ secondary2.title }}" class="dc-img" loading="lazy" decoding="async">
          {% else %}
          <div class="dc-img" style="background: linear-gradient(135deg, #16213e, #e01a4f);"></div>
          {% endif %}
        </div>
        <div class="dc-content">
          {% if secondary2.tags.size > 0 %}
          <span class="cat-tag">{{ secondary2.tags.first }}</span>
          {% endif %}
          <h3>{{ secondary2.title }}</h3>
          <span class="meta">{{ secondary2.date | date: "%B %d, %Y" }}</span>
        </div>
      </a>
    </div>
  </div>
</div>

{% assign trending = site.posts | slice: 3, 8 %}
{% if trending.size > 0 %}
<div class="trending-section">
  <div class="trending-header">
    <h2>Best Reads</h2>
    <a href="{{ '/search/' | relative_url }}" class="see-more">See More →</a>
  </div>
  <div class="trending-scroll">
    {% for post in trending %}
    <div class="trending-card">
      <a href="{{ post.url | relative_url }}">
        <div class="tc-img-wrap">
          {% if post.image %}
          <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}" alt="{{ post.title }}" class="tc-img" loading="lazy" decoding="async">
          {% else %}
          <div class="tc-img" style="background: linear-gradient(135deg, #16213e, #e01a4f);"></div>
          {% endif %}
          <div class="tc-img-overlay"></div>
        </div>
        <div class="tc-content">
          {% if post.tags.size > 0 %}
          <span class="cat-tag">{{ post.tags.first }}</span>
          {% endif %}
          <h3>{{ post.title }}</h3>
          <span class="meta">{{ post.date | date: "%B %d" }}</span>
        </div>
      </a>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}

{% assign ipo_posts = site.posts | where_exp: "p", "p.tags contains 'ipos'" %}
{% if ipo_posts.size > 0 %}
<div class="trending-section">
  <div class="trending-header">
    <h2>Upcoming IPOs</h2>
    <a href="{{ '/ipos/' | relative_url }}" class="see-more">All IPOs →</a>
  </div>
  <div class="trending-scroll">
    {% for post in ipo_posts %}
    <div class="trending-card">
      <a href="{{ post.url | relative_url }}">
        <div class="tc-img-wrap">
          {% if post.image %}
          <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}" alt="{{ post.title }}" class="tc-img" loading="lazy" decoding="async">
          {% else %}
          <div class="tc-img" style="background: linear-gradient(135deg, #1a2e1a, #e01a4f);"></div>
          {% endif %}
          <div class="tc-img-overlay"></div>
        </div>
        <div class="tc-content">
          {% if post.tags.size > 0 %}
          <span class="cat-tag">{{ post.tags.first }}</span>
          {% endif %}
          <h3>{{ post.title }}</h3>
          <span class="meta">{{ post.date | date: "%B %d" }}</span>
        </div>
      </a>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}

<h2 class="section-title" id="latestSection" style="scroll-margin-top:70px">Latest Articles</h2>

<div id="filterBar" class="filter-bar" style="display:none">
  <span>Showing: <strong class="filter-cat-name"></strong></span>
  <button id="clearFilter" class="filter-clear">✕ Clear</button>
</div>

  <div class="post-grid" id="postGrid">
  {% for post in posts offset:4 limit:12 %}
  {% assign page_num = forloop.index0 | divided_by: 4 | plus: 1 %}
  <article class="post-card" data-page="{{ page_num }}"{% if page_num > 1 %} style="display:none"{% endif %}>
    <a href="{{ post.url | relative_url }}">
      <div class="card-img-wrap">
        {% if post.image %}
        <img src="{{ post.image | replace: 'w=1200', 'w=400' | replace: 'w=800', 'w=400' }}" alt="{{ post.title }}" class="post-card-img" loading="lazy" decoding="async">
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

{% elsif posts.size == 0 %}
<div class="page-content">
  <h1>Welcome to PulseTrends</h1>
  <p>Your daily source for trending insights across AI, technology, politics, finance, weather, and business. Articles are generated fresh every day — check back soon for the latest content!</p>
</div>
{% endif %}
