---
layout: default
title: Search
permalink: /search/
---

<div class="page-content">
  <h1>Search Articles</h1>
  <div class="search-box">
    <input type="text" id="searchInput" placeholder="Search articles by title, category, or keyword..." class="search-input" autofocus>
    <span class="search-icon">🔍</span>
  </div>
  <div id="searchResults" class="post-grid" style="margin-top:24px"></div>
  <p id="searchEmpty" class="search-empty" style="display:none">No articles found. Try a different search term.</p>
</div>

<script>
document.addEventListener('DOMContentLoaded', function(){
  var input = document.getElementById('searchInput');
  var results = document.getElementById('searchResults');
  var empty = document.getElementById('searchEmpty');
  var allPosts = [];
  {% for post in site.posts %}
  allPosts.push({
    url: '{{ post.url | relative_url }}',
    title: '{{ post.title | escape }}'.replace(/'/g, "\\'"),
    excerpt: '{{ post.excerpt | strip_html | truncatewords: 30 | escape }}'.replace(/'/g, "\\'"),
    image: '{{ post.image }}',
    category: '{{ post.tags.first }}',
    date: '{{ post.date | date: "%B %d, %Y" }}'
  });
  {% endfor %}

  function renderPosts(posts) {
    if (posts.length === 0) {
      results.innerHTML = '';
      empty.style.display = 'block';
      return;
    }
    empty.style.display = 'none';
    var html = '';
    posts.forEach(function(p) {
      html += '<article class="post-card"><a href="' + p.url + '">';
      if (p.image) {
        html += '<div class="card-img-wrap"><img src="' + p.image + '" alt="' + p.title + '" class="post-card-img" loading="lazy"></div>';
      } else {
        html += '<div class="card-img-wrap"><div class="post-card-img" style="background:linear-gradient(135deg,#16213e,#e01a4f)"></div></div>';
      }
      html += '<div class="post-card-body"><span class="cat-tag">' + p.category + '</span><h3>' + p.title + '</h3><p>' + p.excerpt + '</p><span class="meta">' + p.date + '</span></div></a></article>';
    });
    results.innerHTML = html;
  }

  function searchPosts(q) {
    if (!q) { results.innerHTML = ''; empty.style.display = 'none'; return; }
    var term = q.toLowerCase();
    var matches = allPosts.filter(function(p) {
      return p.title.toLowerCase().indexOf(term) !== -1 ||
             p.category.toLowerCase().indexOf(term) !== -1 ||
             p.excerpt.toLowerCase().indexOf(term) !== -1;
    });
    renderPosts(matches);
  }

  input.addEventListener('input', function() {
    searchPosts(this.value);
  });
});
</script>
