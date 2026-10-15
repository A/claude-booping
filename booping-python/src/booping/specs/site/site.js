(function () {
  var root = document.documentElement;
  var KEY = "specs-theme";
  var ORDER = ["auto", "light", "dark"];
  var ICONS = { auto: "i-auto", light: "i-sun", dark: "i-moon" };
  var theme = document.querySelector(".iconbtn.theme");
  var current = "auto";
  try {
    var saved = localStorage.getItem(KEY);
    if (saved === "light" || saved === "dark") current = saved;
  } catch (e) {}
  function show() {
    if (current === "auto") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", current);
    var label = theme.getAttribute("data-label-" + current);
    theme.setAttribute("aria-label", label);
    theme.setAttribute("title", label);
    theme.querySelector("use").setAttribute("href", "#" + ICONS[current]);
  }
  if (theme) {
    show();
    theme.addEventListener("click", function () {
      current = ORDER[(ORDER.indexOf(current) + 1) % ORDER.length];
      try {
        if (current === "auto") localStorage.removeItem(KEY);
        else localStorage.setItem(KEY, current);
      } catch (e) {}
      show();
    });
  }
  var menu = document.querySelector(".iconbtn.menu");
  var side = document.getElementById("drawer");
  if (!menu || !side) return;
  var body = document.body;
  var scrim = null;
  function close() {
    body.classList.remove("drawer-open");
    menu.setAttribute("aria-expanded", "false");
    if (scrim) scrim.parentNode.removeChild(scrim);
    scrim = null;
    menu.focus();
  }
  function open() {
    body.classList.add("drawer-open");
    menu.setAttribute("aria-expanded", "true");
    scrim = document.createElement("div");
    scrim.className = "scrim";
    scrim.addEventListener("click", close);
    body.appendChild(scrim);
    var first = side.querySelector("a");
    if (first) first.focus();
  }
  menu.addEventListener("click", function () {
    if (body.classList.contains("drawer-open")) close();
    else open();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && body.classList.contains("drawer-open")) close();
  });
})();
