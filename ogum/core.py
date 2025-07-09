"""Compatibility layer exposing core classes and constants."""

from .utils import R, SinteringDataRecord, DataHistory

__all__ = ["R", "SinteringDataRecord", "DataHistory"]

import sys
# Provide backward compatible module name 'core'
sys.modules.setdefault('core', sys.modules[__name__])
