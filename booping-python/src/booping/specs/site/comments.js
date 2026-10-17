(function () {
  var root = document.documentElement;
  var form = document.querySelector("form.search[data-prefix]");
  if (!form) return;
  var prefix = form.getAttribute("data-prefix");
  var siteRoot = new URL(prefix || "./", location.href).href;
  // Comments keep their v1 key and shape; reviewed marks and unsent drafts sit beside them.
  var KEY = "specs-comments:v1:" + siteRoot;
  var REVIEWED_KEY = "specs-reviewed:v1:" + siteRoot;
  var DRAFTS_KEY = "specs-drafts:v1:" + siteRoot;

  function read(key, empty) {
    try {
      var value = JSON.parse(localStorage.getItem(key) || "null");
      if (value && typeof value === "object" && Array.isArray(value) === Array.isArray(empty)) return value;
    } catch (e) {}
    return empty;
  }
  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {}
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

  function loadComments() { return read(KEY, []); }
  function loadReviewed() { return read(REVIEWED_KEY, {}); }
  function loadDrafts() { return read(DRAFTS_KEY, {}); }
  function reviewedList(marks) {
    var out = [];
    for (var ref in marks) if (Object.prototype.hasOwnProperty.call(marks, ref)) out.push(marks[ref]);
    return out;
  }
  // Text typed in a page's whole-record box counts as that page's whole-record comment, Add or not.
  function draftComments() {
    var drafts = loadDrafts();
    var out = [];
    for (var r in drafts) {
      if (!Object.prototype.hasOwnProperty.call(drafts, r)) continue;
      var d = drafts[r];
      if (!d || typeof d !== "object") continue;
      out.push({ id: "draft:" + r, draft: true, ref: r, title: d.title, page: d.page, anchor: "", anchorText: "", kind: "record", quote: "", note: d.note, created: d.created });
    }
    return out;
  }
  function allComments() { return loadComments().concat(draftComments()); }
  function newId() {
    return Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
  }
  function hasNote(c) { return String(c.note || "").trim() !== ""; }
  function newest(a, b) {
    return a.created < b.created ? 1 : a.created > b.created ? -1 : a.id < b.id ? 1 : a.id > b.id ? -1 : 0;
  }
  function localDate() {
    var d = new Date();
    function two(n) { return (n < 10 ? "0" : "") + n; }
    return d.getFullYear() + "-" + two(d.getMonth() + 1) + "-" + two(d.getDate());
  }

  var labelsEl = document.querySelector(".rv, .ob");
  function label(name) {
    return labelsEl ? labelsEl.getAttribute("data-" + name) || "" : "";
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
  var status = document.getElementById("status");
  var statusTimer = null;
  function announce(text) {
    if (!status) return;
    status.textContent = text;
    clearTimeout(statusTimer);
    statusTimer = setTimeout(function () { status.textContent = ""; }, 2000);
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
  function setCount(node, n) {
    if (node) node.textContent = n > 0 ? String(n) : "";
  }

  var article = document.querySelector("article[data-ref]");
  var ref = article && article.getAttribute("data-ref");
  var panel = article && document.querySelector(".rv");
  var outbox = document.querySelector(".ob");

  function counts() {
    var comments = allComments().filter(hasNote);
    var marks = loadReviewed();
    var total = comments.length + reviewedList(marks).length;
    var link = document.querySelector(".outbox");
    if (link) setCount(link.querySelector(".n"), total);
    var btn = document.querySelector(".rv-btn");
    if (btn && ref) {
      var own = comments.filter(function (c) { return c.ref === ref; }).length;
      setCount(btn.querySelector(".n"), own + (marks[ref] ? 1 : 0));
    }
  }

  // Pending note edits, written on a short timer and on leaving the page.
  var pendingNotes = {};
  var pendingDraft = null;
  var flushTimer = null;
  function flush() {
    clearTimeout(flushTimer);
    flushTimer = null;
    var ids = Object.keys(pendingNotes);
    if (ids.length) {
      var list = loadComments();
      list.forEach(function (c) {
        if (Object.prototype.hasOwnProperty.call(pendingNotes, c.id)) c.note = pendingNotes[c.id];
      });
      pendingNotes = {};
      write(KEY, list);
    }
    if (pendingDraft !== null && ref) {
      var drafts = loadDrafts();
      if (pendingDraft.trim()) drafts[ref] = { note: pendingDraft, title: article.getAttribute("data-title"), page: article.getAttribute("data-page"), created: new Date().toISOString() };
      else delete drafts[ref];
      pendingDraft = null;
      write(DRAFTS_KEY, drafts);
    }
    counts();
  }
  function schedule() {
    clearTimeout(flushTimer);
    flushTimer = setTimeout(flush, 300);
  }
  window.addEventListener("pagehide", flush);
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") flush();
  });

  function addComment(fields) {
    flush();
    var list = loadComments();
    var c = { id: newId(), created: new Date().toISOString() };
    for (var k in fields) if (Object.prototype.hasOwnProperty.call(fields, k)) c[k] = fields[k];
    list.push(c);
    write(KEY, list);
    return c;
  }
  function removeComment(id) {
    flush();
    write(KEY, loadComments().filter(function (c) { return c.id !== id; }));
  }

  function copyText(text, done) {
    function fallback() {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.top = "0";
      area.style.left = "-9999px";
      document.body.appendChild(area);
      area.select();
      var ok = false;
      try {
        ok = document.execCommand("copy");
      } catch (e) {}
      document.body.removeChild(area);
      done(ok);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
    } else fallback();
  }

  var renderOutbox = function () {};
  var renderPanel = function () {};
  if (outbox) setupOutbox();
  if (panel && article) setupPanel();
  counts();
  window.addEventListener("storage", function (e) {
    if (e.key !== null && e.key !== KEY && e.key !== REVIEWED_KEY && e.key !== DRAFTS_KEY) return;
    counts();
    if (outbox) renderOutbox();
    if (panel && !panel.contains(document.activeElement)) renderPanel();
  });

  function setupOutbox() {
    var host = outbox.querySelector(".ob-groups");
    var copy = outbox.querySelector(".ob-copy");
    var clear = outbox.querySelector(".ob-clear");
    var empty = outbox.querySelector(".cmt-empty");
    var confirmBox = outbox.querySelector(".ob-confirm");
    function itemCount(groups) {
      return groups.reduce(function (n, g) { return n + g.items.length; }, 0);
    }
    function current() {
      return window.SpecsComments.groups(allComments(), siteRoot, reviewedList(loadReviewed()));
    }
    renderOutbox = function () {
      var groups = current();
      host.textContent = "";
      groups.forEach(function (g) {
        var section = el("section", "ob-group");
        var head = el("div", "ob-row ob-head");
        head.appendChild(el("pre", "ob-text", g.heading));
        var open = el("a", "ob-open", label("open"));
        open.href = prefix + g.page;
        head.appendChild(open);
        section.appendChild(head);
        g.items.forEach(function (item) {
          var row = el("div", "ob-row");
          row.appendChild(el("pre", "ob-text", item.text));
          var ops = el("div", "ob-ops");
          if (item.kind === "comment") {
            var c = item.comment;
            var to = el("a", "ob-open", label("open"));
            to.href = prefix + c.page + (c.anchor ? "#" + encodeURIComponent(c.anchor) : "");
            ops.appendChild(to);
          }
          ops.appendChild(button("ob-del", label("delete"), function () {
            if (item.kind === "comment" && item.comment.draft) {
              var drafts = loadDrafts();
              delete drafts[item.comment.ref];
              write(DRAFTS_KEY, drafts);
            } else if (item.kind === "comment") removeComment(item.comment.id);
            else {
              var marks = loadReviewed();
              delete marks[g.ref];
              write(REVIEWED_KEY, marks);
            }
            renderOutbox();
            counts();
            announce(label("deleted"));
          }));
          row.appendChild(ops);
          section.appendChild(row);
        });
        host.appendChild(section);
      });
      var n = itemCount(groups);
      copy.disabled = !n;
      clear.disabled = !n;
      if (!n) confirmBox.hidden = true;
      empty.hidden = n > 0;
    };
    copy.addEventListener("click", function () {
      var groups = current();
      var n = itemCount(groups);
      if (!n) return;
      copyText(window.SpecsComments.format(allComments(), siteRoot, reviewedList(loadReviewed())), function (ok) {
        announce(ok ? plural("copied-forms", n) : label("copy-failed"));
      });
    });
    var yes = outbox.querySelector(".ob-clear-yes");
    var no = outbox.querySelector(".ob-clear-no");
    clear.addEventListener("click", function () {
      confirmBox.hidden = false;
      no.focus();
    });
    no.addEventListener("click", function () {
      confirmBox.hidden = true;
      clear.focus();
    });
    yes.addEventListener("click", function () {
      var n = itemCount(current());
      confirmBox.hidden = true;
      try {
        localStorage.removeItem(KEY);
        localStorage.removeItem(REVIEWED_KEY);
        localStorage.removeItem(DRAFTS_KEY);
      } catch (e) {}
      renderOutbox();
      counts();
      announce(plural("cleared-forms", n));
      var h = document.querySelector("main h1");
      h.setAttribute("tabindex", "-1");
      h.focus();
    });
    renderOutbox();
  }

  function setupPanel() {
    var body = article.querySelector(".body");
    var aside = document.getElementById("rv-panel");
    var list = panel.querySelector(".rv-list");
    var reviewedBox = panel.querySelector("#rv-reviewed");
    var draftArea = panel.querySelector("#rv-new");
    var addBtn = panel.querySelector(".rv-add");
    var openBtn = document.querySelector(".rv-btn");
    var closeBtn = panel.querySelector(".rv-close");
    var narrow = window.matchMedia("(max-width: 1099px)");
    var title = article.getAttribute("data-title");
    var page = article.getAttribute("data-page");

    // Quote lookup ignores whitespace: a selection's text and the DOM's text nodes break lines differently.
    var chars = [];
    var flat = "";
    (function index() {
      var walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
      var parts = [];
      for (var node = walker.nextNode(); node; node = walker.nextNode()) {
        var data = node.data;
        for (var i = 0; i < data.length; i++) {
          if (/\s/.test(data[i])) continue;
          chars.push({ node: node, offset: i });
          parts.push(data[i]);
        }
      }
      flat = parts.join("");
    })();
    function strip(text) { return String(text || "").replace(/\s+/g, ""); }
    function occurrences(needle) {
      var at = [];
      if (!needle) return at;
      for (var i = flat.indexOf(needle); i !== -1; i = flat.indexOf(needle, i + 1)) at.push(i);
      return at;
    }
    function locate(c) {
      var needle = strip(c.quote);
      var found = occurrences(needle);
      if (!found.length) return null;
      var start = found[Math.min(c.at || 0, found.length - 1)];
      var first = chars[start];
      var last = chars[start + needle.length - 1];
      var range = document.createRange();
      range.setStart(first.node, first.offset);
      range.setEnd(last.node, last.offset + 1);
      return range;
    }
    function occurrenceOf(range, quote) {
      var before = document.createRange();
      before.setStart(body, 0);
      before.setEnd(range.startContainer, range.startOffset);
      var offset = strip(before.toString()).length;
      return occurrences(strip(quote)).filter(function (i) { return i < offset; }).length;
    }

    var HEADS = "h2[id], h3[id], h4[id]";
    function headingText(h) {
      var clone = h.cloneNode(true);
      var extra = clone.querySelectorAll("a.anchor");
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

    var highlights = typeof CSS !== "undefined" && CSS.highlights && typeof Highlight === "function";
    var ranges = {};
    function paintHighlights(activeId) {
      if (!highlights) return;
      var all = new Highlight();
      var active = new Highlight();
      for (var id in ranges) {
        if (!ranges[id]) continue;
        if (id === activeId) active.add(ranges[id]);
        else all.add(ranges[id]);
      }
      CSS.highlights.set("rv", all);
      CSS.highlights.set("rv-on", active);
    }
    function scrollToRange(range) {
      var target = range.startContainer.parentElement;
      if (narrow.matches) closeSheet(false);
      target.scrollIntoView({ block: "center" });
      target.classList.add("rv-flash");
      setTimeout(function () { target.classList.remove("rv-flash"); }, 1600);
    }

    function isOpen() { return root.classList.contains("rv-sheet-open"); }
    function openSheet() {
      if (!narrow.matches || isOpen()) return;
      root.classList.add("rv-sheet-open");
      if (openBtn) openBtn.setAttribute("aria-expanded", "true");
    }
    function closeSheet(refocus) {
      if (!isOpen()) return;
      root.classList.remove("rv-sheet-open");
      if (openBtn) {
        openBtn.setAttribute("aria-expanded", "false");
        if (refocus) openBtn.focus();
      }
    }
    if (openBtn) openBtn.addEventListener("click", function () {
      if (isOpen()) closeSheet(true);
      else {
        openSheet();
        draftArea.focus();
      }
    });
    closeBtn.addEventListener("click", function () { closeSheet(true); });
    var scrim = el("div", "rv-scrim");
    scrim.addEventListener("click", function () { closeSheet(true); });
    aside.parentNode.insertBefore(scrim, aside);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) closeSheet(true);
    });
    narrow.addEventListener("change", function () { if (!narrow.matches) closeSheet(false); });

    function focusCard(id) {
      var area = list.querySelector(".rv-card[data-id='" + id + "'] textarea");
      if (area) area.focus();
    }
    function dropIfEmpty(id, area) {
      // Leaving a card with no note discards it: a selection made only to copy text leaves nothing behind.
      setTimeout(function () {
        if (!document.hasFocus() || area.value.trim() || document.activeElement === area) return;
        delete pendingNotes[id];
        removeComment(id);
        renderPanel();
        counts();
      }, 0);
    }

    function card(c) {
      var li = el("li", "rv-card");
      li.setAttribute("data-id", c.id);
      var where = el("div", "rv-where");
      if (c.anchor) {
        var a = el("a", "rv-anchor", "§ " + c.anchorText);
        a.href = "#" + encodeURIComponent(c.anchor);
        where.appendChild(a);
      } else where.appendChild(el("span", "rv-anchor", label("whole")));
      li.appendChild(where);
      if (c.quote) {
        var range = locate(c);
        ranges[c.id] = range;
        if (range) {
          var q = button("rv-quote", c.quote, function () { scrollToRange(locate(c) || range); });
          li.appendChild(q);
        } else {
          li.appendChild(el("blockquote", "rv-quote", c.quote));
          li.appendChild(el("p", "rv-changed", label("changed")));
        }
      }
      var fieldId = "rv-note-" + c.id;
      var lab = el("label", "vh", label("note"));
      lab.setAttribute("for", fieldId);
      li.appendChild(lab);
      var area = el("textarea", "rv-note");
      area.id = fieldId;
      area.rows = 2;
      area.value = c.note || "";
      area.addEventListener("input", function () {
        pendingNotes[c.id] = area.value;
        schedule();
      });
      area.addEventListener("focus", function () {
        li.classList.add("on");
        paintHighlights(c.id);
      });
      area.addEventListener("blur", function () {
        li.classList.remove("on");
        paintHighlights(null);
        flush();
        dropIfEmpty(c.id, area);
      });
      li.appendChild(area);
      var ops = el("div", "rv-ops");
      ops.appendChild(button("rv-del", label("delete"), function () {
        var cards = Array.prototype.slice.call(list.querySelectorAll(".rv-card"));
        var at = cards.indexOf(li);
        delete pendingNotes[c.id];
        removeComment(c.id);
        renderPanel();
        counts();
        announce(label("deleted"));
        var next = list.querySelectorAll(".rv-card textarea")[at];
        (next || draftArea).focus();
      }));
      li.appendChild(ops);
      li.addEventListener("click", function (e) {
        if (e.target.closest("a, button, textarea")) return;
        area.focus();
      });
      return li;
    }

    renderPanel = function () {
      var own = loadComments().filter(function (c) { return c.ref === ref; }).sort(newest);
      ranges = {};
      list.textContent = "";
      own.forEach(function (c) { list.appendChild(card(c)); });
      if (reviewedBox) reviewedBox.checked = !!loadReviewed()[ref];
      var draft = loadDrafts()[ref];
      if (document.activeElement !== draftArea) draftArea.value = (draft && draft.note) || "";
      addBtn.disabled = !draftArea.value.trim();
      paintHighlights(null);
    };

    if (reviewedBox) reviewedBox.addEventListener("change", function () {
      var marks = loadReviewed();
      if (reviewedBox.checked) marks[ref] = { ref: ref, title: title, page: page, date: localDate(), created: new Date().toISOString() };
      else delete marks[ref];
      write(REVIEWED_KEY, marks);
      counts();
    });
    draftArea.addEventListener("input", function () {
      pendingDraft = draftArea.value;
      addBtn.disabled = !draftArea.value.trim();
      schedule();
    });
    function addDraft() {
      if (!draftArea.value.trim()) return;
      var note = draftArea.value;
      draftArea.value = "";
      pendingDraft = "";
      addComment({ ref: ref, title: title, page: page, anchor: "", anchorText: "", kind: "record", quote: "", note: note });
      renderPanel();
      counts();
      draftArea.focus();
    }
    addBtn.addEventListener("click", addDraft);
    draftArea.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        addDraft();
      }
    });

    var captured = null;
    function capture() {
      var sel = window.getSelection();
      if (!sel || !sel.rangeCount || sel.isCollapsed) {
        captured = null;
        return;
      }
      var range = sel.getRangeAt(0);
      var text = sel.toString();
      if (!body.contains(range.commonAncestorContainer) || !text.trim()) return;
      var key = text + "\u0000" + occurrenceOf(range, text);
      if (key === captured) return;
      captured = key;
      var where = anchorFor(range.startContainer);
      var c = addComment({
        ref: ref,
        title: title,
        page: page,
        anchor: where.anchor,
        anchorText: where.anchorText,
        kind: "span",
        quote: text,
        at: occurrenceOf(range, text),
        note: ""
      });
      renderPanel();
      openSheet();
      focusCard(c.id);
    }
    var pointer = "mouse";
    var down = false;
    var touchTimer = null;
    document.addEventListener("pointerdown", function (e) {
      pointer = e.pointerType || "mouse";
      down = pointer !== "touch";
    });
    document.addEventListener("pointerup", function () {
      if (!down) return;
      down = false;
      setTimeout(capture, 0);
    });
    document.addEventListener("keyup", function (e) {
      if (e.key === "Shift") capture();
    });
    // Touch selections settle through their handles, with no pointerup on the page.
    document.addEventListener("selectionchange", function () {
      if (pointer !== "touch") return;
      clearTimeout(touchTimer);
      touchTimer = setTimeout(capture, 700);
    });

    renderPanel();
  }
})();
