// Каруусель фото на сторінці About. Фото змінюються самі час від часу
// (кожні 5 секунд, ненав'язливо, з плавним переходом), і користувач може
// гортати вручну стрілками — ручний клік скидає таймер, щоб фото не
// перемкнулось саме одразу після ручної дії.

const ABOUT_PHOTOS = [
  { src: "static/images/about-photo-1.jpg", caption: "Place, where I knit and sew" },
  { src: "static/images/about-photo-2.jpg", caption: "My main material and instruments — yarn and needles" },
  { src: "static/images/about-photo-3.jpg", caption: "Some of my knitted things — made with love and care" },
  { src: "static/images/about-photo-4.jpg", caption: "Here I am! Welcome to my shop (this shawl was knitted by me too)" },
  { src: "static/images/about-photo-5.jpg", caption: "One of my work processes" },
];

const AUTO_ADVANCE_MS = 5000;

let currentIndex = 0;
let autoAdvanceTimer = null;

function renderSlide() {
  const img = document.getElementById("carousel-image");
  const caption = document.getElementById("carousel-caption");
  const dotsMount = document.getElementById("carousel-dots");
  if (!img) return;

  const photo = ABOUT_PHOTOS[currentIndex];

  // Плавний перехід: спершу ховаємо поточне фото, тоді міняємо src,
  // і після завантаження показуємо знову — виглядає ненав'язливо, без "стрибка".
  img.classList.add("is-fading");
  window.setTimeout(() => {
    img.src = photo.src;
    img.alt = photo.caption;
    caption.textContent = photo.caption;
    img.onload = () => img.classList.remove("is-fading");
  }, 250);

  dotsMount.innerHTML = ABOUT_PHOTOS.map(
    (_, i) => `<button class="about-carousel__dot ${i === currentIndex ? "is-active" : ""}" data-index="${i}" aria-label="Go to photo ${i + 1}"></button>`
  ).join("");

  dotsMount.querySelectorAll(".about-carousel__dot").forEach((dot) => {
    dot.addEventListener("click", () => {
      currentIndex = parseInt(dot.dataset.index, 10);
      renderSlide();
      restartAutoAdvance();
    });
  });
}

function goNext() {
  currentIndex = (currentIndex + 1) % ABOUT_PHOTOS.length;
  renderSlide();
}

function goPrev() {
  currentIndex = (currentIndex - 1 + ABOUT_PHOTOS.length) % ABOUT_PHOTOS.length;
  renderSlide();
}

function restartAutoAdvance() {
  window.clearInterval(autoAdvanceTimer);
  autoAdvanceTimer = window.setInterval(goNext, AUTO_ADVANCE_MS);
}

document.addEventListener("DOMContentLoaded", () => {
  const prevBtn = document.getElementById("carousel-prev");
  const nextBtn = document.getElementById("carousel-next");
  if (!prevBtn || !nextBtn) return; // цей скрипт підключений лише на about.html

  renderSlide();
  restartAutoAdvance();

  nextBtn.addEventListener("click", () => {
    goNext();
    restartAutoAdvance();
  });
  prevBtn.addEventListener("click", () => {
    goPrev();
    restartAutoAdvance();
  });
});
