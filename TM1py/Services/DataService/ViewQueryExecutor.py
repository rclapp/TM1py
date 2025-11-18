# -*- coding: utf-8 -*-
"""
ViewQueryExecutor - Fluent interface for executing cube view queries.

Provides a fluent interface for executing cube view queries with various output formats
and options.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from TM1py.Services.DataService.Mixins import (
    AsyncMixin,
    FilterMixin,
    PaginationMixin,
    PerformanceMixin,
    SandboxMixin,
)
from TM1py.Utils import CaseAndSpaceInsensitiveTuplesDict

if TYPE_CHECKING:
    import pandas as pd
    from TM1py.Services.CellService import CellService


try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


class ViewQueryExecutor(SandboxMixin, FilterMixin, PerformanceMixin, PaginationMixin, AsyncMixin):
    """
    Fluent interface for executing cube view queries with options.
    
    Supports method chaining for options and multiple terminal operations for different output formats.
    
    Example usage:
        # Get as dictionary
        result = tm1.data.view('Sales', 'Budget').skip_zeros().as_dict()
        
        # Get as DataFrame with options
        df = tm1.data.view('Sales', 'Budget', private=True).sandbox('dev').as_dataframe()
        
        # Get as CSV
        csv = tm1.data.view('Sales', 'Budget').skip_consolidated().as_csv()
        
        # Get values only
        values = tm1.data.view('Sales', 'Budget').as_values()
        
        # Get cell count
        count = tm1.data.view('Sales', 'Budget').count()
    """
    
    def __init__(self, cell_service: "CellService", cube_name: str, view_name: str, private: bool = False):
        """
        Initialize ViewQueryExecutor.
        
        :param cell_service: CellService instance for delegation
        :param cube_name: Name of the cube
        :param view_name: Name of the view
        :param private: Whether the view is private (default: False)
        """
        # Initialize all mixins
        SandboxMixin.__init__(self)
        FilterMixin.__init__(self)
        PerformanceMixin.__init__(self)
        PaginationMixin.__init__(self)
        AsyncMixin.__init__(self)
        
        self._cell_service = cell_service
        self._cube_name = cube_name
        self._view_name = view_name
        self._private = private
    
    def as_dict(self, **kwargs) -> CaseAndSpaceInsensitiveTuplesDict:
        """
        Execute view query and return results as a dictionary.

        Terminal operation - executes the query and returns results.

        When max_workers > 1, the query will be executed in parallel.

        :param kwargs: Additional parameters to pass to CellService.execute_view()
        :return: Dictionary with cell coordinates and values
        """
        return self._cell_service.execute_view(
            cube_name=self._cube_name,
            view_name=self._view_name,
            private=self._private,
            top=self._top,
            skip=self._skip,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            sandbox_name=self._sandbox_name,
            use_compact_json=self._use_compact_json,
            max_workers=self._max_workers,
            async_axis=self._async_axis,
            **kwargs,
        )
    
    def as_dataframe(
        self,
        shaped: bool = False,
        arranged_axes: Optional[Tuple[List, List, List]] = None,
        mdx_headers: bool = False,
        **kwargs,
    ) -> "pd.DataFrame":
        """
        Execute view query and return results as a pandas DataFrame.
        
        Terminal operation - executes the query and returns results.
        
        :param shaped: Return shaped DataFrame (default: False)
        :param arranged_axes: Tuple of (cube, rows, columns) for arranged axes
        :param mdx_headers: Use MDX headers (default: False)
        :param kwargs: Additional parameters to pass to CellService.execute_view_dataframe()
        :return: pandas DataFrame with query results
        """
        return self._cell_service.execute_view_dataframe(
            cube_name=self._cube_name,
            view_name=self._view_name,
            private=self._private,
            top=self._top,
            skip=self._skip,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            sandbox_name=self._sandbox_name,
            use_iterative_json=self._use_iterative_json,
            use_blob=self._use_blob,
            shaped=shaped,
            arranged_axes=arranged_axes,
            mdx_headers=mdx_headers,
            **kwargs,
        )
    
    def as_csv(
        self,
        line_separator: str = "\r\n",
        value_separator: str = ",",
        arranged_axes: Optional[Tuple[List, List, List]] = None,
        mdx_headers: bool = False,
        **kwargs,
    ) -> str:
        """
        Execute view query and return results as CSV string.
        
        Terminal operation - executes the query and returns results.
        
        :param line_separator: Line separator for CSV output (default: "\\r\\n")
        :param value_separator: Value separator for CSV output (default: ",")
        :param arranged_axes: Tuple of (cube, rows, columns) for arranged axes
        :param mdx_headers: Use MDX headers (default: False)
        :param kwargs: Additional parameters to pass to CellService.execute_view_csv()
        :return: CSV string with query results
        """
        return self._cell_service.execute_view_csv(
            cube_name=self._cube_name,
            view_name=self._view_name,
            private=self._private,
            top=self._top,
            skip=self._skip,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            line_separator=line_separator,
            value_separator=value_separator,
            sandbox_name=self._sandbox_name,
            use_iterative_json=self._use_iterative_json,
            use_compact_json=self._use_compact_json,
            use_blob=self._use_blob,
            arranged_axes=arranged_axes,
            mdx_headers=mdx_headers,
            **kwargs,
        )
    
    def as_values(self, **kwargs) -> List[Union[str, float]]:
        """
        Execute view query and return only the cell values (no coordinates).
        
        Terminal operation - executes the query and returns results.
        Optimized for performance when only values are needed.
        
        :param kwargs: Additional parameters to pass to CellService.execute_view_values()
        :return: List of cell values
        """
        return self._cell_service.execute_view_values(
            cube_name=self._cube_name,
            view_name=self._view_name,
            private=self._private,
            sandbox_name=self._sandbox_name,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            use_compact_json=self._use_compact_json,
            **kwargs,
        )
    
    def count(self, **kwargs) -> int:
        """
        Execute view query and return the number of cells in the result.
        
        Terminal operation - executes the query and returns cell count.
        Optimized for performance - does not retrieve cell data.
        
        :param kwargs: Additional parameters to pass to CellService.execute_view_cellcount()
        :return: Number of cells in the result
        """
        return self._cell_service.execute_view_cellcount(
            cube_name=self._cube_name,
            view_name=self._view_name,
            private=self._private,
            sandbox_name=self._sandbox_name,
            **kwargs,
        )
    
    def as_raw(
        self,
        elem_properties: Optional[List[str]] = None,
        member_properties: Optional[List[str]] = None,
        skip_contexts: bool = False,
        **kwargs,
    ) -> Dict:
        """
        Execute view query and return the raw TM1 response.
        
        Terminal operation - executes the query and returns raw JSON from TM1.
        Useful for custom processing, debugging, or when you need full metadata.
        
        :param elem_properties: Element properties to include in response
        :param member_properties: Member properties to include in response
        :param skip_contexts: Skip context information in response
        :param kwargs: Additional parameters to pass to CellService.execute_view_raw()
        :return: Raw TM1 response dictionary with Axes, Cells, and metadata
        """
        return self._cell_service.execute_view_raw(
            cube_name=self._cube_name,
            view_name=self._view_name,
            private=self._private,
            elem_properties=elem_properties,
            member_properties=member_properties,
            top=self._top,
            skip=self._skip,
            skip_contexts=skip_contexts,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            sandbox_name=self._sandbox_name,
            use_compact_json=self._use_compact_json,
            **kwargs,
        )
    
    def as_cellset_id(self, **kwargs) -> str:
        """
        Execute view query and return the cellset ID.
        
        Terminal operation - creates a cellset on the TM1 server and returns its ID.
        The cellset remains on the server for manual operations.
        
        ⚠️ WARNING: You must manually delete the cellset using tm1.cells.delete_cellset(cellset_id)
        to avoid memory leaks on the TM1 server.
        
        :param kwargs: Additional parameters to pass to CellService.create_cellset_from_view()
        :return: Cellset ID string
        """
        return self._cell_service.create_cellset_from_view(
            cube_name=self._cube_name,
            view_name=self._view_name,
            private=self._private,
            sandbox_name=self._sandbox_name,
            **kwargs,
        )

