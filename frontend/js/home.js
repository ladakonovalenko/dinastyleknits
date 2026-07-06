// Головна сторінка: показує невеликий тизер "New releases" (до 4 шт).
// Повний каталог — окрема сторінка patterns.html, щоб головна лишалась легкою.

document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("new-releases-grid");
  if (!container) return;

  try {
    const patterns = await Api.getPatterns({ onlyNew: true });
    renderPatternGrid(container, patterns.slice(0, 4));
  } catch (err) {
    container.innerHTML = `<p class="grid-empty">Не вдалось завантажити патерни. Спробуйте оновити сторінку.</p>`;
  }
});
