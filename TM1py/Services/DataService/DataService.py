# -*- coding: utf-8 -*-
"""
DataService - Fluent builder pattern interface for TM1 data operations.

This service provides a more intuitive and discoverable API for common data operations
compared to the traditional CellService. It uses the builder pattern to enable method
chaining and better IDE autocomplete support.

Example usage:
    # Read data
    df = tm1.data.mdx(query).skip_zeros().use_blob().as_dataframe()

    # Write data
    tm1.data.write(cube, data).use_blob().increment().execute()
"""

from typing import Iterable, List, Union

from mdxpy import MdxBuilder

from TM1py.Services.CellService import CellService
from TM1py.Services.DataService.CoordinateQueryExecutor import CoordinateQueryExecutor
from TM1py.Services.DataService.QueryExecutor import QueryExecutor
from TM1py.Services.DataService.ViewQueryExecutor import ViewQueryExecutor
from TM1py.Services.ObjectService import ObjectService
from TM1py.Services.RestService import RestService


class DataService(ObjectService):
    """
    Fluent interface for TM1 data operations.
    
    This service delegates to CellService for actual operations but provides
    a more intuitive builder pattern interface.
    """
    
    def __init__(self, rest: RestService):
        """
        Initialize DataService.
        
        :param rest: Instance of RestService for TM1 communication
        """
        super().__init__(rest)
        self._cell_service = CellService(rest)
    
    @property
    def cells(self) -> CellService:
        """
        Access to underlying CellService for advanced operations.

        :return: CellService instance
        """
        return self._cell_service

    def mdx(self, mdx: Union[str, MdxBuilder]) -> QueryExecutor:
        """
        Execute an MDX query with fluent options.

        Note: This executes queries. To BUILD/CONSTRUCT MDX queries, use MdxBuilder from mdxpy.

        :param mdx: MDX query string or MdxBuilder object to execute
        :return: QueryExecutor instance for method chaining

        Example usage:
            # With MDX string
            result = tm1.data.mdx("SELECT ...").as_dict()

            # With MdxBuilder from mdxpy
            from mdxpy import MdxBuilder
            query = MdxBuilder.from_cube("Sales").add_hierarchy_set_to_row_axis(...)
            df = tm1.data.mdx(query).skip_zeros().use_blob().as_dataframe()

            # Get cell count
            count = tm1.data.mdx(query).count()
        """
        return QueryExecutor(self._cell_service, mdx)

    def view(self, cube_name: str, view_name: str, private: bool = False) -> ViewQueryExecutor:
        """
        Execute a cube view query with fluent options.

        :param cube_name: Name of the cube
        :param view_name: Name of the view
        :param private: Whether the view is private (default: False)
        :return: ViewQueryExecutor instance for method chaining

        Example usage:
            # Get as dictionary
            result = tm1.data.view('Sales', 'Budget').as_dict()

            # Get as DataFrame with options
            df = tm1.data.view('Sales', 'Budget', private=True).skip_zeros().as_dataframe()

            # Get as CSV
            csv = tm1.data.view('Sales', 'Budget').as_csv()

            # Get cell count
            count = tm1.data.view('Sales', 'Budget').count()
        """
        return ViewQueryExecutor(self._cell_service, cube_name, view_name, private)

    def coordinates(
        self,
        cube_name: str,
        coordinates: Union[Iterable[str], Iterable[Iterable[str]]],
        dimensions: List[str] = None,
    ) -> CoordinateQueryExecutor:
        """
        Read cell value(s) from specific coordinates with fluent options.

        :param cube_name: Name of the cube
        :param coordinates: Single coordinate tuple or list of coordinate tuples
        :param dimensions: Optional list of dimension names
        :return: CoordinateQueryExecutor instance for method chaining

        Example usage:
            # Get single value
            value = tm1.data.coordinates('Sales', ['2024', 'Jan', 'Actual']).as_value()

            # Get single value with sandbox
            value = tm1.data.coordinates('Sales', ['2024', 'Jan', 'Actual']).sandbox('dev').as_value()

            # Get multiple values
            coords = [
                ['2024', 'Jan', 'Actual'],
                ['2024', 'Feb', 'Actual'],
                ['2024', 'Mar', 'Actual']
            ]
            values = tm1.data.coordinates('Sales', coords).as_values()
        """
        return CoordinateQueryExecutor(self._cell_service, cube_name, coordinates, dimensions)
