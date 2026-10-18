---
step: "groom/draft-plan"
asked: "How does the eval suite assert v3?"
decision: "smoke: zero tool calls + JSON contract; regress: exact route, alt_score
  ±1 on kept, 0019<0003 order, llm-rubric judge that missing names each mutant's cut
  option"
why: "Experiment: the list, not the score, is the signal; repo convention smoke deterministic,
  regress judged"
state: reviewed
session: "0c3f5735-fd95-5891-a767-80fb60a7872b"
logged_at: "2026-10-19 03:12"
artifact: "plans/202610190307_adr-scorer-v3/index.md"
---
