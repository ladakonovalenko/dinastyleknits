// Власний, мінімальний лічильник переглядів сторінок — без сторонніх
// сервісів (заміна Vercel Analytics). Надсилає лише шлях сторінки,
// нічого більше: жодних cookies, жодних ідентифікаторів відвідувача.
// Якщо запит не вдався (наприклад, бекенд тимчасово недоступний) —
// тихо ігноруємо, це ніколи не повинно заважати відвідувачу.
(function () {
  if (typeof API_BASE_URL === "undefined") return;
  fetch(`${API_BASE_URL}/api/analytics/track`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path: window.location.pathname }),
    keepalive: true,
  }).catch(() => {});
})();
