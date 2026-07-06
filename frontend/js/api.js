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
};
