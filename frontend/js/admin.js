// Адмінка DinaStyleKnits. Сторінка навмисно не в публічній навігації —
// посилання (yoursite.com/admin.html) дається лише замовниці.
//
// Токен зберігається в localStorage і живе 7 днів (обмеження на бекенді).
// Після цього просто попросить увійти знову.

const TOKEN_KEY = "dinastyleknits_admin_token";

let state = {
  token: localStorage.getItem(TOKEN_KEY) || null,
  patterns: [],
  subscribers: [],
  activeTab: "patterns", // "patterns" | "subscribers" | "newsletter" | "analytics"
  editingSlug: null, // null = форма "додати новий", інакше — slug патерну, який редагується
  formError: "",
  newsletterStatus: "", // повідомлення після спроби відправки (успіх/помилка)
  syncStatus: "", // повідомлення після спроби синхронізації підписників
  analyticsPeriod: "week", // "day" | "week" | "month" | "year"
  patternStatsPeriod: "week", // "day" | "week" | "month" | "year"
};

const root = document.getElementById("admin-root");

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ---------- Ініціалізація ----------

async function init() {
  if (!state.token) {
    renderLogin();
    return;
  }
  try {
    await Api.me(state.token);
    await Promise.all([loadPatterns(), loadSubscribers()]);
    renderDashboard();
  } catch (err) {
    // Токен недійсний/прострочений — просимо увійти знову
    localStorage.removeItem(TOKEN_KEY);
    state.token = null;
    renderLogin("Your session has expired. Please sign in again.");
  }
}

async function loadPatterns() {
  state.patterns = await Api.getPatterns();
}

async function loadSubscribers() {
  state.subscribers = await Api.getSubscribers(state.token);
}

// ---------- Логін ----------

function renderLogin(message = "") {
  root.innerHTML = `
    <div class="container admin-login">
      <h1>DinaStyleKnits Admin</h1>
      <form class="admin-form" id="login-form">
        <div class="admin-field">
          <label for="login-email">Email</label>
          <input type="email" id="login-email" required />
        </div>
        <div class="admin-field">
          <label for="login-password">Password</label>
          <input type="password" id="login-password" required />
        </div>
        <p class="admin-message ${message ? "is-error" : ""}">${escapeHtml(message)}</p>
        <button type="submit" class="btn btn-primary">Sign in</button>
      </form>
    </div>
  `;

  document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    try {
      const { access_token } = await Api.login(email, password);
      localStorage.setItem(TOKEN_KEY, access_token);
      state.token = access_token;
      await Promise.all([loadPatterns(), loadSubscribers()]);
      renderDashboard();
    } catch (err) {
      renderLogin(err.message || "Wrong email or password.");
    }
  });
}

function handleLogout() {
  localStorage.removeItem(TOKEN_KEY);
  state.token = null;
  state.patterns = [];
  state.editingSlug = null;
  renderLogin();
}

// ---------- Дашборд ----------

function renderDashboard() {
  root.innerHTML = `
    <div class="admin-topbar">
      <h1>DinaStyleKnits Admin</h1>
      <button class="btn btn-outline" id="logout-btn">Log out</button>
    </div>
    <div class="admin-container">
      <div class="admin-tabs">
        <button class="admin-tab ${state.activeTab === "patterns" ? "is-active" : ""}" id="tab-patterns" type="button">Patterns</button>
        <button class="admin-tab ${state.activeTab === "subscribers" ? "is-active" : ""}" id="tab-subscribers" type="button">Subscribers (${state.subscribers.length})</button>
        <button class="admin-tab ${state.activeTab === "newsletter" ? "is-active" : ""}" id="tab-newsletter" type="button">Newsletter</button>
        <button class="admin-tab ${state.activeTab === "analytics" ? "is-active" : ""}" id="tab-analytics" type="button">Analytics</button>
        <button class="admin-tab ${state.activeTab === "pattern-stats" ? "is-active" : ""}" id="tab-pattern-stats" type="button">Pattern Stats</button>
      </div>
      <div id="tab-content"></div>
    </div>
  `;

  document.getElementById("logout-btn").addEventListener("click", handleLogout);
  document.getElementById("tab-patterns").addEventListener("click", () => {
    state.activeTab = "patterns";
    renderDashboard();
  });
  document.getElementById("tab-subscribers").addEventListener("click", () => {
    state.activeTab = "subscribers";
    renderDashboard();
  });
  document.getElementById("tab-newsletter").addEventListener("click", () => {
    state.activeTab = "newsletter";
    renderDashboard();
  });
  document.getElementById("tab-analytics").addEventListener("click", () => {
    state.activeTab = "analytics";
    renderDashboard();
  });
  document.getElementById("tab-pattern-stats").addEventListener("click", () => {
    state.activeTab = "pattern-stats";
    renderDashboard();
  });

  if (state.activeTab === "subscribers") {
    renderSubscribersTab();
  } else if (state.activeTab === "newsletter") {
    renderNewsletterTab();
  } else if (state.activeTab === "analytics") {
    renderAnalyticsTab();
  } else if (state.activeTab === "pattern-stats") {
    renderPatternStatsTab();
  } else {
    renderPatternsTab();
  }
}

function renderPatternsTab() {
  const editing = state.editingSlug !== null;
  const editingPattern = editing ? state.patterns.find((p) => p.slug === state.editingSlug) : null;
  const mount = document.getElementById("tab-content");

  mount.innerHTML = `
      <h2 class="admin-section-title">${editing ? "Edit pattern" : "Add new pattern"}</h2>
      <form class="admin-form" id="pattern-form">
        <div class="admin-field">
          <label for="field-title">Title</label>
          <input type="text" id="field-title" required value="${escapeHtml(editingPattern?.title || "")}" />
        </div>
        <div class="admin-field">
          <label for="field-price">Price (as shown on the site, e.g. "USD 6.78")</label>
          <input type="text" id="field-price" required value="${escapeHtml(editingPattern?.price || "")}" />
        </div>
        <div class="admin-field">
          <label for="field-etsy-url">Etsy listing URL</label>
          <input type="url" id="field-etsy-url" required value="${escapeHtml(editingPattern?.etsy_url || "")}" />
        </div>
        <div class="admin-field">
          <label for="field-description">Description (optional)</label>
          <textarea id="field-description">${escapeHtml(editingPattern?.description || "")}</textarea>
        </div>
        <div class="admin-field">
          <label for="field-image">Photo ${editing ? "(leave empty to keep the current one)" : ""}</label>
          <input type="file" id="field-image" accept="image/jpeg,image/png,image/webp" />
        </div>
        <label class="admin-checkbox">
          <input type="checkbox" id="field-is-new" ${editingPattern?.is_new ? "checked" : ""} />
          Show "New" badge
        </label>
        <p class="admin-message ${state.formError ? "is-error" : ""}">${escapeHtml(state.formError)}</p>
        <div class="admin-form-actions">
          <button type="submit" class="btn btn-primary">${editing ? "Save changes" : "Add pattern"}</button>
          ${editing ? `<button type="button" class="btn btn-outline" id="cancel-edit-btn">Cancel</button>` : ""}
        </div>
      </form>

      <h2 class="admin-section-title">All patterns (${state.patterns.length})</h2>
      <div class="admin-list" id="patterns-list">
        ${state.patterns.map(renderListItem).join("") || "<p>No patterns yet.</p>"}
      </div>
  `;

  document.getElementById("pattern-form").addEventListener("submit", handleFormSubmit);
  if (editing) {
    document.getElementById("cancel-edit-btn").addEventListener("click", () => {
      state.editingSlug = null;
      state.formError = "";
      renderDashboard();
    });
  }

  state.patterns.forEach((pattern) => {
    const editBtn = document.getElementById(`edit-${pattern.id}`);
    const deleteBtn = document.getElementById(`delete-${pattern.id}`);
    editBtn?.addEventListener("click", () => {
      state.editingSlug = pattern.slug;
      state.formError = "";
      renderDashboard();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    deleteBtn?.addEventListener("click", () => handleDelete(pattern));
  });
}

function renderSubscribersTab() {
  const mount = document.getElementById("tab-content");

  mount.innerHTML = `
      <div class="admin-subscribers-header">
        <h2 class="admin-section-title" style="margin-top: 0;">Subscribers (${state.subscribers.length})</h2>
        <button class="btn btn-outline" id="export-csv-btn" type="button" ${state.subscribers.length ? "" : "disabled"}>Export CSV</button>
      </div>
      <div class="admin-list">
        ${
          state.subscribers.length
            ? state.subscribers.map(renderSubscriberItem).join("")
            : "<p>No subscribers yet — they'll show up here as soon as someone joins on the homepage.</p>"
        }
      </div>
  `;

  document.getElementById("export-csv-btn")?.addEventListener("click", exportSubscribersCsv);
}

function renderSubscriberItem(subscriber) {
  const date = new Date(subscriber.created_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
  return `
    <div class="admin-list-item">
      <div class="admin-list-item__info">
        <p class="admin-list-item__title">${escapeHtml(subscriber.email)}</p>
        <p class="admin-list-item__price">Joined ${date}</p>
      </div>
    </div>
  `;
}

function exportSubscribersCsv() {
  const rows = [["email", "joined_at"], ...state.subscribers.map((s) => [s.email, s.created_at])];
  const csv = rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "dinastyleknits-subscribers.csv";
  link.click();
  URL.revokeObjectURL(url);
}

function renderListItem(pattern) {
  const imageSrc = Api.fullImageUrl(pattern.image_url);
  return `
    <div class="admin-list-item">
      <div class="admin-list-item__thumb">
        ${imageSrc ? `<img src="${imageSrc}" alt="" />` : ""}
      </div>
      <div class="admin-list-item__info">
        <p class="admin-list-item__title">${escapeHtml(pattern.title)}${pattern.is_new ? " · <span style=\"color:var(--color-accent)\">NEW</span>" : ""}</p>
        <p class="admin-list-item__price">${escapeHtml(pattern.price)}</p>
      </div>
      <div class="admin-list-item__actions">
        <button class="btn btn-outline" id="edit-${pattern.id}" type="button">Edit</button>
        <button class="btn-danger" id="delete-${pattern.id}" type="button">Delete</button>
      </div>
    </div>
  `;
}

// ---------- Analytics ----------

const ANALYTICS_PERIOD_LABELS = { day: "Day", week: "Week", month: "Month", year: "Year" };

async function renderAnalyticsTab() {
  const mount = document.getElementById("tab-content");
  const period = state.analyticsPeriod || "week";

  mount.innerHTML = `
      <h2 class="admin-section-title" style="margin-top: 0;">Site visitors</h2>
      <div class="admin-tabs" style="margin-bottom: var(--space-3);">
        ${Object.entries(ANALYTICS_PERIOD_LABELS)
          .map(
            ([key, label]) =>
              `<button class="admin-tab ${period === key ? "is-active" : ""}" data-period="${key}" type="button">${label}</button>`
          )
          .join("")}
      </div>
      <div id="analytics-content"><p>Loading…</p></div>
  `;

  mount.querySelectorAll("[data-period]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.analyticsPeriod = btn.dataset.period;
      renderAnalyticsTab();
    });
  });

  const content = document.getElementById("analytics-content");
  try {
    const data = await Api.getAnalyticsSummary(state.token, period);
    content.innerHTML = `
      <div style="display: flex; gap: var(--space-4); margin-bottom: var(--space-3);">
        <div>
          <p style="font-size: 2rem; font-weight: 700; margin: 0;">${data.total_pageviews}</p>
          <p style="color: var(--color-gray-500); margin: 0;">Page views</p>
        </div>
        <div>
          <p style="font-size: 2rem; font-weight: 700; margin: 0;">${data.total_visitors}</p>
          <p style="color: var(--color-gray-500); margin: 0;">Visitors</p>
        </div>
      </div>
      ${renderAnalyticsChart(data.daily)}
    `;
  } catch (err) {
    content.innerHTML = `<p class="admin-message is-error">Error: ${escapeHtml(err.message || "Something went wrong.")}</p>`;
  }
}

function renderAnalyticsChart(daily) {
  if (!daily || daily.length === 0) {
    return `<p style="color: var(--color-gray-500);">No data for this period yet.</p>`;
  }

  const width = 700;
  const height = 200;
  const padding = 30;
  const maxValue = Math.max(1, ...daily.map((d) => d.pageviews));
  const barWidth = (width - padding * 2) / daily.length;

  const bars = daily
    .map((d, i) => {
      const barHeight = (d.pageviews / maxValue) * (height - padding * 2);
      const x = padding + i * barWidth;
      const y = height - padding - barHeight;
      return `<rect x="${x + 2}" y="${y}" width="${Math.max(1, barWidth - 4)}" height="${barHeight}" fill="#0297B1" rx="2">
        <title>${escapeHtml(d.date)}: ${d.pageviews} views, ${d.visitors} visitors</title>
      </rect>`;
    })
    .join("");

  const firstLabel = daily[0]?.date || "";
  const lastLabel = daily[daily.length - 1]?.date || "";

  return `
    <svg viewBox="0 0 ${width} ${height + 20}" style="width: 100%; height: auto;">
      <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="var(--color-gray-300)" />
      ${bars}
      <text x="${padding}" y="${height + 15}" font-size="11" fill="var(--color-gray-500)">${escapeHtml(firstLabel)}</text>
      <text x="${width - padding}" y="${height + 15}" font-size="11" fill="var(--color-gray-500)" text-anchor="end">${escapeHtml(lastLabel)}</text>
    </svg>
  `;
}

async function renderPatternStatsTab() {
  const mount = document.getElementById("tab-content");
  const period = state.patternStatsPeriod || "week";

  mount.innerHTML = `
      <h2 class="admin-section-title" style="margin-top: 0;">Product clicks</h2>
      <p style="color: var(--color-gray-500); margin-top: -8px;">How many times each product card was clicked (opened on Etsy).</p>
      <div class="admin-tabs" style="margin-bottom: var(--space-3);">
        ${Object.entries(ANALYTICS_PERIOD_LABELS)
          .map(
            ([key, label]) =>
              `<button class="admin-tab ${period === key ? "is-active" : ""}" data-pstat-period="${key}" type="button">${label}</button>`
          )
          .join("")}
      </div>
      <div id="pattern-stats-content"><p>Loading…</p></div>
  `;

  mount.querySelectorAll("[data-pstat-period]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.patternStatsPeriod = btn.dataset.pstatPeriod;
      renderPatternStatsTab();
    });
  });

  const content = document.getElementById("pattern-stats-content");
  try {
    const data = await Api.getPatternClickStats(state.token, period);
    content.innerHTML = renderPatternStatsList(data.patterns);
  } catch (err) {
    content.innerHTML = `<p class="admin-message is-error">Error: ${escapeHtml(err.message || "Something went wrong.")}</p>`;
  }
}

function renderPatternStatsList(patterns) {
  if (!patterns || patterns.length === 0) {
    return `<p style="color: var(--color-gray-500);">No clicks recorded for this period yet.</p>`;
  }

  const maxClicks = Math.max(1, ...patterns.map((p) => p.clicks));

  return `
    <div class="admin-list">
      ${patterns
        .map((p) => {
          const barPercent = Math.round((p.clicks / maxClicks) * 100);
          return `
            <div class="admin-list-item" style="flex-direction: column; align-items: stretch; gap: 6px;">
              <div style="display: flex; justify-content: space-between;">
                <p class="admin-list-item__title" style="margin: 0;">${escapeHtml(p.title)}</p>
                <p style="margin: 0; font-weight: 700;">${p.clicks}</p>
              </div>
              <div style="background: var(--color-gray-200, #eee); border-radius: 4px; height: 8px; overflow: hidden;">
                <div style="background: #0297B1; height: 100%; width: ${barPercent}%;"></div>
              </div>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderNewsletterTab() {
  const mount = document.getElementById("tab-content");

  mount.innerHTML = `
      <div class="admin-subscribers-header">
        <div>
          <h2 class="admin-section-title" style="margin-top: 0;">Sync subscribers to Resend</h2>
          <p style="color: var(--color-gray-500); margin-top: -8px;">
            Run this if someone subscribed but doesn't show up in Resend yet (e.g. after fixing Resend settings).
          </p>
        </div>
        <button class="btn btn-outline" id="sync-subscribers-btn" type="button">Sync now</button>
      </div>
      <p class="admin-message ${state.syncStatus && state.syncStatus.startsWith("Error") ? "is-error" : state.syncStatus ? "is-success" : ""}">${escapeHtml(state.syncStatus || "")}</p>

      <h2 class="admin-section-title">Send newsletter</h2>
      <p style="color: var(--color-gray-500); margin-top: -8px;">
        Goes out to all ${state.subscribers.length} subscriber${state.subscribers.length === 1 ? "" : "s"} who joined via the homepage form.
      </p>
      <form class="admin-form" id="newsletter-form">
        <div class="admin-field">
          <label for="newsletter-subject">Subject</label>
          <input type="text" id="newsletter-subject" required placeholder="New patterns are here!" />
        </div>
        <div class="admin-field">
          <label for="newsletter-body">Message</label>
          <textarea id="newsletter-body" required rows="8" placeholder="Write your update here. Leave a blank line between paragraphs."></textarea>
        </div>
        <p class="admin-message ${state.newsletterStatus.startsWith("Error") ? "is-error" : state.newsletterStatus ? "is-success" : ""}">${escapeHtml(state.newsletterStatus)}</p>
        <div class="admin-form-actions">
          <button type="submit" class="btn btn-primary" id="newsletter-send-btn">Send to all subscribers</button>
        </div>
      </form>
  `;

  document.getElementById("newsletter-form").addEventListener("submit", handleNewsletterSubmit);
  document.getElementById("sync-subscribers-btn").addEventListener("click", handleSyncSubscribers);
}

async function handleSyncSubscribers() {
  const btn = document.getElementById("sync-subscribers-btn");
  btn.disabled = true;
  btn.textContent = "Syncing…";
  state.syncStatus = "";
  try {
    const result = await Api.syncSubscribersToResend(state.token);
    state.syncStatus =
      `Added ${result.added} new subscriber(s) to Resend, ${result.skipped_existing} already there (untouched).` +
      (result.failed.length ? ` ${result.failed.length} failed.` : "");
  } catch (err) {
    state.syncStatus = `Error: ${err.message || "Something went wrong."}`;
  }
  renderNewsletterTab();
}

async function handleNewsletterSubmit(event) {
  event.preventDefault();
  state.newsletterStatus = "";

  const subject = document.getElementById("newsletter-subject").value.trim();
  const body = document.getElementById("newsletter-body").value.trim();

  const confirmed = window.confirm(
    `Send this email to all ${state.subscribers.length} subscriber(s) right now? This cannot be undone.`
  );
  if (!confirmed) return;

  const sendBtn = document.getElementById("newsletter-send-btn");
  sendBtn.disabled = true;
  sendBtn.textContent = "Sending…";

  try {
    await Api.sendNewsletter(state.token, { subject, body });
    state.newsletterStatus = "Sent! Your subscribers should start receiving it shortly.";
  } catch (err) {
    state.newsletterStatus = `Error: ${err.message || "Something went wrong."}`;
  }
  renderNewsletterTab();
}

// ---------- Форма: створення/редагування ----------

async function handleFormSubmit(event) {
  event.preventDefault();
  state.formError = "";

  const title = document.getElementById("field-title").value.trim();
  const price = document.getElementById("field-price").value.trim();
  const etsy_url = document.getElementById("field-etsy-url").value.trim();
  const description = document.getElementById("field-description").value.trim();
  const is_new = document.getElementById("field-is-new").checked;
  const imageFile = document.getElementById("field-image").files[0] || null;

  const submitBtn = event.target.querySelector('button[type="submit"]');
  submitBtn.disabled = true;

  try {
    let pattern;
    if (state.editingSlug) {
      pattern = await Api.updatePattern(state.token, state.editingSlug, {
        title,
        price,
        etsy_url,
        description,
        is_new,
      });
    } else {
      pattern = await Api.createPattern(state.token, {
        title,
        price,
        etsy_url,
        description,
        is_new,
      });
    }

    if (imageFile) {
      pattern = await Api.uploadPatternImage(state.token, pattern.slug, imageFile);
    }

    state.editingSlug = null;
    await loadPatterns();
    renderDashboard();
  } catch (err) {
    state.formError = err.message || "Something went wrong. Please try again.";
    renderDashboard();
  } finally {
    submitBtn.disabled = false;
  }
}

async function handleDelete(pattern) {
  const confirmed = window.confirm(`Delete "${pattern.title}"? This cannot be undone.`);
  if (!confirmed) return;

  try {
    await Api.deletePattern(state.token, pattern.slug);
    await loadPatterns();
    renderDashboard();
  } catch (err) {
    alert(err.message || "Failed to delete pattern.");
  }
}

document.addEventListener("DOMContentLoaded", init);
