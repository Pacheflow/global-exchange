const menuButton = document.querySelector("[data-menu]");
menuButton?.addEventListener("click", () => {
  const target = document.getElementById(menuButton.getAttribute("aria-controls"));
  const isOpen = target?.classList.toggle("open");
  menuButton.setAttribute("aria-expanded", String(Boolean(isOpen)));
  menuButton.textContent = isOpen ? "close" : "menu";
  menuButton.setAttribute("aria-label", isOpen ? "Cerrar navegación" : "Abrir navegación");
  menuButton.setAttribute("title", isOpen ? "Cerrar navegación" : "Abrir navegación");
});

// Material state layer for semantic links and project-specific controls.
// Django Material already supplies it to <c-button.*>; this extends the same
// interaction to anchors that behave as navigation actions.
const materialInteractiveSelector = [
  ".button",
  ".menu-toggle",
  ".main-nav a",
  ".login-link",
  ".text-action",
  ".sidebar-nav a",
  ".sidebar-context a",
  ".sidebar-user a",
  ".action-list > a",
  ".row-actions a",
  ".row-actions button",
  ".choice-list label > span",
  ".swap-currencies",
  ".account-menu",
  ".profile-dropdown a",
  ".table-action",
  ".dashboard-section-heading > a",
  ".quick-actions-grid > a",
].join(",");

document.querySelectorAll(materialInteractiveSelector).forEach((control) => {
  control.classList.add("material-interactive");
  control.addEventListener("pointerdown", (event) => {
    const bounds = control.getBoundingClientRect();
    control.style.setProperty("--ripple-x", `${event.clientX - bounds.left}px`);
    control.style.setProperty("--ripple-y", `${event.clientY - bounds.top}px`);
  });
});

const profileMenu = document.querySelector(".dashboard-profile-menu");
if (profileMenu) {
  document.addEventListener("click", (event) => {
    if (profileMenu.open && !profileMenu.contains(event.target)) profileMenu.removeAttribute("open");
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && profileMenu.open) {
      profileMenu.removeAttribute("open");
      profileMenu.querySelector("summary")?.focus();
    }
  });
}

document.querySelectorAll("form[data-confirm]").forEach((form) =>
  form.addEventListener("submit", (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  }),
);
setTimeout(() => document.querySelector(".messages")?.remove(), 5000);

const converter = document.querySelector("[data-converter]");
if (converter) {
  const ratesInPyg = { PYG: 1, USD: 7360, EUR: 8680, BRL: 1370 };
  const amount = converter.querySelector("[data-converter-amount]");
  const from = converter.querySelector("[data-converter-from]");
  const to = converter.querySelector("[data-converter-to]");
  const result = converter.querySelector("[data-converter-result]");
  const rateLabel = document.querySelector("[data-converter-rate]");
  const swap = converter.querySelector("[data-converter-swap]");

  const formatValue = (value, currency) => new Intl.NumberFormat("es-PY", {
    minimumFractionDigits: currency === "PYG" ? 0 : 2,
    maximumFractionDigits: currency === "PYG" ? 0 : 2,
  }).format(value);

  const updateConversion = () => {
    const numericAmount = Math.max(Number.parseFloat(amount.value) || 0, 0);
    const unitRate = ratesInPyg[from.value] / ratesInPyg[to.value];
    result.textContent = formatValue(numericAmount * unitRate, to.value);
    rateLabel.textContent = `1 ${from.value} = ${formatValue(unitRate, to.value)} ${to.value}`;
  };

  amount.addEventListener("input", updateConversion);
  from.addEventListener("change", updateConversion);
  to.addEventListener("change", updateConversion);
  swap.addEventListener("click", () => {
    [from.value, to.value] = [to.value, from.value];
    updateConversion();
  });
  updateConversion();
}
