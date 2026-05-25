(function() {
  'use strict';

  // ─── Header Scroll Listener ───
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

  // ─── Mobile Menu ───
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

  // ─── Dropdown Navigation ───
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

  // ─── Active Navigation Link ───
  var currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a, .mobile-panel-body a').forEach(function(a) {
    var href = a.getAttribute('href');
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      a.classList.add('nav-active');
    }
  });

  // ─── Category Tag Colors ───
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

  // ─── Multi-Section Pagination ───
  function initPagination(gridId, paginationId, perPage) {
    var grid = document.getElementById(gridId);
    var paginationEl = document.getElementById(paginationId);
    if (!grid || !paginationEl) return;

    var cards = Array.from(grid.querySelectorAll('.section-card'));
    if (cards.length === 0) return;

    var currentPage = 1;
    var totalPages = Math.ceil(cards.length / perPage) || 1;

    function showPage(p) {
      currentPage = p;
      cards.forEach(function(c, idx) {
        var pageIdx = Math.floor(idx / perPage) + 1;
        c.style.display = pageIdx === p ? '' : 'none';
      });
      renderPagination();
    }

    function renderPagination() {
      if (totalPages <= 1) { paginationEl.innerHTML = ''; return; }

      var html = '';
      if (currentPage > 1) {
        html += '<a href="#" data-page="' + (currentPage - 1) + '" class="prev" rel="prev" aria-label="Previous page">&lsaquo; <span class="pg-label">Prev</span></a>';
      } else {
        html += '<span class="disabled" aria-hidden="true">&lsaquo; <span class="pg-label">Prev</span></span>';
      }
      for (var i = 1; i <= totalPages; i++) {
        html += i === currentPage ? '<span class="active">' + i + '</span>' : '<a href="#" data-page="' + i + '">' + i + '</a>';
      }
      if (currentPage < totalPages) {
        html += '<a href="#" data-page="' + (currentPage + 1) + '" class="next" rel="next" aria-label="Next page"><span class="pg-label">Next</span> &rsaquo;</a>';
      } else {
        html += '<span class="disabled" aria-hidden="true"><span class="pg-label">Next</span> &rsaquo;</span>';
      }
      paginationEl.innerHTML = html;

      paginationEl.querySelectorAll('a[data-page]').forEach(function(a) {
        a.addEventListener('click', function(e) {
          e.preventDefault();
          showPage(parseInt(this.getAttribute('data-page')));
          grid.scrollIntoView({ block: 'start', behavior: 'smooth' });
        });
      });
    }

    showPage(1);
  }

  // Initialize pagination for all sections
  initPagination('latestGrid', 'latestPagination', 4);
  initPagination('techGrid', 'techPagination', 4);
  initPagination('marketsGrid', 'marketsPagination', 4);
  initPagination('ipoGrid', 'ipoPagination', 4);

  // ─── IPO Dashboard Stats ───
  function loadIPOStats() {
    fetch('/ipodashboard/data/ipos.json')
      .then(function(res) { return res.json(); })
      .catch(function(err) { console.error('Failed to load IPO data:', err); })
      .then(function(data) {
        if (!data || !Array.isArray(data)) return;

        var today = new Date();
        today.setHours(0, 0, 0, 0);

        var upcoming = 0, open = 0, closing = 0, listed = 0;

        data.forEach(function(ipo) {
          var status = (ipo.status || '').toLowerCase();
          if (status === 'upcoming' || status === 'scheduled') upcoming++;
          else if (status === 'open') open++;
          else if (status === 'closing soon') closing++;
          else if (status === 'listed') listed++;
        });

        document.getElementById('upcomingBadge') && (document.getElementById('upcomingBadge').textContent = upcoming);
        document.getElementById('openBadge') && (document.getElementById('openBadge').textContent = open);
        document.getElementById('closingBadge') && (document.getElementById('closingBadge').textContent = closing);
        document.getElementById('listedBadge') && (document.getElementById('listedBadge').textContent = listed);

        // Render IPO cards (top 5)
        renderIPOCards(data.slice(0, 5));
      });
  }

  function renderIPOCards(ipos) {
    var container = document.getElementById('ipoCardsContainer');
    if (!container) return;

    container.innerHTML = ipos.map(function(ipo) {
      var logo = (ipo.company || ipo.ticker || '?').substring(0, 2).toUpperCase();
      var status = (ipo.status || 'unknown').toLowerCase();
      return '<div class="ipo-card">' +
        '<div class="ipo-card-logo">' + logo + '</div>' +
        '<div class="ipo-card-info">' +
        '<div class="ipo-card-name">' + (ipo.company || ipo.ticker || 'Unknown') + '</div>' +
        '<div class="ipo-card-status">' + (ipo.listing_date || '—') + '</div>' +
        '</div>' +
        '<span class="ipo-card-badge">' + status + '</span>' +
        '</div>';
    }).join('');
  }

  loadIPOStats();
})();
