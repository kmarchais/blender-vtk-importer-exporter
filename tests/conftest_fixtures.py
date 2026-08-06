# Configuration of pytest fixtures
#   see https://docs.pytest.org/en/stable/reference/reference.html#fixtures

import numpy as np
import pyvista as pv

import pytest


@pytest.fixture(scope="session")
def pvUG_three_segments():
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
    vtk_data = pv.UnstructuredGrid(cells, celltypes, points)
    return vtk_data


@pytest.fixture(scope="session")
def pvUG_one_triangle():
    points = np.asarray(
        [[0.0, 0.0, 0.0],
         [1.0, 0.0, 0.0],
         [0.0, 1.0, 0.0]]
    )
    cells = np.asarray([3, 0, 1, 2])
    celltypes = [pv.CellType.TRIANGLE]
    vtk_data = pv.UnstructuredGrid(cells, celltypes, points)
    return vtk_data


@pytest.fixture(scope="session")
def pvPD_one_point():
    points = np.asarray([1.0, 2.0, 3.0])
    vtk_data = pv.PolyData(points)
    return vtk_data
    
