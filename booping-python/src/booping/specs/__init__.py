# booping.context imports booping.specs.rules, and the specs modules import booping.context
# submodules; loading the context package first keeps the cycle resolvable from either entry.
import booping.context  # noqa: F401  # pyright: ignore[reportUnusedImport]
