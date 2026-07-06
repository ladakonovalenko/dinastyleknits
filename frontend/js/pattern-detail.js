// Сторінка /pattern-detail.html?slug=... — повна сторінка товару.
// "Опис" (за словами замовниці) — це весь товар цілком: фото, назва,
// ціна, опис і кнопка переходу на Etsy для покупки.

document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("pattern-detail");
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const slug = params.get("slug");

  if (!slug) {
    renderNotFound(container);
    return;
  }

  try {
    const pattern = await Api.getPattern(slug);
    if (!pattern) {
      renderNotFound(container);
      return;
    }
    renderDetail(container, pattern);
    document.title = `${pattern.title} — DinaStyleKnits`;
  } catch (err) {
    console.error("Failed to load pattern:", err);
    container.innerHTML = `<p class="grid-empty">Couldn't load this pattern. Please try refreshing the page.</p>`;
  }
});

function renderDetail(container, pattern) {
  const imageSrc = Api.imageUrl(pattern.image_filename);
  const description = pattern.description
    ? escapeHtml(pattern.description)
    : "The description for this pattern is coming soon.";

  container.innerHTML = `
    <p class="breadcrumb"><a href="patterns.html">← All patterns</a></p>
    <div class="pattern-detail">
      <div class="pattern-detail__image">
        ${imageSrc ? `<img src="${imageSrc}" alt="${escapeHtml(pattern.title)}" />` : ""}
      </div>
      <div>
        ${pattern.is_new ? `<span class="badge-new">New</span>` : ""}
        <h1>${escapeHtml(pattern.title)}</h1>
        <p class="pattern-detail__price">${escapeHtml(pattern.price)}</p>
        <p class="pattern-detail__description">${description}</p>
        <a class="btn btn-accent" href="${pattern.etsy_url}" target="_blank" rel="noopener">
          Buy on Etsy
        </a>
      </div>
    </div>
  `;
}

function renderNotFound(container) {
  container.innerHTML = `
    <div class="stub-page">
      <h1>Pattern not found</h1>
      <p>This link may be outdated. Browse the full pattern collection instead.</p>
      <p style="margin-top: 24px;"><a class="btn btn-outline" href="patterns.html">All patterns</a></p>
    </div>
  `;
}
