# -*- coding: utf-8 -*-
import configparser
import unittest
from pathlib import Path

from mdxpy import MdxBuilder, MdxHierarchySet, Member

from TM1py.Services import TM1Service
from TM1py.Services.CellService import CellService
from TM1py.Services.DataService.CoordinateQueryExecutor import CoordinateQueryExecutor
from TM1py.Services.DataService.DataService import DataService
from TM1py.Services.DataService.QueryExecutor import QueryExecutor
from TM1py.Services.DataService.ViewQueryExecutor import ViewQueryExecutor
from TM1py.Services.ObjectService import ObjectService


class TestDataServiceInitialization(unittest.TestCase):
    """Test DataService initialization and basic structure"""
    
    tm1: TM1Service
    
    @classmethod
    def setUpClass(cls):
        """Establish connection to TM1"""
        cls.config = configparser.ConfigParser()
        cls.config.read(Path(__file__).parent.joinpath("config.ini"))
        cls.tm1 = TM1Service(**cls.config["tm1srv01"])
    
    def test_dataservice_inherits_from_objectservice(self):
        """DataService should inherit from ObjectService"""
        data_service = DataService(self.tm1._tm1_rest)
        self.assertIsInstance(data_service, ObjectService)
    
    def test_dataservice_has_cell_service(self):
        """DataService should have a CellService instance"""
        data_service = DataService(self.tm1._tm1_rest)
        self.assertIsInstance(data_service._cell_service, CellService)
    
    def test_dataservice_cells_property(self):
        """DataService.cells should return CellService instance"""
        data_service = DataService(self.tm1._tm1_rest)
        self.assertIsInstance(data_service.cells, CellService)
        self.assertIs(data_service.cells, data_service._cell_service)
    
    def test_dataservice_has_rest_service(self):
        """DataService should have access to RestService via _rest"""
        data_service = DataService(self.tm1._tm1_rest)
        self.assertIsNotNone(data_service._rest)
        self.assertIs(data_service._rest, self.tm1._tm1_rest)
    
    def test_dataservice_version_property(self):
        """DataService should have version property from ObjectService"""
        data_service = DataService(self.tm1._tm1_rest)
        self.assertIsNotNone(data_service.version)
        self.assertEqual(data_service.version, self.tm1.version)
    
    @classmethod
    def tearDownClass(cls):
        """Close TM1 connection"""
        cls.tm1.logout()


class TestTM1ServiceDataIntegration(unittest.TestCase):
    """Test that DataService is properly integrated into TM1Service"""

    tm1: TM1Service

    @classmethod
    def setUpClass(cls):
        """Establish connection to TM1"""
        cls.config = configparser.ConfigParser()
        cls.config.read(Path(__file__).parent.joinpath("config.ini"))
        cls.tm1 = TM1Service(**cls.config["tm1srv01"])

    def test_tm1_has_data_attribute(self):
        """TM1Service should have a 'data' attribute"""
        self.assertTrue(hasattr(self.tm1, 'data'))

    def test_tm1_data_is_dataservice(self):
        """tm1.data should be a DataService instance"""
        self.assertIsInstance(self.tm1.data, DataService)

    def test_tm1_data_has_cells_property(self):
        """tm1.data.cells should return CellService"""
        self.assertIsInstance(self.tm1.data.cells, CellService)

    def test_tm1_data_shares_rest_service(self):
        """tm1.data should share the same RestService as tm1"""
        self.assertIs(self.tm1.data._rest, self.tm1._tm1_rest)

    def test_tm1_data_version_matches(self):
        """tm1.data.version should match tm1.version"""
        self.assertEqual(self.tm1.data.version, self.tm1.version)

    def test_tm1_data_has_mdx_method(self):
        """tm1.data should have mdx() method"""
        self.assertTrue(hasattr(self.tm1.data, 'mdx'))

    def test_tm1_data_mdx_returns_executor(self):
        """tm1.data.mdx() should return QueryExecutor"""
        mdx_query = "SELECT FROM [SomeView]"
        executor = self.tm1.data.mdx(mdx_query)
        self.assertIsInstance(executor, QueryExecutor)

    def test_tm1_data_mdx_executor_has_mdx(self):
        """QueryExecutor should store the MDX query"""
        mdx_query = "SELECT FROM [SomeView]"
        executor = self.tm1.data.mdx(mdx_query)
        self.assertEqual(executor._mdx, mdx_query)

    def test_tm1_data_mdx_accepts_mdxbuilder(self):
        """tm1.data.mdx() should accept MdxBuilder objects"""
        mdx_builder = MdxBuilder.from_cube("SomeCube")
        executor = self.tm1.data.mdx(mdx_builder)
        self.assertIsInstance(executor, QueryExecutor)
        self.assertIsInstance(executor._mdx, MdxBuilder)

    def test_tm1_data_has_view_method(self):
        """tm1.data should have view() method"""
        self.assertTrue(hasattr(self.tm1.data, 'view'))

    def test_tm1_data_view_returns_executor(self):
        """tm1.data.view() should return ViewQueryExecutor"""
        executor = self.tm1.data.view('SomeCube', 'SomeView')
        self.assertIsInstance(executor, ViewQueryExecutor)

    def test_tm1_data_view_executor_has_cube_and_view(self):
        """ViewQueryExecutor should store cube and view names"""
        executor = self.tm1.data.view('SomeCube', 'SomeView')
        self.assertEqual(executor._cube_name, 'SomeCube')
        self.assertEqual(executor._view_name, 'SomeView')
        self.assertFalse(executor._private)

    def test_tm1_data_view_executor_private(self):
        """ViewQueryExecutor should handle private parameter"""
        executor = self.tm1.data.view('SomeCube', 'SomeView', private=True)
        self.assertTrue(executor._private)

    def test_tm1_data_has_coordinates_method(self):
        """tm1.data should have coordinates() method"""
        self.assertTrue(hasattr(self.tm1.data, 'coordinates'))

    def test_tm1_data_coordinates_returns_executor(self):
        """tm1.data.coordinates() should return CoordinateQueryExecutor"""
        executor = self.tm1.data.coordinates('SomeCube', ['Elem1', 'Elem2'])
        self.assertIsInstance(executor, CoordinateQueryExecutor)

    def test_tm1_data_coordinates_executor_has_cube_and_coords(self):
        """CoordinateQueryExecutor should store cube and coordinates"""
        coords = ['Elem1', 'Elem2', 'Elem3']
        executor = self.tm1.data.coordinates('SomeCube', coords)
        self.assertEqual(executor._cube_name, 'SomeCube')
        self.assertEqual(list(executor._coordinates), coords)

    @classmethod
    def tearDownClass(cls):
        """Close TM1 connection"""
        cls.tm1.logout()


if __name__ == "__main__":
    unittest.main()
