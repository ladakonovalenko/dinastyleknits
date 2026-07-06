// Адмінка DinaStyleKnits. Сторінка навмисно не в публічній навігації —
// посилання (yoursite.com/admin.html) дається лише замовниці.
//
// Токен зберігається в localStorage і живе 7 днів (обмеження на бекенді).
// Після цього просто попросить увійти знову.

const TOKEN_KEY = "dinastyleknits_admin_token";

let state = {
  token: localStorage.getItem(TOKEN_KEY) || null,
  patterns: [],
  editingSlug: null, // null = форма "додати новий", інакше — slug патерну, який редагується
  formError: "",
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
    await loadPatterns();
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
      await loadPatterns();
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
  const editing = state.editingSlug !== null;
  const editingPattern = editing ? state.patterns.find((p) => p.slug === state.editingSlug) : null;

  root.innerHTML = `
    <div class="admin-topbar">
      <h1>DinaStyleKnits Admin</h1>
      <button class="btn btn-outline" id="logout-btn">Log out</button>
    </div>
    <div class="admin-container">
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
    </div>
  `;

  document.getElementById("logout-btn").addEventListener("click", handleLogout);
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
