# -*- coding: utf-8 -*-
"""Backward-compatibility shim. Target implementation: scripts.crawlers.append_new_social_crawl"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.crawlers.append_new_social_crawl import *

if __name__ == "__main__":
    import runpy
    runpy.run_module("scripts.crawlers.append_new_social_crawl", run_name="__main__")
