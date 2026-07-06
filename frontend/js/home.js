// Головна сторінка (об'єднана з колишньою /patterns.html за рішенням
// замовниці): показує повну сітку всіх патернів одразу під hero-блоком.

document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("all-patterns-grid");
  if (!container) return;

  try {
    const patterns = await Api.getPatterns();
    renderPatternGrid(container, patterns);
  } catch (err) {
    container.innerHTML = `<p class="grid-empty">Couldn't load patterns. Please try refreshing the page.</p>`;
  }
});
