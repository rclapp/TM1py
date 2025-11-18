# -*- coding: utf-8 -*-
import unittest

from TM1py.Services.DataService.CoordinateQueryExecutor import CoordinateQueryExecutor

from .TM1pyTestCase import TM1pyTestCase


class TestCoordinateQueryExecutor(TM1pyTestCase):
    """Test CoordinateQueryExecutor functionality - inherits test infrastructure from TM1pyTestCase"""

    @classmethod
    def setUpClass(cls):
        """Establish connection to TM1 and create test fixtures"""
        # Call parent setUpClass to create all test cubes, dimensions, views, etc.
        super().setUpClass()

        # Single coordinate for testing
        cls.single_coordinate = ["Element 1", "Element 1", "Element 1"]

        # Multiple coordinates for testing
        cls.multiple_coordinates = [
            ["Element 1", "Element 1", "Element 1"],
            ["Element 2", "Element 2", "Element 2"],
            ["Element 3", "Element 3", "Element 3"],
        ]
    
    def test_coordinatequeryexecutor_initialization_single(self):
        """Test CoordinateQueryExecutor can be initialized with single coordinate"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        )
        self.assertIsInstance(executor, CoordinateQueryExecutor)
        self.assertEqual(executor._cube_name, self.cube_name)
        self.assertTrue(executor._is_single)
        self.assertIs(executor._cell_service, self.tm1.cells)
    
    def test_coordinatequeryexecutor_initialization_multiple(self):
        """Test CoordinateQueryExecutor can be initialized with multiple coordinates"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.multiple_coordinates
        )
        self.assertIsInstance(executor, CoordinateQueryExecutor)
        self.assertEqual(executor._cube_name, self.cube_name)
        self.assertFalse(executor._is_single)
    
    def test_coordinatequeryexecutor_has_mixin_methods(self):
        """Test CoordinateQueryExecutor has sandbox mixin methods"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        )
        
        # SandboxMixin
        self.assertTrue(hasattr(executor, 'sandbox'))
    
    def test_coordinatequeryexecutor_has_terminal_operations(self):
        """Test CoordinateQueryExecutor has all terminal operations"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        )
        
        self.assertTrue(hasattr(executor, 'as_value'))
        self.assertTrue(hasattr(executor, 'as_values'))
    
    def test_as_value_returns_value(self):
        """Test as_value() returns a single value"""
        result = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        ).as_value()
        
        # Should be a string or float
        self.assertTrue(isinstance(result, (str, float, int)))
    
    def test_as_value_with_sandbox(self):
        """Test as_value() works with sandbox option"""
        result = (CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        )
        .sandbox(None)
        .as_value())
        
        self.assertTrue(isinstance(result, (str, float, int)))
    
    def test_as_value_raises_on_multiple_coordinates(self):
        """Test as_value() raises ValueError when used with multiple coordinates"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.multiple_coordinates
        )
        
        with self.assertRaises(ValueError) as context:
            executor.as_value()
        
        self.assertIn("single coordinates", str(context.exception))
        self.assertIn("as_values()", str(context.exception))
    
    def test_as_values_returns_list_single(self):
        """Test as_values() returns a list even with single coordinate"""
        result = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        ).as_values()
        
        # Should be a list
        self.assertIsInstance(result, list)
        
        # Should have one element
        self.assertEqual(len(result), 1)
    
    def test_as_values_returns_list_multiple(self):
        """Test as_values() returns a list with multiple coordinates"""
        result = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.multiple_coordinates
        ).as_values()
        
        # Should be a list
        self.assertIsInstance(result, list)
        
        # Should have three elements
        self.assertEqual(len(result), 3)
    
    def test_as_values_with_sandbox(self):
        """Test as_values() works with sandbox option"""
        result = (CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.multiple_coordinates
        )
        .sandbox(None)
        .as_values())
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
    
    def test_method_chaining_returns_self(self):
        """Test that option methods return self for chaining"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        )
        
        # Test chaining
        result = executor.sandbox(None)
        self.assertIs(result, executor)
    
    def test_as_value_parity_with_cellservice(self):
        """Test as_value() produces same result as CellService.get_value()"""
        # Using executor
        executor_result = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        ).as_value()
        
        # Using CellService directly
        cellservice_result = self.tm1.cells.get_value(
            cube_name=self.cube_name,
            elements=self.single_coordinate
        )
        
        # Results should be equal
        self.assertEqual(executor_result, cellservice_result)
    
    def test_as_values_parity_with_cellservice_single(self):
        """Test as_values() with single coordinate produces same result as CellService.get_values()"""
        # Using executor
        executor_result = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.single_coordinate
        ).as_values()
        
        # Using CellService directly
        cellservice_result = self.tm1.cells.get_values(
            cube_name=self.cube_name,
            element_sets=[self.single_coordinate]
        )
        
        # Results should be equal
        self.assertEqual(executor_result, cellservice_result)
    
    def test_as_values_parity_with_cellservice_multiple(self):
        """Test as_values() with multiple coordinates produces same result as CellService.get_values()"""
        # Using executor
        executor_result = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            self.multiple_coordinates
        ).as_values()
        
        # Using CellService directly
        cellservice_result = self.tm1.cells.get_values(
            cube_name=self.cube_name,
            element_sets=self.multiple_coordinates
        )
        
        # Results should be equal
        self.assertEqual(executor_result, cellservice_result)
    
    def test_detect_single_coordinate_with_strings(self):
        """Test _detect_single_coordinate correctly identifies single coordinate"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            ["Element1", "Element2", "Element3"]
        )
        
        self.assertTrue(executor._is_single)
    
    def test_detect_single_coordinate_with_lists(self):
        """Test _detect_single_coordinate correctly identifies multiple coordinates"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            [["Element1", "Element2"], ["Element3", "Element4"]]
        )
        
        self.assertFalse(executor._is_single)
    
    def test_detect_single_coordinate_with_empty(self):
        """Test _detect_single_coordinate handles empty coordinates"""
        executor = CoordinateQueryExecutor(
            self.tm1.cells,
            self.cube_name,
            []
        )

        # Empty should be treated as single
        self.assertTrue(executor._is_single)


if __name__ == "__main__":
    unittest.main()

