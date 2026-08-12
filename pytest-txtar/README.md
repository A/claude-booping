# pytest-txtar

Contract testing for command-line tools, driven by [txtar](https://pkg.go.dev/golang.org/x/tools/txtar)
archives: one file per case carrying the fixture tree, the invocation, and everything asserted about
the result — stdout, stderr, exit code, and files left behind.

Each case runs in a fresh sandbox; paths that vary per run are normalized to tokens before
comparison, and a golden-update flow rewrites assertions from the actual run.

The package is layered: `pytest_txtar.txtar` parses the archive format, the pytest-free core
(`case`, `sandbox`, `compare`, `update`) executes and compares cases parameterized by a
`TxtarSpec`, and a pytest plugin collects `*.txtar` files as test items.

Status: pre-release, under construction.

## License

MIT. `src/pytest_txtar/txtar.py` is a port of `golang.org/x/tools/txtar` and carries the upstream
BSD-3-Clause notice — see [LICENSE](LICENSE).
