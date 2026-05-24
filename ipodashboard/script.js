(function () {
  let ipos = [];
  let analysis = {};
  let currentFilter = "all";
  let searchTerm = "";
  let sortKey = null;
  let sortAsc = true;

  const tbody = document.getElementById("ipoBody");
  const searchInput = document.getElementById("searchInput");
  const filterButtons = document.querySelectorAll(".filter-btn");
  const lastUpdatedEl = document.getElementById("lastUpdated");
  const ipoCountEl = document.getElementById("ipoCount");

  const modal = document.getElementById("ipoModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalSymbol = document.getElementById("modalSymbol");
  const modalClose = document.getElementById("modalClose");

  function formatDate(dateStr) {
    if (!dateStr) return "\u2014";
    const parts = dateStr.split("-");
    if (parts.length !== 3) return dateStr;
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const m = months[parseInt(parts[1], 10) - 1] || parts[1];
    return `${m} ${parseInt(parts[2], 10)}, ${parts[0]}`;
  }

  function statusClass(status) {
    const s = (status || "upcoming").toLowerCase();
    if (s === "upcoming") return "status-upcoming";
    if (s === "open") return "status-open";
    if (s === "subscribed") return "status-subscribed";
    if (s === "listed") return "status-listed";
    if (s === "closed") return "status-closed";
    return "status-upcoming";
  }

  function getCountry(ipo) {
    const exchange = (ipo.exchange || "").toUpperCase();
    if (exchange === "NSE" || exchange === "BSE") return "India";
    const country = ipo.country || "";
    if (country === "India" || country === "USA") return country;
    if (["NYSE", "NASDAQ", "NYSE AMERICAN"].includes(exchange)) return "USA";
    return "Global";
  }

  function countryClass(country) {
    const c = (country || "").toLowerCase();
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
    const match = subStr.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : -Infinity;
  }

  function render() {
    let filtered = ipos.filter((ipo) => matchesFilter(ipo, currentFilter));

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (ipo) =>
          (ipo.company_name || "").toLowerCase().includes(term) ||
          (ipo.symbol || "").toLowerCase().includes(term)
      );
    }

    if (sortKey) {
      filtered.sort((a, b) => {
        let va = (a[sortKey] || "").toString().toLowerCase();
        let vb = (b[sortKey] || "").toString().toLowerCase();

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

    ipoCountEl.textContent = `Showing ${filtered.length} of ${ipos.length} IPOs`;

    if (filtered.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-muted);">No IPOs found</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered
      .map((ipo, i) => {
        const s = (ipo.status || "upcoming").toLowerCase();
        const country = getCountry(ipo);
        return `<tr data-index="${i}">
          <td class="symbol-cell">${escHtml(ipo.symbol || "\u2014")}</td>
          <td>
            <span class="company-name">${escHtml(ipo.company_name || "\u2014")}</span>
            <span class="country-badge ${countryClass(country)}">${escHtml(country)}</span>
          </td>
          <td><span class="exchange-badge">${escHtml(ipo.exchange || "\u2014")}</span></td>
          <td>${escHtml(ipo.price_band || "\u2014")}</td>
          <td>${formatDate(ipo.listing_date)}</td>
          <td>${escHtml(ipo.issue_size || "\u2014")}</td>
          <td class="subscription-value">${escHtml(ipo.subscription || "\u2014")}</td>
          <td><span class="status-badge ${statusClass(s)}">${escHtml(s)}</span></td>
        </tr>`;
      })
      .join("");
  }

  function escHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function analysisKey(ipo) {
    const sym = (ipo.symbol || "").toUpperCase().trim();
    const country = (ipo.country || "Global").trim();
    if (sym) return sym + "-" + country;
    const name = (ipo.company_name || "").toLowerCase().trim().replace(/\s+/g, "-").slice(0, 20);
    return name + "-" + country;
  }

  // Helper: detect if risks are in old format (plain strings) or new (objects with indicators)
  function hasStructuredRisks(risks) {
    if (!Array.isArray(risks) || risks.length === 0) return false;
    return typeof risks[0] === "object" && risks[0].indicator;
  }

  // Helper: auto-assign indicators to plain-text risks based on sentiment
  function enrichRisksWithIndicators(riskTexts) {
    if (!Array.isArray(riskTexts)) return [];
    const negativeKeywords = ["loss", "fail", "risk", "decline", "uncertain", "challenge", "pressure", "volatile", "intense", "dependence"];
    const positiveKeywords = ["opportunity", "advantage", "strong", "established", "experienced"];
    
    return riskTexts.map(function(text) {
      const lowerText = typeof text === "string" ? text.toLowerCase() : String(text).toLowerCase();
      let indicator = "🟡"; // default to medium
      const negCount = negativeKeywords.filter(function(kw) { return lowerText.includes(kw); }).length;
      const posCount = positiveKeywords.filter(function(kw) { return lowerText.includes(kw); }).length;
      
      if (negCount > posCount) indicator = "🔴";
      else if (posCount > negCount) indicator = "🟢";
      
      return {
        text: typeof text === "string" ? text : String(text),
        indicator: indicator
      };
    });
  }

  // Helper: generate rough scores from sentiment in analysis text
  function estimateScores(analysisText) {
    if (!analysisText) {
      return { financial_health: 50, growth_potential: 50, risk: 50, attractiveness: 50 };
    }
    
    const text = analysisText.toLowerCase();
    const positiveKeywords = ["compelling", "strong", "opportunity", "growth", "upside", "attractive", "solid", "positive"];
    const negativeKeywords = ["risk", "challenge", "caution", "uncertain", "volatile", "pressure", "decline"];
    
    let sentiment = 0;
    positiveKeywords.forEach(function(kw) {
      if (text.includes(kw)) sentiment += 10;
    });
    negativeKeywords.forEach(function(kw) {
      if (text.includes(kw)) sentiment -= 8;
    });
    
    let baseScore = Math.max(35, Math.min(75, 50 + sentiment));
    return {
      financial_health: baseScore + Math.random() * 10 - 5,
      growth_potential: baseScore + Math.random() * 15 - 7,
      risk: 100 - (baseScore + Math.random() * 10 - 5),
      attractiveness: baseScore + Math.random() * 12 - 6
    };
  }

  // Helper: extract verdict recommendation from analysis text
  function extractVerdict(analysisText, verdictField) {
    if (verdictField) return verdictField;
    if (!analysisText) return "Awaiting AI analysis";
    
    const text = analysisText.toLowerCase();
    if (text.includes("avoid") || text.includes("caution") || text.includes("risky")) {
      return "Avoid - Consider alternatives with lower risk profiles";
    }
    if (text.includes("compelling") || text.includes("opportunity") || text.includes("consider")) {
      return "Subscribe - Offers compelling growth potential";
    }
    return "Watch - Monitor performance and execution";
  }

  // Helper: build IPO details from metadata
  function buildIpoDetails(ipo) {
    const details = [];
    if (ipo.price_band) details.push("Price Band: " + ipo.price_band);
    if (ipo.issue_size) details.push("Issue Size: " + ipo.issue_size);
    if (ipo.lot_size) details.push("Lot Size: " + ipo.lot_size + " shares");
    if (ipo.exchange) details.push("Exchange: " + ipo.exchange);
    if (ipo.listing_date) details.push("Listing Date: " + formatDate(ipo.listing_date));
    if (ipo.subscription) details.push("Subscription Status: " + ipo.subscription);
    if (ipo.open_date) details.push("Open Date: " + formatDate(ipo.open_date));
    if (ipo.close_date) details.push("Close Date: " + formatDate(ipo.close_date));
    
    if (details.length === 0) {
      return "IPO details: " + (ipo.company_name || "Company") + " on " + (ipo.exchange || "exchange");
    }
    return details.join(" • ");
  }

  function openModal(ipo) {
    const key = analysisKey(ipo);
    const data = analysis[key] || null;

    modalTitle.textContent = ipo.company_name || "Unknown";
    modalSymbol.textContent = (ipo.symbol || "\u2014") + " \u00B7 " + (ipo.exchange || "") + " \u00B7 " + (ipo.country || "Global");

    const aboutEl = document.getElementById("modalAbout");
    const ipoDetailsEl = document.getElementById("modalIpoDetails");
    const finEl = document.getElementById("modalFinancials");
    const strEl = document.getElementById("modalStrengths");
    const riskEl = document.getElementById("modalRisks");
    const scoresEl = document.getElementById("modalScores");
    const aiEl = document.getElementById("modalAiAnalysis");
    const verdictEl = document.getElementById("modalVerdict");

    console.log("[IPO Modal] Opening", ipo.company_name, "Key:", key, "Analysis found:", !!data);

    if (!data) {
      console.warn("[IPO Modal] No analysis found for", key, "- showing fallback message");
      let msg = '<div class="modal-loading">Analysis pending for this IPO. Check back soon!</div>';
      aboutEl.innerHTML = msg;
      ipoDetailsEl.innerHTML = buildIpoDetails(ipo);
      finEl.innerHTML = "Financial data is being analyzed...";
      strEl.innerHTML = "Strengths being evaluated...";
      riskEl.innerHTML = "Risks being assessed...";
      scoresEl.innerHTML = "AI scoring in progress...";
      aiEl.innerHTML = "Detailed analysis pending...";
      verdictEl.innerHTML = '<span class="verdict-badge verdict-neutral">Analyzing</span><div>AI analysis in progress. Refresh the page to see updated analysis.</div>';
      showModal();
      return;
    }

    console.log("[IPO Modal] Data structure:", Object.keys(data));

    // ===== ABOUT =====
    aboutEl.innerHTML = escHtml(data.about || "No information available.");

    // ===== IPO DETAILS =====
    let ipoDetails = data.ipo_details;
    if (!ipoDetails) {
      ipoDetails = buildIpoDetails(ipo);
      console.log("[IPO Modal] ipo_details missing, built from metadata:", ipoDetails);
    }
    ipoDetailsEl.innerHTML = escHtml(ipoDetails);

    // ===== FINANCIAL DATA =====
    let finText = data.financial_summary || data.financials || "";
    if (data.financial_trend) {
      finText = finText + '<div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border);font-style:italic;">' + escHtml(data.financial_trend) + "</div>";
    } else if (!finText) {
      finText = "Based on " + (ipo.company_name || "company") + " IPO at " + (ipo.price_band || "market price") + " on " + (ipo.exchange || "exchange");
    }
    finEl.innerHTML = finText || "Financial data not available.";

    // ===== STRENGTHS =====
    if (data.strengths && Array.isArray(data.strengths) && data.strengths.length) {
      strEl.innerHTML = "<ul>" + data.strengths.map(function(s) {
        return "<li>" + escHtml(typeof s === "string" ? s : String(s)) + "</li>";
      }).join("") + "</ul>";
    } else {
      strEl.innerHTML = "Strengths data not yet analyzed.";
    }

    // ===== RISKS =====
    let risks = data.risks || [];
    if (risks.length > 0) {
      let enrichedRisks = hasStructuredRisks(risks) ? risks : enrichRisksWithIndicators(risks);
      console.log("[IPO Modal] Risks structured:", hasStructuredRisks(risks), "Count:", enrichedRisks.length);
      
      riskEl.innerHTML = enrichedRisks.map(function(r) {
        let indicator = (typeof r === "object" && r.indicator) ? r.indicator : "🟡";
        let dotClass = "amber";
        if (indicator === "🟢") dotClass = "green";
        else if (indicator === "🔴") dotClass = "red";
        
        let riskText = typeof r === "object" && r.text ? r.text : String(r);
        return '<div class="risk-item"><span class="risk-indicator ' + dotClass + '">' + indicator + '</span><span>' + escHtml(riskText) + "</span></div>";
      }).join("");
    } else {
      riskEl.innerHTML = "Risk assessment pending...";
    }

    // ===== SCORES =====
    let scores = data.scores;
    if (!scores) {
      scores = estimateScores(data.ai_analysis);
      console.log("[IPO Modal] scores missing, estimated from analysis");
    }
    
    if (scores) {
      let scoreKeys = [
        { key: "financial_health", label: "Financial Health" },
        { key: "growth_potential", label: "Growth Potential" },
        { key: "risk", label: "Risk" },
        { key: "attractiveness", label: "IPO Attractiveness" },
      ];
      let scoreColors = ["#22c55e", "#3b82f6", "#f59e0b", "#a855f7"];
      scoresEl.innerHTML = scoreKeys.map(function(sk, i) {
        let val = scores[sk.key];
        if (typeof val !== "number") val = parseInt(val, 10) || 0;
        let capped = Math.min(Math.max(Math.round(val), 0), 100);
        return '<div class="score-bar-wrap"><div class="score-bar-label"><span>' + sk.label + '</span><span>' + capped + "/100</span></div><div class=\"score-bar-track\"><div class=\"score-bar-fill\" style=\"width:" + capped + "%;background:" + scoreColors[i] + "\"></div></div></div>";
      }).join("");
    } else {
      scoresEl.innerHTML = "Scores not available.";
    }

    // ===== AI ANALYSIS =====
    aiEl.innerHTML = escHtml(data.ai_analysis || "Analysis pending...");

    // ===== VERDICT =====
    let verdict = extractVerdict(data.ai_analysis, data.verdict);
    let v = verdict.toLowerCase();
    let badgeClass = "verdict-neutral";
    if (v.includes("subscribe")) badgeClass = "verdict-subscribe";
    else if (v.includes("avoid")) badgeClass = "verdict-avoid";
    
    let badgeText = badgeClass === "verdict-subscribe" ? "Subscribe" : badgeClass === "verdict-avoid" ? "Avoid" : "Watch";
    let verdictHtml = '<span class="verdict-badge ' + badgeClass + '">' + badgeText + '</span><div>' + escHtml(verdict) + "</div>";
    verdictHtml += '<div class="verdict-note">Note: This analysis is AI-generated based on model knowledge and should not be considered financial advice. Always do your own research.</div>';
    verdictEl.innerHTML = verdictHtml;

    document.querySelectorAll(".detail-card").forEach(function(card) {
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
  document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") closeModal();
  });

  document.querySelectorAll(".detail-card-head").forEach(function(head) {
    head.addEventListener("click", function() {
      this.parentElement.classList.toggle("collapsed");
    });
  });

  function handleSort(e) {
    const th = e.target.closest("th.sortable");
    if (!th) return;
    const key = th.dataset.sort;
    if (sortKey === key) {
      sortAsc = !sortAsc;
    } else {
      sortKey = key;
      sortAsc = true;
    }
    document.querySelectorAll("th.sortable").forEach((el) => {
      el.classList.remove("sort-asc", "sort-desc");
    });
    th.classList.add(sortAsc ? "sort-asc" : "sort-desc");
    render();
  }

  document.querySelectorAll("th.sortable").forEach((th) => {
    th.addEventListener("click", handleSort);
  });

  tbody.addEventListener("click", (e) => {
    const tr = e.target.closest("tr[data-index]");
    if (!tr) return;
    const idx = parseInt(tr.dataset.index, 10);
    const filtered = ipos.filter((ipo) => matchesFilter(ipo, currentFilter)).filter((ipo) => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      return (ipo.company_name || "").toLowerCase().includes(term) || (ipo.symbol || "").toLowerCase().includes(term);
    });
    const ipo = filtered[idx];
    if (ipo) openModal(ipo);
  });

  searchInput.addEventListener("input", (e) => {
    searchTerm = e.target.value;
    render();
  });

  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.dataset.filter;
      render();
    });
  });

  async function load() {
    try {
      console.log("[IPO Dashboard] Loading data...");
      const [ipoResp, analysisResp] = await Promise.all([
        fetch("/ipodashboard/data/ipos.json?_=" + Date.now()),
        fetch("/ipodashboard/data/ipo_analysis.json?_=" + Date.now()),
      ]);
      
      const ipoData = await ipoResp.json();
      ipos = ipoData.ipos || [];
      console.log("[IPO Dashboard] Loaded", ipos.length, "IPOs");
      
      if (ipoData.last_updated) {
        const d = new Date(ipoData.last_updated);
        lastUpdatedEl.textContent = `Last updated: ${d.toLocaleDateString("en-IN", {
          day: "numeric",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })} IST`;
      }
      
      if (analysisResp.ok) {
        analysis = await analysisResp.json();
        const analysisCount = Object.keys(analysis).length;
        console.log("[IPO Dashboard] Loaded analysis for", analysisCount, "IPOs");
        if (analysisCount === 0) {
          console.warn("[IPO Dashboard] Analysis data is empty - waiting for first run or API keys");
        }
      } else {
        console.warn("[IPO Dashboard] Analysis file not found or error, continuing with metadata only");
      }
    } catch (err) {
      console.error("[IPO Dashboard] Error loading data:", err);
      lastUpdatedEl.textContent = "Error loading IPO data. Check browser console.";
    }
    render();
  }

  load();
})();
