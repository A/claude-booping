(function () {
  function row(label, pressedCount, sortText) {
    return label + (pressedCount > 0 ? " (" + pressedCount + ")" : "") + " · " + sortText;
  }
  function removable(pressed, removeTemplate) {
    var out = [];
    for (var i = 0; i < pressed.length; i++) {
      var p = pressed[i];
      out.push({
        key: p.key,
        value: p.value,
        text: p.label,
        aria: removeTemplate.split("{label}").join(p.label)
      });
    }
    return out;
  }
  globalThis.SpecsFilters = { row: row, removable: removable };
})();
