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
      isMenuOpen ? closePanel() : openPanel();
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
  var sections = [];

  function initPagination(gridId, paginationId, perPage) {
    var grid = document.getElementById(gridId);
    var paginationEl = document.getElementById(paginationId);
    if (!grid || !paginationEl) return;

    var cards = Array.from(grid.querySelectorAll('.section-card, .left-card'));
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
    sections.push({ grid: grid, paginationEl: paginationEl });
  }

  initPagination('leftGrid', 'leftPagination', 5);
  initPagination('latestGrid', 'latestPagination', 4);
  initPagination('techGrid', 'techPagination', 4);
  initPagination('marketsGrid', 'marketsPagination', 4);
  initPagination('ipoNewsGrid', 'ipoNewsPagination', 4);

  // ─── Scroll Reveal Pagination ───
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.3 });

    sections.forEach(function(s) {
      if (s.paginationEl && s.paginationEl.innerHTML.trim() !== '') {
        observer.observe(s.paginationEl);
      }
    });
  } else {
    sections.forEach(function(s) {
      if (s.paginationEl) s.paginationEl.classList.add('visible');
    });
  }

  // ─── IPO Stock Cards (fetch JSON, show first 8) ───
  function loadIPOStocks() {
    var container = document.getElementById('ipoStockList');
    if (!container) return;

    fetch('/ipodashboard/data/ipos.json')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        var ipos = data.ipos || data;
        if (!Array.isArray(ipos)) return;
        var first8 = ipos.slice(0, 8);
        container.innerHTML = first8.map(function(ipo) {
          var name = ipo.company_name || ipo.company || 'Unknown';
          var ticker = ipo.symbol || ipo.ticker || '';
          var price = ipo.price_band || '';
          var date = ipo.listing_date || '';
          var status = (ipo.status || 'unknown').toLowerCase();
          var statusClass = status === 'open' ? 'open' : status === 'listed' ? 'listed' : status === 'upcoming' || status === 'scheduled' ? 'upcoming' : 'closing';
          return '<div class="ipo-stock-card">' +
            '<div class="ipo-stock-name">' + name + '</div>' +
            '<div class="ipo-stock-meta">' +
            (ticker ? '<span class="ipo-stock-ticker">$' + ticker + '</span>' : '') +
            '<span class="ipo-stock-dot">&#9679;</span>' +
            '<span class="ipo-stock-status ' + statusClass + '">' + status + '</span>' +
            '</div>' +
            '<div class="ipo-stock-details">' +
            (price ? '<span class="ipo-stock-price">' + price + '</span>' : '') +
            (price && date ? '<span>|</span>' : '') +
            (date ? '<span class="ipo-stock-date">' + date + '</span>' : '') +
            '</div>' +
            '</div>';
        }).join('');
      })
      .catch(function() {
        container.innerHTML = '<div style="padding:12px;font-size:0.75em;color:var(--text-muted);text-align:center;">IPO data unavailable</div>';
      });
  }

  loadIPOStocks();
})();
