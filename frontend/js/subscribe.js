// Обробник форми підписки. Форма зараз лише збирає email у БД (без
// інтеграції з розсилками — за домовленістю це буде додано пізніше,
// коли з'явиться потреба реально відправляти листи).

function initSubscribeForm() {
  const form = document.getElementById("subscribe-form");
  if (!form) return;

  const input = form.querySelector('input[type="email"]');
  const messageEl = form.querySelector(".subscribe__message");
  const button = form.querySelector("button");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    messageEl.textContent = "";
    messageEl.className = "subscribe__message";
    button.disabled = true;

    try {
      await Api.subscribe(input.value.trim());
      messageEl.textContent = "Дякуємо! Ви підписані на новини й знижки.";
      messageEl.classList.add("is-success");
      form.reset();
    } catch (err) {
      messageEl.textContent = "Щось пішло не так. Перевірте email і спробуйте ще раз.";
      messageEl.classList.add("is-error");
    } finally {
      button.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", initSubscribeForm);
