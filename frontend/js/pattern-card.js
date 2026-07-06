// Спільна функція рендерингу картки патерну — використовується і на головній
// (тизер), і на /patterns.html (повна сітка), і на /new.html.

function renderPatternCard(pattern) {
  const imageSrc = Api.imageUrl(pattern.image_filename);
  const badge = pattern.is_new ? `<span class="badge-new">New</span>` : "";

  return `
    <a class="pattern-card" href="pattern-detail.html?slug=${encodeURIComponent(pattern.slug)}">
      <div class="pattern-card__image">
        ${imageSrc ? `<img src="${imageSrc}" alt="${escapeHtml(pattern.title)}" loading="lazy" />` : ""}
      </div>
      ${badge}
      <p class="pattern-card__title">${escapeHtml(pattern.title)}</p>
      <p class="pattern-card__price">${escapeHtml(pattern.price)}</p>
    </a>
  `;
}

function renderPatternGrid(container, patterns) {
  if (!patterns.length) {
    container.innerHTML = `<p class="grid-empty">Nothing here yet — patterns are coming very soon.</p>`;
    return;
  }
  container.innerHTML = patterns.map(renderPatternCard).join("");
}

// Проста екранізація, щоб назви товарів безпечно вставлялись в innerHTML
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
