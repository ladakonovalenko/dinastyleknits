// Відео на сторінці Blog. Мініатюри вантажаться напряму з YouTube CDN
// (img.youtube.com) — це загальнодоступні картинки, призначені саме для
// вбудовування на сторонніх сайтах, тож жодних додаткових дозволів не треба.
//
// Список — усі 21 відео, надані замовницею, у тому самому порядку, в якому
// вона їх надіслала. Назви звірено з реальним списком відео на її каналі.

const VIDEOS = [
  { id: "I5HASduxtvA", title: "Cozy Crochet Bouqle Gloves You'll Wear Every Day I New Collection Overview" },
  { id: "k3dFqdKFIcU", title: "New Crochet Wool Beanie Collection for Women | Cozy & Stylish Winter Hats 2025-26" },
  { id: "751-CwDZ-NI", title: "Crochet Cape with Ruffle -SEND MESH CAPE -Overview of the new design" },
  { id: "iOALy5falic", title: "Top 3 crochet & knitting patterns by DinaStyleKnits / Short Podcast /Eng" },
  { id: "5IZ4wErzR2s", title: "How to Crochet a small black Crossbody Bag/ Short Step-by-step Tutorial" },
  { id: "CvZwSPcjGOg", title: "How to Knit an Asymmetrical Shawl with a Ruffled Border | Step-by-Step Tutorial" },
  { id: "f0NMGVPePYo", title: "Hand Knitted Triangle Shawl Knitted from One Side/Easy Garter Stitch Shawl/Details" },
  { id: "emY_adSdZig", title: "How To Crochet Fishnet Mesh Fingerless Gloves /Arm Warmers/Step-By-Step Tutorial" },
  { id: "wRTXbMJ--kg", title: "How to knit triangle shawl with long ends / Knitting for beginners /Step-by-step tutorial" },
  { id: "GIVm-bIhZM0", title: "How to knit M1B (Make 1 Below) Continental Knitting 2 methods / Invisible increase" },
  { id: "E-PdKBv4OFU", title: "How to Crochet Cape Capelet Shawl Easy Tutorial for Beginners" },
  { id: "kXIqObwgmJQ", title: "How to Knit a Super Easy Asymmetrical Shawl/Starting with 3 Stitches Tutorial" },
  { id: "Sj1tWsmKp84", title: "How to Knit Super Easy Chunky Scarf-DIY Step-by-Step Tutorial for Beginners" },
  { id: "oIS3A9RoohY", title: "How To Knit Easy Yoke Poncho Capelet/ Knitting Tutorial for Beginners" },
  { id: "Yz0iE7ep7Y0", title: "How To Knit With Flexi Flip /Step-By Step & Useful Tips / Crazy Trio Socks Needles" },
  { id: "ylvUreCc-Ew", title: "How to knit easy fingerless gloves / arm warmers / all secrets for beginners" },
  { id: "BCgNP7a8vTA", title: "Easy Knitted Shawl For Beginners I How To Knit Your First Shawl I Step-By-Step Tutorial" },
  { id: "j1rrE5jMeCs", title: "Crochet Flower Choker Necklace Easy Tutorial DIY" },
  { id: "5NWy-LhKCss", title: "How to Crochet Evil Eye Tote Bag: A Step-by-Step Tutorial" },
  { id: "ashTyIupx_4", title: "How to knit a crescent shawl for beginners - Tutorial Preview" },
  { id: "5qi3uugjyM0", title: "Black Granny Square Crochet Tote Bag: Easy Tutorial" },
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
