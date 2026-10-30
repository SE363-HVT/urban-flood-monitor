# -*- coding: utf-8 -*-
"""Backward-compatibility shim. Target implementation: scripts.dataset.finalize_master_10k_clean"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.dataset.finalize_master_10k_clean import *

if __name__ == "__main__":
    import runpy
    runpy.run_module("scripts.dataset.finalize_master_10k_clean", run_name="__main__")
