from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from booping.context import Context
from booping.rendering import find_plugin_root

if TYPE_CHECKING:
    import argparse


def handle(args: argparse.Namespace) -> int:
    _ = args
    plugin_root = find_plugin_root(str(Path.cwd()))
    ctx = Context.assemble(plugin_root)
    print(yaml.dump(ctx.model_dump(mode="json"), default_flow_style=False))
    return 0