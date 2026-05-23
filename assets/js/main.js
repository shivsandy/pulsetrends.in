(function() {
  'use strict';

  var ticking = false;
  var progressBar = document.querySelector('.scroll-progress');
  var header = document.getElementById('header');
  var globeContainer = document.getElementById('globe-container');

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(function() {
        var scrollY = window.scrollY;

        // Scroll progress bar
        if (progressBar) {
          var docHeight = document.documentElement.scrollHeight - window.innerHeight;
          var pct = docHeight > 0 ? (scrollY / docHeight) * 100 : 0;
          progressBar.style.width = pct + '%';
        }

        // Header shrink
        if (header) {
          if (scrollY > 50) {
            header.classList.add('scrolled');
          } else {
            header.classList.remove('scrolled');
          }
        }

        // Globe parallax
        if (globeContainer) {
          globeContainer.style.transform = 'translateY(' + (scrollY * -0.08) + 'px)';
        }

        ticking = false;
      });
      ticking = true;
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });

  // ─── Mobile Menu ───
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

  // ─── Scroll Reveal ───
  var revealElements = document.querySelectorAll('.reveal');
  if (revealElements.length > 0 && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    revealElements.forEach(function(el) {
      observer.observe(el);
    });
  } else {
    revealElements.forEach(function(el) {
      el.classList.add('visible');
    });
  }

  // ─── Smooth anchor links ───
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ─── Card stagger ───
  var postCards = document.querySelectorAll('.post-card');
  postCards.forEach(function(card, i) {
    card.style.setProperty('--card-delay', (i * 0.08) + 's');
  });

  // ─── Dynamic active nav link ───
  var currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a, .mobile-nav a').forEach(function(a) {
    var href = a.getAttribute('href');
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      a.classList.add('nav-active');
    }
  });

  // ─── Category color coding ───
  var tags = document.querySelectorAll('.cat-tag');
  var tagColors = {
    crypto: ['#f7931a', '#ffb347'],
    bitcoin: ['#f7931a', '#ffb347'],
    stock: ['#00b894', '#55efc4'],
    ai: ['#6c5ce7', '#a29bfe'],
    tech: ['#0984e3', '#74b9ff'],
    gaming: ['#e17055', '#fab1a0'],
    mobile: ['#00cec9', '#81ecec'],
    sport: ['#fd79a8', '#e84393'],
    health: ['#00b894', '#55efc4'],
    science: ['#74b9ff', '#a29bfe'],
    space: ['#6c5ce7', '#a29bfe'],
    business: ['#fdcb6e', '#ffeaa7'],
    politics: ['#d63031', '#e17055'],
    world: ['#636e72', '#b2bec3'],
    entertainment: ['#fd79a8', '#e84393'],
    weather: ['#74b9ff', '#81ecec'],
    finance: ['#fdcb6e', '#ffeaa7'],
  };
  tags.forEach(function(tag) {
    var text = tag.textContent.trim().toLowerCase();
    for (var key in tagColors) {
      if (text.indexOf(key) !== -1) {
        tag.style.background = 'linear-gradient(135deg, ' + tagColors[key][0] + ', ' + tagColors[key][1] + ')';
        break;
      }
    }
  });

})();
