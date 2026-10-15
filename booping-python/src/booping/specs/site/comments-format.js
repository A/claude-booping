(function () {
  function cmp(a, b) {
    return a < b ? -1 : a > b ? 1 : 0;
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
  function formatComments(comments, siteRoot) {
    var byRef = {};
    var refs = [];
    for (var i = 0; i < comments.length; i++) {
      var c = comments[i];
      if (!Object.prototype.hasOwnProperty.call(byRef, c.ref)) {
        byRef[c.ref] = [];
        refs.push(c.ref);
      }
      byRef[c.ref].push(c);
    }
    refs.sort(cmp);
    var parts = [];
    for (var r = 0; r < refs.length; r++) {
      var list = byRef[refs[r]].slice().sort(function (a, b) {
        return cmp(a.created, b.created) || cmp(a.id, b.id);
      });
      parts.push("## " + refs[r] + " — " + list[0].title);
      for (var j = 0; j < list.length; j++) {
        parts.push(anchorLine(list[j], siteRoot));
        var quote = quoteBlock(list[j].quote);
        if (quote) parts.push(quote);
        var note = String(list[j].note || "").replace(/\s+$/, "");
        if (note) parts.push(note);
      }
    }
    return parts.length ? parts.join("\n\n") + "\n" : "";
  }
  globalThis.SpecsComments = { format: formatComments };
})();
