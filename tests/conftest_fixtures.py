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
def manufactured_fields(size=5): # size: largest number of cells or points
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
    

@pytest.fixture(scope="session")
def pvUG_three_segments(manufactured_fields):
    points = np.asarray(
        [[0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [0.0, 1.0, 0.0]]
    )
    cells = np.asarray(
        [2, 0, 1,
         2, 1, 2,
         2, 2, 0]
    )
    celltypes = np.full((len(cells)//3), pv.CellType.LINE)
    dataset = pv.UnstructuredGrid(cells, celltypes, points)
    set_attributes(dataset, manufactured_fields)
    return dataset
    

@pytest.fixture(scope="session")
def pvUG_one_triangle(manufactured_fields):
    points = np.asarray(
        [[0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [0.0, 1.0, 0.0]]
    )
    cells = np.asarray([3, 0, 1, 2])
    celltypes = [pv.CellType.TRIANGLE]
    dataset = pv.UnstructuredGrid(cells, celltypes, points)
    set_attributes(dataset, manufactured_fields)
    return dataset
    

@pytest.fixture(scope="session")
def pvPD_one_point(manufactured_fields):
    points = np.asarray([1.0, 2.0, 3.0])
    dataset = pv.PolyData(points)
    set_attributes(dataset, manufactured_fields)
    return dataset
    
