# -*- coding: utf-8 -*-
"""Backward-compatibility shim. Target implementation: scripts.figures.generate_full_stats_v3"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.figures.generate_full_stats_v3 import *

if __name__ == "__main__":
    import runpy
    runpy.run_module("scripts.figures.generate_full_stats_v3", run_name="__main__")
