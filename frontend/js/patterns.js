// Сторінка /patterns.html — повна сітка з усіх 13 (і майбутніх) патернів.

document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("patterns-grid");
  if (!container) return;

  try {
    const patterns = await Api.getPatterns();
    renderPatternGrid(container, patterns);
  } catch (err) {
    container.innerHTML = `<p class="grid-empty">Не вдалось завантажити патерни. Спробуйте оновити сторінку.</p>`;
  }
});
