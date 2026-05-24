---
layout: default
title: Home
---

{% assign posts = site.posts %}

{% if posts.size > 0 %}
{% assign featured = posts.first %}
<div class="hero-featured">
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

<div id="filterBar" class="filter-bar" style="display:none">
  <span>Showing: <strong class="filter-cat-name"></strong></span>
  <button id="clearFilter" class="filter-clear">✕ Clear</button>
</div>

<div class="post-grid" id="postGrid">
  {% for post in posts offset:1 %}
  <article class="post-card" data-page="{{ forloop.index0 | divided_by: 4 | plus: 1 }}">
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
<div class="page-content">
  <h1>Welcome to PulseTrends</h1>
  <p>Your daily source for trending insights across AI, technology, politics, finance, weather, and business. Articles are generated fresh every day — check back soon for the latest content!</p>
</div>
{% endif %}

<script>
document.addEventListener('DOMContentLoaded', function(){
  var grid = document.getElementById('postGrid');
  var cards = Array.from(grid.querySelectorAll('.post-card'));
  var perPage = 4;
  var activeCategory = null;
  var currentPage = 1;

  function showPage(p) {
    currentPage = p;
    var idx = 0;
    cards.forEach(function(c) {
      if (c.dataset.matchCategory === '1') {
        var pageIdx = Math.floor(idx / perPage);
        c.style.display = (pageIdx + 1 === p) ? '' : 'none';
        idx++;
      } else {
        c.style.display = 'none';
      }
    });
    renderPagination();
  }

  function applyFilter() {
    var matchCount = 0;
    cards.forEach(function(c) {
      var tag = c.querySelector('.cat-tag');
      var match = !activeCategory || (tag && tag.textContent.trim().toLowerCase() === activeCategory);
      c.dataset.matchCategory = match ? '1' : '0';
      if (match) matchCount++;
    });
    totalPages = Math.ceil(matchCount / perPage) || 1;
    showPage(1);
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

  var totalPages = 1;

  window.filterByCategory = function(cat) {
    var filterBar = document.getElementById('filterBar');
    if (cat === activeCategory) {
      activeCategory = null;
      if (filterBar) filterBar.style.display = 'none';
    } else {
      activeCategory = cat;
      if (filterBar) {
        filterBar.style.display = 'flex';
        filterBar.querySelector('.filter-cat-name').textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
      }
    }
    var url = new URL(window.location);
    if (activeCategory) {
      url.searchParams.set('category', activeCategory);
    } else {
      url.searchParams.delete('category');
    }
    history.pushState({}, '', url);
    applyFilter();
  };

  document.getElementById('clearFilter').addEventListener('click', function() {
    window.filterByCategory(activeCategory);
  });

  var params = new URLSearchParams(window.location.search);
  var catFromUrl = params.get('category');
  if (catFromUrl) {
    activeCategory = catFromUrl.toLowerCase();
    var fb = document.getElementById('filterBar');
    if (fb) {
      fb.style.display = 'flex';
      fb.querySelector('.filter-cat-name').textContent = activeCategory.charAt(0).toUpperCase() + activeCategory.slice(1);
    }
  }
  applyFilter();
});
</script>
