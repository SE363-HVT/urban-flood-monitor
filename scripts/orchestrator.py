# -*- coding: utf-8 -*-
"""Backward-compatibility shim. Target implementation: scripts.pipeline.orchestrator"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.pipeline.orchestrator import *

if __name__ == "__main__":
    import runpy
    runpy.run_module("scripts.pipeline.orchestrator", run_name="__main__")
