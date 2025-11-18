# -*- coding: utf-8 -*-
"""
Base test case class for TM1py tests.

This class provides shared test infrastructure (setup/teardown) for both CellService
and DataService tests, without inheriting test methods.
"""
import configparser
import unittest
from pathlib import Path

from mdxpy import MdxBuilder, MdxHierarchySet, Member

from TM1py import Sandbox
from TM1py.Objects import (
    AnonymousSubset,
    Cube,
    Dimension,
    Element,
    ElementAttribute,
    Hierarchy,
    MDXView,
    NativeView,
)
from TM1py.Services import TM1Service
from TM1py.Utils import Utils


class TM1pyTestCase(unittest.TestCase):
    """
    Base test case that provides shared test infrastructure.

    This class sets up test cubes, dimensions, views, and data that can be used
    by both CellService and DataService tests. It does NOT contain any test methods,
    so inheriting from it won't cause those tests to run.
    """

    tm1: TM1Service
    prefix = "TM1py_Tests_Cell_"
    cube_name = prefix + "Cube"
    view_name = prefix + "View"
    mdx_view_name = prefix + "MdxView"
    mdx_view_2_name = prefix + "MdxView2"
    dimension_names = [prefix + "Dimension1", prefix + "Dimension2", prefix + "Dimension3"]
    string_cube_name = prefix + "StringCube"
    string_dimension_names = [prefix + "StringDimension1", prefix + "StringDimension2", prefix + "StringDimension3"]
    cells_in_string_cube = {
        ("d1e1", "d2e1", "d3e1"): "String1",
        ("d1e2", "d2e2", "d3e2"): "String2",
        ("d1e3", "d2e3", "d3e3"): "String3",
    }

    latin_1_encoded_text = "Èd5áÂè"

    cube_rps1_name = prefix + "Cube" + "_RPS1"
    cube_rps2_name = prefix + "Cube" + "_RPS2"

    cube_with_consolidations_name = cube_name + "_With_Consolidations"
    dimensions_with_consolidations_names = [
        dimension_name + "_With_Consolidations" for dimension_name in dimension_names
    ]
    cube_with_rules_name = cube_name + "_With_Rules"

    dimension_rps1_name = prefix + "Dimension" + "_RPS1"
    dimension_rps2_name = prefix + "Dimension" + "_RPS2"

    sandbox_name = prefix + "sandbox"

    target_coordinates = list(
        zip(
            ("Element " + str(e) for e in range(1, 101)),
            ("Element " + str(e) for e in range(1, 101)),
            ("Element " + str(e) for e in range(1, 101)),
        )
    )

    dimension_with_hierarchies_name = prefix + "Dimension_With_Hierarchies"

    cube_with_five_dimensions = prefix + "Cube_with_five_dimensions"

    five_dimensions = [
        cube_with_five_dimensions + "_" + str(1),
        cube_with_five_dimensions + "_" + str(2),
        cube_with_five_dimensions + "_" + str(3),
        cube_with_five_dimensions + "_" + str(4),
        cube_with_five_dimensions + "_" + str(5),
    ]

    @classmethod
    def setUpClass(cls):
        """
        Establishes a connection to TM1 and creates TM1 objects to use across all tests
        """

        # Connection to TM1
        cls.config = configparser.ConfigParser()
        cls.config.read(Path(__file__).parent.joinpath("config.ini"))
        cls.tm1 = TM1Service(**cls.config["tm1srv01"])

        # Build Dimensions
        for dimension_name in cls.dimension_names:
            elements = [Element("Element {}".format(str(j)), "Numeric") for j in range(1, 1001)]

            element_attributes = [
                ElementAttribute("Attr1", "String"),
                ElementAttribute("Attr2", "Numeric"),
                ElementAttribute("Attr3", "Numeric"),
                ElementAttribute("NA", "Numeric"),
            ]
            hierarchy = Hierarchy(
                dimension_name=dimension_name,
                name=dimension_name,
                elements=elements,
                element_attributes=element_attributes,
            )
            dimension = Dimension(dimension_name, [hierarchy])
            if cls.tm1.dimensions.exists(dimension.name):
                cls.tm1.dimensions.update(dimension)
            else:
                cls.tm1.dimensions.update_or_create(dimension)

        cls._write_attribute_values()

        # Build Cube
        cube = Cube(cls.cube_name, cls.dimension_names)
        if not cls.tm1.cubes.exists(cls.cube_name):
            cls.tm1.cubes.update_or_create(cube)

        # Build cube view
        view = NativeView(
            cube_name=cls.cube_name, view_name=cls.view_name, suppress_empty_columns=True, suppress_empty_rows=True
        )
        view.add_row(
            dimension_name=cls.dimension_names[0],
            subset=AnonymousSubset(
                dimension_name=cls.dimension_names[0], expression="{[" + cls.dimension_names[0] + "].Members}"
            ),
        )
        view.add_row(
            dimension_name=cls.dimension_names[1],
            subset=AnonymousSubset(
                dimension_name=cls.dimension_names[1], expression="{[" + cls.dimension_names[1] + "].Members}"
            ),
        )
        view.add_column(
            dimension_name=cls.dimension_names[2],
            subset=AnonymousSubset(
                dimension_name=cls.dimension_names[2], expression="{[" + cls.dimension_names[2] + "].Members}"
            ),
        )
        if not cls.tm1.views.exists(cls.cube_name, view.name, private=False):
            cls.tm1.views.update_or_create(view=view, private=False)

        # build mdx cube view
        query = MdxBuilder.from_cube(cls.cube_name)
        query = query.rows_non_empty().columns_non_empty()
        query.add_hierarchy_set_to_row_axis(MdxHierarchySet.all_members(cls.dimension_names[0], cls.dimension_names[0]))
        query.add_hierarchy_set_to_row_axis(MdxHierarchySet.all_members(cls.dimension_names[1], cls.dimension_names[1]))
        query.add_hierarchy_set_to_column_axis(
            MdxHierarchySet.all_members(cls.dimension_names[2], cls.dimension_names[2])
        )
        mdx_view = MDXView(cls.cube_name, cls.mdx_view_name, query.to_mdx())
        cls.tm1.views.update_or_create(mdx_view, private=False)

        mdx = (
            MdxBuilder.from_cube(cls.cube_name)
            .add_member_tuple_to_columns(Member.of(cls.dimension_names[0], "Element 1"))
            .add_member_tuple_to_rows(Member.of(cls.dimension_names[1], "Element 1"))
            .add_member_to_where(Member.of(cls.dimension_names[2], "Element 1"))
            .to_mdx()
        )
        mdx_view = MDXView(cls.cube_name, view_name=cls.mdx_view_2_name, MDX=mdx)
        cls.tm1.views.update_or_create(mdx_view)

        cls.build_cube_with_rules()

        cls.build_cube_with_consolidations()

        # For tests on string related methods
        cls.build_string_cube()

        cls.build_assets_for_relative_proportional_spread()

        cls.create_or_update_dimension_with_hierarchies()

        cls.create_cube_with_five_dimensions()

    @classmethod
    def _write_attribute_values(cls):
        for dimension_name in cls.dimension_names:
            elements = [Element("Element {}".format(str(j)), "Numeric") for j in range(1, 1001)]
            attribute_cube = "}ElementAttributes_" + dimension_name
            attribute_values = {}
            for element in elements:
                attribute_values[(element.name, "Attr1")] = "TM1py" if element.name != "Element 2" else ""
                attribute_values[(element.name, "Attr2")] = "2"
                attribute_values[(element.name, "Attr3")] = "3"
                attribute_values[(element.name, "NA")] = "4"
            cls.tm1.cells.write(attribute_cube, attribute_values, use_blob=True)

    def setUp(self):
        """
        Reset data before each test run
        """
        # set correct version before test, as it is overwritten in a test case
        self.tm1._tm1_rest.set_version()

        # populate data in cube

        # cellset of data that shall be written
        self.cellset = Utils.CaseAndSpaceInsensitiveTuplesDict()
        value = 1
        for element1, element2, element3 in self.target_coordinates:
            self.cellset[(element1, element2, element3)] = value

        # Sum of all the values that we write in the cube. serves as a checksum.
        self.total_value = sum(self.cellset.values())

        # Fill cube with values
        self.tm1.cells.write_values(self.cube_name, self.cellset)

        self.tm1.cells.write_values(self.string_cube_name, self.cells_in_string_cube)

        if not self.tm1.sandboxes.exists(self.sandbox_name):
            self.tm1.sandboxes.create(Sandbox(self.sandbox_name, True))

        self._write_attribute_values()

    def tearDown(self):
        """
        Clear data from cubes after each test run
        """
        self.tm1.processes.execute_ti_code("CubeClearData('" + self.cube_name + "');")
        self.tm1.processes.execute_ti_code("CubeClearData('" + self.string_cube_name + "');")
        self.tm1.processes.execute_ti_code("CubeClearData('" + self.cube_rps1_name + "');")
        self.tm1.processes.execute_ti_code("CubeClearData('" + self.cube_rps2_name + "');")

    @classmethod
    def build_string_cube(cls):
        if cls.tm1.cubes.exists(cls.string_cube_name):
            cls.tm1.cubes.delete(cls.string_cube_name)

        for d, dimension_name in enumerate(cls.string_dimension_names, start=1):
            dimension = Dimension(dimension_name)
            hierarchy = Hierarchy(dimension_name, dimension_name)
            for i in range(1, 5, 1):
                element_name = "d" + str(d) + "e" + str(i)
                hierarchy.add_element(element_name=element_name, element_type="String")
            dimension.add_hierarchy(hierarchy)
            cls.tm1.dimensions.update_or_create(dimension)

        cube = Cube(name=cls.string_cube_name, dimensions=cls.string_dimension_names)
        cls.tm1.elements.add_elements(
            dimension_name=cube.dimensions[-1], hierarchy_name=cube.dimensions[-1], elements=[Element("n1", "Numeric")]
        )

        cls.tm1.cubes.update_or_create(cube)



    @classmethod
    def remove_string_cube(cls):
        if cls.tm1.cubes.exists(cube_name=cls.string_cube_name):
            cls.tm1.cubes.delete(cube_name=cls.string_cube_name)
        for dimension_name in cls.string_dimension_names:
            if cls.tm1.dimensions.exists(dimension_name=dimension_name):
                cls.tm1.dimensions.delete(dimension_name=dimension_name)

    @classmethod
    def build_cube_with_rules(cls):
        cube = Cube(name=cls.cube_with_rules_name, dimensions=cls.dimension_names)

        cube.rules = f"""
        ['{cls.dimension_names[0]}':'Element 1'] = N: 1;\r\n
        ['{cls.dimension_names[0]}':'Element 2'] = N: ['{cls.dimension_names[0]}':'Element 1'] ;\r\n
        ['{cls.dimension_names[0]}':'Element 3'] = N: ['{cls.dimension_names[0]}':'Element 2'] ;\r\n
        """
        cls.tm1.cubes.update_or_create(cube)

    @classmethod
    def remove_cube_with_rules(cls):
        cls.tm1.cubes.delete(cls.cube_with_rules_name)

    @classmethod
    def build_cube_with_consolidations(cls):
        for dimension_name_source, dimension_name_target in zip(
            cls.dimension_names, cls.dimensions_with_consolidations_names
        ):
            dimension = cls.tm1.dimensions.get(dimension_name=dimension_name_source)
            dimension.name = dimension_name_target
            hierarchy = dimension.get_hierarchy(dimension_name_target)
            for element in hierarchy:
                hierarchy.add_edge(parent="TOTAL_" + dimension_name_target, component=element.name, weight=1)
            hierarchy.add_element("TOTAL_" + dimension_name_target, "Consolidated")
            cls.tm1.dimensions.update_or_create(dimension)

        cube = Cube(name=cls.cube_with_consolidations_name, dimensions=cls.dimensions_with_consolidations_names)
        cls.tm1.cubes.update_or_create(cube)

    @classmethod
    def remove_cube_with_consolidations(cls):
        if cls.tm1.cubes.exists(cube_name=cls.cube_with_consolidations_name):
            cls.tm1.cubes.delete(cube_name=cls.cube_with_consolidations_name)
        for dimension_name in cls.dimensions_with_consolidations_names:
            if cls.tm1.dimensions.exists(dimension_name=dimension_name):
                cls.tm1.dimensions.delete(dimension_name=dimension_name)

    @classmethod
    def create_cube_with_five_dimensions(cls):
        for dimension_name in cls.five_dimensions:
            hierarchy = Hierarchy(
                dimension_name=dimension_name,
                name=dimension_name,
                elements=[Element("e1", "Numeric"), Element("e2", "Numeric"), Element("e3", "Numeric")],
            )
            dimension = Dimension(name=dimension_name, hierarchies=[hierarchy])
            cls.tm1.dimensions.update_or_create(dimension)
        cube = Cube(cls.cube_with_five_dimensions, dimensions=cls.five_dimensions)
        cls.tm1.cubes.update_or_create(cube)

        cells = {
            ("e1", "e1", "e1", "e1", "e1"): 1,
            ("e2", "e2", "e2", "e2", "e2"): 2,
            ("e3", "e3", "e3", "e3", "e3"): 3,
        }
        cls.tm1.cells.write(cls.cube_with_five_dimensions, cells)

    @classmethod
    def remove_cube_with_five_dimensions(cls):
        if cls.tm1.cubes.exists(cube_name=cls.cube_with_five_dimensions):
            cls.tm1.cubes.delete(cube_name=cls.cube_with_five_dimensions)
        for dimension_name in cls.five_dimensions:
            if cls.tm1.dimensions.exists(dimension_name=dimension_name):
                cls.tm1.dimensions.delete(dimension_name=dimension_name)

    @classmethod
    def build_assets_for_relative_proportional_spread(cls):
        # Build dimensions for RPS tests
        for dimension_name in [cls.dimension_rps1_name, cls.dimension_rps2_name]:
            elements = [Element("Element {}".format(str(j)), "Numeric") for j in range(1, 11)]
            hierarchy = Hierarchy(dimension_name=dimension_name, name=dimension_name, elements=elements)
            dimension = Dimension(dimension_name, [hierarchy])
            cls.tm1.dimensions.update_or_create(dimension)

        # Build cubes for RPS tests
        cube = Cube(cls.cube_rps1_name, [cls.dimension_rps1_name] + cls.dimension_names[1:])
        cls.tm1.cubes.update_or_create(cube)

        cube = Cube(cls.cube_rps2_name, cls.dimension_names[:1] + [cls.dimension_rps2_name] + cls.dimension_names[2:])
        cls.tm1.cubes.update_or_create(cube)

    @classmethod
    def remove_assets_for_relative_proportional_spread(cls):
        for cube_name in [cls.cube_rps1_name, cls.cube_rps2_name]:
            if cls.tm1.cubes.exists(cube_name):
                cls.tm1.cubes.delete(cube_name)
        for dimension_name in [cls.dimension_rps1_name, cls.dimension_rps2_name]:
            if cls.tm1.dimensions.exists(dimension_name):
                cls.tm1.dimensions.delete(dimension_name)

    @classmethod
    def create_or_update_dimension_with_hierarchies(cls):
        dimension = Dimension(cls.dimension_with_hierarchies_name)
        hierarchy = Hierarchy(name=cls.dimension_with_hierarchies_name, dimension_name=cls.dimension_with_hierarchies_name)
        hierarchy.add_element("Total Years", "Consolidated")
        hierarchy.add_element("No Year", "Numeric")
        for year in range(1989, 2040, 1):
            hierarchy.add_element(str(year), "Numeric")
            hierarchy.add_edge("Total Years", str(year), 1)
        dimension.add_hierarchy(hierarchy)
        cls.tm1.dimensions.update_or_create(dimension)

    # Delete Cube and Dimensions
    @classmethod
    def tearDownClass(cls):
        cls.tm1.cubes.delete(cls.cube_name)
        cls.remove_string_cube()
        cls.remove_cube_with_rules()
        cls.remove_cube_with_consolidations()
        cls.remove_cube_with_five_dimensions()
        for dimension_name in cls.dimension_names:
            cls.tm1.dimensions.delete(dimension_name)
        cls.remove_assets_for_relative_proportional_spread()

        if cls.tm1.sandboxes.exists(cls.sandbox_name):
            cls.tm1.sandboxes.delete(cls.sandbox_name)

        cls.tm1.dimensions.delete(cls.dimension_with_hierarchies_name)

        cls.tm1.logout()
