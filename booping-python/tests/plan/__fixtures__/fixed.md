# Demo plan

## Context

Some context.

## Milestones

### M01 — Parser core
sp: 3
depends_on: []

#### Tasks

| Task | Description |
|------|-------------|
| 1.1 | Write `src/a.py` |

#### Definition of Done

- [ ] parser exists

#### References

- `src/b.py`

#### Verify

```
pytest tests/a_test.py
```

### M02 — CLI wiring
sp: 2
depends_on: [M01]

#### Tasks

- wire `src/cli.py`

#### Definition of Done

- [ ] cli runs

#### References

#### Verify

`booping --help`

## Final Verification

- [ ] all green
