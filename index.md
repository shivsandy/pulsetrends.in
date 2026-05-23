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
  <article class="post-card reveal" data-page="{{ forloop.index0 | divided_by: 12 | plus: 1 }}">
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
(function(){
  var perPage = 12;
  var cards = document.querySelectorAll('#postGrid .post-card');
  var totalPages = Math.ceil(cards.length / perPage) || 1;
  var currentPage = 1;

  function showPage(p) {
    currentPage = p;
    cards.forEach(function(c, i) {
      var pageNum = Math.floor(i / perPage) + 1;
      c.style.display = pageNum === p ? '' : 'none';
    });
    renderPagination();
  }

  function renderPagination() {
    var el = document.getElementById('pagination');
    if (!el || totalPages <= 1) { if (el) el.innerHTML = ''; return; }
    var html = '';

    if (currentPage > 1) {
      html += '<a href="#" data-page="' + (currentPage - 1) + '" class="prev">&larr; Previous</a>';
    } else {
      html += '<span class="disabled">&larr; Previous</span>';
    }

    for (var i = 1; i <= totalPages; i++) {
      if (i === currentPage) {
        html += '<span class="active">' + i + '</span>';
      } else {
        html += '<a href="#" data-page="' + i + '">' + i + '</a>';
      }
    }

    if (currentPage < totalPages) {
      html += '<a href="#" data-page="' + (currentPage + 1) + '" class="next">Next &rarr;</a>';
    } else {
      html += '<span class="disabled">Next &rarr;</span>';
    }

    html += '<span class="page-info">Page ' + currentPage + ' of ' + totalPages + '</span>';
    el.innerHTML = html;

    el.querySelectorAll('a[data-page]').forEach(function(a) {
      a.addEventListener('click', function(e) {
        e.preventDefault();
        showPage(parseInt(this.getAttribute('data-page')));
        window.scrollTo({ top: document.getElementById('postGrid').offsetTop - 100, behavior: 'smooth' });
      });
    });
  }

  showPage(1);
})();
</script>
