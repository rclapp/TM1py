# -*- coding: utf-8 -*-
import unittest

from mdxpy import MdxBuilder, MdxHierarchySet, Member

from TM1py.Services.DataService.QueryExecutor import QueryExecutor
from TM1py.Utils import CaseAndSpaceInsensitiveTuplesDict

from .TM1pyTestCase import TM1pyTestCase


class TestQueryExecutor(TM1pyTestCase):
    """Test QueryExecutor functionality - inherits test infrastructure from TestCellService"""

    @classmethod
    def setUpClass(cls):
        """Establish connection to TM1 and create test fixtures"""
        # Call parent setUpClass to create all test cubes, dimensions, views, etc.
        super().setUpClass()

        # Simple MDX query for testing
        cls.mdx_query = f"""
        SELECT
        {{[{cls.dimension_names[0]}].[Element 1]}} ON ROWS,
        {{[{cls.dimension_names[1]}].[Element 1]}} ON COLUMNS
        FROM [{cls.cube_name}]
        """

        # MdxBuilder query for testing
        cls.mdx_builder = (MdxBuilder.from_cube(cls.cube_name)
                          .add_hierarchy_set_to_row_axis(
                              MdxHierarchySet.member(Member.of(cls.dimension_names[0], "Element 1")))
                          .add_hierarchy_set_to_column_axis(
                              MdxHierarchySet.member(Member.of(cls.dimension_names[1], "Element 1"))))
    
    def test_mdxquerybuilder_initialization(self):
        """Test QueryExecutor can be initialized with MDX string"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        self.assertIsInstance(builder, QueryExecutor)
        self.assertEqual(builder._mdx, self.mdx_query)
        self.assertIs(builder._cell_service, self.tm1.cells)

    def test_mdxquerybuilder_initialization_with_mdxbuilder(self):
        """Test QueryExecutor can be initialized with MdxBuilder object"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_builder)
        self.assertIsInstance(builder, QueryExecutor)
        self.assertIsInstance(builder._mdx, MdxBuilder)
        self.assertIs(builder._cell_service, self.tm1.cells)
    
    def test_mdxquerybuilder_has_mixin_methods(self):
        """Test QueryExecutor has all mixin methods"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        
        # SandboxMixin
        self.assertTrue(hasattr(builder, 'sandbox'))
        
        # FilterMixin
        self.assertTrue(hasattr(builder, 'skip_zeros'))
        self.assertTrue(hasattr(builder, 'skip_consolidated'))
        self.assertTrue(hasattr(builder, 'skip_rule_derived'))
        
        # PerformanceMixin
        self.assertTrue(hasattr(builder, 'use_blob'))
        self.assertTrue(hasattr(builder, 'use_compact_json'))
        self.assertTrue(hasattr(builder, 'use_iterative_json'))
        
        # PaginationMixin
        self.assertTrue(hasattr(builder, 'top'))
        self.assertTrue(hasattr(builder, 'skip'))
        
        # AttributeMixin
        self.assertTrue(hasattr(builder, 'include_attributes'))
        self.assertTrue(hasattr(builder, 'cell_properties'))
    
    def test_mdxquerybuilder_has_terminal_operations(self):
        """Test QueryExecutor has all terminal operations"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        
        self.assertTrue(hasattr(builder, 'as_dict'))
        self.assertTrue(hasattr(builder, 'as_dataframe'))
        self.assertTrue(hasattr(builder, 'as_csv'))
        self.assertTrue(hasattr(builder, 'as_values'))
        self.assertTrue(hasattr(builder, 'as_pivot'))
        self.assertTrue(hasattr(builder, 'count'))
    
    def test_as_dict_returns_dict(self):
        """Test as_dict() returns CaseAndSpaceInsensitiveTuplesDict"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.as_dict()
        
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)
    
    def test_as_dict_with_skip_zeros(self):
        """Test as_dict() with skip_zeros option"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.skip_zeros().as_dict()
        
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)
    
    def test_as_dict_method_chaining(self):
        """Test method chaining returns self"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.skip_zeros()
        
        self.assertIs(result, builder)
    
    def test_as_dataframe_returns_dataframe(self):
        """Test as_dataframe() returns pandas DataFrame"""
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("pandas not installed")
        
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.as_dataframe()
        
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_as_dataframe_with_options(self):
        """Test as_dataframe() with multiple options chained"""
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("pandas not installed")
        
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.skip_zeros().use_compact_json().as_dataframe()
        
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_as_csv_returns_string(self):
        """Test as_csv() returns CSV string"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.as_csv()
        
        self.assertIsInstance(result, str)
        # CSV should have at least a header line
        self.assertGreater(len(result), 0)
    
    def test_as_csv_with_custom_separators(self):
        """Test as_csv() with custom separators"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.as_csv(value_separator=";", line_separator="\n")
        
        self.assertIsInstance(result, str)
        self.assertIn(";", result)
    
    def test_as_values_returns_list(self):
        """Test as_values() returns list"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.as_values()
        
        self.assertIsInstance(result, list)
    
    def test_as_values_with_skip_zeros(self):
        """Test as_values() with skip_zeros option"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.skip_zeros().as_values()
        
        self.assertIsInstance(result, list)
    
    def test_as_pivot_returns_dataframe(self):
        """Test as_pivot() returns pandas DataFrame"""
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("pandas not installed")
        
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.as_pivot()
        
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_as_pivot_with_options(self):
        """Test as_pivot() with dropna and fill_value options"""
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("pandas not installed")
        
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.as_pivot(dropna=True, fill_value=0)
        
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_count_returns_int(self):
        """Test count() returns integer"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.count()
        
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
    
    def test_multiple_options_chained(self):
        """Test chaining multiple options together"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = (
            builder
            .skip_zeros()
            .skip_consolidated()
            .use_compact_json()
            .top(100)
        )
        
        self.assertIs(result, builder)
        self.assertTrue(builder._skip_zeros)
        self.assertTrue(builder._skip_consolidated_cells)
        self.assertTrue(builder._use_compact_json)
        self.assertEqual(builder._top, 100)
    
    def test_pagination_options(self):
        """Test top() and skip() pagination options"""
        builder = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = builder.top(10).skip(5).as_dict()

        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)


class TestQueryExecutorParity(TM1pyTestCase):
    """Test that QueryExecutor produces same results as CellService - inherits test infrastructure from TestCellService"""

    @classmethod
    def setUpClass(cls):
        """Establish connection to TM1 and create test fixtures"""
        # Call parent setUpClass to create all test cubes, dimensions, views, etc.
        super().setUpClass()

        cls.mdx_query = f"""
        SELECT
        {{[{cls.dimension_names[0]}].[Element 1]}} ON ROWS,
        {{[{cls.dimension_names[1]}].[Element 1]}} ON COLUMNS
        FROM [{cls.cube_name}]
        """

        # MdxBuilder query for testing
        cls.mdx_builder = (MdxBuilder.from_cube(cls.cube_name)
                          .add_hierarchy_set_to_row_axis(
                              MdxHierarchySet.member(Member.of(cls.dimension_names[0], "Element 1")))
                          .add_hierarchy_set_to_column_axis(
                              MdxHierarchySet.member(Member.of(cls.dimension_names[1], "Element 1"))))
    
    def test_as_dict_parity_with_cellservice(self):
        """Test as_dict() produces same result as CellService.execute_mdx()"""
        # Using builder
        builder_result = QueryExecutor(self.tm1.cells, self.mdx_query).as_dict()
        
        # Using CellService directly
        cellservice_result = self.tm1.cells.execute_mdx(self.mdx_query)
        
        # Results should be equal
        self.assertEqual(builder_result, cellservice_result)
    
    def test_as_values_parity_with_cellservice(self):
        """Test as_values() produces same result as CellService.execute_mdx_values()"""
        # Using builder
        builder_result = QueryExecutor(self.tm1.cells, self.mdx_query).as_values()
        
        # Using CellService directly
        cellservice_result = self.tm1.cells.execute_mdx_values(self.mdx_query)
        
        # Results should be equal
        self.assertEqual(builder_result, cellservice_result)
    
    def test_count_parity_with_cellservice(self):
        """Test count() produces same result as CellService.execute_mdx_cellcount()"""
        # Using builder
        builder_result = QueryExecutor(self.tm1.cells, self.mdx_query).count()

        # Using CellService directly
        cellservice_result = self.tm1.cells.execute_mdx_cellcount(self.mdx_query)

        # Results should be equal
        self.assertEqual(builder_result, cellservice_result)

    def test_as_raw_returns_dict(self):
        """Test as_raw() returns a dictionary with raw TM1 response"""
        result = QueryExecutor(self.tm1.cells, self.mdx_query).as_raw()

        # Should be a dictionary
        self.assertIsInstance(result, dict)

        # Should have expected keys from TM1 raw response
        self.assertIn('Axes', result)
        self.assertIn('Cells', result)

    def test_as_raw_with_options(self):
        """Test as_raw() works with chained options"""
        result = (QueryExecutor(self.tm1.cells, self.mdx_query)
                  .skip_zeros()
                  .as_raw())

        # Should be a dictionary
        self.assertIsInstance(result, dict)
        self.assertIn('Axes', result)
        self.assertIn('Cells', result)

    def test_as_raw_parity_with_cellservice(self):
        """Test as_raw() produces same result as CellService.execute_mdx_raw()"""
        # Using builder
        builder_result = QueryExecutor(self.tm1.cells, self.mdx_query).as_raw()

        # Using CellService directly
        cellservice_result = self.tm1.cells.execute_mdx_raw(self.mdx_query)

        # Results should be equal
        self.assertEqual(builder_result, cellservice_result)

    def test_as_cellset_id_returns_string(self):
        """Test as_cellset_id() returns a cellset ID string"""
        cellset_id = QueryExecutor(self.tm1.cells, self.mdx_query).as_cellset_id()

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

    def test_as_cellset_id_with_sandbox(self):
        """Test as_cellset_id() works with sandbox option"""
        # Note: This test assumes no sandbox, just tests the option is passed
        cellset_id = (QueryExecutor(self.tm1.cells, self.mdx_query)
                      .sandbox(None)
                      .as_cellset_id())

        try:
            # Should be a string
            self.assertIsInstance(cellset_id, str)
            self.assertTrue(len(cellset_id) > 0)

        finally:
            # Clean up
            self.tm1.cells.delete_cellset(cellset_id)

    def test_as_cellset_id_parity_with_cellservice(self):
        """Test as_cellset_id() creates same cellset as CellService.create_cellset()"""
        # Using builder
        builder_cellset_id = QueryExecutor(self.tm1.cells, self.mdx_query).as_cellset_id()

        # Using CellService directly
        cellservice_cellset_id = self.tm1.cells.create_cellset(self.mdx_query)

        try:
            # Both should be strings
            self.assertIsInstance(builder_cellset_id, str)
            self.assertIsInstance(cellservice_cellset_id, str)

            # Both should be usable
            builder_data = self.tm1.cells.extract_cellset_raw(builder_cellset_id, delete_cellset=False)
            cellservice_data = self.tm1.cells.extract_cellset_raw(cellservice_cellset_id, delete_cellset=False)

            # Data should be equivalent (same structure)
            self.assertEqual(builder_data.keys(), cellservice_data.keys())

        finally:
            # Clean up both cellsets
            self.tm1.cells.delete_cellset(builder_cellset_id)
            self.tm1.cells.delete_cellset(cellservice_cellset_id)

    def test_as_dict_with_mdxbuilder(self):
        """Test as_dict() works with MdxBuilder object"""
        result = QueryExecutor(self.tm1.cells, self.mdx_builder).as_dict()

        # Should be a CaseAndSpaceInsensitiveTuplesDict
        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_as_dataframe_with_mdxbuilder(self):
        """Test as_dataframe() works with MdxBuilder object"""
        result = QueryExecutor(self.tm1.cells, self.mdx_builder).as_dataframe()

        import pandas as pd
        self.assertIsInstance(result, pd.DataFrame)

    def test_as_csv_with_mdxbuilder(self):
        """Test as_csv() works with MdxBuilder object"""
        result = QueryExecutor(self.tm1.cells, self.mdx_builder).as_csv()

        # Should be a string
        self.assertIsInstance(result, str)
        self.assertIn(',', result)

    def test_as_values_with_mdxbuilder(self):
        """Test as_values() works with MdxBuilder object"""
        result = QueryExecutor(self.tm1.cells, self.mdx_builder).as_values()

        # Should be a list
        self.assertIsInstance(result, list)

    def test_count_with_mdxbuilder(self):
        """Test count() works with MdxBuilder object"""
        result = QueryExecutor(self.tm1.cells, self.mdx_builder).count()

        # Should be an integer
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

    def test_as_raw_with_mdxbuilder(self):
        """Test as_raw() works with MdxBuilder object"""
        result = QueryExecutor(self.tm1.cells, self.mdx_builder).as_raw()

        # Should be a dictionary
        self.assertIsInstance(result, dict)
        self.assertIn('Axes', result)
        self.assertIn('Cells', result)

    def test_as_cellset_id_with_mdxbuilder(self):
        """Test as_cellset_id() works with MdxBuilder object"""
        cellset_id = QueryExecutor(self.tm1.cells, self.mdx_builder).as_cellset_id()

        try:
            # Should be a string
            self.assertIsInstance(cellset_id, str)
            self.assertTrue(len(cellset_id) > 0)

        finally:
            # Clean up
            self.tm1.cells.delete_cellset(cellset_id)

    def test_mdxbuilder_with_chaining(self):
        """Test MdxBuilder works with option chaining"""
        result = (QueryExecutor(self.tm1.cells, self.mdx_builder)
                  .skip_zeros()
                  .sandbox(None)
                  .as_dict())

        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_has_max_workers_method(self):
        """Test QueryExecutor has max_workers() method from AsyncMixin"""
        executor = QueryExecutor(self.tm1.cells, self.mdx_query)
        self.assertTrue(hasattr(executor, 'max_workers'))
        self.assertTrue(callable(executor.max_workers))

    def test_has_async_axis_method(self):
        """Test QueryExecutor has async_axis() method from AsyncMixin"""
        executor = QueryExecutor(self.tm1.cells, self.mdx_query)
        self.assertTrue(hasattr(executor, 'async_axis'))
        self.assertTrue(callable(executor.async_axis))

    def test_max_workers_default(self):
        """Test max_workers defaults to 1 (synchronous)"""
        executor = QueryExecutor(self.tm1.cells, self.mdx_query)
        self.assertEqual(executor._max_workers, 1)

    def test_max_workers_chaining(self):
        """Test max_workers() returns self for chaining"""
        executor = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = executor.max_workers(8)
        self.assertIs(result, executor)
        self.assertEqual(executor._max_workers, 8)

    def test_async_axis_default(self):
        """Test async_axis defaults to 0 (columns)"""
        executor = QueryExecutor(self.tm1.cells, self.mdx_query)
        self.assertEqual(executor._async_axis, 0)

    def test_async_axis_chaining(self):
        """Test async_axis() returns self for chaining"""
        executor = QueryExecutor(self.tm1.cells, self.mdx_query)
        result = executor.async_axis(1)
        self.assertIs(result, executor)
        self.assertEqual(executor._async_axis, 1)

    def test_async_with_as_dict(self):
        """Test as_dict() works with max_workers > 1"""
        result = (QueryExecutor(self.tm1.cells, self.mdx_query)
                  .max_workers(2)
                  .as_dict())

        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)

    def test_async_with_as_dataframe(self):
        """Test as_dataframe() works with max_workers > 1"""
        import pandas as pd
        result = (QueryExecutor(self.tm1.cells, self.mdx_query)
                  .max_workers(2)
                  .as_dataframe())

        self.assertIsInstance(result, pd.DataFrame)

    def test_async_with_chaining(self):
        """Test async options work with other option chaining"""
        result = (QueryExecutor(self.tm1.cells, self.mdx_query)
                  .max_workers(4)
                  .async_axis(1)
                  .skip_zeros()
                  .sandbox(None)
                  .as_dict())

        self.assertIsInstance(result, CaseAndSpaceInsensitiveTuplesDict)


if __name__ == "__main__":
    unittest.main()

