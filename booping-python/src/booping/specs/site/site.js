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
  var status = document.getElementById("status");
  var statusTimer = null;
  function announce(text) {
    if (!status) return;
    status.textContent = text;
    clearTimeout(statusTimer);
    statusTimer = setTimeout(function () { status.textContent = ""; }, 2000);
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a.anchor");
    if (!a || !navigator.clipboard) return;
    var url = location.href.split("#")[0] + a.getAttribute("href");
    navigator.clipboard.writeText(url).then(function () {
      announce(status ? status.getAttribute("data-copied") : "");
    }, function () {});
  });
  document.addEventListener("click", function (e) {
    if (e.button !== 0 || !e.target.closest) return;
    var row = e.target.closest(".row");
    var link = row && row.querySelector("a.t[href]");
    if (!link || e.target.closest("a, button, input, select, textarea")) return;
    var sel = window.getSelection && window.getSelection();
    if (sel && !sel.isCollapsed) return;
    var href = link.getAttribute("href");
    if (e.ctrlKey || e.metaKey) window.open(href, "_blank", "noopener");
    else location.assign(href);
  });
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    var target = id && document.getElementById(id);
    if (!target) return;
    for (var el = target.parentElement; el; el = el.parentElement) {
      if (el.tagName === "DETAILS" && !el.open) el.open = true;
    }
  }
  openTarget();
  window.addEventListener("hashchange", openTarget);
  var railLinks = document.querySelectorAll(".rail .toc a");
  if (railLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    var targets = [];
    for (var i = 0; i < railLinks.length; i++) {
      var heading = document.getElementById(decodeURIComponent(railLinks[i].getAttribute("href").slice(1)));
      if (heading) {
        byId[heading.id] = railLinks[i];
        targets.push(heading);
      }
    }
    var crossed = {};
    var currentLink = null;
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        // Above the observed band means the heading has scrolled past the top 30%.
        crossed[entry.target.id] = entry.isIntersecting || entry.boundingClientRect.top < entry.rootBounds.top;
      });
      var last = null;
      targets.forEach(function (t) { if (crossed[t.id]) last = t; });
      var link = last ? byId[last.id] : null;
      if (link === currentLink) return;
      if (currentLink) currentLink.removeAttribute("aria-current");
      if (link) link.setAttribute("aria-current", "location");
      currentLink = link;
    }, { rootMargin: "0px 0px -70% 0px" });
    targets.forEach(function (t) { spy.observe(t); });
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
