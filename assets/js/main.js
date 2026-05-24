(function() {
  'use strict';

  // Suppress TradingView warnings globally
  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'notification') {
      // Suppress TradingView notifications
      e.stopImmediatePropagation();
    }
  }, true);

  // Hide any TradingView popups that appear
  function hideTradingViewPopups() {
    var notifClass = document.querySelectorAll('[class*="notification"], [class*="warning"], [class*="popup"]');
    notifClass.forEach(function(el) {
      if (el.style) el.style.display = 'none';
    });
  }

  // Run on load and periodically
  hideTradingViewPopups();
  setInterval(hideTradingViewPopups, 500);

  var ticking = false;
  var header = document.getElementById('header');

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(function() {
        var scrollY = window.scrollY;
        if (header) {
          if (scrollY > 50) {
            header.classList.add('scrolled');
          } else {
            header.classList.remove('scrolled');
          }
        }
        ticking = false;
      });
      ticking = true;
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });

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

  // Scroll Reveal
  var revealElements = document.querySelectorAll('.reveal');
  if (revealElements.length > 0 && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05, rootMargin: '50px 0px' });
    revealElements.forEach(function(el) {
      observer.observe(el);
    });
  } else {
    revealElements.forEach(function(el) {
      el.classList.add('visible');
    });
  }

  // Smooth anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'auto' });
      }
    });
  });

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
      this.textContent = catList.classList.contains('collapsed') ? '+' : '−';
    });
  });

  // Dynamic active nav link
  var currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(function(a) {
    var href = a.getAttribute('href');
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      a.classList.add('nav-active');
    }
  });

  // Category color coding
  var tags = document.querySelectorAll('.cat-tag');
  var tagColors = {
    crypto: '#f59e0b',
    bitcoin: '#f59e0b',
    stock: '#10b981',
    ai: '#8b5cf6',
    tech: '#3b82f6',
    gaming: '#ec4899',
    mobile: '#06b6d4',
    sport: '#ef4444',
    health: '#10b981',
    science: '#3b82f6',
    space: '#8b5cf6',
    business: '#f59e0b',
    politics: '#ef4444',
    world: '#6b7280',
    entertainment: '#ec4899',
    weather: '#3b82f6',
    finance: '#f59e0b',
  };
  tags.forEach(function(tag) {
    var text = tag.textContent.trim().toLowerCase();
    for (var key in tagColors) {
      if (text.indexOf(key) !== -1) {
        tag.style.background = tagColors[key];
        break;
      }
    }
  });

})();
