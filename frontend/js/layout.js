// Спільна шапка й футер інжектяться на кожній сторінці в <div id="site-header">
// та <div id="site-footer">. Так розмітка й лінки соцмереж редагуються в одному
// місці, а не в 5+ окремих HTML-файлах.
//
// Активна сторінка визначається через <body data-page="...">, значення якого
// має збігатись з data-page на відповідному <a> в навігації.

const SOCIAL_LINKS = [
  {
    label: "Facebook",
    url: "https://www.facebook.com/pages/Dinastyleknits/1541734096057441",
    icon: `<svg class="icon-facebook" viewBox="2 3 19 19" fill="currentColor"><path d="M13.5 21v-7.5h2.4l.4-3h-2.8V8.6c0-.9.2-1.5 1.5-1.5h1.4V4.2c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3v2.1H7v3h2.7V21h3.8z"/></svg>`,
  },
  {
    label: "Instagram",
    url: "http://instagram.com/dina.style",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="0.9" fill="currentColor" stroke="none"/></svg>`,
  },
  {
    label: "Pinterest",
    url: "https://www.pinterest.com/dinastyleknits/",
    icon: `<svg viewBox="3 2 18 21" fill="currentColor"><path d="M12 3C7.6 3 4.5 6 4.5 9.6c0 2.1 1.1 3.7 2.8 4.3.3.1.5 0 .6-.3l.2-.9c.1-.2 0-.4-.1-.6-.4-.5-.7-1.2-.7-2.1 0-2.8 2.1-5.3 5.5-5.3 3 0 4.6 1.8 4.6 4.3 0 3.2-1.4 5.9-3.5 5.9-1.1 0-2-.9-1.7-2.1.3-1.4 1-2.9 1-3.9 0-.9-.5-1.7-1.5-1.7-1.2 0-2.2 1.3-2.2 3 0 1.1.4 1.8.4 1.8s-1.2 5.2-1.5 6.1c-.4 1.5-.2 3.6-.1 3.8 0 .1.2.1.2 0 .1-.1 1.4-1.8 1.9-3.5.1-.5.7-2.9.7-2.9.4.7 1.4 1.3 2.6 1.3 3.4 0 5.9-3.1 5.9-7.2C19.6 5.9 16.2 3 12 3z"/></svg>`,
  },
  {
    label: "Etsy shop",
    url: "https://www.etsy.com/shop/DinaStyleKnits",
    icon: `<img src="static/images/etsy-icon.png" alt="" class="social-icon-img" />`,
  },
];

const NAV_LINKS = [
  { label: "Home", href: "index.html", page: "home" },
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
      `<li><a href="${link.url}" target="_blank" rel="noopener" aria-label="${link.label}">${link.icon}</a></li>`
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
