---
layout: default
title: Live Stock Markets
permalink: /markets/
description: "Live stock market charts and indices for India, US, UK, Japan, Germany, and more. Real-time NSE, BSE, S&P 500, NASDAQ, FTSE, DAX, Nikkei data."
---

<div class="page-content">
  <h1>Live Stock Markets — All Countries</h1>
  <p>Real-time stock market index charts for major global exchanges. Data powered by TradingView.</p>

  <div id="allCharts" class="all-markets-grid"></div>
</div>

<script>
(function() {
  var countries = [
    { name: 'India', flag: '🇮🇳', ticker: 'BSE:SENSEX', label: 'SENSEX' },
    { name: 'India', flag: '🇮🇳', ticker: 'NSE:NIFTY50', label: 'NIFTY 50' },
    { name: 'United States', flag: '🇺🇸', ticker: 'FOREXCOM:SPXUSD', label: 'S&P 500' },
    { name: 'United States', flag: '🇺🇸', ticker: 'FOREXCOM:NSXUSD', label: 'NASDAQ 100' },
    { name: 'United Kingdom', flag: '🇬🇧', ticker: 'FOREXCOM:UKXGBP', label: 'FTSE 100' },
    { name: 'Japan', flag: '🇯🇵', ticker: 'INDEX:NKY', label: 'Nikkei 225' },
    { name: 'Germany', flag: '🇩🇪', ticker: 'INDEX:DEU40', label: 'DAX' },
    { name: 'Hong Kong', flag: '🇭🇰', ticker: 'INDEX:HSI', label: 'Hang Seng' },
    { name: 'China', flag: '🇨🇳', ticker: 'INDEX:SHCOMP', label: 'Shanghai Composite' },
    { name: 'Canada', flag: '🇨🇦', ticker: 'INDEX:GSPTSE', label: 'S&P/TSX Composite' },
    { name: 'Australia', flag: '🇦🇺', ticker: 'INDEX:AS51', label: 'ASX 200' },
    { name: 'France', flag: '🇫🇷', ticker: 'INDEX:CAC40', label: 'CAC 40' },
    { name: 'South Korea', flag: '🇰🇷', ticker: 'INDEX:KSIC', label: 'KOSPI' },
    { name: 'Brazil', flag: '🇧🇷', ticker: 'INDEX:BVSP', label: 'Bovespa' },
  ];

  function createWidget(containerId, ticker) {
    if (!window.TradingView) return;
    
    try {
      new TradingView.widget({
        container_id: containerId,
        autosize: true,
        symbol: ticker,
        interval: 'D',
        timezone: 'UTC',
        theme: 'light',
        style: '1',
        locale: 'en',
        enable_publishing: false,
        hide_top_toolbar: false,
        hide_side_toolbar: true,
        allow_symbol_change: false,
        save_image: false,
        width: '100%',
        height: 380,
        hide_legend: false,
      });
    } catch (e) {
      console.error('Widget error:', e);
    }
  }

  function initCharts() {
    var grid = document.getElementById('allCharts');
    if (!grid) return;

    countries.forEach(function(c, idx) {
      var wrapper = document.createElement('div');
      wrapper.className = 'market-chart-card';

      var heading = document.createElement('h3');
      heading.textContent = c.flag + ' ' + c.name + ' — ' + c.label;
      wrapper.appendChild(heading);

      var container = document.createElement('div');
      container.className = 'tradingview-container';
      container.id = 'tv_' + idx;
      container.dataset.ticker = c.ticker;
      wrapper.appendChild(container);
      grid.appendChild(wrapper);

      createWidget(container.id, c.ticker);
    });

    // Aggressive notification closing
    setTimeout(function() { closeAllNotifications(); }, 500);
    setTimeout(function() { closeAllNotifications(); }, 1000);
    setTimeout(function() { closeAllNotifications(); }, 2000);
    setTimeout(function() { closeAllNotifications(); }, 3000);
  }

  function closeAllNotifications() {
    var selectors = [
      '.notification',
      '[class*="notification"]',
      '[class*="warning"]',
      '[class*="alert"]',
      '[class*="popup"]',
      '[class*="modal"]',
      '[class*="dialog"]',
      '[role="alert"]',
      '[role="alertdialog"]',
      '.tv-popover',
      '.tv-modal',
    ];

    selectors.forEach(function(selector) {
      try {
        var elements = document.querySelectorAll(selector);
        elements.forEach(function(el) {
          if (el && el.style) {
            el.setAttribute('style', 'display: none !important; visibility: hidden; opacity: 0;');
          }
        });
      } catch (e) {}
    });

    var buttons = document.querySelectorAll('button, [role="button"]');
    buttons.forEach(function(btn) {
      var text = (btn.textContent || '').toLowerCase();
      var ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
      if (text.includes('close') || text.includes('dismiss') || 
          ariaLabel.includes('close') || ariaLabel.includes('dismiss') ||
          ariaLabel.includes('symbol') || text.includes('symbol')) {
        try {
          btn.click();
        } catch (e) {}
      }
    });

    var allDivs = document.querySelectorAll('div');
    allDivs.forEach(function(div) {
      var text = div.textContent || '';
      if (text.includes('only available on TradingView') || 
          text.includes('symbol is only') ||
          text.includes('available on')) {
        if (div.parentNode) div.parentNode.style.display = 'none';
        div.style.display = 'none';
      }
    });
  }

  // Load TradingView library
  var script = document.createElement('script');
  script.src = 'https://s3.tradingview.com/tv.js';
  script.async = true;
  script.onload = function() {
    setTimeout(initCharts, 100);
    setTimeout(function() { closeAllNotifications(); }, 200);
    setTimeout(function() { closeAllNotifications(); }, 500);
  };
  script.onerror = function() {
    console.error('Failed to load TradingView');
  };
  document.head.appendChild(script);

  // Continuous monitoring for 10 seconds
  var checkInterval = setInterval(function() {
    closeAllNotifications();
  }, 1000);
  setTimeout(function() {
    clearInterval(checkInterval);
  }, 10000);

  // Monitor DOM for new notifications
  if (window.MutationObserver) {
    var observer = new MutationObserver(function(mutations) {
      var hasChanges = false;
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') hasChanges = true;
      });
      if (hasChanges) closeAllNotifications();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'style'],
    });
  }
})();
</script>
