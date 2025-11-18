# -*- coding: utf-8 -*-
"""
QueryExecutor - Fluent interface for executing MDX queries.

Provides a fluent interface for executing MDX queries with various output formats
and options. Not to be confused with MdxBuilder (from mdxpy) which constructs MDX queries.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from mdxpy import MdxBuilder

from TM1py.Services.DataService.Mixins import (
    AsyncMixin,
    AttributeMixin,
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


class QueryExecutor(SandboxMixin, FilterMixin, PerformanceMixin, PaginationMixin, AttributeMixin, AsyncMixin):
    """
    Fluent interface for executing MDX queries with options.

    This class is for EXECUTING queries, not building them.
    Use MdxBuilder (from mdxpy) to BUILD/CONSTRUCT MDX query strings.

    Supports method chaining for options and multiple terminal operations for different output formats.

    Accepts both MDX query strings and MdxBuilder objects from mdxpy.

    Example usage:
        # With MDX string
        result = tm1.data.mdx("SELECT ...").skip_zeros().as_dict()

        # With MdxBuilder from mdxpy
        from mdxpy import MdxBuilder
        query = MdxBuilder.from_cube("Sales").add_hierarchy_set_to_row_axis(...)
        df = tm1.data.mdx(query).skip_zeros().use_blob().sandbox('dev').as_dataframe()

        # Get as CSV
        csv = tm1.data.mdx(query).skip_consolidated().as_csv()

        # Get values only
        values = tm1.data.mdx(query).as_values()

        # Get cell count
        count = tm1.data.mdx(query).count()
    """

    def __init__(self, cell_service: "CellService", mdx: Union[str, MdxBuilder]):
        """
        Initialize QueryExecutor.

        :param cell_service: CellService instance for delegation
        :param mdx: MDX query string or MdxBuilder object to execute
        """
        # Initialize all mixins
        SandboxMixin.__init__(self)
        FilterMixin.__init__(self)
        PerformanceMixin.__init__(self)
        PaginationMixin.__init__(self)
        AttributeMixin.__init__(self)
        AsyncMixin.__init__(self)

        self._cell_service = cell_service
        self._mdx = mdx
    
    def as_dict(self, **kwargs) -> CaseAndSpaceInsensitiveTuplesDict:
        """
        Execute MDX query and return results as a dictionary.

        Terminal operation - executes the query and returns results.

        When max_workers > 1, the query will be executed in parallel.

        :param kwargs: Additional parameters to pass to CellService.execute_mdx()
        :return: Dictionary with cell coordinates and values
        """
        mdx_string = self._mdx.to_mdx() if isinstance(self._mdx, MdxBuilder) else self._mdx
        return self._cell_service.execute_mdx(
            mdx=mdx_string,
            cell_properties=self._cell_properties,
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
    
    def as_dataframe(self, **kwargs) -> "pd.DataFrame":
        """
        Execute MDX query and return results as a pandas DataFrame.

        Terminal operation - executes the query and returns results.

        When max_workers > 1, the query will be executed in parallel.

        :param kwargs: Additional parameters to pass to CellService.execute_mdx_dataframe()
        :return: pandas DataFrame with query results
        """
        mdx_string = self._mdx.to_mdx() if isinstance(self._mdx, MdxBuilder) else self._mdx
        return self._cell_service.execute_mdx_dataframe(
            mdx=mdx_string,
            top=self._top,
            skip=self._skip,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            sandbox_name=self._sandbox_name,
            include_attributes=self._include_attributes,
            use_iterative_json=self._use_iterative_json,
            use_compact_json=self._use_compact_json,
            use_blob=self._use_blob,
            **kwargs,
        )
    
    def as_csv(
        self,
        line_separator: str = "\r\n",
        value_separator: str = ",",
        **kwargs,
    ) -> str:
        """
        Execute MDX query and return results as CSV string.
        
        Terminal operation - executes the query and returns results.
        
        :param line_separator: Line separator for CSV output (default: "\\r\\n")
        :param value_separator: Value separator for CSV output (default: ",")
        :param kwargs: Additional parameters to pass to CellService.execute_mdx_csv()
        :return: CSV string with query results
        """
        return self._cell_service.execute_mdx_csv(
            mdx=self._mdx,
            top=self._top,
            skip=self._skip,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            line_separator=line_separator,
            value_separator=value_separator,
            sandbox_name=self._sandbox_name,
            include_attributes=self._include_attributes,
            use_iterative_json=self._use_iterative_json,
            use_compact_json=self._use_compact_json,
            use_blob=self._use_blob,
            **kwargs,
        )
    
    def as_values(self, **kwargs) -> List[Union[str, float]]:
        """
        Execute MDX query and return only the cell values (no coordinates).
        
        Terminal operation - executes the query and returns results.
        Optimized for performance when only values are needed.
        
        :param kwargs: Additional parameters to pass to CellService.execute_mdx_values()
        :return: List of cell values
        """
        return self._cell_service.execute_mdx_values(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            use_compact_json=self._use_compact_json,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            **kwargs,
        )
    
    def as_pivot(
        self,
        dropna: bool = False,
        fill_value: Any = None,
        **kwargs,
    ) -> "pd.DataFrame":
        """
        Execute MDX query and return results as a pivot DataFrame.
        
        Terminal operation - executes the query and returns results.
        Returns data in the shape as specified in the MDX query.
        
        :param dropna: Drop rows/columns with all NaN values (default: False)
        :param fill_value: Value to use for missing data (default: None)
        :param kwargs: Additional parameters to pass to CellService.execute_mdx_dataframe_pivot()
        :return: pandas DataFrame in pivot format
        """
        return self._cell_service.execute_mdx_dataframe_pivot(
            mdx=self._mdx,
            dropna=dropna,
            fill_value=fill_value,
            sandbox_name=self._sandbox_name,
            **kwargs,
        )
    
    def count(self, **kwargs) -> int:
        """
        Execute MDX query and return the number of cells in the result.

        Terminal operation - executes the query and returns cell count.
        Optimized for performance - does not retrieve cell data.

        :param kwargs: Additional parameters to pass to CellService.execute_mdx_cellcount()
        :return: Number of cells in the result
        """
        return self._cell_service.execute_mdx_cellcount(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            **kwargs,
        )

    def as_raw(
        self,
        elem_properties: Optional[List[str]] = None,
        member_properties: Optional[List[str]] = None,
        skip_contexts: bool = False,
        include_hierarchies: bool = False,
        **kwargs,
    ) -> Dict:
        """
        Execute MDX query and return the raw TM1 response.

        Terminal operation - executes the query and returns raw JSON from TM1.
        Useful for custom processing, debugging, or when you need full metadata.

        :param elem_properties: Element properties to include in response
        :param member_properties: Member properties to include in response
        :param skip_contexts: Skip context information in response
        :param include_hierarchies: Include hierarchy information in response
        :param kwargs: Additional parameters to pass to CellService.execute_mdx_raw()
        :return: Raw TM1 response dictionary with Axes, Cells, and metadata

        Example usage:
            # Get raw response for custom processing
            raw = tm1.data.mdx(query).skip_zeros().as_raw()

            # Access raw structure
            axes = raw['Axes']
            cells = raw['Cells']
        """
        return self._cell_service.execute_mdx_raw(
            mdx=self._mdx,
            cell_properties=self._cell_properties,
            elem_properties=elem_properties,
            member_properties=member_properties,
            top=self._top,
            skip=self._skip,
            skip_contexts=skip_contexts,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            sandbox_name=self._sandbox_name,
            include_hierarchies=include_hierarchies,
            use_compact_json=self._use_compact_json,
            **kwargs,
        )

    def as_cellset_id(self, **kwargs) -> str:
        """
        Execute MDX query and return the cellset ID.

        Terminal operation - creates a cellset on the TM1 server and returns its ID.
        The cellset remains on the server for manual operations.

        ⚠️ WARNING: You must manually delete the cellset using tm1.cells.delete_cellset(cellset_id)
        to avoid memory leaks on the TM1 server.

        :param kwargs: Additional parameters to pass to CellService.create_cellset()
        :return: Cellset ID string

        Example usage:
            # Create cellset
            cellset_id = tm1.data.mdx(query).sandbox('dev').as_cellset_id()

            # Use cellset for multiple operations
            raw_data = tm1.cells.extract_cellset_raw(cellset_id)
            csv_data = tm1.cells.extract_cellset_csv(cellset_id)
            df = tm1.cells.extract_cellset_dataframe(cellset_id)

            # Clean up (IMPORTANT!)
            tm1.cells.delete_cellset(cellset_id)

        Use cases:
            - Reusing cellsets for multiple extractions
            - Manual cellset manipulation
            - Writing to cellsets
            - Performance optimization (create once, extract multiple times)
        """
        return self._cell_service.create_cellset(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            **kwargs,
        )

