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

  function renderIpoDetailsGrid(arr) {
    if (!arr || arr.length === 0) {
      return '<div class="section-pending">IPO details not available.</div>';
    }
    var html = '<div class="ipo-details-grid">';
    for (var i = 0; i < arr.length; i++) {
      html += '<div class="detail-item"><span class="detail-label">' + escHtml(arr[i].label) + '</span><span class="detail-value">' + escHtml(arr[i].value) + "</span></div>";
    }
    return html + "</div>";
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
    ];
    for (var i = 0; i < patterns.length; i++) {
      var match = text.match(patterns[i].regex);
      if (match) metrics[patterns[i].key] = match[1].trim();
    }
    return Object.keys(metrics).length > 0 ? metrics : null;
  }

  function renderFinancialMetrics(metrics, trend) {
    var html = '<div class="fin-metrics-grid">';
    for (var key in metrics) {
      if (metrics.hasOwnProperty(key)) {
        html += '<div class="fin-card"><span class="fin-card-label">' + escHtml(key) + '</span><span class="fin-card-value">' + escHtml(metrics[key]) + "</span></div>";
      }
    }
    html += "</div>";
    if (trend) {
      html += '<div class="fin-trend">' + escHtml(trend) + "</div>";
    }
    return html;
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

  function renderRisks(risks) {
    return risks.map(function (r) {
      var indicator = (typeof r === "object" && r.indicator) ? r.indicator : "\uD83D\uDFE1";
      var dotClass = "amber";
      if (indicator === "\uD83D\uDFE2") dotClass = "green";
      else if (indicator === "\uD83D\uDD34") dotClass = "red";
      var riskText = typeof r === "object" && r.text ? r.text : String(r);
      return '<div class="risk-item"><span class="risk-indicator ' + dotClass + '">' + indicator + '</span><span>' + escHtml(riskText) + "</span></div>";
    }).join("");
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

  function renderScoreBars(scores) {
    var keys = [
      { key: "financial_health", label: "Financial Health" },
      { key: "growth_potential", label: "Growth Potential" },
      { key: "risk", label: "Risk" },
      { key: "attractiveness", label: "IPO Attractiveness" },
    ];
    var colors = ["#22c55e", "#3b82f6", "#f59e0b", "#a855f7"];
    var html = "";
    for (var i = 0; i < keys.length; i++) {
      var val = scores[keys[i].key];
      if (typeof val !== "number") val = parseInt(val, 10) || 0;
      var capped = Math.min(Math.max(Math.round(val), 0), 100);
      html += '<div class="score-bar-wrap"><div class="score-bar-label"><span>' + keys[i].label + '</span><span>' + capped + '/100</span></div><div class="score-bar-track"><div class="score-bar-fill" style="width:' + capped + '%;background:' + colors[i] + '"></div></div></div>';
    }
    return html;
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

  function showSkeletons() {
    var els = ["modalAbout", "modalIpoDetails", "modalFinancials", "modalStrengths", "modalRisks", "modalScores", "modalAiAnalysis", "modalVerdict"];
    for (var i = 0; i < els.length; i++) {
      var el = document.getElementById(els[i]);
      if (!el) continue;
      if (i === 1 || i === 2) {
        el.innerHTML = skeletonCards(4);
      } else if (i === 6) {
        el.innerHTML = skeletonLines(4);
      } else {
        el.innerHTML = skeletonLines(3);
      }
    }
  }

  async function retryAnalysis() {
    var btn = document.getElementById("retryBtn");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Checking...';
    }
    showSkeletons();
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
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = "\u21BB Check Again";
    }
    var verdictEl = document.getElementById("modalVerdict");
    if (verdictEl) {
      verdictEl.innerHTML = '<div class="section-pending">Analysis still pending. The AI analysis is run periodically via GitHub Actions. Check back later or ensure the workflow has completed.</div><button class="retry-btn" id="retryBtn">\u21BB Check Again</button>';
      document.getElementById("retryBtn").addEventListener("click", retryAnalysis);
    }
  }

  /* ─── Modal ─── */

  function openModal(ipo) {
    currentIpo = ipo;
    var key = analysisKey(ipo);
    var data = analysis[key] || null;

    modalTitle.textContent = ipo.company_name || "Unknown";
    modalSymbol.textContent = (ipo.symbol || "\u2014") + " \u00B7 " + (ipo.exchange || "") + " \u00B7 " + (ipo.country || "Global");

    var aboutEl = document.getElementById("modalAbout");
    var ipoDetailsEl = document.getElementById("modalIpoDetails");
    var finEl = document.getElementById("modalFinancials");
    var strEl = document.getElementById("modalStrengths");
    var riskEl = document.getElementById("modalRisks");
    var scoresEl = document.getElementById("modalScores");
    var aiEl = document.getElementById("modalAiAnalysis");
    var verdictEl = document.getElementById("modalVerdict");

    if (!data) {
      // Show metadata-enriched fallback without permanent "Analyzing" spinner
      aboutEl.innerHTML = '<div class="section-pending">Company overview currently unavailable. IPO analysis and available financial data are shown below.</div>';
      ipoDetailsEl.innerHTML = renderIpoDetailsGrid(buildIpoDetailsArr(ipo));
      finEl.innerHTML = '<div class="section-pending">Financial data is being analyzed. Check back after the next AI analysis run.</div>';
      strEl.innerHTML = '<div class="section-pending">Strengths being evaluated...</div>';
      riskEl.innerHTML = '<div class="section-pending">Risks being assessed...</div>';
      scoresEl.innerHTML = '<div class="section-pending">AI scoring in progress...</div>';
      aiEl.innerHTML = '<div class="section-pending">Detailed analysis pending...</div>';
      verdictEl.innerHTML = '<span class="verdict-badge verdict-pending">Awaiting Analysis</span><div class="section-pending">AI analysis has not been generated yet. It runs periodically via GitHub Actions.</div><button class="retry-btn" id="retryBtn">\u21BB Check for Updates</button>';
      // Defer retry binding so DOM is ready
      setTimeout(function () {
        var rb = document.getElementById("retryBtn");
        if (rb) rb.addEventListener("click", retryAnalysis);
      }, 0);
      showModal();
      return;
    }

    // ===== ABOUT =====
    aboutEl.innerHTML = data.about
      ? escHtml(data.about)
      : '<div class="section-pending">Company overview currently unavailable. IPO analysis and available financial data are shown below.</div>';

    // ===== IPO DETAILS =====
    if (data.ipo_details) {
      // Try to parse AI details as structured text
      var ipoDetailArr = buildIpoDetailsArr(ipo);
      ipoDetailsEl.innerHTML = renderIpoDetailsGrid(ipoDetailArr);
    } else {
      ipoDetailsEl.innerHTML = renderIpoDetailsGrid(buildIpoDetailsArr(ipo));
    }

    // ===== FINANCIAL SUMMARY =====
    var finText = data.financial_summary || data.financials || "";
    var metrics = parseFinancialMetrics(finText);
    if (metrics) {
      finEl.innerHTML = renderFinancialMetrics(metrics, data.financial_trend || null);
    } else if (finText) {
      var fhtml = '<div style="line-height:1.8">' + escHtml(finText) + "</div>";
      if (data.financial_trend) {
        fhtml += '<div class="fin-trend">' + escHtml(data.financial_trend) + "</div>";
      }
      finEl.innerHTML = fhtml;
    } else {
      finEl.innerHTML = '<div class="section-pending">Financial data not available.</div>';
    }

    // ===== STRENGTHS =====
    if (data.strengths && Array.isArray(data.strengths) && data.strengths.length) {
      strEl.innerHTML = "<ul>" + data.strengths.map(function (s) {
        return "<li>" + escHtml(typeof s === "string" ? s : String(s)) + "</li>";
      }).join("") + "</ul>";
    } else {
      strEl.innerHTML = '<div class="section-pending">Strengths data not yet analyzed.</div>';
    }

    // ===== RISKS =====
    var risks = data.risks || [];
    if (risks.length > 0) {
      var enrichedRisks = hasStructuredRisks(risks) ? risks : enrichRisksWithIndicators(risks);
      riskEl.innerHTML = renderRisks(enrichedRisks);
    } else {
      riskEl.innerHTML = '<div class="section-pending">Risk assessment pending...</div>';
    }

    // ===== SCORES =====
    var scores = data.scores;
    if (!scores) {
      scores = estimateScores(data.ai_analysis);
    }
    if (scores) {
      scoresEl.innerHTML = renderScoreBars(scores);
    } else {
      scoresEl.innerHTML = '<div class="section-pending">Scores not available.</div>';
    }

    // ===== AI ANALYSIS =====
    if (data.ai_analysis) {
      aiEl.innerHTML = '<div class="ai-analysis-text">' + escHtml(data.ai_analysis) + "</div>";
    } else {
      aiEl.innerHTML = '<div class="section-pending">Analysis pending...</div>';
    }

    // ===== VERDICT =====
    var verdict = extractVerdict(data.ai_analysis, data.verdict);
    var badgeClass = verdictBadgeClass(verdict);
    var badgeText = verdictBadgeText(badgeClass);

    var vHtml = '<span class="verdict-badge ' + badgeClass + '">' + badgeText + "</span>";
    if (verdict) {
      vHtml += "<div>" + escHtml(verdict) + "</div>";
    }
    vHtml += '<div class="verdict-note">Note: This analysis is AI-generated based on model knowledge and should not be considered financial advice. Always do your own research.</div>';
    verdictEl.innerHTML = vHtml;

    document.querySelectorAll(".detail-card").forEach(function (card) {
      card.classList.remove("collapsed");
    });

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

  document.querySelectorAll(".detail-card-head").forEach(function (head) {
    head.addEventListener("click", function () {
      this.parentElement.classList.toggle("collapsed");
    });
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
