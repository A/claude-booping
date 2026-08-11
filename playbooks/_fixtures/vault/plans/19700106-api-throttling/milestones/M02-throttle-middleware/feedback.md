**Blocked (1/2)**: `pytest tests/api/middleware_test.py` failed — an under-limit client was rejected once the window rolled over.

Checked the commit diff against the Definition of Done. The middleware resets its counter on the wrong boundary, so the first request of a new window inherits the previous window's count.

Next attempt: reset the counter against the window the request falls in, and cover the boundary case in `tests/api/middleware_test.py`.
