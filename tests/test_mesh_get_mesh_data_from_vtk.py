# Unit tests of mesh.get_mesh_data_from_vtk()

import pytest

from utilities import *


m_mesh = import_submodule("mesh")


# Parametrization of the characteristics of a test case
#   name:       Name of the fixture manufacturing the dataset
#               see conftest_fixtures.py
#   n_vertices: Expected number of points
#   n_edges:    Expected number of edges
#   n_faces:    Expected number of faces
#               Can be different according to the type of PyVista DataSet
#               Set to -1 for non-testable types of cell (e.g. PIXEL not supported by PolyData)
#   xout:       Expected result of a test. Supported values are:
#               - pass: no failure
#               - skip_ntest: to skip non-testable types of cell
#               - xfail_dline: expected failure because lines are not yet supported from PolyData
#               - xfail_vsize: expected failure because variable sizes are not yet supported from UnstructuredGrid
@pytest.mark.parametrize(
    "name, n_vertices, n_edges, n_faces, xout",
    [
        pytest.param(
            "PolyData_one_vertex", 1, 0, 0,
            {"PolyData": "pass", "UnstructuredGrid": "pass"}, id="one_vertex",
        ),
        pytest.param(
            "PolyData_one_polyvertex", 2, 0, 0,
            {"PolyData": "pass", "UnstructuredGrid": "xfail_vsize"}, id="one_polyvertex"
        ),
        pytest.param(
            "PolyData_one_line", 2, 1, 0,
            {"PolyData": "xfail_dline", "UnstructuredGrid": "pass"}, id="one_line"
        ),
        pytest.param(
            "PolyData_one_polyline", 3, 2, 0,
            {"PolyData": "xfail_dline", "UnstructuredGrid": "xfail_vsize"}, id="one_polyline"
        ),
        pytest.param(
            "PolyData_one_triangle", 3, 0, 1,
            {"PolyData": "pass", "UnstructuredGrid": "pass"}, id="one_triangle"
        ),
        pytest.param(
            "PolyData_one_quad", 4, 0, {"PolyData": 2, "UnstructuredGrid": 1},
            {"PolyData": "pass", "UnstructuredGrid": "pass"}, id="one_quad"
        ),
        pytest.param(
            "PolyData_one_polygon", 6, 0, {"PolyData": 4, "UnstructuredGrid": 1},
            {"PolyData": "pass", "UnstructuredGrid": "xfail_vsize"}, id="one_polygon"
        ),
        pytest.param(
            "PolyData_one_strip", 4, 0, 2,
            {"PolyData": "pass", "UnstructuredGrid": "xfail_vsize"}, id="one_strip"
        ),
        pytest.param(
            "PolyData_one_merged", 25, 3, {"PolyData": 9, "UnstructuredGrid": 5},
            {"PolyData": "xfail_dline", "UnstructuredGrid": "xfail_vsize"}, id="one_merged"
        ),
        pytest.param(
            "UnstructuredGrid_one_pixel", 4, 0, {"PolyData": -1, "UnstructuredGrid": 1},
            {"PolyData": "skip_ntest", "UnstructuredGrid": "pass"}, id="one_pixel"
        ),
        pytest.param(
            "UnstructuredGrid_one_tetrahedron", 4, 0, {"PolyData": -1, "UnstructuredGrid": 0},
            {"PolyData": "skip_ntest", "UnstructuredGrid": "pass"}, id="one_tetrahedron"
        ),
        pytest.param(
            "UnstructuredGrid_one_shuffled", 37, 7, {"PolyData": -1, "UnstructuredGrid": 10},
            {"PolyData": "skip_ntest", "UnstructuredGrid": "xfail_vsize"}, id="one_shuffled"
        ),
        pytest.param(
            "PolyData_two_vertexes", 2, 0, 0,
            {"PolyData": "pass", "UnstructuredGrid": "pass"}, id="two_vertexes"
        ),
        pytest.param(
            "PolyData_two_polyvertexes", 5, 0, 0,
            {"PolyData": "pass", "UnstructuredGrid": "xfail_vsize"}, id="two_polyvertexes"
        ),
        pytest.param(
            "PolyData_two_lines", 3, 2, 0,
            {"PolyData": "xfail_dline", "UnstructuredGrid": "pass"}, id="two_lines"
        ),
        pytest.param(
            "PolyData_two_polylines", 6, 5, 0,
            {"PolyData": "xfail_dline", "UnstructuredGrid": "xfail_vsize"}, id="two_polylines"
        ),
        pytest.param(
            "PolyData_two_triangles", 4, 0, 2,
            {"PolyData": "pass", "UnstructuredGrid": "pass"}, id="two_triangles"
        ),
        pytest.param(
            "PolyData_two_quads", 6, 0, {"PolyData": 4, "UnstructuredGrid": 2},
            {"PolyData": "pass", "UnstructuredGrid": "pass"}, id="two_quads"
        ),
        pytest.param(
            "PolyData_two_polygons", 9, 0, {"PolyData": 7, "UnstructuredGrid": 2},
            {"PolyData": "pass", "UnstructuredGrid": "xfail_vsize"}, id="two_polygons"
        ),
        pytest.param(
            "PolyData_two_strips", 7, 0, 5,
            {"PolyData": "pass", "UnstructuredGrid": "xfail_vsize"}, id="two_strips"
        ),
        pytest.param(
            "PolyData_two_merged", 31, 7, {"PolyData": 18, "UnstructuredGrid": 8},
            {"PolyData": "xfail_dline", "UnstructuredGrid": "xfail_vsize"}, id="two_merged"
        ),
        pytest.param(
            "UnstructuredGrid_two_pixels", 6, 0, {"PolyData": -1, "UnstructuredGrid": 2},
            {"PolyData": "skip_ntest", "UnstructuredGrid": "pass"}, id="two_pixels"
        ),
        pytest.param(
            "UnstructuredGrid_two_tetrahedrons", 6, 0, {"PolyData": -1, "UnstructuredGrid": 0},
            {"PolyData": "skip_ntest", "UnstructuredGrid": "pass"}, id="two_tetrahedrons"
        ),
        pytest.param(
            "UnstructuredGrid_two_shuffled", 37, 7, {"PolyData": -1, "UnstructuredGrid": 10},
            {"PolyData": "skip_ntest", "UnstructuredGrid": "xfail_vsize"}, id="two_shuffled"
        ),
    ],
)

# Parametrization of the type of PyVista DataSet
@pytest.mark.parametrize("dataset_type", ["PolyData", "UnstructuredGrid"])

class TestClass:
    
    def test_counts(
        self,
        dataset_type,
        name, n_vertices, n_edges, n_faces, xout,
        request
    ):
        match xout[dataset_type]:
            case "pass":
                pass
            case "skip_ntest":
                pytest.skip("Non-testable type(s) of cell")
            case "xfail_dline":
                request.node.add_marker(pytest.mark.xfail(
                    reason="PolyData conversion currently drops line cells",
                    raises=AssertionError,
                    strict=True,
                ))
            case "xfail_vsize":
                request.node.add_marker(pytest.mark.xfail(
                    reason="cells_dict cannot handle these variable-size cells",
                    raises=ValueError,
                    strict=True,
                ))
            case _:
                msg = f"Unsupported expected result: {xout[dataset_type]}."
                raise ValueError(msg)
                
        dataset = request.getfixturevalue(name)
        match dataset_type:
            case "PolyData":
                vtk_data = dataset
            case "UnstructuredGrid":
                vtk_data = dataset.cast_to_unstructured_grid()
            case _:
                msg = f"Unsupported PyVista DataSet type: {dataset_type}."
                raise ValueError(msg)
                
        vertices, edges, faces = m_mesh.get_mesh_data_from_vtk(vtk_data)

        assert len(vertices) == n_vertices
        assert len(edges)    == n_edges
        if isinstance(n_faces, dict):
            assert len(faces) == n_faces[dataset_type]
        else:
            assert len(faces) == n_faces


@pytest.mark.xfail(
    reason="PIXEL connectivity needs perimeter ordering for Blender",
    raises=AssertionError,
    strict=True,
)
def test_pixel_connectivity(UnstructuredGrid_two_pixels):
    _, _, faces = m_mesh.get_mesh_data_from_vtk(UnstructuredGrid_two_pixels)
    assert [list(face) for face in faces] == [
        [0, 1, 4, 3],
        [1, 2, 5, 4],
    ]
        
