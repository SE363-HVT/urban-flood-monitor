# -*- coding: utf-8 -*-
"""Backward-compatibility shim. Target implementation: scripts.dataset.enrich_master_v3_to_10k"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.dataset.enrich_master_v3_to_10k import *

if __name__ == "__main__":
    import runpy
    runpy.run_module("scripts.dataset.enrich_master_v3_to_10k", run_name="__main__")
