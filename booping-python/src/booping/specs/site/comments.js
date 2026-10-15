(function () {
  var root = document.documentElement;
  var form = document.querySelector("form.search[data-prefix]");
  if (!form) return;
  var siteRoot = new URL(form.getAttribute("data-prefix"), location.href).href;
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
  refresh();
  window.addEventListener("storage", function (e) {
    if (e.key === null || e.key === KEY) refresh();
  });

  var compose = document.querySelector("dialog.cmt-compose");
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
