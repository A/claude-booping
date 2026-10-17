(function () {
  function cmp(a, b) {
    return a < b ? -1 : a > b ? 1 : 0;
  }
  function own(obj, key) {
    return Object.prototype.hasOwnProperty.call(obj, key);
  }
  function encodeAnchor(id) {
    return id.replace(/%/g, "%25").replace(/ /g, "%20").replace(/\(/g, "%28").replace(/\)/g, "%29");
  }
  function anchorLine(c, siteRoot) {
    if (!c.anchor) return "[" + c.title + "](" + siteRoot + c.page + ")";
    return "[§ " + c.anchorText + "](" + siteRoot + c.page + "#" + encodeAnchor(c.anchor) + ")";
  }
  function quoteBlock(quote) {
    var lines = String(quote || "").split(/\r\n|\r|\n/);
    var out = [];
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (line) out.push("> " + line);
    }
    return out.join("\n");
  }
  function noteText(c) {
    return String(c.note || "").replace(/\s+$/, "");
  }
  function commentText(c, siteRoot) {
    var parts = [anchorLine(c, siteRoot)];
    var quote = quoteBlock(c.quote);
    if (quote) parts.push(quote);
    parts.push(noteText(c));
    return parts.join("\n\n");
  }
  // A comment without a note is a card still being written: it is not sent.
  function groups(comments, siteRoot, reviewed) {
    var byRef = {};
    var list = [];
    function group(ref, title, page) {
      if (!own(byRef, ref)) {
        byRef[ref] = { ref: ref, title: title, page: page, latest: "", reviewed: null, comments: [] };
        list.push(byRef[ref]);
      }
      return byRef[ref];
    }
    for (var i = 0; i < comments.length; i++) {
      var c = comments[i];
      if (!noteText(c).trim()) continue;
      var g = group(c.ref, c.title, c.page);
      g.comments.push(c);
      if (c.created > g.latest) g.latest = c.created;
    }
    var marks = reviewed || [];
    for (var m = 0; m < marks.length; m++) {
      var r = marks[m];
      var rg = group(r.ref, r.title, r.page);
      rg.reviewed = r;
      if (r.created > rg.latest) rg.latest = r.created;
    }
    list.sort(function (a, b) {
      return cmp(b.latest, a.latest) || cmp(a.ref, b.ref);
    });
    for (var k = 0; k < list.length; k++) {
      var gr = list[k];
      gr.comments.sort(function (a, b) {
        return cmp(b.created, a.created) || cmp(b.id, a.id);
      });
      gr.heading = "## " + gr.ref + " — " + gr.title;
      gr.items = [];
      if (gr.reviewed) gr.items.push({ kind: "reviewed", text: gr.ref + " — reviewed " + gr.reviewed.date });
      for (var j = 0; j < gr.comments.length; j++) {
        gr.items.push({ kind: "comment", comment: gr.comments[j], text: commentText(gr.comments[j], siteRoot) });
      }
    }
    return list;
  }
  function format(comments, siteRoot, reviewed) {
    var list = groups(comments, siteRoot, reviewed);
    var parts = [];
    for (var i = 0; i < list.length; i++) {
      parts.push(list[i].heading);
      for (var j = 0; j < list[i].items.length; j++) parts.push(list[i].items[j].text);
    }
    return parts.length ? parts.join("\n\n") + "\n" : "";
  }
  globalThis.SpecsComments = { format: format, groups: groups };
})();
