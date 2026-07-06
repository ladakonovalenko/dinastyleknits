// Відео на сторінці Blog. Мініатюри вантажаться напряму з YouTube CDN
// (img.youtube.com) — це загальнодоступні картинки, призначені саме для
// вбудовування на сторонніх сайтах, тож жодних додаткових дозволів не треба.
//
// Список — усі 21 відео, надані замовницею, у ЗВОРОТНОМУ порядку до того,
// в якому вона їх надіслала (за її проханням).
//
// ⚠️ Для 2 відео назви підтверджені (знайдені раніше через пошук). Для
// решти 19 YouTube тимчасово заблокував автоматичне отримання назв
// (rate limit на момент розробки) — там стоїть чесна загальна позначка
// "DinaStyleKnits Tutorial" замість вигаданої назви. Сама мініатюра й
// посилання при цьому повністю реальні та робочі. Коли потрібно —
// перезапустіть спробу отримати назви пізніше, або попросіть замовницю
// продиктувати назви цих 19 відео, і просто впишіть їх сюди вручну.

const VIDEOS = [
  { id: "5qi3uugjyM0", title: "DinaStyleKnits Tutorial" },
  { id: "ashTyIupx_4", title: "DinaStyleKnits Tutorial" },
  { id: "5NWy-LhKCss", title: "DinaStyleKnits Tutorial" },
  { id: "j1rrE5jMeCs", title: "DinaStyleKnits Tutorial" },
  { id: "BCgNP7a8vTA", title: "DinaStyleKnits Tutorial" },
  { id: "ylvUreCc-Ew", title: "DinaStyleKnits Tutorial" },
  { id: "Yz0iE7ep7Y0", title: "DinaStyleKnits Tutorial" },
  { id: "oIS3A9RoohY", title: "DinaStyleKnits Tutorial" },
  { id: "Sj1tWsmKp84", title: "DinaStyleKnits Tutorial" },
  { id: "kXIqObwgmJQ", title: "How to Knit a Super Easy Asymmetrical Shawl — Starting with 3 Stitches" },
  { id: "E-PdKBv4OFU", title: "DinaStyleKnits Tutorial" },
  { id: "GIVm-bIhZM0", title: "DinaStyleKnits Tutorial" },
  { id: "wRTXbMJ--kg", title: "How to Knit a Triangle Shawl with Long Ends — Step-by-Step Tutorial" },
  { id: "emY_adSdZig", title: "DinaStyleKnits Tutorial" },
  { id: "f0NMGVPePYo", title: "DinaStyleKnits Tutorial" },
  { id: "CvZwSPcjGOg", title: "DinaStyleKnits Tutorial" },
  { id: "5IZ4wErzR2s", title: "DinaStyleKnits Tutorial" },
  { id: "iOALy5falic", title: "DinaStyleKnits Tutorial" },
  { id: "751-CwDZ-NI", title: "DinaStyleKnits Tutorial" },
  { id: "k3dFqdKFIcU", title: "DinaStyleKnits Tutorial" },
  { id: "I5HASduxtvA", title: "DinaStyleKnits Tutorial" },
];

function renderVideoCard(video) {
  const thumbnailUrl = `https://i.ytimg.com/vi/${video.id}/hqdefault.jpg`;
  const videoUrl = `https://www.youtube.com/watch?v=${video.id}`;

  return `
    <a class="video-card" href="${videoUrl}" target="_blank" rel="noopener">
      <div class="video-card__thumb">
        <img src="${thumbnailUrl}" alt="${escapeHtmlBlog(video.title)}" loading="lazy" />
        <span class="video-card__play">&#9654;</span>
      </div>
      <p class="video-card__title">${escapeHtmlBlog(video.title)}</p>
    </a>
  `;
}

function escapeHtmlBlog(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("video-grid");
  if (!grid) return;
  grid.innerHTML = VIDEOS.map(renderVideoCard).join("");
});
