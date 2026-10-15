(function () {
  var root = document.documentElement;
  var form = document.querySelector("form.search[data-prefix]");
  if (!form) return;
  var siteRoot = new URL(form.getAttribute("data-prefix") || "./", location.href).href;
  var KEY = "specs-comments:v1:" + siteRoot;
  var article = document.querySelector("article[data-ref]");

  function load() {
    try {
      var list = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(list) ? list : [];
    } catch (e) {
      return [];
    }
  }
  function save(list) {
    try {
      localStorage.setItem(KEY, JSON.stringify(list));
      return true;
    } catch (e) {
      return false;
    }
  }
  function newId() {
    return Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
  }
  function add(fields) {
    var list = load();
    var comment = { id: newId() };
    for (var k in fields) {
      if (Object.prototype.hasOwnProperty.call(fields, k)) comment[k] = fields[k];
    }
    list.push(comment);
    save(list);
    refresh();
    return comment;
  }
  function update(id, fields) {
    var list = load();
    for (var i = 0; i < list.length; i++) {
      if (list[i].id !== id) continue;
      for (var k in fields) {
        if (Object.prototype.hasOwnProperty.call(fields, k)) list[i][k] = fields[k];
      }
    }
    save(list);
    refresh();
  }
  function remove(id) {
    save(load().filter(function (c) { return c.id !== id; }));
    refresh();
  }

  function setCount(el, n) {
    if (el) el.textContent = n > 0 ? String(n) : "";
  }
  function refresh() {
    var list = load();
    var nav = document.querySelector(".cmt-nav");
    if (nav) {
      nav.hidden = false;
      setCount(nav.querySelector(".n"), list.length);
    }
    var open = document.querySelector(".cmt-open");
    if (open && article) {
      var ref = article.getAttribute("data-ref");
      setCount(open.querySelector(".n"), list.filter(function (c) { return c.ref === ref; }).length);
    }
    if (sheet && article && sheet.open) renderSheet();
    if (groups) renderGroups();
  }

  var works = false;
  try {
    var probe = KEY + ":probe";
    localStorage.setItem(probe, "1");
    localStorage.removeItem(probe);
    works = true;
  } catch (e) {}
  if (!works) return;
  root.classList.add("cmt");

  var compose = document.querySelector("dialog.cmt-compose");
  var prefix = form.getAttribute("data-prefix");
  var status = document.getElementById("status");
  var statusTimer = null;
  function label(name) {
    return compose ? compose.getAttribute("data-" + name) || "" : "";
  }
  function plural(name, n) {
    var forms;
    try {
      forms = JSON.parse(label(name));
    } catch (e) {
      return String(n);
    }
    var i;
    if (forms.length >= 3) {
      if (n % 10 === 1 && n % 100 !== 11) i = 0;
      else if (n % 10 >= 2 && n % 10 <= 4 && !(n % 100 >= 12 && n % 100 <= 14)) i = 1;
      else i = 2;
    } else i = n === 1 ? 0 : forms.length - 1;
    return forms[i].replace("{n}", n);
  }
  function announce(text) {
    if (!status) return;
    status.textContent = text;
    clearTimeout(statusTimer);
    statusTimer = setTimeout(function () { status.textContent = ""; }, 2000);
  }
  function byCreated(a, b) {
    return a.created < b.created ? -1 : a.created > b.created ? 1 : a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
  }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }
  function button(cls, text, onClick) {
    var b = el("button", cls, text);
    b.type = "button";
    b.addEventListener("click", onClick);
    return b;
  }

  var editing = null;
  var editDraft = "";
  var noteLabel = compose && compose.querySelector("label[for='cmt-note']");

  function item(c, href, onAnchor) {
    var li = el("li", "cmt-item");
    li.setAttribute("data-id", c.id);
    var a = el("a", "cmt-anchor", c.anchor ? "§ " + c.anchorText : c.title);
    a.href = href;
    if (onAnchor) a.addEventListener("click", onAnchor);
    li.appendChild(a);
    if (c.sent) li.appendChild(el("span", "badge cmt-sent", label("sent")));
    if (c.quote) li.appendChild(el("blockquote", "cmt-q", c.quote));
    if (editing === c.id) {
      var fieldId = "cmt-edit-" + c.id;
      var lab = el("label", "cmt-edit-label", noteLabel ? noteLabel.textContent : "");
      lab.setAttribute("for", fieldId);
      var area = el("textarea", "cmt-edit");
      area.id = fieldId;
      area.rows = 4;
      area.value = editDraft;
      var save = button("cmt-save", label("save"), function () {
        if (!area.value.trim()) return;
        editing = null;
        update(c.id, { note: area.value, sent: false });
        var again = document.querySelector(".cmt-item[data-id='" + c.id + "'] .cmt-edit-btn");
        if (again) again.focus();
      });
      save.disabled = !area.value.trim();
      area.addEventListener("input", function () {
        editDraft = area.value;
        save.disabled = !area.value.trim();
      });
      var cancel = button("cmt-cancel", label("cancel"), function () {
        editing = null;
        refresh();
        var again = document.querySelector(".cmt-item[data-id='" + c.id + "'] .cmt-edit-btn");
        if (again) again.focus();
      });
      var acts = el("div", "cmt-actions");
      acts.appendChild(save);
      acts.appendChild(cancel);
      li.appendChild(lab);
      li.appendChild(area);
      li.appendChild(acts);
      return li;
    }
    li.appendChild(el("p", "cmt-note", c.note));
    var ops = el("div", "cmt-ops");
    ops.appendChild(button("cmt-edit-btn", label("edit"), function () {
      editing = c.id;
      editDraft = c.note;
      refresh();
      var area = document.getElementById("cmt-edit-" + c.id);
      if (area) area.focus();
    }));
    ops.appendChild(button("cmt-del", label("delete"), function () {
      var container = li.closest(".cmt-groups") || li.closest(".cmt-list");
      var items = Array.prototype.slice.call(container.querySelectorAll(".cmt-item"));
      var at = items.indexOf(li);
      if (editing === c.id) editing = null;
      remove(c.id);
      announce(label("deleted"));
      var next = container.querySelectorAll(".cmt-item")[at];
      var target = next ? next.querySelector("a") : container.parentNode.querySelector("h1, h2");
      if (target) {
        if (!next) target.setAttribute("tabindex", "-1");
        target.focus();
      }
    }));
    li.appendChild(ops);
    return li;
  }

  function copyText(text, done) {
    function fallback() {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.top = "0";
      area.style.left = "-9999px";
      var host = document.querySelector("dialog[open]") || document.body;
      host.appendChild(area);
      area.select();
      var ok = false;
      try {
        ok = document.execCommand("copy");
      } catch (e) {}
      host.removeChild(area);
      done(ok);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
    } else fallback();
  }

  function wireActions(box, scope) {
    var copy = box.querySelector(".cmt-copy");
    var clear = box.querySelector(".cmt-clear");
    if (copy) copy.addEventListener("click", function () {
      var list = scope();
      if (!list.length || !window.SpecsComments) return;
      copyText(window.SpecsComments.format(list, siteRoot), function (ok) {
        if (!ok) {
          announce(label("copy-failed"));
          return;
        }
        var ids = {};
        list.forEach(function (c) { ids[c.id] = true; });
        var all = load();
        all.forEach(function (c) { if (ids[c.id]) c.sent = true; });
        save(all);
        refresh();
        announce(plural("copied-forms", list.length));
      });
    });
    if (clear) clear.addEventListener("click", function () {
      var ids = {};
      var n = 0;
      scope().forEach(function (c) {
        if (c.sent) {
          ids[c.id] = true;
          n++;
        }
      });
      if (!n) return;
      save(load().filter(function (c) { return !ids[c.id]; }));
      refresh();
      announce(plural("cleared-forms", n));
    });
  }
  function setActions(box, list) {
    var copy = box.querySelector(".cmt-copy");
    var clear = box.querySelector(".cmt-clear");
    if (copy) copy.disabled = !list.length;
    if (clear) clear.disabled = !list.some(function (c) { return c.sent; });
    var empty = box.querySelector(".cmt-empty");
    if (empty) empty.hidden = list.length > 0;
  }

  var sheet = document.querySelector("dialog.cmt-sheet");
  var openBtn = document.querySelector(".cmt-open");
  function recordScope() {
    var ref = article.getAttribute("data-ref");
    return load().filter(function (c) { return c.ref === ref; }).sort(byCreated);
  }
  function renderSheet() {
    var list = recordScope();
    var ul = sheet.querySelector(".cmt-list");
    ul.textContent = "";
    list.forEach(function (c) {
      ul.appendChild(item(c, "#" + c.anchor, function () { sheet.close(); }));
    });
    setActions(sheet, list);
  }
  if (sheet && article) {
    wireActions(sheet, recordScope);
    if (openBtn) openBtn.addEventListener("click", function () {
      renderSheet();
      sheet.showModal();
    });
    sheet.querySelector(".cmt-close").addEventListener("click", function () { sheet.close(); });
    sheet.addEventListener("close", function () {
      editing = null;
      if (openBtn) openBtn.focus();
    });
  }

  var groups = document.querySelector(".cmt-groups");
  var page = groups && groups.parentNode;
  function allScope() {
    return load().sort(byCreated);
  }
  function renderGroups() {
    var list = allScope();
    var byRef = {};
    var refs = [];
    list.forEach(function (c) {
      if (!byRef[c.ref]) {
        byRef[c.ref] = [];
        refs.push(c.ref);
      }
      byRef[c.ref].push(c);
    });
    refs.sort(function (a, b) { return a < b ? -1 : a > b ? 1 : 0; });
    groups.textContent = "";
    refs.forEach(function (ref) {
      var first = byRef[ref][0];
      var section = el("section", "cmt-group");
      var h = el("h2");
      var link = el("a");
      link.href = prefix + first.page;
      link.appendChild(el("span", "ref", ref));
      link.appendChild(document.createTextNode(" " + first.title));
      h.appendChild(link);
      section.appendChild(h);
      var ul = el("ul", "cmt-list");
      byRef[ref].forEach(function (c) {
        ul.appendChild(item(c, prefix + c.page + (c.anchor ? "#" + c.anchor : ""), null));
      });
      section.appendChild(ul);
      groups.appendChild(section);
    });
    setActions(page, list);
  }
  if (groups) wireActions(page, allScope);

  refresh();
  window.addEventListener("storage", function (e) {
    if (e.key === null || e.key === KEY) refresh();
  });

  var body = article && article.querySelector(".body");
  if (!compose || !body) return;
  var HEADS = "h2[id], h3[id], h4[id]";
  var BLOCKS = "p, li, blockquote, td, pre";
  var ICON = '<svg class="ic" aria-hidden="true"><use href="#i-comment"/></svg>';

  function headingText(h) {
    var clone = h.cloneNode(true);
    var extra = clone.querySelectorAll("a.anchor, button.cmt-add");
    for (var i = 0; i < extra.length; i++) extra[i].parentNode.removeChild(extra[i]);
    return clone.textContent.trim();
  }
  function anchorFor(node) {
    var heads = body.querySelectorAll(HEADS);
    var found = null;
    for (var i = 0; i < heads.length; i++) {
      var h = heads[i];
      if (h === node || h.contains(node) || h.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING) found = h;
      else break;
    }
    return found ? { anchor: found.id, anchorText: headingText(found) } : { anchor: "", anchorText: "" };
  }
  function topChild(node) {
    while (node && node.parentNode !== body) node = node.parentNode;
    return node;
  }

  var heads = body.querySelectorAll(HEADS);
  for (var h = 0; h < heads.length; h++) {
    var link = heads[h].querySelector("a.anchor");
    if (!link) continue;
    var sectionBtn = document.createElement("button");
    sectionBtn.type = "button";
    sectionBtn.className = "cmt-add";
    sectionBtn.setAttribute("aria-label", compose.getAttribute("data-comment-section"));
    sectionBtn.innerHTML = ICON;
    link.parentNode.insertBefore(sectionBtn, link.nextSibling);
  }

  var floatBtn = document.createElement("button");
  floatBtn.type = "button";
  floatBtn.className = "cmt-float";
  floatBtn.hidden = true;
  floatBtn.innerHTML = ICON + "<span></span>";
  var floatMode = null;
  var pending = null;

  function showFloat(mode, label, after, rect, beside) {
    floatMode = mode;
    floatBtn.querySelector("span").textContent = label;
    if (after && floatBtn.previousSibling !== after) after.parentNode.insertBefore(floatBtn, after.nextSibling);
    floatBtn.hidden = false;
    var box = body.getBoundingClientRect();
    var top = beside ? rect.top - box.top : rect.bottom - box.top + 6;
    var left = beside ? box.width - floatBtn.offsetWidth : rect.left - box.left;
    floatBtn.style.top = top + "px";
    floatBtn.style.left = Math.max(0, Math.min(left, box.width - floatBtn.offsetWidth)) + "px";
  }
  function hideFloat() {
    floatMode = null;
    floatBtn.hidden = true;
  }

  var timer = null;
  function checkSelection() {
    if (compose.open) return;
    var sel = window.getSelection();
    if (!sel || !sel.rangeCount || sel.isCollapsed) {
      if (floatMode === "span") hideFloat();
      return;
    }
    var range = sel.getRangeAt(0);
    var text = sel.toString();
    if (!body.contains(range.commonAncestorContainer) || !text.trim()) {
      hideFloat();
      return;
    }
    var rects = range.getClientRects();
    var rect = rects.length ? rects[rects.length - 1] : range.getBoundingClientRect();
    pending = { kind: "span", quote: text, node: range.startContainer, range: range.cloneRange() };
    showFloat("span", compose.getAttribute("data-comment"), topChild(range.endContainer), rect, false);
  }
  function onSelection(e) {
    if (e && e.target === floatBtn) return;
    clearTimeout(timer);
    timer = setTimeout(checkSelection, 150);
  }
  document.addEventListener("selectionchange", onSelection);
  document.addEventListener("pointerup", onSelection);
  document.addEventListener("keyup", onSelection);

  body.addEventListener("click", function (e) {
    if (e.target.closest("a, button")) return;
    var sel = window.getSelection();
    if (sel && !sel.isCollapsed && sel.toString().trim()) return;
    var block = e.target.closest(BLOCKS);
    if (!block || !body.contains(block)) {
      hideFloat();
      return;
    }
    pending = { kind: "paragraph", quote: block.textContent, node: block, range: null };
    showFloat("paragraph", compose.getAttribute("data-comment-paragraph"), topChild(block), block.getBoundingClientRect(), true);
  });
  document.addEventListener("click", function (e) {
    if (floatMode === "paragraph" && !body.contains(e.target)) hideFloat();
  });
  floatBtn.addEventListener("mousedown", function (e) { e.preventDefault(); });
  floatBtn.addEventListener("click", function () {
    if (!pending) return;
    var where = anchorFor(pending.node);
    openCompose({ kind: pending.kind, anchor: where.anchor, anchorText: where.anchorText, quote: pending.quote }, floatBtn, pending.range);
  });
  body.addEventListener("click", function (e) {
    var btn = e.target.closest("button.cmt-add");
    if (!btn) return;
    var head = btn.parentNode;
    var text = headingText(head);
    openCompose({ kind: "section", anchor: head.id, anchorText: text, quote: text }, btn, null);
  });

  var quoteEl = compose.querySelector(".cmt-quote");
  var note = compose.querySelector("textarea");
  var saveBtn = compose.querySelector(".cmt-save");
  var draft = null;
  var opener = null;
  var openRange = null;
  var saved = false;

  function openCompose(d, from, range) {
    draft = d;
    opener = from;
    openRange = range;
    saved = false;
    quoteEl.textContent = d.quote;
    note.value = "";
    saveBtn.disabled = true;
    compose.showModal();
    note.focus();
  }
  function doSave() {
    if (!draft || !note.value.trim()) return;
    add({
      ref: article.getAttribute("data-ref"),
      title: article.getAttribute("data-title"),
      page: article.getAttribute("data-page"),
      anchor: draft.anchor,
      anchorText: draft.anchorText,
      kind: draft.kind,
      quote: draft.quote,
      note: note.value,
      created: new Date().toISOString(),
      sent: false
    });
    saved = true;
    compose.close();
  }
  note.addEventListener("input", function () { saveBtn.disabled = !note.value.trim(); });
  note.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      doSave();
    }
  });
  saveBtn.addEventListener("click", doSave);
  compose.querySelector(".cmt-cancel").addEventListener("click", function () { compose.close(); });
  compose.addEventListener("close", function () {
    var sel = window.getSelection();
    if (saved) {
      if (sel) sel.removeAllRanges();
      if (opener === floatBtn) {
        hideFloat();
        var head = draft.anchor && document.getElementById(draft.anchor);
        var btn = head && head.querySelector("button.cmt-add");
        if (btn) btn.focus();
        return;
      }
    } else if (openRange && sel) {
      sel.removeAllRanges();
      sel.addRange(openRange);
    }
    if (opener && !opener.hidden) opener.focus();
  });
})();
