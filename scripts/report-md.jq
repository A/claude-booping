# Markdown run report for `just eval-md` — status, per-check reasons, and the output artifact
# of every test case.
def checkname: (.assertion.value // "" | tostring) as $v
  | if $v | test("^[A-Z-]+:") then ($v | capture("^(?<n>[A-Z-]+):").n)
    else .assertion.type end;
.results.stats as $s
| "# \(.config.description // "eval run")",
  "",
  "**\(if ($s.failures + ($s.errors // 0)) == 0 then "✅ PASS" else "❌ FAILED" end)** — \($s.successes) passed, \($s.failures) failed\(if ($s.errors // 0) > 0 then ", \($s.errors) errored" else "" end)",
  "",
  (.results.results[]
    | "## \(if .gradingResult.pass then "✓" else "✗" end) \(.testCase.description // "test")",
      "",
      (.gradingResult.componentResults[]?
        | "- \(if .pass then "✓" else "✗" end) **\(checkname)** — \(.reason)"),
      "",
      "### Output",
      "",
      "`````markdown",
      (.response.output // "(no output)"),
      "`````",
      "")
