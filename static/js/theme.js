(() => {
  const storageKey = "gcondid-theme";
  const root = document.documentElement;
  const preferred = () => localStorage.getItem(storageKey) || "dark";
  const apply = (theme) => {
    root.dataset.theme = theme;
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.textContent = theme === "dark" ? "Tema claro" : "Tema escuro";
    });
  };
  apply(preferred());
  window.addEventListener("DOMContentLoaded", () => {
    apply(preferred());
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.addEventListener("click", () => {
        const next = root.dataset.theme === "dark" ? "light" : "dark";
        localStorage.setItem(storageKey, next);
        apply(next);
      });
    });
  });
})();
