(function () {
  var bar = document.querySelector(".filters");
  var list = document.querySelector("ul.rows");
  if (!bar || !list) return;
  var KEYS = ["type", "source", "status", "flag"];
  var lang = document.documentElement.lang;
  var rows = Array.prototype.slice.call(list.querySelectorAll(".row"));
  var chips = Array.prototype.slice.call(bar.querySelectorAll(".chip"));
  var select = bar.querySelector("select.sort");
  var count = bar.querySelector(".count");
  var empty = bar.nextElementSibling;
  var forms = JSON.parse(count.getAttribute("data-forms"));
  var fallback = bar.getAttribute("data-default-sort");
  var openBtn = bar.querySelector("button.filter-open");
  var activeRow = bar.querySelector("div.filter-active");
  var sheet = bar.querySelector("dialog.filter-sheet");

  function plural(n) {
    var i;
    if (forms.length >= 3) {
      if (n % 10 === 1 && n % 100 !== 11) i = 0;
      else if (n % 10 >= 2 && n % 10 <= 4 && !(n % 100 >= 12 && n % 100 <= 14)) i = 1;
      else i = 2;
    } else i = n === 1 ? 0 : forms.length - 1;
    return forms[i].replace("{n}", n);
  }
  function values(row, key) {
    if (key === "flag") return (row.getAttribute("data-flags") || "").split(" ");
    return [row.getAttribute("data-" + key)];
  }
  function active() {
    var on = {};
    chips.forEach(function (chip) {
      if (chip.getAttribute("aria-pressed") !== "true") return;
      var key = chip.getAttribute("data-key");
      (on[key] = on[key] || []).push(chip.getAttribute("data-value"));
    });
    return on;
  }
  function chipLabel(chip) {
    var copy = chip.cloneNode(true);
    Array.prototype.forEach.call(copy.querySelectorAll(".n, svg"), function (el) { el.remove(); });
    return copy.textContent.trim();
  }
  function pressedChips() {
    return chips.filter(function (chip) { return chip.getAttribute("aria-pressed") === "true"; });
  }
  function renderRow(pressed) {
    if (!openBtn || !window.SpecsFilters) return;
    var option = select.options[select.selectedIndex];
    openBtn.textContent = SpecsFilters.row(
      openBtn.getAttribute("data-label"), pressed.length, option ? option.textContent : ""
    );
  }
  function renderActive(pressed) {
    if (!activeRow || !window.SpecsFilters) return;
    var items = SpecsFilters.removable(pressed.map(function (chip) {
      return { key: chip.getAttribute("data-key"), value: chip.getAttribute("data-value"), label: chipLabel(chip) };
    }), activeRow.getAttribute("data-remove") || "{label}");
    activeRow.textContent = "";
    items.forEach(function (item, i) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chip chip-x";
      btn.setAttribute("aria-label", item.aria);
      btn.appendChild(document.createTextNode(item.text));
      var x = document.createElement("span");
      x.setAttribute("aria-hidden", "true");
      x.textContent = "×";
      btn.appendChild(x);
      btn.addEventListener("click", function () {
        pressed[i].setAttribute("aria-pressed", "false");
        apply();
        write();
        var left = activeRow.querySelectorAll(".chip-x");
        (left[i] || left[left.length - 1] || openBtn).focus();
      });
      activeRow.appendChild(btn);
    });
  }
  function order(row) { return Number(row.getAttribute("data-order")); }
  function newestFirst(a, b) {
    var x = a.getAttribute("data-updated"), y = b.getAttribute("data-updated");
    if (x === y) return 0;
    if (!x) return 1;
    if (!y) return -1;
    return x < y ? 1 : -1;
  }
  var SORTS = {
    number: function () { return 0; },
    updated: newestFirst,
    title: function (a, b) {
      return a.getAttribute("data-title").localeCompare(b.getAttribute("data-title"), lang);
    },
    review: function (a, b) {
      var x = a.getAttribute("data-created-by") === "claude" ? 0 : 1;
      var y = b.getAttribute("data-created-by") === "claude" ? 0 : 1;
      if (x !== y) return x - y;
      var u = a.getAttribute("data-updated"), v = b.getAttribute("data-updated");
      if (u === v) return 0;
      if (!u) return 1;
      if (!v) return -1;
      return u < v ? -1 : 1;
    }
  };
  function apply() {
    var on = active();
    var shown = 0;
    rows.forEach(function (row) {
      var ok = KEYS.every(function (key) {
        if (!on[key]) return true;
        return values(row, key).some(function (v) { return on[key].indexOf(v) >= 0; });
      });
      row.hidden = !ok;
      if (ok) shown++;
    });
    var by = SORTS[select.value] || SORTS.number;
    rows.slice().sort(function (a, b) { return by(a, b) || order(a) - order(b); })
      .forEach(function (row) { list.appendChild(row); });
    count.textContent = plural(shown);
    empty.hidden = shown > 0;
    var pressed = pressedChips();
    renderRow(pressed);
    renderActive(pressed);
  }
  function write() {
    var on = active();
    var parts = [];
    KEYS.forEach(function (key) {
      if (on[key]) parts.push(key + "=" + on[key].map(encodeURIComponent).join(","));
    });
    if (select.value !== fallback) parts.push("sort=" + encodeURIComponent(select.value));
    var url = location.pathname + location.search + (parts.length ? "#" + parts.join("&") : "");
    history.replaceState(null, "", url);
  }
  function read() {
    var state = {};
    location.hash.slice(1).split("&").forEach(function (pair) {
      var at = pair.indexOf("=");
      if (at < 0) return;
      try {
        state[pair.slice(0, at)] = pair.slice(at + 1).split(",").map(decodeURIComponent);
      } catch (e) {}
    });
    chips.forEach(function (chip) {
      var picked = state[chip.getAttribute("data-key")] || [];
      chip.setAttribute("aria-pressed", String(picked.indexOf(chip.getAttribute("data-value")) >= 0));
    });
    var sort = (state.sort || [])[0];
    select.value = SORTS[sort] && select.querySelector('option[value="' + sort + '"]') ? sort : fallback;
    apply();
  }
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chip.setAttribute("aria-pressed", String(chip.getAttribute("aria-pressed") !== "true"));
      apply();
      write();
    });
  });
  select.addEventListener("change", function () { apply(); write(); });
  window.addEventListener("hashchange", read);
  if (sheet && openBtn) {
    openBtn.addEventListener("click", function () { sheet.showModal(); });
    Array.prototype.forEach.call(sheet.querySelectorAll(".filter-close, .filter-done"), function (btn) {
      btn.addEventListener("click", function () { sheet.close(); });
    });
    sheet.addEventListener("click", function (e) { if (e.target === sheet) sheet.close(); });
    sheet.addEventListener("close", function () { openBtn.focus(); });
    var phone = window.matchMedia("(max-width: 760px)");
    phone.addEventListener("change", function () { if (!phone.matches && sheet.open) sheet.close(); });
  }
  read();
})();
