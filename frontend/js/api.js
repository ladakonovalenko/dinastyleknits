// Тонка обгортка над fetch — тримає всі виклики до бекенду в одному місці,
// щоб зміна структури API не вимагала правок у кожному файлі сторінки.

const Api = {
  async getPatterns({ onlyNew = false } = {}) {
    const url = new URL(`${API_BASE_URL}/api/patterns`);
    if (onlyNew) url.searchParams.set("only_new", "true");
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to load pattern list");
    return res.json();
  },

  async getPattern(slug) {
    const res = await fetch(`${API_BASE_URL}/api/patterns/${encodeURIComponent(slug)}`);
    if (res.status === 404) return null;
    if (!res.ok) throw new Error("Failed to load pattern");
    return res.json();
  },

  async subscribe(email) {
    const res = await fetch(`${API_BASE_URL}/api/subscribers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Failed to subscribe");
    }
    return res.json();
  },

  imageUrl(filename) {
    if (!filename) return "";
    return `${API_BASE_URL}/static/images/${filename}`;
  },

  // image_url від бекенду вже враховує, звідки фото — зі старих статичних
  // файлів чи з БД (нові товари з адмінки). Тут просто додаємо базовий домен.
  fullImageUrl(imageUrl) {
    if (!imageUrl) return "";
    return `${API_BASE_URL}${imageUrl}`;
  },

  // ---------- Адмінка ----------

  async login(email, password) {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Login failed");
    }
    return res.json();
  },

  async me(token) {
    const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Invalid session");
    return res.json();
  },

  async createPattern(token, data) {
    const res = await fetch(`${API_BASE_URL}/api/patterns`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to create pattern");
    }
    return res.json();
  },

  async updatePattern(token, slug, data) {
    const res = await fetch(`${API_BASE_URL}/api/patterns/${encodeURIComponent(slug)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to update pattern");
    }
    return res.json();
  },

  async deletePattern(token, slug) {
    const res = await fetch(`${API_BASE_URL}/api/patterns/${encodeURIComponent(slug)}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok && res.status !== 204) throw new Error("Failed to delete pattern");
  },

  async uploadPatternImage(token, slug, file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE_URL}/api/patterns/${encodeURIComponent(slug)}/image`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }, // Content-Type не задаємо — браузер сам виставить multipart boundary
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to upload image");
    }
    return res.json();
  },
};
