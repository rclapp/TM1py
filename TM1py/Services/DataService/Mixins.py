# -*- coding: utf-8 -*-
"""
Mixin classes for DataService builders to enable code reuse and fluent interface.
Each mixin provides a specific set of options that can be chained together.
"""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
else:
    try:
        from typing import Self
    except ImportError:
        from typing_extensions import Self


class SandboxMixin:
    """Mixin to add sandbox context support to builders."""
    
    def __init__(self):
        self._sandbox_name: Optional[str] = None
    
    def sandbox(self, sandbox_name: str) -> Self:
        """Execute query in the context of a specific sandbox.
        
        :param sandbox_name: Name of the sandbox
        :return: Self for method chaining
        """
        self._sandbox_name = sandbox_name
        return self


class FilterMixin:
    """Mixin to add cell filtering options to builders."""
    
    def __init__(self):
        self._skip_zeros: bool = False
        self._skip_consolidated_cells: bool = False
        self._skip_rule_derived_cells: bool = False
    
    def skip_zeros(self, skip: bool = True) -> Self:
        """Skip cells with zero values.
        
        :param skip: Whether to skip zeros (default: True)
        :return: Self for method chaining
        """
        self._skip_zeros = skip
        return self
    
    def skip_consolidated(self, skip: bool = True) -> Self:
        """Skip consolidated cells.
        
        :param skip: Whether to skip consolidated cells (default: True)
        :return: Self for method chaining
        """
        self._skip_consolidated_cells = skip
        return self
    
    def skip_rule_derived(self, skip: bool = True) -> Self:
        """Skip rule-derived cells.
        
        :param skip: Whether to skip rule-derived cells (default: True)
        :return: Self for method chaining
        """
        self._skip_rule_derived_cells = skip
        return self


class PerformanceMixin:
    """Mixin to add performance optimization options to builders."""
    
    def __init__(self):
        self._use_blob: bool = False
        self._use_compact_json: bool = False
        self._use_iterative_json: bool = False
    
    def use_blob(self, use: bool = True) -> Self:
        """Use blob (CSV) for faster data transfer (10x faster for large datasets).
        
        :param use: Whether to use blob (default: True)
        :return: Self for method chaining
        """
        self._use_blob = use
        return self
    
    def use_compact_json(self, use: bool = True) -> Self:
        """Use compact JSON format for better performance.
        
        :param use: Whether to use compact JSON (default: True)
        :return: Self for method chaining
        """
        self._use_compact_json = use
        return self
    
    def use_iterative_json(self, use: bool = True) -> Self:
        """Use iterative JSON parsing for lower memory footprint.
        
        :param use: Whether to use iterative JSON (default: True)
        :return: Self for method chaining
        """
        self._use_iterative_json = use
        return self


class PaginationMixin:
    """Mixin to add pagination support to builders."""
    
    def __init__(self):
        self._top: Optional[int] = None
        self._skip: Optional[int] = None
    
    def top(self, n: int) -> Self:
        """Limit the number of cells returned.
        
        :param n: Maximum number of cells to return
        :return: Self for method chaining
        """
        self._top = n
        return self
    
    def skip(self, n: int) -> Self:
        """Skip the first n cells.
        
        :param n: Number of cells to skip
        :return: Self for method chaining
        """
        self._skip = n
        return self


class AttributeMixin:
    """Mixin to add attribute handling options to builders."""
    
    def __init__(self):
        self._include_attributes: bool = False
        self._cell_properties: Optional[List[str]] = None
    
    def include_attributes(self, include: bool = True) -> Self:
        """Include element attributes in the result.
        
        :param include: Whether to include attributes (default: True)
        :return: Self for method chaining
        """
        self._include_attributes = include
        return self
    
    def cell_properties(self, properties: List[str]) -> Self:
        """Specify which cell properties to include.
        
        :param properties: List of cell property names
        :return: Self for method chaining
        """
        self._cell_properties = properties
        return self


class AsyncMixin:
    """Mixin to add async/parallel execution options to builders."""

    def __init__(self):
        self._max_workers: int = 1
        self._async_axis: int = 0

    def max_workers(self, n: int) -> Self:
        """
        Set the number of parallel workers for async execution.

        When max_workers > 1, the query will be executed in parallel by splitting
        the result set along the specified axis (rows or columns).

        :param n: Number of parallel workers (default: 1 for synchronous execution)
        :return: Self for method chaining

        Example:
            # Execute query with 8 parallel workers
            df = tm1.data.mdx(query).max_workers(8).as_dataframe()
        """
        self._max_workers = n
        return self

    def async_axis(self, axis: int) -> Self:
        """
        Set which axis to parallelize on when using max_workers > 1.

        :param axis: 0 for columns (default), 1 for rows
        :return: Self for method chaining

        Example:
            # Parallelize along rows instead of columns
            df = tm1.data.mdx(query).max_workers(8).async_axis(1).as_dataframe()
        """
        self._async_axis = axis
        return self


class WriteMixin:
    """Mixin to add write operation options to builders."""

    def __init__(self):
        self._increment: bool = False
        self._skip_non_updateable: bool = False
        self._use_ti: bool = False
        self._use_blob_write: bool = False
        self._use_cellset: bool = False
        self._allow_spread: bool = False
    
    def increment(self, inc: bool = True) -> Self:
        """Increment existing values instead of replacing them.
        
        :param inc: Whether to increment (default: True)
        :return: Self for method chaining
        """
        self._increment = inc
        return self
    
    def skip_non_updateable(self, skip: bool = True) -> Self:
        """Skip cells that cannot be updated (consolidated, rule-derived).
        
        :param skip: Whether to skip non-updateable cells (default: True)
        :return: Self for method chaining
        """
        self._skip_non_updateable = skip
        return self
    
    def use_ti(self, use: bool = True) -> Self:
        """Use TurboIntegrator process for writing (good for large writes).
        
        :param use: Whether to use TI (default: True)
        :return: Self for method chaining
        """
        if use:
            self._use_ti = True
            self._use_blob_write = False
            self._use_cellset = False
        else:
            self._use_ti = False
        return self
    
    def use_blob_write(self, use: bool = True) -> Self:
        """Use blob (CSV) for writing (10x faster for large datasets).
        
        :param use: Whether to use blob (default: True)
        :return: Self for method chaining
        """
        if use:
            self._use_blob_write = True
            self._use_ti = False
            self._use_cellset = False
        else:
            self._use_blob_write = False
        return self
    
    def use_cellset(self, use: bool = True) -> Self:
        """Use cellset for writing (default method).
        
        :param use: Whether to use cellset (default: True)
        :return: Self for method chaining
        """
        if use:
            self._use_cellset = True
            self._use_ti = False
            self._use_blob_write = False
        else:
            self._use_cellset = False
        return self
    
    def allow_spread(self, allow: bool = True) -> Self:
        """Allow spreading values to consolidated cells.
        
        :param allow: Whether to allow spread (default: True)
        :return: Self for method chaining
        """
        self._allow_spread = allow
        return self
