// Головна сторінка (об'єднана з колишньою /patterns.html за рішенням
// замовниці): показує повну сітку всіх патернів одразу під hero-блоком.

document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("all-patterns-grid");
  if (!container) return;

  try {
    const patterns = await Api.getPatterns();
    renderPatternGrid(container, patterns);
    injectProductSchema(patterns);
  } catch (err) {
    container.innerHTML = `<p class="grid-empty">Couldn't load patterns. Please try refreshing the page.</p>`;
  }
});

// Базова Schema.org розмітка (JSON-LD) — допомагає пошуковикам (Google тощо)
// розуміти, що на сторінці перелічені конкретні товари з цінами, а не просто
// текст. Ціна береться як число з рядка "USD 6.78" — якщо формат ціни колись
// зміниться на щось геть інше, цю функцію треба буде підправити.
function injectProductSchema(patterns) {
  const items = patterns.map((pattern, index) => {
    const priceMatch = pattern.price.match(/[\d.]+/);
    return {
      "@type": "ListItem",
      position: index + 1,
      item: {
        "@type": "Product",
        name: pattern.title,
        image: Api.fullImageUrl(pattern.image_url) || undefined,
        url: pattern.etsy_url,
        offers: {
          "@type": "Offer",
          price: priceMatch ? priceMatch[0] : undefined,
          priceCurrency: "USD",
          url: pattern.etsy_url,
          availability: "https://schema.org/InStock",
        },
      },
    };
  });

  const schema = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: items,
  };

  const script = document.createElement("script");
  script.type = "application/ld+json";
  script.textContent = JSON.stringify(schema);
  document.head.appendChild(script);
}
