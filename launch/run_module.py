#!/usr/bin/env python3
"""Small launcher for compiled policy modules."""

import importlib
import sys

if len(sys.argv) < 2:
    raise SystemExit("usage: run_module.py MODULE [ARGS...]")
module_name = sys.argv.pop(1)
module = importlib.import_module(module_name)
raise SystemExit(module.main(sys.argv[1:]))
