# -*- coding: utf-8 -*-
"""
DataService - Fluent builder pattern for TM1 data operations.

This package provides a simplified, discoverable API for common data operations
as an alternative to the comprehensive CellService.
"""

from TM1py.Services.DataService.CoordinateQueryExecutor import CoordinateQueryExecutor
from TM1py.Services.DataService.DataService import DataService
from TM1py.Services.DataService.Mixins import (
    AsyncMixin,
    AttributeMixin,
    FilterMixin,
    PaginationMixin,
    PerformanceMixin,
    SandboxMixin,
    WriteMixin,
)
from TM1py.Services.DataService.QueryExecutor import QueryExecutor
from TM1py.Services.DataService.ViewQueryExecutor import ViewQueryExecutor

__all__ = [
    "DataService",
    "QueryExecutor",
    "ViewQueryExecutor",
    "CoordinateQueryExecutor",
    "AsyncMixin",
    "AttributeMixin",
    "FilterMixin",
    "PaginationMixin",
    "PerformanceMixin",
    "SandboxMixin",
    "WriteMixin",
]

