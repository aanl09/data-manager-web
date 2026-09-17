const API = ""; // same origin

// Tab switching
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("panel-" + btn.dataset.tab).classList.add("active");
  });
});

// Field pencarian per sheet
const SEARCH_FIELDS = {
  user: ["ID", "SID"],
  jb: ["IDJB"],
  terminasi: ["TERMINASI"],
  sarpen: ["SITE"],
};

async function doSearch(sheet) {
  const container = document.getElementById("result-" + sheet);
  container.innerHTML = "Memuat…";

  const params = new URLSearchParams();
  for (const field of SEARCH_FIELDS[sheet]) {
    const el = document.getElementById(`${sheet}-${field}`);
    if (el && el.value.trim()) params.append(field, el.value.trim());
  }

  try {
    const res = await fetch(`${API}/api/${sheet}?${params.toString()}`);
    const data = await res.json();
    if (!res.ok) {
      container.innerHTML = `<p class="error">Error: ${data.error || res.status}</p>`;
      return;
    }
    renderTable(container, data);
  } catch (e) {
    container.innerHTML = `<p class="error">Gagal terhubung ke server: ${e.message}</p>`;
  }
}

function renderTable(container, data) {
  const rows = data.rows || [];
  if (rows.length === 0) {
    container.innerHTML = `<p class="empty">Tidak ada data ditemukan.</p>`;
    return;
  }
  const highlight = new Set(data.highlight || []);
  const headers = Object.keys(rows[0]);

  let html = `<p class="count">Ditemukan <strong>${data.count}</strong> baris.</p>`;
  html += "<table><thead><tr>";
  for (const h of headers) {
    html += `<th class="${highlight.has(h) ? "highlight" : ""}">${escapeHtml(h)}</th>`;
  }
  html += "</tr></thead><tbody>";
  for (const row of rows) {
    html += "<tr>";
    for (const h of headers) {
      html += `<td class="${highlight.has(h) ? "highlight" : ""}">${escapeHtml(row[h] ?? "")}</td>`;
    }
    html += "</tr>";
  }
  html += "</tbody></table>";
  container.innerHTML = html;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Tampilkan backend aktif
fetch(`${API}/api/health`)
  .then((r) => r.json())
  .then((d) => {
    document.getElementById("backend-badge").textContent = "backend: " + d.backend;
  })
  .catch(() => {
    document.getElementById("backend-badge").textContent = "offline";
  });
