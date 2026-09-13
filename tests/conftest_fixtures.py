# Configuration of pytest fixtures
#   see https://docs.pytest.org/en/stable/reference/reference.html#fixtures

import numpy as np
import pyvista as pv
from vtk import vtkDataSetAttributes as vtkAttributeTypes

import pytest

from conftest_utilities import *


# Scalar, vector and tensor fields with strictly ordered values
#   Examples with integers and size=3:
#   scalars: [ 1,   vectors: [[ 1,  2,  3],   tcoords: [[ 8,  9],
#             11,             [11, 12, 13],             [18, 19],
#             21]             [21, 22, 23]]             [28, 29]]
#   tensors: [[ 1,  2,  3,  4,  5,  6,  7,  8,  9],
#             [11, 12, 13, 14, 15, 16, 17, 18, 19],
#             [21, 22, 23, 24, 25, 26, 27, 28, 29]]
@pytest.fixture(scope="session")
def manufactured_fields(size=41): # size: largest number of cells or points
    # Table [t(i,j)] such that t(i,j) = j + 10*i
    #   with i index of line and j index of column
    #   i and j start at 0
    int_indices = np.arange(size*10).reshape((size,-1))
    
    # List of (name, type, array)
    fields = [
        ("int_scalars", vtkAttributeTypes.SCALARS, int_indices[:,1]  ),
        ("int_vectors", vtkAttributeTypes.VECTORS, int_indices[:,1:4]),
        ("int_tensors", vtkAttributeTypes.TENSORS, int_indices[:,1:] ),
        ("flt_scalars", vtkAttributeTypes.SCALARS, int_indices[:,0]   + 0.5),
        ("flt_vectors", vtkAttributeTypes.VECTORS, int_indices[:,0:3] + 0.5),
        ("flt_normals", vtkAttributeTypes.NORMALS, int_indices[:,3:6] + 0.5),
        ("flt_tcoords", vtkAttributeTypes.TCOORDS, int_indices[:,8:]  + 0.5),
        ("flt_tensors", vtkAttributeTypes.TENSORS, int_indices[:,1:]  + 0.5)
    ]
    return fields
    

# VERTEX cells
@pytest.fixture(scope="session")
def PolyData_two_vertexes(manufactured_fields, request):
    points = np.asarray(
        [[3.0, 1.5, 3.0],
         [3.0, 2.0, 3.0]]
    )
    verts = np.hstack(
        [[1, 0],
         [1, 1]]
    )
    return make_PolyData(
        request, 
        points, manufactured_fields, 
        verts=verts
    )
    

# POLY_VERTEX cells
@pytest.fixture(scope="session")
def PolyData_two_polyvertexes(manufactured_fields, request):
    points = np.asarray(
        [[0.0, 1.0, 3.0],
         [0.0, 1.5, 3.0],
         [1.0, 1.0, 3.0],
         [1.5, 1.0, 3.0],
         [1.0, 1.5, 3.0]]
    )
    verts = np.hstack(
        [[2, 0, 1],
         [3, 2, 3, 4]]
    )
    return make_PolyData(
        request, 
        points, manufactured_fields, 
        verts=verts
    )
    

# LINE cells
@pytest.fixture(scope="session")
def PolyData_two_lines(manufactured_fields, request):
    points = np.asarray(
        [[1.0, 3.0, 3.0],
         [1.0, 3.5, 3.0],
         [0.0, 4.5, 3.0]]
    )
    lines = np.hstack(
        [[2, 1, 2],
         [2, 0, 1]]
    )
    return make_PolyData(
        request, 
        points, manufactured_fields, 
        lines=lines
    )
    

# POLY_LINE cells
@pytest.fixture(scope="session")
def PolyData_two_polylines(manufactured_fields, request):
    points = np.asarray(
        [[2.0, 3.0, 3.0],
         [2.0, 3.5, 3.0],
         [2.5, 4.5, 3.0],
         [3.0, 4.5, 3.0],
         [3.0, 4.0, 3.0],
         [2.5, 3.5, 3.0]]
    )
    lines = np.hstack(
        [[3, 5, 4, 3],
         [4, 3, 2, 1, 0]]
    )
    return make_PolyData(
        request, 
        points, manufactured_fields, 
        lines=lines
    )
    

# TRIANGLE cells
@pytest.fixture(scope="session")
def PolyData_two_triangles(manufactured_fields, request):
    points = np.asarray(
        [[1.0, 3.5, 3.0],
         [2.0, 3.5, 3.0],
         [2.0, 4.5, 3.0],
         [1.0, 4.5, 3.0]]
    )
    faces = np.hstack(
        [[3, 1, 2, 3],
         [3, 0, 1, 3]]
    )
    return make_PolyData(
        request, 
        points, manufactured_fields, 
        faces=faces
    )
    

# QUAD cells
@pytest.fixture(scope="session")
def PolyData_two_quads(manufactured_fields, request):
    points = np.asarray(
        [[1.0, 2.0, 3.0],
         [2.0, 2.0, 3.0],
         [3.0, 2.0, 3.0],
         [1.0, 3.0, 3.0],
         [2.0, 3.0, 3.0],
         [3.0, 3.5, 3.0]]
    )
    faces = np.hstack(
        [[4, 0, 1, 4, 3],
         [4, 1, 2, 5, 4]]
    )
    return make_PolyData(
        request, 
        points, manufactured_fields, 
        faces=faces
    )
    

# POLYGON cells
@pytest.fixture(scope="session")
def PolyData_two_polygons(manufactured_fields, request):
    points = np.asarray(
        [[1.0, 2.0, 3.0],
         [2.0, 2.0, 3.0],
         [2.0, 1.5, 3.0],
         [2.5, 1.5, 3.0],
         [3.0, 1.0, 3.0],
         [2.5, 0.5, 3.0],
         [2.0, 0.5, 3.0],
         [1.5, 1.0, 3.0],
         [1.0, 1.5, 3.0]]
    )
    faces = np.hstack(
        [[6, 7, 6, 5, 4, 3, 2],
         [5, 7, 2, 1, 0, 8]]
    )
    return make_PolyData(
        request, 
        points, manufactured_fields, 
        faces=faces
    )
    

# TRIANGLE_STRIP cells
@pytest.fixture(scope="session")
def PolyData_two_strips(manufactured_fields, request):
    points = np.asarray(
        [[-2.0, 1.0, 3.0],
         [-1.0, 1.0, 3.0],
         [-1.0, 2.0, 3.0],
         [ 0.0, 2.0, 3.0],
         [ 1.0, 2.0, 3.0],
         [ 0.0, 3.0, 3.0],
         [ 1.0, 3.0, 3.0]]
    )
    strips = np.hstack(
        [[4, 0, 1, 2, 3],
         [5, 2, 5, 3, 6, 4]]
    )
    return make_PolyData(
        request, 
        points, manufactured_fields, 
        strips=strips
    )
    

# PIXEL cells
@pytest.fixture(scope="session")
def UnstructuredGrid_two_pixels(manufactured_fields, request):
    points = np.asarray(
        [[-1.0, 4.5, 3.0],
         [-0.5, 4.5, 3.0],
         [ 0.0, 4.5, 3.0],
         [-1.0, 5.0, 3.0],
         [-0.5, 5.0, 3.0],
         [ 0.0, 5.0, 3.0]]
    )
    cells = np.hstack(
        [[4, 0, 1, 3, 4],
         [4, 1, 2, 4, 5]]
    )
    celltypes = np.full(
        2,
        pv.CellType.PIXEL, dtype=np.int8
    )
    return make_UnstructuredGrid(
        request, 
        points, manufactured_fields, 
        cells, celltypes
    )
    

# TETRA cells
@pytest.fixture(scope="session")
def UnstructuredGrid_two_tetrahedrons(manufactured_fields, request):
    points = np.asarray(
        [[-2.0, 3.0, 3.0],
         [-1.0, 3.0, 3.0],
         [-2.0, 4.0, 3.0],
         [-1.0, 4.0, 2.0],
         [-2.0, 5.0, 3.0],
         [-1.0, 5.0, 3.0]]
    )
    cells = np.hstack(
        [[4, 0, 2, 1, 3],
         [4, 2, 4, 5, 3]]
    )
    celltypes = np.full(
        2,
        pv.CellType.TETRA, dtype=np.int8
    )
    return make_UnstructuredGrid(
        request, 
        points, manufactured_fields, 
        cells, celltypes
    )
    

# Merging of single type datasets

@pytest.fixture(scope="session")
def PolyData_two_merged(
    PolyData_two_vertexes,
    PolyData_two_polyvertexes,
    PolyData_two_lines,
    PolyData_two_polylines,
    PolyData_two_triangles,
    PolyData_two_quads,
    PolyData_two_polygons,
    PolyData_two_strips,
    manufactured_fields,
    request
):
    dataset = merge_datasets(
        request, manufactured_fields,
        name_list=list(locals().keys())[:-2] # -2 to skip "manufactured_fields" and "request"
    )
    dump_dataset(dataset, request)
    return dataset
    

@pytest.fixture(scope="session")
def UnstructuredGrid_two_shuffled(
    PolyData_two_merged,
    UnstructuredGrid_two_pixels,
    UnstructuredGrid_two_tetrahedrons,
    manufactured_fields,
    request
):
    full_dataset = merge_datasets(
        request, manufactured_fields,
        name_list=list(locals().keys())[:-2] # -2 to skip "manufactured_fields" and "request"
    )
    dataset = merge_datasets(
        request, manufactured_fields,
        dataset_list=[
            remove_cells(full_dataset, invert_selection=False),
            remove_cells(full_dataset, invert_selection=True)
        ]
    )
    dump_dataset(dataset, request)    
    return dataset
    

# Manufacturing of the datasets with a single cell

@pytest.fixture(scope="session")
def PolyData_one_vertex(PolyData_two_vertexes, request):
    return strip_dataset(PolyData_two_vertexes, request)
    

@pytest.fixture(scope="session")
def PolyData_one_polyvertex(PolyData_two_polyvertexes, request):
    return strip_dataset(PolyData_two_polyvertexes, request)
    

@pytest.fixture(scope="session")
def PolyData_one_line(PolyData_two_lines, request):
    return strip_dataset(PolyData_two_lines, request)
    

@pytest.fixture(scope="session")
def PolyData_one_polyline(PolyData_two_polylines, request):
    return strip_dataset(PolyData_two_polylines, request)
    

@pytest.fixture(scope="session")
def PolyData_one_triangle(PolyData_two_triangles, request):
    return strip_dataset(PolyData_two_triangles, request)
    

@pytest.fixture(scope="session")
def PolyData_one_quad(PolyData_two_quads, request):
    return strip_dataset(PolyData_two_quads, request)
    

@pytest.fixture(scope="session")
def PolyData_one_polygon(PolyData_two_polygons, request):
    return strip_dataset(PolyData_two_polygons, request)
    

@pytest.fixture(scope="session")
def PolyData_one_strip(PolyData_two_strips, request):
    return strip_dataset(PolyData_two_strips, request)
    

@pytest.fixture(scope="session")
def PolyData_one_merged(PolyData_two_merged, request):
    return strip_dataset(PolyData_two_merged, request)
    

@pytest.fixture(scope="session")
def UnstructuredGrid_one_pixel(UnstructuredGrid_two_pixels, request):
    return strip_dataset(UnstructuredGrid_two_pixels, request)
    

@pytest.fixture(scope="session")
def UnstructuredGrid_one_tetrahedron(UnstructuredGrid_two_tetrahedrons, request):
    return strip_dataset(UnstructuredGrid_two_tetrahedrons, request)
    

@pytest.fixture(scope="session")
def UnstructuredGrid_one_shuffled(UnstructuredGrid_two_shuffled, request):
    return strip_dataset(UnstructuredGrid_two_shuffled, request)
    
