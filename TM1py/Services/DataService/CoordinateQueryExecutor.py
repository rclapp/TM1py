# -*- coding: utf-8 -*-
"""
CoordinateQueryExecutor - Fluent interface for reading cell values by coordinates.

Provides a fluent interface for reading cell values from specific coordinates.
"""

from typing import TYPE_CHECKING, Iterable, List, Union

from TM1py.Services.DataService.Mixins import SandboxMixin

if TYPE_CHECKING:
    from TM1py.Services.CellService import CellService


try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


class CoordinateQueryExecutor(SandboxMixin):
    """
    Fluent interface for reading cell values by coordinates.
    
    Supports method chaining for options and terminal operations for reading values.
    
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
    
    def __init__(
        self,
        cell_service: "CellService",
        cube_name: str,
        coordinates: Union[Iterable[str], Iterable[Iterable[str]]],
        dimensions: List[str] = None,
    ):
        """
        Initialize CoordinateQueryExecutor.
        
        :param cell_service: CellService instance for delegation
        :param cube_name: Name of the cube
        :param coordinates: Single coordinate tuple or list of coordinate tuples
        :param dimensions: Optional list of dimension names (for coordinate validation)
        """
        # Initialize mixin
        SandboxMixin.__init__(self)
        
        self._cell_service = cell_service
        self._cube_name = cube_name
        self._coordinates = coordinates
        self._dimensions = dimensions
        
        # Determine if single or multiple coordinates
        self._is_single = self._detect_single_coordinate(coordinates)
    
    def _detect_single_coordinate(self, coordinates: Union[Iterable[str], Iterable[Iterable[str]]]) -> bool:
        """
        Detect if coordinates represent a single cell or multiple cells.
        
        :param coordinates: Coordinates to check
        :return: True if single coordinate, False if multiple
        """
        # Convert to list to inspect
        coords_list = list(coordinates)
        
        # Empty coordinates
        if not coords_list:
            return True
        
        # Check if first element is a string (single coordinate)
        # or an iterable (multiple coordinates)
        first_elem = coords_list[0]
        if isinstance(first_elem, str):
            return True
        
        # If it's an iterable, it's multiple coordinates
        return False
    
    def as_value(self, **kwargs) -> Union[str, float]:
        """
        Get the value from a single cell coordinate.
        
        Terminal operation - executes the query and returns a single value.
        
        :param kwargs: Additional parameters to pass to CellService.get_value()
        :return: Cell value (string or float)
        :raises ValueError: If coordinates represent multiple cells
        
        Example usage:
            value = tm1.data.coordinates('Sales', ['2024', 'Jan', 'Actual']).as_value()
        """
        if not self._is_single:
            raise ValueError(
                "as_value() can only be used with single coordinates. "
                "Use as_values() for multiple coordinates."
            )
        
        return self._cell_service.get_value(
            cube_name=self._cube_name,
            elements=self._coordinates,
            dimensions=self._dimensions,
            sandbox_name=self._sandbox_name,
            **kwargs,
        )
    
    def as_values(self, **kwargs) -> List[Union[str, float]]:
        """
        Get values from multiple cell coordinates.
        
        Terminal operation - executes the query and returns a list of values.
        
        :param kwargs: Additional parameters to pass to CellService.get_values()
        :return: List of cell values (strings or floats)
        
        Example usage:
            coords = [
                ['2024', 'Jan', 'Actual'],
                ['2024', 'Feb', 'Actual'],
                ['2024', 'Mar', 'Actual']
            ]
            values = tm1.data.coordinates('Sales', coords).as_values()
        """
        # If single coordinate, wrap in list for get_values
        if self._is_single:
            element_sets = [self._coordinates]
        else:
            element_sets = self._coordinates
        
        return self._cell_service.get_values(
            cube_name=self._cube_name,
            element_sets=element_sets,
            dimensions=self._dimensions,
            sandbox_name=self._sandbox_name,
            **kwargs,
        )

