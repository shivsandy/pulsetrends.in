(function() {
  'use strict';

  var header = document.getElementById('header');

  var secHeader = document.getElementById('secHeader');
  var lastScrollY = 0, wasScrolled = false, wasSecVisible = false;

  // Header + secondary header on scroll (rAF-throttled, state-cached)
  var ticking = false;
  window.addEventListener('scroll', function() {
    if (!ticking) {
      requestAnimationFrame(function() {
        var scrollY = window.scrollY;
        var nowScrolled = scrollY > 50;
        if (nowScrolled !== wasScrolled) { header && header.classList.toggle('scrolled', nowScrolled); wasScrolled = nowScrolled; }
        if (secHeader) {
          var nowSecVisible = scrollY > 100 && !(scrollY > 450 && scrollY > lastScrollY);
          if (nowSecVisible !== wasSecVisible) {
            secHeader.classList.toggle('is-visible', nowSecVisible);
            header && header.classList.toggle('sec-active', nowSecVisible);
            wasSecVisible = nowSecVisible;
          }
        }
        lastScrollY = scrollY;
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  // Mobile Categories Dropdown
  var menuToggle = document.getElementById('menuToggle');
  var mobileCats = document.getElementById('mobileCats');
  var isMenuOpen = false;
  if (menuToggle && mobileCats) {
    menuToggle.addEventListener('click', function() {
      isMenuOpen = !isMenuOpen;
      mobileCats.classList.toggle('open', isMenuOpen);
    });
    mobileCats.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', function() {
        mobileCats.classList.remove('open');
        isMenuOpen = false;
      });
    });
  }

  // Desktop Nav Dropdown
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

  // Sidebar Categories Toggle
  document.querySelectorAll('.cat-toggle').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var widget = this.closest('.sidebar-widget');
      var catList = widget ? widget.querySelector('.sidebar-cat') : null;
      if (!catList) return;
      catList.classList.toggle('collapsed');
      this.textContent = catList.classList.contains('collapsed') ? '+' : '\u2212';
    });
  });

  // Active nav link
  var currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a, .mobile-categories a').forEach(function(a) {
    var href = a.getAttribute('href');
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      a.classList.add('nav-active');
    }
  });

  // Category filtering via data-category links (only intercept on homepage)
  document.querySelectorAll('[data-category]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      var cat = this.getAttribute('data-category');
      if (typeof window.filterByCategory === 'function') {
        e.preventDefault();
        window.filterByCategory(cat);
        if (mobileCats && isMenuOpen) {
          mobileCats.classList.remove('open');
          isMenuOpen = false;
        }
        if (dropdown) dropdown.classList.remove('nav-dropdown-open');
      }
    });
  });

  // Category tag colors
  var tagColors = {
    crypto: '#f59e0b', bitcoin: '#f59e0b', stock: '#10b981',
    ai: '#8b5cf6', tech: '#3b82f6', gaming: '#ec4899',
    mobile: '#06b6d4', sport: '#ef4444', health: '#10b981',
    science: '#3b82f6', space: '#8b5cf6', business: '#f59e0b',
    politics: '#ef4444', world: '#6b7280', entertainment: '#ec4899',
    weather: '#3b82f6', finance: '#f59e0b', phones: '#e17055',
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

})();
