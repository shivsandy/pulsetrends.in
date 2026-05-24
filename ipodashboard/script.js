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

  function ipoTypeClass(type) {
    const t = (type || "").toLowerCase();
    if (t === "mainboard") return "ipo-type-mainboard";
    if (t === "sme") return "ipo-type-sme";
    if (t === "fpo") return "ipo-type-fpo";
    return "ipo-type-mainboard";
  }

  function gmpClass(val) {
    if (!val || val === "\u2014") return "gmp-none";
    const cleaned = val.replace(/[^0-9.\-]/g, "");
    if (!cleaned) return "gmp-none";
    const num = parseFloat(cleaned);
    if (isNaN(num)) return "gmp-none";
    return num >= 0 ? "gmp-positive" : "gmp-negative";
  }

  function parseSubscription(subStr) {
    if (!subStr) return -Infinity;
    const match = subStr.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : -Infinity;
  }

  function render() {
    let filtered = ipos;

    if (currentFilter !== "all") {
      filtered = filtered.filter((ipo) => (ipo.status || "upcoming").toLowerCase() === currentFilter);
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter((ipo) => (ipo.company_name || "").toLowerCase().includes(term));
    }

    if (sortKey) {
      filtered.sort((a, b) => {
        let va = (a[sortKey] || "").toString().toLowerCase();
        let vb = (b[sortKey] || "").toString().toLowerCase();

        if (sortKey === "lot_size") {
          va = parseFloat(va) || 0;
          vb = parseFloat(vb) || 0;
        } else if (sortKey === "gmp") {
          va = parseFloat(va.replace(/[^0-9.\-]/g, "")) || 0;
          vb = parseFloat(vb.replace(/[^0-9.\-]/g, "")) || 0;
        } else if (sortKey === "subscription") {
          va = parseSubscription(a.subscription);
          vb = parseSubscription(b.subscription);
        } else if (sortKey === "open_date" || sortKey === "close_date" || sortKey === "listing_date") {
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
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:40px;color:var(--text-muted);">No IPOs found</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered
      .map((ipo) => {
        const s = (ipo.status || "upcoming").toLowerCase();
        return `<tr>
          <td>
            <span class="company-name">${escHtml(ipo.company_name || "\u2014")}</span>
            <span class="ipo-type-badge ${ipoTypeClass(ipo.ipo_type)}">${escHtml(ipo.ipo_type || "mainboard")}</span>
          </td>
          <td>${escHtml(ipo.price_band || "\u2014")}</td>
          <td>${formatDate(ipo.open_date)}</td>
          <td>${formatDate(ipo.close_date)}</td>
          <td>${formatDate(ipo.listing_date)}</td>
          <td>${escHtml(ipo.lot_size || "\u2014")}</td>
          <td>${escHtml(ipo.issue_size || "\u2014")}</td>
          <td class="${gmpClass(ipo.gmp)}">${escHtml(ipo.gmp || "\u2014")}</td>
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
