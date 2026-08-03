# Unitary tests of mesh.vtk_to_mesh()

import importlib

import numpy as np
import pyvista as pv


m_mesh = importlib.import_module("blender-vtk-importer-exporter-main.mesh")


class TestClass:
    
    def test_one_triangle(self):
        points = np.asarray(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0]]
        )
        cells = np.asarray([3, 0, 1, 2])
        celltypes = [pv.CellType.TRIANGLE]
        vtk_data = pv.UnstructuredGrid(cells, celltypes, points)
        mesh = m_mesh.vtk_to_mesh(vtk_data, "one_triangle")
        assert (
            (len(mesh.vertices), len(mesh.edges), len(mesh.polygons)) == 
            (                 3,               3,                  1)
        )
        