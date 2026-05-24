(function () {
  let ipos = [];
  let currentFilter = "all";
  let searchTerm = "";
  let sortKey = null;
  let sortAsc = true;

  const tbody = document.getElementById("ipoBody");
  const searchInput = document.getElementById("searchInput");
  const filterButtons = document.querySelectorAll(".filter-btn");
  const lastUpdatedEl = document.getElementById("lastUpdated");
  const ipoCountEl = document.getElementById("ipoCount");

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
      .map((ipo) => {
        const s = (ipo.status || "upcoming").toLowerCase();
        const country = getCountry(ipo);
        return `<tr>
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
      const resp = await fetch("/ipodashboard/data/ipos.json?_=" + Date.now());
      const data = await resp.json();
      ipos = data.ipos || [];
      if (data.last_updated) {
        const d = new Date(data.last_updated);
        lastUpdatedEl.textContent = `Last updated: ${d.toLocaleDateString("en-IN", {
          day: "numeric",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })} IST`;
      }
    } catch (err) {
      lastUpdatedEl.textContent = "Could not load IPO data. Ensure the scraper has run.";
    }
    render();
  }

  load();
})();
