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
    container.innerHTML = `<p class="grid-empty">Не вдалось завантажити патерн. Спробуйте оновити сторінку.</p>`;
  }
});

function renderDetail(container, pattern) {
  const imageSrc = Api.imageUrl(pattern.image_filename);
  const description = pattern.description
    ? escapeHtml(pattern.description)
    : "Опис цього патерну зʼявиться тут найближчим часом.";

  container.innerHTML = `
    <p class="breadcrumb"><a href="patterns.html">← Усі патерни</a></p>
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
          Купити на Etsy
        </a>
      </div>
    </div>
  `;
}

function renderNotFound(container) {
  container.innerHTML = `
    <div class="stub-page">
      <h1>Патерн не знайдено</h1>
      <p>Можливо, посилання застаріле. Перегляньте весь каталог патернів.</p>
      <p style="margin-top: 24px;"><a class="btn btn-outline" href="patterns.html">Усі патерни</a></p>
    </div>
  `;
}
