(function () {
  var theme;
  try {
    theme = localStorage.getItem("airbridge-site-theme");
  } catch (_) {}
  if (theme !== "light" && theme !== "dark")
    theme = matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  document.documentElement.dataset.theme = theme;
})();
