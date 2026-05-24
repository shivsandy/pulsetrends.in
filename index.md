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

<div class="post-grid" id="postGrid">
  {% for post in posts offset:1 %}
  <article class="post-card reveal" data-page="{{ forloop.index0 | divided_by: 5 | plus: 1 }}">
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

<div class="pagination" id="pagination"></div>

{% if posts.size == 0 %}
<div class="page-content reveal">
  <h1>Welcome to PulseTrends</h1>
  <p>Your daily source for trending insights across AI, technology, politics, finance, weather, and business. Articles are generated fresh every day — check back soon for the latest content!</p>
</div>
{% endif %}

<script>
document.addEventListener('DOMContentLoaded', function(){
  var cards = document.querySelectorAll('#postGrid .post-card');
  var perPage = 5;
  var totalPages = Math.ceil(cards.length / perPage) || 1;

  function getRange(p) {
    var start = (p - 1) * perPage;
    return [start, start + perPage];
  }

  function showPage(p) {
    currentPage = p;
    var range = getRange(p);
    cards.forEach(function(c, i) {
      c.style.display = (i >= range[0] && i < range[1]) ? '' : 'none';
    });
    renderPagination();
  }

  function renderPagination() {
    var el = document.getElementById('pagination');
    if (!el) return;
    if (totalPages <= 1) { el.innerHTML = ''; return; }

    var html = '';
    if (currentPage > 1) {
      html += '<a href="#" data-page="' + (currentPage - 1) + '" class="prev" aria-label="Previous page">&lsaquo;</a>';
    } else {
      html += '<span class="disabled" aria-hidden="true">&lsaquo;</span>';
    }
    for (var i = 1; i <= totalPages; i++) {
      html += i === currentPage ? '<span class="active">' + i + '</span>' : '<a href="#" data-page="' + i + '">' + i + '</a>';
    }
    if (currentPage < totalPages) {
      html += '<a href="#" data-page="' + (currentPage + 1) + '" class="next" aria-label="Next page">&rsaquo;</a>';
    } else {
      html += '<span class="disabled" aria-hidden="true">&rsaquo;</span>';
    }
    html += '<span class="page-info">' + currentPage + ' / ' + totalPages + '</span>';
    el.innerHTML = html;

    el.querySelectorAll('a[data-page]').forEach(function(a) {
      a.addEventListener('click', function(e) {
        e.preventDefault();
        showPage(parseInt(this.getAttribute('data-page')));
        var top = document.getElementById('postGrid');
        if (top) top.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  showPage(1);
});
</script>
