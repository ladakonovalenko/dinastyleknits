// Сторінка /new.html — усі патерни, позначені is_new=true в адмінці.

document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("new-grid");
  if (!container) return;

  try {
    const patterns = await Api.getPatterns({ onlyNew: true });
    renderPatternGrid(container, patterns);
  } catch (err) {
    container.innerHTML = `<p class="grid-empty">Не вдалось завантажити патерни. Спробуйте оновити сторінку.</p>`;
  }
});
