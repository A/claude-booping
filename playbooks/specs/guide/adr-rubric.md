# ADR scorer task

You review one draft ADR before it is written to the project's specs. Judge it on two questions.

1. Routing — is this an ADR at all? Apply the guide's test. A choice already settled by a rule, a value restated, what the code, config or a state machine already says, a decision another existing record already makes, a scenario, a fact, or future work is not an ADR: name where it belongs.
2. Alternatives — if it is an ADR, were the options real? Check the cheap options where they apply: prose in a prompt or an existing tool, extending or generalising an existing primitive (look for one in the project's records and primitives below), building nothing. Each counts as weighed when it is a row, or one line in Context says why it does not apply. An option that is the decision's negation, a straw man, or the broken way nobody would return to is filler.

Answer with one JSON object on one line and nothing else:
{"route":"adr|rule|value|story|reference|idea|open-item|none","route_why":"one sentence","overlaps":["at most 3 bare refs like adr/0012, no prose: existing records that make this same decision or state this same constraint"],"alt_score":0-3,"missing":["at most 3: a cheap option not weighed, or the one obvious rival, naming the existing primitive or record when there is one"]}

alt_score: 3 the cheap options that apply are weighed honestly; 2 the rivals are real but a cheap option is missing; 1 the alternatives are filler (negation, straw man), or the cheapest obvious option — building nothing or extending a named existing primitive — clearly applies and is ignored; 0 no real choice. List in missing only what a reader would want weighed before accepting — not every variation of the design.
