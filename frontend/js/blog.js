// Відео на сторінці Blog. Мініатюри вантажаться напряму з YouTube CDN
// (img.youtube.com) — це загальнодоступні картинки, призначені саме для
// вбудовування на сторонніх сайтах, тож жодних додаткових дозволів не треба.
//
// Список відео зараз зібраний вручну (реальні відео з каналу замовниці).
// Коли з'являться нові відео чи потрібно оновити список — просто додайте
// новий об'єкт з id (це частина посилання після "watch?v=") та title.

const VIDEOS = [
  {
    id: "wRTXbMJ--kg",
    title: "How to Knit a Triangle Shawl with Long Ends — Step-by-Step Tutorial",
  },
  {
    id: "G1nwg2Xc7pE",
    title: "Alpaca Hand Knit Shawl — New Asymmetrical Shawl Wrap Design",
  },
  {
    id: "kXIqObwgmJQ",
    title: "How to Knit a Super Easy Asymmetrical Shawl — Starting with 3 Stitches",
  },
  {
    id: "nR_Pi0b6GOg",
    title: "Dancing Shadows Shawl Pattern",
  },
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
