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
    { name: 'India', flag: '🇮🇳', ticker: 'NSE:NIFTY', label: 'NIFTY 50' },
    { name: 'India', flag: '🇮🇳', ticker: 'BSE:SENSEX', label: 'SENSEX' },
    { name: 'United States', flag: '🇺🇸', ticker: 'SP:SPX', label: 'S&P 500' },
    { name: 'United States', flag: '🇺🇸', ticker: 'NASDAQ:IXIC', label: 'NASDAQ Composite' },
    { name: 'United Kingdom', flag: '🇬🇧', ticker: 'TVC:UKX', label: 'FTSE 100' },
    { name: 'Japan', flag: '🇯🇵', ticker: 'NIKKEI:NI225', label: 'Nikkei 225' },
    { name: 'Germany', flag: '🇩🇪', ticker: 'TVC:DAX', label: 'DAX' },
    { name: 'Hong Kong', flag: '🇭🇰', ticker: 'TVC:HSI', label: 'Hang Seng' },
    { name: 'China', flag: '🇨🇳', ticker: 'TVC:SHCOMP', label: 'Shanghai Composite' },
    { name: 'Canada', flag: '🇨🇦', ticker: 'TVC:TSX', label: 'S&P/TSX Composite' },
    { name: 'Australia', flag: '🇦🇺', ticker: 'TVC:ASX200', label: 'ASX 200' },
    { name: 'France', flag: '🇫🇷', ticker: 'TVC:CAC', label: 'CAC 40' },
    { name: 'South Korea', flag: '🇰🇷', ticker: 'TVC:KOSPI', label: 'KOSPI' },
    { name: 'Brazil', flag: '🇧🇷', ticker: 'BMFBOVESPA:BVSP', label: 'IBOVESPA' },
  ];

  function createWidget(containerId, ticker) {
    new TradingView.widget({
      container_id: containerId,
      autosize: true,
      symbol: ticker,
      interval: 'D',
      timezone: 'Etc/UTC',
      theme: 'dark',
      style: '1',
      locale: 'en',
      toolbar_bg: '#070708',
      enable_publishing: false,
      hide_top_toolbar: true,
      hide_side_toolbar: false,
      allow_symbol_change: false,
      save_image: false,
      width: '100%',
      height: 320,
      studies: ['RSI@tv-basicstudies'],
    });
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
      container.id = 'tv_' + c.ticker.replace(/[^a-zA-Z0-9]/g, '_');
      container.dataset.ticker = c.ticker;
      wrapper.appendChild(container);
      grid.appendChild(wrapper);

      // Lazy load: only create widget when scrolled into view
      if ('IntersectionObserver' in window && idx > 1) {
        var obs = new IntersectionObserver(function(entries) {
          entries.forEach(function(entry) {
            if (entry.isIntersecting) {
              createWidget(entry.target.id, entry.target.dataset.ticker);
              obs.unobserve(entry.target);
            }
          });
        }, { rootMargin: '200px' });
        obs.observe(container);
      } else {
        createWidget(container.id, c.ticker);
      }
    });
  }

  var existing = document.getElementById('tradingview-script');
  if (!existing) {
    var script = document.createElement('script');
    script.id = 'tradingview-script';
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = initCharts;
    document.head.appendChild(script);
  } else if (typeof TradingView !== 'undefined') {
    initCharts();
  }
})();
</script>
