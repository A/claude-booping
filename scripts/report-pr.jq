# One plain-text block per eval suite, for the PR comment's single code fence: a header
# line, the tally, then one line per test case with its failing checks nested. No markdown
# — the whole comment is one fenced block, so anything structural would render literally.
# Invoked once per suite JSON with --arg suite <playbook>/<step>.
def oneline: gsub("[\r\n\t]+"; " ") | gsub(" +"; " ")
  | if (length > 240) then (.[0:240] + " …") else . end;

# A check's display name: the leading ALL-CAPS tag of a deterministic assert's value
# (MDCHECK:, FILES:, RETURN:), else the assertion type.
def checkname: (.assertion.value // "" | tostring) as $v
  | if $v | test("^[A-Z-]+:") then ($v | capture("^(?<n>[A-Z-]+):").n)
    else (.assertion.type // "assert") end;

def casename: (if (.testCase.metadata.tier // null) then "[\(.testCase.metadata.tier)] " else "" end)
  + ((.testCase.description // .testCase.vars.fixture // "test") | tostring);

.results.stats as $s
| "# \($suite)",
  "PASSED: \($s.successes), FAILED: \($s.failures)"
  + (if ($s.errors // 0) > 0 then ", ERRORED: \($s.errors)" else "" end),
  "",
  (.results.results[]
    | (if .gradingResult.pass then "PASS" else "FAIL" end) as $mark
    | "- \($mark): \(casename)",
      (if .error then "    - ERROR: \(.error | tostring | oneline)" else empty end),
      (if .gradingResult.pass then empty
       else (.gradingResult.componentResults[]?
              | select(.pass | not)
              | "    - FAIL: \(checkname) — \(.reason // "" | tostring | oneline)")
       end))
