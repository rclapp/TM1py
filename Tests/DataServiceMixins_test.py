# -*- coding: utf-8 -*-
import unittest

from TM1py.Services.DataService.Mixins import (
    AsyncMixin,
    AttributeMixin,
    FilterMixin,
    PaginationMixin,
    PerformanceMixin,
    SandboxMixin,
    WriteMixin,
)


class TestSandboxMixin(unittest.TestCase):
    """Test SandboxMixin in isolation"""

    def setUp(self):
        self.mixin = SandboxMixin()

    def test_sandbox_sets_value(self):
        result = self.mixin.sandbox("dev")
        self.assertEqual(self.mixin._sandbox_name, "dev")

    def test_sandbox_returns_self(self):
        result = self.mixin.sandbox("dev")
        self.assertIs(result, self.mixin)

    def test_sandbox_default_is_none(self):
        self.assertIsNone(self.mixin._sandbox_name)

    def test_sandbox_chaining(self):
        # Test that we can chain (returns self)
        result = self.mixin.sandbox("dev").sandbox("prod")
        self.assertEqual(self.mixin._sandbox_name, "prod")
        self.assertIs(result, self.mixin)


class TestFilterMixin(unittest.TestCase):
    """Test FilterMixin in isolation"""

    def setUp(self):
        self.mixin = FilterMixin()

    def test_skip_zeros_default(self):
        self.assertFalse(self.mixin._skip_zeros)

    def test_skip_zeros_sets_true(self):
        result = self.mixin.skip_zeros()
        self.assertTrue(self.mixin._skip_zeros)

    def test_skip_zeros_sets_false(self):
        result = self.mixin.skip_zeros(False)
        self.assertFalse(self.mixin._skip_zeros)

    def test_skip_zeros_returns_self(self):
        result = self.mixin.skip_zeros()
        self.assertIs(result, self.mixin)

    def test_skip_consolidated_default(self):
        self.assertFalse(self.mixin._skip_consolidated_cells)

    def test_skip_consolidated_sets_true(self):
        result = self.mixin.skip_consolidated()
        self.assertTrue(self.mixin._skip_consolidated_cells)

    def test_skip_consolidated_returns_self(self):
        result = self.mixin.skip_consolidated()
        self.assertIs(result, self.mixin)

    def test_skip_rule_derived_default(self):
        self.assertFalse(self.mixin._skip_rule_derived_cells)

    def test_skip_rule_derived_sets_true(self):
        result = self.mixin.skip_rule_derived()
        self.assertTrue(self.mixin._skip_rule_derived_cells)

    def test_skip_rule_derived_returns_self(self):
        result = self.mixin.skip_rule_derived()
        self.assertIs(result, self.mixin)

    def test_chaining_multiple_filters(self):
        result = self.mixin.skip_zeros().skip_consolidated().skip_rule_derived()
        self.assertTrue(self.mixin._skip_zeros)
        self.assertTrue(self.mixin._skip_consolidated_cells)
        self.assertTrue(self.mixin._skip_rule_derived_cells)
        self.assertIs(result, self.mixin)


class TestPerformanceMixin(unittest.TestCase):
    """Test PerformanceMixin in isolation"""

    def setUp(self):
        self.mixin = PerformanceMixin()

    def test_use_blob_default(self):
        self.assertFalse(self.mixin._use_blob)

    def test_use_blob_sets_true(self):
        result = self.mixin.use_blob()
        self.assertTrue(self.mixin._use_blob)

    def test_use_blob_returns_self(self):
        result = self.mixin.use_blob()
        self.assertIs(result, self.mixin)

    def test_use_compact_json_default(self):
        self.assertFalse(self.mixin._use_compact_json)

    def test_use_compact_json_sets_true(self):
        result = self.mixin.use_compact_json()
        self.assertTrue(self.mixin._use_compact_json)

    def test_use_compact_json_returns_self(self):
        result = self.mixin.use_compact_json()
        self.assertIs(result, self.mixin)

    def test_use_iterative_json_default(self):
        self.assertFalse(self.mixin._use_iterative_json)

    def test_use_iterative_json_sets_true(self):
        result = self.mixin.use_iterative_json()
        self.assertTrue(self.mixin._use_iterative_json)

    def test_use_iterative_json_returns_self(self):
        result = self.mixin.use_iterative_json()
        self.assertIs(result, self.mixin)

    def test_chaining_performance_options(self):
        result = self.mixin.use_blob().use_compact_json()
        self.assertTrue(self.mixin._use_blob)
        self.assertTrue(self.mixin._use_compact_json)
        self.assertIs(result, self.mixin)


class TestPaginationMixin(unittest.TestCase):
    """Test PaginationMixin in isolation"""

    def setUp(self):
        self.mixin = PaginationMixin()

    def test_top_default(self):
        self.assertIsNone(self.mixin._top)

    def test_top_sets_value(self):
        result = self.mixin.top(100)
        self.assertEqual(self.mixin._top, 100)

    def test_top_returns_self(self):
        result = self.mixin.top(100)
        self.assertIs(result, self.mixin)

    def test_skip_default(self):
        self.assertIsNone(self.mixin._skip)

    def test_skip_sets_value(self):
        result = self.mixin.skip(50)
        self.assertEqual(self.mixin._skip, 50)

    def test_skip_returns_self(self):
        result = self.mixin.skip(50)
        self.assertIs(result, self.mixin)

    def test_chaining_pagination(self):
        result = self.mixin.top(100).skip(50)
        self.assertEqual(self.mixin._top, 100)
        self.assertEqual(self.mixin._skip, 50)
        self.assertIs(result, self.mixin)


class TestAttributeMixin(unittest.TestCase):
    """Test AttributeMixin in isolation"""

    def setUp(self):
        self.mixin = AttributeMixin()

    def test_include_attributes_default(self):
        self.assertFalse(self.mixin._include_attributes)

    def test_include_attributes_sets_true(self):
        result = self.mixin.include_attributes()
        self.assertTrue(self.mixin._include_attributes)

    def test_include_attributes_returns_self(self):
        result = self.mixin.include_attributes()
        self.assertIs(result, self.mixin)

    def test_cell_properties_default(self):
        self.assertIsNone(self.mixin._cell_properties)

    def test_cell_properties_sets_value(self):
        props = ["Value", "RuleDerived"]
        result = self.mixin.cell_properties(props)
        self.assertEqual(self.mixin._cell_properties, props)

    def test_cell_properties_returns_self(self):
        result = self.mixin.cell_properties(["Value"])
        self.assertIs(result, self.mixin)

    def test_chaining_attributes(self):
        result = self.mixin.include_attributes().cell_properties(["Value"])
        self.assertTrue(self.mixin._include_attributes)
        self.assertEqual(self.mixin._cell_properties, ["Value"])
        self.assertIs(result, self.mixin)


class TestAsyncMixin(unittest.TestCase):
    """Test AsyncMixin in isolation"""

    def setUp(self):
        self.mixin = AsyncMixin()

    def test_max_workers_default(self):
        self.assertEqual(self.mixin._max_workers, 1)

    def test_max_workers_sets_value(self):
        result = self.mixin.max_workers(8)
        self.assertEqual(self.mixin._max_workers, 8)

    def test_max_workers_returns_self(self):
        result = self.mixin.max_workers(8)
        self.assertIs(result, self.mixin)

    def test_async_axis_default(self):
        self.assertEqual(self.mixin._async_axis, 0)

    def test_async_axis_sets_value(self):
        result = self.mixin.async_axis(1)
        self.assertEqual(self.mixin._async_axis, 1)

    def test_async_axis_returns_self(self):
        result = self.mixin.async_axis(1)
        self.assertIs(result, self.mixin)

    def test_chaining_async_options(self):
        result = self.mixin.max_workers(16).async_axis(1)
        self.assertEqual(self.mixin._max_workers, 16)
        self.assertEqual(self.mixin._async_axis, 1)
        self.assertIs(result, self.mixin)


class TestWriteMixin(unittest.TestCase):
    """Test WriteMixin in isolation"""

    def setUp(self):
        self.mixin = WriteMixin()

    def test_increment_default(self):
        self.assertFalse(self.mixin._increment)

    def test_increment_sets_true(self):
        result = self.mixin.increment()
        self.assertTrue(self.mixin._increment)

    def test_increment_returns_self(self):
        result = self.mixin.increment()
        self.assertIs(result, self.mixin)

    def test_skip_non_updateable_default(self):
        self.assertFalse(self.mixin._skip_non_updateable)

    def test_skip_non_updateable_sets_true(self):
        result = self.mixin.skip_non_updateable()
        self.assertTrue(self.mixin._skip_non_updateable)

    def test_skip_non_updateable_returns_self(self):
        result = self.mixin.skip_non_updateable()
        self.assertIs(result, self.mixin)

    def test_use_ti_default(self):
        self.assertFalse(self.mixin._use_ti)

    def test_use_ti_sets_true(self):
        result = self.mixin.use_ti()
        self.assertTrue(self.mixin._use_ti)
        self.assertFalse(self.mixin._use_blob_write)
        self.assertFalse(self.mixin._use_cellset)

    def test_use_ti_returns_self(self):
        result = self.mixin.use_ti()
        self.assertIs(result, self.mixin)

    def test_use_blob_write_default(self):
        self.assertFalse(self.mixin._use_blob_write)

    def test_use_blob_write_sets_true(self):
        result = self.mixin.use_blob_write()
        self.assertTrue(self.mixin._use_blob_write)
        self.assertFalse(self.mixin._use_ti)
        self.assertFalse(self.mixin._use_cellset)

    def test_use_blob_write_returns_self(self):
        result = self.mixin.use_blob_write()
        self.assertIs(result, self.mixin)

    def test_use_cellset_default(self):
        self.assertFalse(self.mixin._use_cellset)

    def test_use_cellset_sets_true(self):
        result = self.mixin.use_cellset()
        self.assertTrue(self.mixin._use_cellset)
        self.assertFalse(self.mixin._use_ti)
        self.assertFalse(self.mixin._use_blob_write)

    def test_use_cellset_returns_self(self):
        result = self.mixin.use_cellset()
        self.assertIs(result, self.mixin)

    def test_write_method_mutual_exclusion(self):
        # Set use_ti, then use_blob_write should clear it
        self.mixin.use_ti()
        self.assertTrue(self.mixin._use_ti)
        
        self.mixin.use_blob_write()
        self.assertFalse(self.mixin._use_ti)
        self.assertTrue(self.mixin._use_blob_write)
        
        self.mixin.use_cellset()
        self.assertFalse(self.mixin._use_ti)
        self.assertFalse(self.mixin._use_blob_write)
        self.assertTrue(self.mixin._use_cellset)

    def test_allow_spread_default(self):
        self.assertFalse(self.mixin._allow_spread)

    def test_allow_spread_sets_true(self):
        result = self.mixin.allow_spread()
        self.assertTrue(self.mixin._allow_spread)

    def test_allow_spread_returns_self(self):
        result = self.mixin.allow_spread()
        self.assertIs(result, self.mixin)

    def test_chaining_write_options(self):
        result = self.mixin.increment().skip_non_updateable().use_ti()
        self.assertTrue(self.mixin._increment)
        self.assertTrue(self.mixin._skip_non_updateable)
        self.assertTrue(self.mixin._use_ti)
        self.assertIs(result, self.mixin)


class TestMixinCombination(unittest.TestCase):
    """Test that mixins can be combined in a single class"""

    def test_multiple_mixins_combined(self):
        # Create a class that uses multiple mixins
        class CombinedBuilder(SandboxMixin, FilterMixin, PerformanceMixin):
            def __init__(self):
                SandboxMixin.__init__(self)
                FilterMixin.__init__(self)
                PerformanceMixin.__init__(self)

        builder = CombinedBuilder()
        
        # Test chaining across mixins
        result = builder.sandbox("dev").skip_zeros().use_blob()
        
        self.assertEqual(builder._sandbox_name, "dev")
        self.assertTrue(builder._skip_zeros)
        self.assertTrue(builder._use_blob)
        self.assertIs(result, builder)


if __name__ == "__main__":
    unittest.main()
