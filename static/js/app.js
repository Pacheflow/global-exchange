document
  .querySelector("[data-menu]")
  ?.addEventListener("click", () =>
    document.querySelector("#main-menu")?.classList.toggle("open"),
  );
document.querySelectorAll("form[data-confirm]").forEach((form) =>
  form.addEventListener("submit", (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  }),
);
setTimeout(() => document.querySelector(".messages")?.remove(), 5000);
