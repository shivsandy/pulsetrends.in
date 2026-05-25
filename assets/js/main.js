(function() {
  'use strict';

  var header = document.getElementById('header');

  var ticking = false;
  window.addEventListener('scroll', function() {
    if (!ticking) {
      requestAnimationFrame(function() {
        header && header.classList.toggle('scrolled', window.scrollY > 50);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  var menuToggle = document.getElementById('menuToggle');
  var mobilePanel = document.getElementById('mobilePanel');
  var mobileOverlay = document.getElementById('mobileOverlay');
  var panelClose = document.getElementById('panelClose');
  var isMenuOpen = false;

  function closePanel() {
    mobilePanel.classList.remove('open');
    mobileOverlay.classList.remove('open');
    document.body.style.overflow = '';
    isMenuOpen = false;
  }

  function openPanel() {
    mobilePanel.classList.add('open');
    mobileOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    isMenuOpen = true;
  }

  if (menuToggle && mobilePanel) {
    menuToggle.addEventListener('click', function() {
      if (isMenuOpen) { closePanel(); } else { openPanel(); }
    });
    if (panelClose) panelClose.addEventListener('click', closePanel);
    if (mobileOverlay) mobileOverlay.addEventListener('click', closePanel);
    mobilePanel.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', closePanel);
    });
  }

  var dropdown = document.querySelector('.nav-dropdown');
  var dropdownTrigger = document.querySelector('.dropdown-trigger');
  if (dropdown && dropdownTrigger) {
    dropdownTrigger.addEventListener('click', function(e) {
      e.preventDefault();
      dropdown.classList.toggle('nav-dropdown-open');
    });
    document.addEventListener('click', function(e) {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('nav-dropdown-open');
      }
    });
  }

  var currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a, .mobile-panel-body a').forEach(function(a) {
    var href = a.getAttribute('href');
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      a.classList.add('nav-active');
    }
  });

  document.querySelectorAll('[data-category]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      var cat = this.getAttribute('data-category');
      if (typeof window.filterByCategory === 'function') {
        e.preventDefault();
        window.filterByCategory(cat);
        var target = document.getElementById('latestSection');
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (isMenuOpen) { closePanel(); }
        if (dropdown) dropdown.classList.remove('nav-dropdown-open');
      }
    });
  });

  var tagColors = {
    crypto: '#f59e0b', bitcoin: '#f59e0b', stock: '#10b981',
    ai: '#8b5cf6', tech: '#3b82f6', gaming: '#ec4899',
    mobile: '#06b6d4', sport: '#ef4444', health: '#10b981',
    science: '#3b82f6', space: '#8b5cf6', business: '#f59e0b',
    politics: '#ef4444', world: '#6b7280', entertainment: '#ec4899',
    weather: '#3b82f6', finance: '#f59e0b', phones: '#e17055', ipos: '#e17055',
  };
  document.querySelectorAll('.cat-tag').forEach(function(tag) {
    var text = tag.textContent.trim().toLowerCase();
    for (var key in tagColors) {
      if (text.indexOf(key) !== -1) {
        tag.style.background = tagColors[key];
        break;
      }
    }
  });

  var grid = document.getElementById('postGrid');
  if (!grid) return;

  var cards = Array.from(grid.querySelectorAll('.post-card'));
  var perPage = 4;
  var activeCategory = null;
  var currentPage = 1;
  var totalPages = 1;

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
        if (top) top.scrollIntoView({ block: 'start' });
      });
    });
  }

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

  var clearBtn = document.getElementById('clearFilter');
  if (clearBtn) {
    clearBtn.addEventListener('click', function() {
      window.filterByCategory(activeCategory);
    });
  }

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
})();
