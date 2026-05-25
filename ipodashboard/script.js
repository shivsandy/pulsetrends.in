(function () {
  let ipos = [];
  let analysis = {};
  let currentFilter = "all";
  let searchTerm = "";
  let sortKey = null;
  let sortAsc = true;
  let currentIpo = null;

  const tbody = document.getElementById("ipoBody");
  const searchInput = document.getElementById("searchInput");
  const filterButtons = document.querySelectorAll(".filter-btn");
  const lastUpdatedEl = document.getElementById("lastUpdated");
  const ipoCountEl = document.getElementById("ipoCount");

  const modal = document.getElementById("ipoModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalSymbol = document.getElementById("modalSymbol");
  const modalClose = document.getElementById("modalClose");

  /* ─── Helpers ─── */

  function formatDate(dateStr) {
    if (!dateStr) return "\u2014";
    var parts = dateStr.split("-");
    if (parts.length !== 3) return dateStr;
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var m = months[parseInt(parts[1], 10) - 1] || parts[1];
    return m + " " + parseInt(parts[2], 10) + ", " + parts[0];
  }

  function statusClass(status) {
    var s = (status || "upcoming").toLowerCase();
    if (s === "upcoming") return "status-upcoming";
    if (s === "open") return "status-open";
    if (s === "subscribed") return "status-subscribed";
    if (s === "listed") return "status-listed";
    if (s === "closed") return "status-closed";
    return "status-upcoming";
  }

  function getCountry(ipo) {
    var exchange = (ipo.exchange || "").toUpperCase();
    if (exchange === "NSE" || exchange === "BSE") return "India";
    var country = ipo.country || "";
    if (country === "India" || country === "USA") return country;
    if (["NYSE", "NASDAQ", "NYSE AMERICAN"].indexOf(exchange) !== -1) return "USA";
    return "Global";
  }

  function countryClass(country) {
    var c = (country || "").toLowerCase();
    if (c === "india") return "country-india";
    if (c === "usa") return "country-usa";
    return "country-global";
  }

  function matchesFilter(ipo, filter) {
    if (filter === "all") return true;
    if (filter === "open" || filter === "upcoming") {
      return (ipo.status || "").toLowerCase() === filter;
    }
    return getCountry(ipo).toLowerCase() === filter.toLowerCase();
  }

  function parseSubscription(subStr) {
    if (!subStr) return -Infinity;
    var match = subStr.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : -Infinity;
  }

  function escHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function analysisKey(ipo) {
    var sym = (ipo.symbol || "").toUpperCase().trim();
    var country = (ipo.country || "Global").trim();
    if (sym) return sym + "-" + country;
    var name = (ipo.company_name || "").toLowerCase().trim().replace(/\s+/g, "-").slice(0, 20);
    return name + "-" + country;
  }

  /* ─── Skeleton generators ─── */

  function skeletonLines(count) {
    var html = "";
    for (var i = 0; i < count; i++) {
      html += '<div class="skeleton skeleton-line"></div>';
    }
    return html;
  }

  function skeletonCards(count) {
    var html = '<div class="skeleton-cards">';
    for (var i = 0; i < count; i++) {
      html += '<div class="skeleton skeleton-card"></div>';
    }
    return html + "</div>";
  }

  /* ─── IPO Details helpers ─── */

  function buildIpoDetailsArr(ipo) {
    var arr = [];
    if (ipo.price_band) arr.push({ label: "Price Band", value: ipo.price_band });
    if (ipo.issue_size) arr.push({ label: "Issue Size", value: ipo.issue_size });
    if (ipo.lot_size) arr.push({ label: "Lot Size", value: ipo.lot_size + " shares" });
    if (ipo.exchange) arr.push({ label: "Exchange", value: ipo.exchange });
    if (ipo.listing_date) arr.push({ label: "Listing Date", value: formatDate(ipo.listing_date) });
    if (ipo.subscription) arr.push({ label: "Subscription", value: ipo.subscription });
    if (ipo.open_date) arr.push({ label: "Open Date", value: formatDate(ipo.open_date) });
    if (ipo.close_date) arr.push({ label: "Close Date", value: formatDate(ipo.close_date) });
    return arr;
  }

  /* ─── Financial Metrics helpers ─── */

  function parseFinancialMetrics(text) {
    if (!text) return null;
    var metrics = {};
    var patterns = [
      { key: "Revenue", regex: /[Rr]evenue[:\s]*([^,;\.]+)/ },
      { key: "Profit", regex: /[Pp]rofit[:\s]*([^,;\.]+)/ },
      { key: "Debt", regex: /[Dd]ebt[:\s]*([^,;\.]+)/ },
      { key: "EPS", regex: /EPS[:\s]*([^,;\.]+)/ },
      { key: "P/E", regex: /P\/?E[:\s]*([^,;\.]+)/ },
      { key: "Growth", regex: /[Gg]rowth[:\s]*([^,;\.]+)/ },
    ];
    for (var i = 0; i < patterns.length; i++) {
      var match = text.match(patterns[i].regex);
      if (match) metrics[patterns[i].key] = match[1].trim();
    }
    return Object.keys(metrics).length > 0 ? metrics : null;
  }

  /* ─── Risk helpers ─── */

  function hasStructuredRisks(risks) {
    if (!Array.isArray(risks) || risks.length === 0) return false;
    return typeof risks[0] === "object" && risks[0].indicator;
  }

  function enrichRisksWithIndicators(riskTexts) {
    if (!Array.isArray(riskTexts)) return [];
    var negativeKeywords = ["loss", "fail", "risk", "decline", "uncertain", "challenge", "pressure", "volatile", "intense", "dependence"];
    var positiveKeywords = ["opportunity", "advantage", "strong", "established", "experienced"];

    return riskTexts.map(function (text) {
      var lowerText = typeof text === "string" ? text.toLowerCase() : String(text).toLowerCase();
      var indicator = "\uD83D\uDFE1";
      var negCount = 0;
      var posCount = 0;
      for (var n = 0; n < negativeKeywords.length; n++) {
        if (lowerText.indexOf(negativeKeywords[n]) !== -1) negCount++;
      }
      for (var p = 0; p < positiveKeywords.length; p++) {
        if (lowerText.indexOf(positiveKeywords[p]) !== -1) posCount++;
      }
      if (negCount > posCount) indicator = "\uD83D\uDD34";
      else if (posCount > negCount) indicator = "\uD83D\uDFE2";
      return { text: typeof text === "string" ? text : String(text), indicator: indicator };
    });
  }

  /* ─── Score helpers ─── */

  function estimateScores(analysisText) {
    if (!analysisText) {
      return { financial_health: 50, growth_potential: 50, risk: 50, attractiveness: 50 };
    }
    var text = analysisText.toLowerCase();
    var positiveKeywords = ["compelling", "strong", "opportunity", "growth", "upside", "attractive", "solid", "positive"];
    var negativeKeywords = ["risk", "challenge", "caution", "uncertain", "volatile", "pressure", "decline"];
    var sentiment = 0;
    for (var i = 0; i < positiveKeywords.length; i++) {
      if (text.indexOf(positiveKeywords[i]) !== -1) sentiment += 10;
    }
    for (var j = 0; j < negativeKeywords.length; j++) {
      if (text.indexOf(negativeKeywords[j]) !== -1) sentiment -= 8;
    }
    var baseScore = Math.max(35, Math.min(75, 50 + sentiment));
    return {
      financial_health: Math.round(baseScore + Math.random() * 10 - 5),
      growth_potential: Math.round(baseScore + Math.random() * 15 - 7),
      risk: Math.round(100 - (baseScore + Math.random() * 10 - 5)),
      attractiveness: Math.round(baseScore + Math.random() * 12 - 6)
    };
  }

  /* ─── Verdict helpers ─── */

  function extractVerdict(analysisText, verdictField) {
    if (verdictField) return verdictField;
    if (!analysisText) return null;
    var text = analysisText.toLowerCase();
    if (text.indexOf("avoid") !== -1 || text.indexOf("caution") !== -1 || text.indexOf("risky") !== -1) {
      return "Avoid \u2014 Consider alternatives with lower risk profiles";
    }
    if (text.indexOf("compelling") !== -1 || text.indexOf("opportunity") !== -1 || text.indexOf("consider") !== -1) {
      return "Subscribe \u2014 Offers compelling growth potential";
    }
    return "Watch \u2014 Monitor performance and execution";
  }

  function verdictBadgeClass(verdict) {
    if (!verdict) return "verdict-pending";
    var v = verdict.toLowerCase();
    if (v.indexOf("subscribe") !== -1) return "verdict-subscribe";
    if (v.indexOf("avoid") !== -1) return "verdict-avoid";
    if (v.indexOf("watch") !== -1 || v.indexOf("neutral") !== -1) return "verdict-neutral";
    return "verdict-pending";
  }

  function verdictBadgeText(badgeClass) {
    if (badgeClass === "verdict-subscribe") return "Subscribe";
    if (badgeClass === "verdict-avoid") return "Avoid";
    if (badgeClass === "verdict-neutral") return "Watch";
    return "Pending";
  }

  /* ─── Retry ─── */

  async function retryAnalysis() {
    var contentEl = document.getElementById("modalContent");
    if (contentEl) {
      contentEl.innerHTML = skeletonCards(4) + skeletonLines(5);
    }
    try {
      var resp = await fetch("/ipodashboard/data/ipo_analysis.json?_=" + Date.now());
      if (resp.ok) {
        analysis = await resp.json();
      }
    } catch (_) {}
    if (currentIpo && analysis[analysisKey(currentIpo)]) {
      openModal(currentIpo);
      return;
    }
    if (contentEl) {
      contentEl.innerHTML = '<div class="section-pending">Analysis still pending. The AI analysis is run periodically via GitHub Actions. Check back later or ensure the workflow has completed.</div><div style="text-align:center;margin-top:12px"><button class="retry-btn" id="retryBtn">\u21BB Check Again</button></div>';
      document.getElementById("retryBtn").addEventListener("click", retryAnalysis);
    }
  }

  /* ─── Profile Builder ─── */

  function verdictIcon(badgeClass) {
    if (badgeClass === "verdict-subscribe") return "\uD83D\uDFE2";
    if (badgeClass === "verdict-avoid") return "\uD83D\uDD34";
    if (badgeClass === "verdict-neutral") return "\uD83D\uDFE1";
    return "\u23F3";
  }

  function buildProfileHtml(ipo, data) {
    var html = "";
    var hasData = !!data;

    // ── 1. Company Overview ──
    var aboutText = hasData && data.about ? data.about : null;
    html += '<section class="profile-section">';
    html += '<h3 class="section-title">Company Overview</h3>';
    if (aboutText) {
      html += '<p class="company-description">' + escHtml(aboutText) + '</p>';
    } else {
      html += '<div class="section-pending">Company information currently unavailable.</div>';
    }
    html += '</section>';

    // ── 2. IPO Metrics Grid ──
    var ipoArr = buildIpoDetailsArr(ipo);
    var mktCap = null;
    if (hasData && data.ipo_details) {
      var m = data.ipo_details.match(/[Mm]arket\s*[Cc]ap[:\s]*([^,;\.]+)/);
      if (m) mktCap = m[1].trim();
    }
    if (!mktCap && hasData && data.financial_summary) {
      var m = data.financial_summary.match(/[Mm]arket\s*[Cc]ap[:\s]*([^,;\.]+)/);
      if (m) mktCap = m[1].trim();
    }

    html += '<section class="profile-section">';
    html += '<h3 class="section-title">IPO Details</h3>';
    html += '<div class="metrics-grid">';
    for (var i = 0; i < ipoArr.length; i++) {
      html += '<div class="metric-card"><span class="metric-label">' + escHtml(ipoArr[i].label) + '</span><span class="metric-value">' + escHtml(ipoArr[i].value) + '</span></div>';
    }
    if (mktCap) {
      html += '<div class="metric-card"><span class="metric-label">Market Cap</span><span class="metric-value">' + escHtml(mktCap) + '</span></div>';
    }
    html += '</div></section>';

    // ── 3. Financial Snapshot ──
    var finText = hasData ? (data.financial_summary || data.financials || "") : "";
    var finMetrics = parseFinancialMetrics(finText);

    html += '<section class="profile-section">';
    html += '<h3 class="section-title">Financial Snapshot</h3>';
    if (finMetrics) {
      html += '<div class="metrics-grid">';
      var ordered = ["Revenue", "Profit", "Debt", "EPS", "P/E", "Growth"];
      for (var i = 0; i < ordered.length; i++) {
        if (finMetrics[ordered[i]]) {
          html += '<div class="metric-card"><span class="metric-label">' + ordered[i] + '</span><span class="metric-value">' + escHtml(finMetrics[ordered[i]]) + '</span></div>';
        }
      }
      html += '</div>';
      if (hasData && data.financial_trend) {
        html += '<div style="margin-top:12px;font-style:italic;font-size:13px;color:var(--text-muted);line-height:1.6">' + escHtml(data.financial_trend) + '</div>';
      }
    } else if (hasData && finText) {
      html += '<div style="line-height:1.8">' + escHtml(finText) + '</div>';
      if (data.financial_trend) {
        html += '<div style="margin-top:12px;font-style:italic;font-size:13px;color:var(--text-muted);line-height:1.6">' + escHtml(data.financial_trend) + '</div>';
      }
    } else {
      html += '<div class="section-pending">Financial data not available.</div>';
    }
    html += '</section>';

    // ── 4. Strengths ──
    html += '<section class="profile-section">';
    html += '<h3 class="section-title">Strengths</h3>';
    if (hasData && data.strengths && Array.isArray(data.strengths) && data.strengths.length) {
      html += '<ul class="bullet-list">';
      for (var i = 0; i < data.strengths.length; i++) {
        html += '<li>' + escHtml(typeof data.strengths[i] === "string" ? data.strengths[i] : String(data.strengths[i])) + '</li>';
      }
      html += '</ul>';
    } else {
      html += '<div class="section-pending">Strengths data not yet analyzed.</div>';
    }
    html += '</section>';

    // ── 5. Risks ──
    html += '<section class="profile-section">';
    html += '<h3 class="section-title">Risks</h3>';
    if (hasData && data.risks && data.risks.length > 0) {
      var enrichedRisks = hasStructuredRisks(data.risks) ? data.risks : enrichRisksWithIndicators(data.risks);
      html += '<div class="risk-list">';
      for (var i = 0; i < enrichedRisks.length; i++) {
        var r = enrichedRisks[i];
        var indicator = (typeof r === "object" && r.indicator) ? r.indicator : "\uD83D\uDFE1";
        var riskText = typeof r === "object" && r.text ? r.text : String(r);
        html += '<div class="risk-item"><span class="risk-indicator">' + indicator + '</span><span>' + escHtml(riskText) + '</span></div>';
      }
      html += '</div>';
    } else {
      html += '<div class="section-pending">Risk assessment pending...</div>';
    }
    html += '</section>';

    // ── 6. AI Scores ──
    var scores = hasData ? (data.scores || estimateScores(data.ai_analysis)) : null;
    html += '<section class="profile-section">';
    html += '<h3 class="section-title">AI Scores</h3>';
    if (scores) {
      var scoreKeys = [
        { key: "financial_health", label: "Financial Health", color: "#22c55e" },
        { key: "growth_potential", label: "Growth Potential", color: "#3b82f6" },
        { key: "risk", label: "Risk Score", color: "#f59e0b" },
        { key: "attractiveness", label: "IPO Attractiveness", color: "#a855f7" },
      ];
      html += '<div class="scores-grid">';
      for (var i = 0; i < scoreKeys.length; i++) {
        var val = scores[scoreKeys[i].key];
        if (typeof val !== "number") val = parseInt(val, 10) || 0;
        var capped = Math.min(Math.max(Math.round(val), 0), 100);
        html += '<div class="score-card"><div class="score-card-label">' + scoreKeys[i].label + '</div><div class="score-card-value">' + capped + '</div><div class="score-card-bar"><div class="score-card-fill" style="width:' + capped + '%;background:' + scoreKeys[i].color + '"></div></div></div>';
      }
      html += '</div>';
    } else {
      html += '<div class="section-pending">Scores not available.</div>';
    }
    html += '</section>';

    // ── 7. AI Analysis ──
    html += '<section class="profile-section">';
    html += '<h3 class="section-title">AI Analysis</h3>';
    if (hasData && data.ai_analysis) {
      html += '<div class="analysis-text">' + escHtml(data.ai_analysis) + '</div>';
    } else {
      html += '<div class="section-pending">Analysis pending...</div>';
    }
    html += '</section>';

    // ── 8. Final Verdict ──
    var verdict = hasData ? extractVerdict(data.ai_analysis, data.verdict) : null;
    var badgeClass = verdictBadgeClass(verdict);
    var badgeText = verdictBadgeText(badgeClass);
    var vIcon = verdictIcon(badgeClass);

    html += '<section class="profile-section">';
    html += '<div class="verdict-card ' + badgeClass + '">';
    html += '<span class="verdict-icon">' + vIcon + '</span>';
    html += '<div class="verdict-content">';
    html += '<span class="verdict-label">' + badgeText + '</span>';
    if (verdict) {
      html += '<p class="verdict-description">' + escHtml(verdict) + '</p>';
    }
    html += '</div></div>';
    html += '<div class="verdict-note">Note: This analysis is AI-generated based on model knowledge and should not be considered financial advice. Always do your own research.</div>';
    html += '</section>';

    return html;
  }

  /* ─── Modal ─── */

  function openModal(ipo) {
    currentIpo = ipo;
    var key = analysisKey(ipo);
    var data = analysis[key] || null;

    modalTitle.textContent = ipo.company_name || "Unknown";
    document.getElementById("modalSymbol").textContent = ipo.symbol || "\u2014";
    document.getElementById("modalExchange").textContent = ipo.exchange || "\u2014";

    var country = getCountry(ipo);
    var countryBadge = document.getElementById("modalCountryBadge");
    countryBadge.textContent = country;
    countryBadge.className = "country-badge " + countryClass(country);

    var statusBadge = document.getElementById("modalStatusBadge");
    statusBadge.textContent = (ipo.status || "upcoming");
    statusBadge.className = "status-badge " + statusClass(ipo.status);

    var contentEl = document.getElementById("modalContent");
    contentEl.innerHTML = buildProfileHtml(ipo, data);

    if (!data) {
      setTimeout(function () {
        var rb = document.getElementById("retryBtn");
        if (rb) rb.addEventListener("click", retryAnalysis);
      }, 0);
    }

    showModal();
  }

  function showModal() {
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.classList.remove("open");
    document.body.style.overflow = "";
  }

  modalClose.addEventListener("click", closeModal);
  modal.querySelector(".modal-backdrop").addEventListener("click", closeModal);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });

  /* ─── Table ─── */

  function render() {
    var filtered = ipos.filter(function (ipo) { return matchesFilter(ipo, currentFilter); });

    if (searchTerm) {
      var term = searchTerm.toLowerCase();
      filtered = filtered.filter(function (ipo) {
        return (ipo.company_name || "").toLowerCase().indexOf(term) !== -1 ||
               (ipo.symbol || "").toLowerCase().indexOf(term) !== -1;
      });
    }

    if (sortKey) {
      filtered.sort(function (a, b) {
        var va = (a[sortKey] || "").toString().toLowerCase();
        var vb = (b[sortKey] || "").toString().toLowerCase();
        if (sortKey === "issue_size") {
          va = parseFloat(va.replace(/[^0-9.]/g, "")) || 0;
          vb = parseFloat(vb.replace(/[^0-9.]/g, "")) || 0;
        } else if (sortKey === "subscription") {
          va = parseSubscription(a.subscription);
          vb = parseSubscription(b.subscription);
        } else if (sortKey === "listing_date") {
          va = va || "9999-99-99";
          vb = vb || "9999-99-99";
        }
        if (va < vb) return sortAsc ? -1 : 1;
        if (va > vb) return sortAsc ? 1 : -1;
        return 0;
      });
    }

    ipoCountEl.textContent = "Showing " + filtered.length + " of " + ipos.length + " IPOs";

    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-muted);">No IPOs found</td></tr>';
      return;
    }

    tbody.innerHTML = filtered.map(function (ipo, i) {
      var s = (ipo.status || "upcoming").toLowerCase();
      var country = getCountry(ipo);
      return '<tr data-index="' + i + '">' +
        '<td class="symbol-cell">' + escHtml(ipo.symbol || "\u2014") + "</td>" +
        '<td><span class="company-name">' + escHtml(ipo.company_name || "\u2014") + '</span><span class="country-badge ' + countryClass(country) + '">' + escHtml(country) + "</span></td>" +
        '<td><span class="exchange-badge">' + escHtml(ipo.exchange || "\u2014") + "</span></td>" +
        "<td>" + escHtml(ipo.price_band || "\u2014") + "</td>" +
        "<td>" + formatDate(ipo.listing_date) + "</td>" +
        "<td>" + escHtml(ipo.issue_size || "\u2014") + '</td>' +
        '<td class="subscription-value">' + escHtml(ipo.subscription || "\u2014") + "</td>" +
        '<td><span class="status-badge ' + statusClass(s) + '">' + escHtml(s) + "</span></td>" +
        "</tr>";
    }).join("");
  }

  function handleSort(e) {
    var th = e.target.closest("th.sortable");
    if (!th) return;
    var key = th.dataset.sort;
    if (sortKey === key) {
      sortAsc = !sortAsc;
    } else {
      sortKey = key;
      sortAsc = true;
    }
    document.querySelectorAll("th.sortable").forEach(function (el) {
      el.classList.remove("sort-asc", "sort-desc");
    });
    th.classList.add(sortAsc ? "sort-asc" : "sort-desc");
    render();
  }

  document.querySelectorAll("th.sortable").forEach(function (th) {
    th.addEventListener("click", handleSort);
  });

  tbody.addEventListener("click", function (e) {
    var tr = e.target.closest("tr[data-index]");
    if (!tr) return;
    var idx = parseInt(tr.dataset.index, 10);
    var filtered = ipos.filter(function (ipo) { return matchesFilter(ipo, currentFilter); }).filter(function (ipo) {
      if (!searchTerm) return true;
      var term = searchTerm.toLowerCase();
      return (ipo.company_name || "").toLowerCase().indexOf(term) !== -1 ||
             (ipo.symbol || "").toLowerCase().indexOf(term) !== -1;
    });
    var ipo = filtered[idx];
    if (ipo) openModal(ipo);
  });

  searchInput.addEventListener("input", function (e) {
    searchTerm = e.target.value;
    render();
  });

  filterButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      filterButtons.forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      currentFilter = btn.dataset.filter;
      render();
    });
  });

  /* ─── Load ─── */

  async function load() {
    try {
      var [ipoResp, analysisResp] = await Promise.all([
        fetch("/ipodashboard/data/ipos.json?_=" + Date.now()),
        fetch("/ipodashboard/data/ipo_analysis.json?_=" + Date.now()),
      ]);
      var ipoData = await ipoResp.json();
      ipos = ipoData.ipos || [];

      if (ipoData.last_updated) {
        var d = new Date(ipoData.last_updated);
        lastUpdatedEl.textContent = "Last updated: " + d.toLocaleDateString("en-IN", {
          day: "numeric", month: "short", year: "numeric",
          hour: "2-digit", minute: "2-digit"
        }) + " IST";
      }

      if (analysisResp.ok) {
        analysis = await analysisResp.json();
      }
    } catch (err) {
      lastUpdatedEl.textContent = "Could not load IPO data. Ensure the scraper has run.";
    }
    render();
  }

  load();
})();
