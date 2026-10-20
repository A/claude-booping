(function () {
  var form = document.querySelector("form.search");
  if (!form) return;
  var root = document.documentElement;
  var input = form.querySelector("input");
  var list = form.querySelector("#search-list");
  var openBtn = document.querySelector(".iconbtn.search-btn");
  var closeBtn = form.querySelector(".search-close");
  var prefix = form.getAttribute("data-prefix");
  var page = document.querySelector("form.search-page");
  var phone = window.matchMedia("(max-width: 760px)");
  var WEIGHTS = [["title", 8], ["tags", 4], ["summary", 2], ["body", 1]];
  var index = null, body = null, wanted = {}, results = [], active = -1;

  function words(text) {
    return String(text || "").toLowerCase().replace(/ё/g, "е").split(/[^\p{L}\p{N}]+/u)
      .filter(Boolean);
  }
  function stem(w) { return w.length > 7 ? w.slice(0, -3) : w.length > 5 ? w.slice(0, -2) : w; }
  function load(name, ready) {
    if (wanted[name]) return;
    wanted[name] = true;
    var s = document.createElement("script");
    s.src = prefix + name;
    s.onload = ready;
    document.head.appendChild(s);
  }
  function prepare() {
    index = (window.SPECS_INDEX || []).map(function (r) {
      return { r: r, ref: words(r.ref).join(" "), title: words(r.title),
        tags: words((r.tags || []).join(" ")), summary: words(r.summary), body: null };
    });
  }
  function onIndex() { prepare(); attachBody(); refresh(true); }
  function onBody() { attachBody(); refresh(false); }
  function attachBody() {
    body = window.SPECS_BODY || null;
    if (!body || !index) return;
    index.forEach(function (e) { e.body = words(body[e.r.id]); });
  }
  function ensureIndex() {
    if (window.SPECS_INDEX) { if (!index) onIndex(); } else load("search-index.js", onIndex);
  }
  function ensureBody() {
    if (window.SPECS_BODY) { if (!body) onBody(); } else load("search-body.js", onBody);
  }
  function search(q) {
    var terms = words(q);
    if (!terms.length || !index) return [];
    var found = [];
    index.forEach(function (e, order) {
      var score = 0;
      var all = terms.every(function (t) {
        var s = stem(t), best = e.ref.indexOf(t) >= 0 ? 10 : 0;
        WEIGHTS.forEach(function (f) {
          if (f[1] > best && e[f[0]] && e[f[0]].some(function (w) { return w.indexOf(s) === 0; }))
            best = f[1];
        });
        score += best;
        return best > 0;
      });
      if (all) found.push({ e: e, score: score, order: order });
    });
    return found.sort(function (a, b) { return b.score - a.score || a.order - b.order; })
      .map(function (x) { return x.e.r; });
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function entry(r, cls) {
    var a = el("a", "t", r.title || r.ref);
    a.href = prefix + r.url;
    var item = el("li", cls);
    item.appendChild(el("code", "ref", r.ref));
    item.appendChild(a);
    var why = el("span", "why");
    if (r.status) why.appendChild(el("span", "badge st-" + r.status, r.status_label));
    item.appendChild(why);
    return item;
  }
  function allHref() { return prefix + "search.html?q=" + encodeURIComponent(input.value); }
  function setActive(i) {
    var opts = list.children;
    active = i;
    for (var k = 0; k < opts.length; k++) opts[k].setAttribute("aria-selected", String(k === i));
    if (i >= 0) input.setAttribute("aria-activedescendant", opts[i].id);
    else input.removeAttribute("aria-activedescendant");
  }
  function show(open) {
    list.hidden = !open;
    input.setAttribute("aria-expanded", String(open));
    if (!open) setActive(-1);
  }
  function refresh(fresh) {
    if (page) renderPage();
    var keep = !fresh && active >= 0 && active < results.length ? results[active].id : null;
    if (!index || !input.value.trim()) { results = []; show(false); return; }
    ensureBody();
    results = search(input.value).slice(0, 8);
    list.textContent = "";
    results.forEach(function (r, i) {
      var li = entry(r, null);
      li.id = "search-opt-" + i;
      li.setAttribute("role", "option");
      list.appendChild(li);
    });
    var more = el("li", "all");
    more.id = "search-opt-all";
    more.setAttribute("role", "option");
    var a = el("a", null, form.getAttribute("data-all") + " →");
    a.href = allHref();
    more.appendChild(a);
    list.appendChild(more);
    show(document.activeElement === input);
    var at = keep === null ? -1 : results.map(function (r) { return r.id; }).indexOf(keep);
    setActive(at);
  }
  function renderPage() {
    var q = page.querySelector("input").value;
    var out = document.querySelector("ul.search-results");
    var count = document.querySelector("p.count");
    var forms = JSON.parse(count.getAttribute("data-forms"));
    var found = search(q);
    out.textContent = "";
    found.forEach(function (r) {
      var row = entry(r, "row");
      if (r.summary) row.appendChild(el("span", "s", r.summary));
      out.appendChild(row);
    });
    var n = found.length, i;
    if (forms.length >= 3) {
      i = n % 10 === 1 && n % 100 !== 11 ? 0
        : n % 10 >= 2 && n % 10 <= 4 && !(n % 100 >= 12 && n % 100 <= 14) ? 1 : 2;
    } else i = n === 1 ? 0 : forms.length - 1;
    count.textContent = q.trim() ? forms[i].replace("{n}", n) : "";
    document.querySelector("p.empty").hidden = !q.trim() || n > 0;
  }
  function openOverlay() { root.classList.add("search-open"); ensureIndex(); input.focus(); }
  function closeOverlay() {
    root.classList.remove("search-open");
    show(false);
    if (openBtn) openBtn.focus();
  }

  input.addEventListener("focus", ensureIndex);
  input.addEventListener("input", function () { refresh(true); });
  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      if (list.hidden) refresh(true);
      var n = list.children.length;
      if (list.hidden || !n) return;
      e.preventDefault();
      var step = e.key === "ArrowDown" ? 1 : -1;
      setActive(active < 0 ? (step > 0 ? 0 : n - 1) : (active + step + n) % n);
    } else if (e.key === "Enter" && !list.hidden && active >= 0) {
      e.preventDefault();
      location.href = list.children[active].querySelector("a").href;
    } else if (e.key === "Escape") {
      e.preventDefault();
      if (!list.hidden) show(false);
      else if (root.classList.contains("search-open")) closeOverlay();
      else { input.value = ""; input.blur(); }
    }
  });
  input.addEventListener("blur", function () {
    setTimeout(function () { if (!form.contains(document.activeElement)) show(false); }, 150);
  });
  if (openBtn) openBtn.addEventListener("click", openOverlay);
  if (closeBtn) closeBtn.addEventListener("click", closeOverlay);
  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target;
    if (t && (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable)) return;
    e.preventDefault();
    if (phone.matches) openOverlay();
    else { ensureIndex(); input.focus(); }
  });
  if (page) {
    var q = new URLSearchParams(location.search).get("q") || "";
    var field = page.querySelector("input");
    field.value = q;
    input.value = q;
    field.addEventListener("input", renderPage);
    ensureIndex();
    ensureBody();
  }
})();
