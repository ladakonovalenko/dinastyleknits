// Спільна шапка й футер інжектяться на кожній сторінці в <div id="site-header">
// та <div id="site-footer">. Так розмітка й лінки соцмереж редагуються в одному
// місці, а не в 5+ окремих HTML-файлах.
//
// Активна сторінка визначається через <body data-page="...">, значення якого
// має збігатись з data-page на відповідному <a> в навігації.

const SOCIAL_LINKS = [
  { label: "Facebook", short: "F", url: "https://www.facebook.com/pages/Dinastyleknits/1541734096057441" },
  { label: "Instagram", short: "I", url: "http://instagram.com/dina.style" },
  { label: "Pinterest", short: "P", url: "https://www.pinterest.com/dinastyleknits/" },
  { label: "Etsy shop", short: "E", url: "https://www.etsy.com/shop/DinaStyleKnits" },
];

const NAV_LINKS = [
  { label: "Home", href: "index.html", page: "home" },
  { label: "Patterns", href: "patterns.html", page: "patterns" },
  { label: "New", href: "new.html", page: "new" },
  { label: "Blog", href: "blog.html", page: "blog" },
  { label: "About", href: "about.html", page: "about" },
];

function renderHeader() {
  const mount = document.getElementById("site-header");
  if (!mount) return;

  const currentPage = document.body.dataset.page;

  const navHtml = NAV_LINKS.map(
    (link) =>
      `<li><a href="${link.href}" data-page="${link.page}" class="${link.page === currentPage ? "is-active" : ""}">${link.label}</a></li>`
  ).join("");

  mount.innerHTML = `
    <div class="site-header__inner">
      <a href="index.html" class="brand">
        <img src="static/images/emblem.png" alt="" />
        DinaStyleKnits
      </a>
      <ul class="nav-links" id="nav-links">${navHtml}</ul>
      <button class="nav-toggle" id="nav-toggle" aria-label="Open menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  `;

  const toggle = document.getElementById("nav-toggle");
  const links = document.getElementById("nav-links");
  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}

function renderFooter() {
  const mount = document.getElementById("site-footer");
  if (!mount) return;

  const socialHtml = SOCIAL_LINKS.map(
    (link) =>
      `<li><a href="${link.url}" target="_blank" rel="noopener" aria-label="${link.label}">${link.short}</a></li>`
  ).join("");

  mount.innerHTML = `
    <div class="container site-footer__inner">
      <p class="footer-copy">© ${new Date().getFullYear()} DinaStyleKnits · Since 2014</p>
      <ul class="social-links">${socialHtml}</ul>
    </div>
  `;
}

document.addEventListener("DOMContentLoaded", () => {
  renderHeader();
  renderFooter();
});
