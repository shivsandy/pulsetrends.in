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

    if (!data) {
      var msg = '<div class="modal-loading">Analysis pending for this IPO</div>';
      aboutEl.innerHTML = msg;
      ipoDetailsEl.innerHTML = "";
      finEl.innerHTML = "";
      strEl.innerHTML = "";
      riskEl.innerHTML = "";
      scoresEl.innerHTML = "";
      aiEl.innerHTML = "";
      verdictEl.innerHTML = "";
      showModal();
      return;
    }

    aboutEl.innerHTML = escHtml(data.about || "No information available.");
    ipoDetailsEl.innerHTML = escHtml(data.ipo_details || "Not available.");

    var finText = data.financial_summary || "";
    if (data.financial_trend) {
      finText = finText + '<div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border);font-style:italic;">' + escHtml(data.financial_trend) + "</div>";
    }
    finEl.innerHTML = finText || "Financial data not available.";

    strEl.innerHTML = (data.strengths && data.strengths.length)
      ? "<ul>" + data.strengths.map(function(s) { return "<li>" + escHtml(s) + "</li>"; }).join("") + "</ul>"
      : "Not available.";

    if (data.risks && data.risks.length) {
      riskEl.innerHTML = data.risks.map(function(r) {
        var indicator = r.indicator || "🟡";
        var dotClass = "green";
        if (indicator === "🟡") dotClass = "amber";
        else if (indicator === "🔴") dotClass = "red";
        return '<div class="risk-item"><span class="risk-indicator ' + dotClass + '">' + indicator + '</span><span>' + escHtml(r.text || r) + "</span></div>";
      }).join("");
    } else {
      riskEl.innerHTML = "Not available.";
    }

    if (data.scores) {
      var scoreKeys = [
        { key: "financial_health", label: "Financial Health" },
        { key: "growth_potential", label: "Growth Potential" },
        { key: "risk", label: "Risk" },
        { key: "attractiveness", label: "IPO Attractiveness" },
      ];
      var scoreColors = ["#22c55e", "#3b82f6", "#f59e0b", "#a855f7"];
      scoresEl.innerHTML = scoreKeys.map(function(sk, i) {
        var val = data.scores[sk.key];
        if (typeof val !== "number") val = parseInt(val, 10) || 0;
        var capped = Math.min(Math.max(val, 0), 100);
        return '<div class="score-bar-wrap"><div class="score-bar-label"><span>' + sk.label + '</span><span>' + capped + "/100</span></div><div class=\"score-bar-track\"><div class=\"score-bar-fill\" style=\"width:" + capped + "%;background:" + scoreColors[i] + "\"></div></div></div>";
      }).join("");
    } else {
      scoresEl.innerHTML = "Scores not available.";
    }

    aiEl.innerHTML = escHtml(data.ai_analysis || "No analysis available.");

    var verdictHtml = "";
    if (data.verdict) {
      var v = data.verdict.toLowerCase();
      var badgeClass = "verdict-neutral";
      if (v.indexOf("subscribe") !== -1) badgeClass = "verdict-subscribe";
      else if (v.indexOf("avoid") !== -1) badgeClass = "verdict-avoid";
      var badgeText = badgeClass === "verdict-subscribe" ? "Subscribe" : badgeClass === "verdict-avoid" ? "Avoid" : "Neutral";
      verdictHtml = '<span class="verdict-badge ' + badgeClass + '">' + badgeText + '</span><div>' + escHtml(data.verdict) + "</div>";
    }
    verdictHtml += '<div class="verdict-note">Note: This analysis is AI-generated based on model knowledge and should not be considered financial advice. Always do your own research.</div>';
    verdictEl.innerHTML = verdictHtml || "Verdict not available.";

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
      const [ipoResp, analysisResp] = await Promise.all([
        fetch("/ipodashboard/data/ipos.json?_=" + Date.now()),
        fetch("/ipodashboard/data/ipo_analysis.json?_=" + Date.now()),
      ]);
      const ipoData = await ipoResp.json();
      ipos = ipoData.ipos || [];
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
      }
    } catch (err) {
      lastUpdatedEl.textContent = "Could not load IPO data. Ensure the scraper has run.";
    }
    render();
  }

  load();
})();
