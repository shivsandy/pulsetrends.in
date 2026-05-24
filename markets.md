---
layout: default
title: Live Stock Markets
permalink: /markets/
description: "Live stock market charts and indices for India, US, UK, Japan, Germany, and more."
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
    { name: 'United States', flag: '🇺🇸', ticker: 'FOREXCOM:SPXUSD', label: 'S&P 500' },
    { name: 'United States', flag: '🇺🇸', ticker: 'FOREXCOM:NSXUSD', label: 'NASDAQ 100' },
    { name: 'United Kingdom', flag: '🇬🇧', ticker: 'FOREXCOM:UKXGBP', label: 'FTSE 100' },
    { name: 'Japan', flag: '🇯🇵', ticker: 'INDEX:NKY', label: 'Nikkei 225' },
    { name: 'Germany', flag: '🇩🇪', ticker: 'INDEX:DEU40', label: 'DAX' },
    { name: 'Hong Kong', flag: '🇭🇰', ticker: 'INDEX:HSI', label: 'Hang Seng' },
    { name: 'China', flag: '🇨🇳', ticker: 'INDEX:SHCOMP', label: 'Shanghai Comp' },
    { name: 'Canada', flag: '🇨🇦', ticker: 'INDEX:GSPTSE', label: 'TSX' },
    { name: 'Australia', flag: '🇦🇺', ticker: 'INDEX:AS51', label: 'ASX 200' },
    { name: 'France', flag: '🇫🇷', ticker: 'INDEX:CAC40', label: 'CAC 40' },
    { name: 'South Korea', flag: '🇰🇷', ticker: 'INDEX:KSIC', label: 'KOSPI' },
    { name: 'Brazil', flag: '🇧🇷', ticker: 'INDEX:BVSP', label: 'Bovespa' },
  ];

  var loaded = 0;

  function createWidget(containerId, ticker, label) {
    if (!window.TradingView) return;

    try {
      new TradingView.widget({
        container_id: containerId,
        autosize: true,
        symbol: ticker,
        interval: 'D',
        timezone: 'UTC',
        theme: 'dark',
        style: '1',
        locale: 'en',
        enable_publishing: false,
        hide_top_toolbar: true,
        hide_side_toolbar: true,
        allow_symbol_change: false,
        save_image: false,
        width: '100%',
        height: 380,
      });
      loaded++;
    } catch (e) {
      console.error('Widget error for ' + label + ':', e);
      document.getElementById(containerId).innerHTML = '<div style="padding:30px;text-align:center;color:#666">Unavailable</div>';
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
      wrapper.appendChild(container);
      grid.appendChild(wrapper);
      createWidget(container.id, c.ticker, c.label);
    });
  }

  // Load TradingView
  if (!window.TradingView) {
    var s = document.createElement('script');
    s.src = 'https://s3.tradingview.com/tv.js';
    s.async = true;
    s.onload = function() {
      setTimeout(initCharts, 200);
    };
    s.onerror = function() {
      document.getElementById('allCharts').innerHTML = '<div style="padding:40px;text-align:center;color:#888">Failed to load charts. Please refresh.</div>';
    };
    document.head.appendChild(s);
  } else {
    initCharts();
  }
})();
</script>
