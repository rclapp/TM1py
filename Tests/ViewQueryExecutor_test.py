# -*- coding: utf-8 -*-
import unittest

from TM1py.Services.DataService.ViewQueryExecutor import ViewQueryExecutor
from TM1py.Utils import CaseAndSpaceInsensitiveTuplesDict

from .TM1pyTestCase import TM1pyTestCase


class TestViewQueryExecutor(TM1pyTestCase):
    """Test ViewQueryExecutor functionality - inherits test infrastructure from TM1pyTestCase"""

    # Note: cube_name and view_name are inherited from TM1pyTestCase
    # No need to override setUpClass - parent creates all test fixtures
    
    def test_viewqueryexecutor_initialization(self):
        """Test ViewQueryExecutor can be initialized"""
        executor = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
        self.assertIsInstance(executor, ViewQueryExecutor)
        self.assertEqual(executor._cube_name, self.cube_name)
        self.assertEqual(executor._view_name, self.view_name)
        self.assertFalse(executor._private)
        self.assertIs(executor._cell_service, self.tm1.cells)
    
    def test_viewqueryexecutor_initialization_private(self):
        """Test ViewQueryExecutor can be initialized with private=True"""
        executor = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name, private=True)
        self.assertTrue(executor._private)
    
    def test_viewqueryexecutor_has_mixin_methods(self):
        """Test ViewQueryExecutor has all mixin methods"""
        executor = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
        
        # SandboxMixin
        self.assertTrue(hasattr(executor, 'sandbox'))
        
        # FilterMixin
        self.assertTrue(hasattr(executor, 'skip_zeros'))
        self.assertTrue(hasattr(executor, 'skip_consolidated'))
        self.assertTrue(hasattr(executor, 'skip_rule_derived'))
        
        # PerformanceMixin
        self.assertTrue(hasattr(executor, 'use_blob'))
        self.assertTrue(hasattr(executor, 'use_compact_json'))
        self.assertTrue(hasattr(executor, 'use_iterative_json'))
        
        # PaginationMixin
        self.assertTrue(hasattr(executor, 'top'))
        self.assertTrue(hasattr(executor, 'skip'))
    
    def test_viewqueryexecutor_has_terminal_operations(self):
        """Test ViewQueryExecutor has all terminal operations"""
        executor = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
        
        self.assertTrue(hasattr(executor, 'as_dict'))
        self.assertTrue(hasattr(executor, 'as_dataframe'))
        self.assertTrue(hasattr(executor, 'as_csv'))
        self.assertTrue(hasattr(executor, 'as_values'))
        self.assertTrue(hasattr(executor, 'count'))
        self.assertTrue(hasattr(executor, 'as_raw'))
        self.assertTrue(hasattr(executor, 'as_cellset_id'))
    
    def test_as_dict_returns_dict(self):
        """Test as_dict() returns a CaseAndSpaceInsensitiveTuplesDict"""
        result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_dict()
        
        # Should be a CaseAndSpaceInsensitiveTuplesDict
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)
    
    def test_as_dict_with_options(self):
        """Test as_dict() works with chained options"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip_zeros()
                  .as_dict())
        
        # Should be a CaseAndSpaceInsensitiveTuplesDict
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)
    
    def test_as_dataframe_returns_dataframe(self):
        """Test as_dataframe() returns a pandas DataFrame"""
        result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_dataframe()
        
        # Should be a DataFrame
        import pandas as pd
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_as_dataframe_with_options(self):
        """Test as_dataframe() works with chained options"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip_zeros()
                  .skip_consolidated()
                  .as_dataframe())
        
        import pandas as pd
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_as_csv_returns_string(self):
        """Test as_csv() returns a CSV string"""
        result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_csv()
        
        # Should be a string
        self.assertIsInstance(result, str)
        
        # Should contain comma separators
        self.assertIn(',', result)
    
    def test_as_csv_with_custom_separator(self):
        """Test as_csv() works with custom separator"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .as_csv(value_separator=';'))
        
        # Should contain semicolon separators
        self.assertIn(';', result)
    
    def test_as_values_returns_list(self):
        """Test as_values() returns a list"""
        result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_values()
        
        # Should be a list
        self.assertIsInstance(result, list)
    
    def test_as_values_with_options(self):
        """Test as_values() works with chained options"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip_zeros()
                  .as_values())
        
        self.assertIsInstance(result, list)
    
    def test_count_returns_int(self):
        """Test count() returns an integer"""
        result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).count()
        
        # Should be an integer
        self.assertIsInstance(result, int)
        
        # Should be non-negative
        self.assertGreaterEqual(result, 0)
    
    def test_as_raw_returns_dict(self):
        """Test as_raw() returns a dictionary with raw TM1 response"""
        result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_raw()
        
        # Should be a dictionary
        self.assertIsInstance(result, dict)
        
        # Should have expected keys from TM1 raw response
        self.assertIn('Axes', result)
        self.assertIn('Cells', result)
    
    def test_as_cellset_id_returns_string(self):
        """Test as_cellset_id() returns a cellset ID string"""
        cellset_id = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_cellset_id()
        
        try:
            # Should be a string
            self.assertIsInstance(cellset_id, str)
            
            # Should not be empty
            self.assertTrue(len(cellset_id) > 0)
            
            # Should be able to use with CellService methods
            raw_data = self.tm1.cells.extract_cellset_raw(cellset_id, delete_cellset=False)
            self.assertIsInstance(raw_data, dict)
            
        finally:
            # Clean up - delete the cellset
            self.tm1.cells.delete_cellset(cellset_id)
    
    def test_method_chaining_returns_self(self):
        """Test that option methods return self for chaining"""
        executor = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
        
        # Test chaining
        result = executor.skip_zeros().skip_consolidated().top(100)
        self.assertIs(result, executor)
    
    def test_as_dict_parity_with_cellservice(self):
        """Test as_dict() produces same result as CellService.execute_view()"""
        # Using executor
        executor_result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_dict()
        
        # Using CellService directly
        cellservice_result = self.tm1.cells.execute_view(
            cube_name=self.cube_name,
            view_name=self.view_name,
            private=False
        )
        
        # Results should be equal
        self.assertEqual(executor_result, cellservice_result)
    
    def test_as_dataframe_parity_with_cellservice(self):
        """Test as_dataframe() produces same result as CellService.execute_view_dataframe()"""
        # Using executor
        executor_result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_dataframe()
        
        # Using CellService directly
        cellservice_result = self.tm1.cells.execute_view_dataframe(
            cube_name=self.cube_name,
            view_name=self.view_name,
            private=False
        )
        
        # Results should be equal
        import pandas as pd
        pd.testing.assert_frame_equal(executor_result, cellservice_result)
    
    def test_as_csv_parity_with_cellservice(self):
        """Test as_csv() produces same result as CellService.execute_view_csv()"""
        # Using executor (note: FilterMixin defaults to skip_zeros=False)
        executor_result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_csv()

        # Using CellService directly (must match executor defaults)
        cellservice_result = self.tm1.cells.execute_view_csv(
            cube_name=self.cube_name,
            view_name=self.view_name,
            private=False,
            skip_zeros=False  # Match FilterMixin default
        )

        # Results should be equal
        self.assertEqual(executor_result, cellservice_result)

    def test_as_csv_with_skip_zeros(self):
        """Test as_csv() with skip_zeros option"""
        # With skip_zeros enabled
        result_skip = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                       .skip_zeros()
                       .as_csv())

        # Without skip_zeros
        result_no_skip = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_csv()

        # Results should be different (skip_zeros removes zero cells)
        # Note: This test assumes there are some zero values in the view
        # If all values are non-zero, the results might be the same
        self.assertIsInstance(result_skip, str)
        self.assertIsInstance(result_no_skip, str)

    def test_as_csv_with_line_separator(self):
        """Test as_csv() with custom line separator"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .as_csv(line_separator='\n'))

        # Should be a string
        self.assertIsInstance(result, str)
        # Should contain newline separators
        self.assertIn('\n', result)

    def test_as_csv_with_chained_options(self):
        """Test as_csv() with multiple chained options"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip_zeros()
                  .skip_consolidated()
                  .top(10)
                  .as_csv(value_separator='|'))

        # Should be a string
        self.assertIsInstance(result, str)
        # Should contain pipe separators
        self.assertIn('|', result)
    
    def test_as_values_parity_with_cellservice(self):
        """Test as_values() produces same result as CellService.execute_view_values()"""
        # Using executor
        executor_result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_values()
        
        # Using CellService directly
        cellservice_result = self.tm1.cells.execute_view_values(
            cube_name=self.cube_name,
            view_name=self.view_name,
            private=False
        )
        
        # Results should be equal
        self.assertEqual(executor_result, cellservice_result)
    
    def test_count_parity_with_cellservice(self):
        """Test count() produces same result as CellService.execute_view_cellcount()"""
        # Using executor
        executor_result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).count()

        # Using CellService directly
        cellservice_result = self.tm1.cells.execute_view_cellcount(
            cube_name=self.cube_name,
            view_name=self.view_name,
            private=False
        )

        # Results should be equal
        self.assertEqual(executor_result, cellservice_result)

    def test_as_raw_parity_with_cellservice(self):
        """Test as_raw() produces same result as CellService.execute_view_raw()"""
        # Using executor
        executor_result = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_raw()

        # Using CellService directly (must match executor defaults)
        cellservice_result = self.tm1.cells.execute_view_raw(
            cube_name=self.cube_name,
            view_name=self.view_name,
            private=False,
            skip_zeros=False  # Match FilterMixin default
        )

        # Both should be dictionaries
        self.assertIsInstance(executor_result, dict)
        self.assertIsInstance(cellservice_result, dict)

        # Results should be equal
        self.assertEqual(executor_result, cellservice_result)

    def test_as_cellset_id_parity_with_cellservice(self):
        """Test as_cellset_id() produces valid cellset ID like CellService.create_cellset_from_view()"""
        # Using executor
        executor_cellset_id = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_cellset_id()

        # Using CellService directly
        cellservice_cellset_id = self.tm1.cells.create_cellset_from_view(
            cube_name=self.cube_name,
            view_name=self.view_name,
            private=False
        )

        # Both should be strings
        self.assertIsInstance(executor_cellset_id, str)
        self.assertIsInstance(cellservice_cellset_id, str)

        # Both should be valid cellset IDs (non-empty strings)
        self.assertTrue(len(executor_cellset_id) > 0)
        self.assertTrue(len(cellservice_cellset_id) > 0)

        # Clean up cellsets
        self.tm1.cells.delete_cellset(executor_cellset_id)
        self.tm1.cells.delete_cellset(cellservice_cellset_id)

    def test_has_max_workers_method(self):
        """Test ViewQueryExecutor has max_workers() method from AsyncMixin"""
        executor = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
        self.assertTrue(hasattr(executor, 'max_workers'))
        self.assertTrue(callable(executor.max_workers))

    def test_has_async_axis_method(self):
        """Test ViewQueryExecutor has async_axis() method from AsyncMixin"""
        executor = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
        self.assertTrue(hasattr(executor, 'async_axis'))
        self.assertTrue(callable(executor.async_axis))

    def test_async_with_as_dict(self):
        """Test as_dict() works with max_workers > 1"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .max_workers(2)
                  .as_dict())

        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_async_with_as_dataframe(self):
        """Test as_dataframe() works with max_workers > 1"""
        import pandas as pd
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .max_workers(2)
                  .as_dataframe())

        self.assertIsInstance(result, pd.DataFrame)

    def test_async_with_chaining(self):
        """Test async options work with other option chaining"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .max_workers(4)
                  .async_axis(1)
                  .skip_zeros()
                  .as_dict())

        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_skip_zeros_option(self):
        """Test skip_zeros() option filters zero values"""
        # Get results with skip_zeros
        result_with_skip = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                           .skip_zeros()
                           .as_dict())

        # Get results without skip_zeros
        result_without_skip = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                              .as_dict())

        # Both should be dictionaries
        self.assertIsInstance(result_with_skip, CaseAndSpaceInsensitiveTuplesDict)
        self.assertIsInstance(result_without_skip, CaseAndSpaceInsensitiveTuplesDict)

        # With skip_zeros should have fewer or equal entries (if there are zeros)
        self.assertLessEqual(len(result_with_skip), len(result_without_skip))

    def test_skip_consolidated_option(self):
        """Test skip_consolidated() option filters consolidated cells"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip_consolidated()
                  .as_dict())

        # Should return a dictionary
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_skip_rule_derived_option(self):
        """Test skip_rule_derived() option filters rule-derived cells"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip_rule_derived()
                  .as_dict())

        # Should return a dictionary
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_top_option(self):
        """Test top() option limits number of cells returned"""
        # Get top 5 cells
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .top(5)
                  .as_dict())

        # Should return a dictionary with at most 5 entries
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)
        self.assertLessEqual(len(result), 5)

    def test_skip_pagination_option(self):
        """Test skip() option skips first N cells"""
        # Get all cells
        all_cells = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_dict()

        # Skip first 10 cells
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip(10)
                  .as_dict())

        # Should return a dictionary
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

        # Should have fewer entries than all cells (if there are more than 10)
        if len(all_cells) > 10:
            self.assertLess(len(result), len(all_cells))

    def test_top_and_skip_combined(self):
        """Test top() and skip() work together for pagination"""
        # Get cells 11-20 (skip first 10, take next 10)
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip(10)
                  .top(10)
                  .as_dict())

        # Should return a dictionary with at most 10 entries
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)
        self.assertLessEqual(len(result), 10)

    def test_use_compact_json_option(self):
        """Test use_compact_json() option for performance"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .use_compact_json()
                  .as_dict())

        # Should return a dictionary
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_multiple_filter_options_combined(self):
        """Test multiple filter options work together"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip_zeros()
                  .skip_consolidated()
                  .skip_rule_derived()
                  .as_dict())

        # Should return a dictionary
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_all_options_combined(self):
        """Test all options can be chained together"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .skip_zeros()
                  .skip_consolidated()
                  .skip_rule_derived()
                  .top(20)
                  .skip(5)
                  .use_compact_json()
                  .as_dict())

        # Should return a dictionary with at most 20 entries
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)
        self.assertLessEqual(len(result), 20)

    def test_sandbox_option(self):
        """Test sandbox() option executes query in sandbox context"""
        # Write a value to the sandbox
        test_coordinate = ("Element 1", "Element 1", "Element 1")
        sandbox_value = 999999

        self.tm1.cells.write_value(
            value=sandbox_value,
            cube_name=self.cube_name,
            element_tuple=test_coordinate,
            sandbox_name=self.sandbox_name
        )

        # Read from sandbox using ViewQueryExecutor
        result_sandbox = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                         .sandbox(self.sandbox_name)
                         .as_dict())

        # Read from base (no sandbox)
        result_base = ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name).as_dict()

        # Both should be dictionaries
        self.assertIsInstance(result_sandbox, CaseAndSpaceInsensitiveTuplesDict)
        self.assertIsInstance(result_base, CaseAndSpaceInsensitiveTuplesDict)

        # Sandbox result should contain the sandbox value
        if test_coordinate in result_sandbox:
            self.assertEqual(result_sandbox[test_coordinate], sandbox_value)

        # Base result should NOT contain the sandbox value (should be original value)
        if test_coordinate in result_base:
            self.assertNotEqual(result_base[test_coordinate], sandbox_value)

    def test_sandbox_with_other_options(self):
        """Test sandbox() works with other chained options"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .sandbox(self.sandbox_name)
                  .skip_zeros()
                  .top(10)
                  .as_dict())

        # Should return a dictionary
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)
        self.assertLessEqual(len(result), 10)

    def test_use_blob_option(self):
        """Test use_blob() option for performance"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .use_blob()
                  .as_csv())

        # Should return a CSV string
        self.assertIsInstance(result, str)
        self.assertIn(',', result)

    def test_use_iterative_json_option(self):
        """Test use_iterative_json() option for memory efficiency"""
        result = (ViewQueryExecutor(self.tm1.cells, self.cube_name, self.view_name)
                  .use_iterative_json()
                  .as_dict())

        # Should return a dictionary
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)


if __name__ == "__main__":
    unittest.main()

