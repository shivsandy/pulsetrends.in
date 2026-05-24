(function() {
  'use strict';

  var header = document.getElementById('header');

  // Header shrink on scroll (throttled)
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

  // Mobile Menu
  var menuToggle = document.getElementById('menuToggle');
  var mobileNav = document.getElementById('mobileNav');
  if (menuToggle && mobileNav) {
    menuToggle.addEventListener('click', function() {
      mobileNav.classList.toggle('open');
      document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
    });
    mobileNav.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', function() {
        mobileNav.classList.remove('open');
        document.body.style.overflow = '';
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

  // Mobile Categories Submenu
  var mCatToggle = document.querySelector('.mobile-cat-toggle');
  var mCatList = document.querySelector('.mobile-cat-list');
  if (mCatToggle && mCatList) {
    mCatToggle.addEventListener('click', function() {
      mCatList.classList.toggle('open');
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
  document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(function(a) {
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
        if (mobileNav && mobileNav.classList.contains('open')) {
          mobileNav.classList.remove('open');
          document.body.style.overflow = '';
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
    weather: '#3b82f6', finance: '#f59e0b',
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
