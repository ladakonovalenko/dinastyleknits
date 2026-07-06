// Спільна функція рендерингу картки патерну — використовується і на головній
// (повна сітка "All patterns"), і на /new.html.
//
// За рішенням замовниці (як експеримент) — клік по картці веде одразу на
// відповідний товар на Etsy, в нову вкладку, без проміжної сторінки на
// нашому сайті. Раніше існувала окрема сторінка pattern-detail.html для
// цього — видалена як невикористана (є в git-історії, якщо колись знадобиться).

function renderPatternCard(pattern) {
  const imageSrc = Api.fullImageUrl(pattern.image_url);
  const badge = pattern.is_new ? `<span class="badge-new">New</span>` : "";

  return `
    <a class="pattern-card" href="${pattern.etsy_url}" target="_blank" rel="noopener">
      <div class="pattern-card__image">
        ${imageSrc ? `<img src="${imageSrc}" alt="${escapeHtml(pattern.title)}" loading="lazy" />` : ""}
      </div>
      <p class="pattern-card__title">${badge}${escapeHtml(pattern.title)}</p>
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
