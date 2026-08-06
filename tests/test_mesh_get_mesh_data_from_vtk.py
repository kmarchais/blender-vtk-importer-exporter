# Unit tests of mesh.get_mesh_data_from_vtk()

import importlib

import numpy as np
import pyvista as pv


m_mesh = importlib.import_module("blender-vtk-importer-exporter-main.mesh")


class TestClass_UnstructuredGrid:
    
    def test_three_segments(self):
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
        vertices, edges, faces = m_mesh.get_mesh_data_from_vtk(vtk_data)
        n_vert_edge_face = (
            len(vertices),
            len(edges),
            len(faces)
        )
        assert n_vert_edge_face == (3, 3, 0)
        

    def test_one_triangle(self):
        points = np.asarray(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0]]
        )
        cells = np.asarray([3, 0, 1, 2])
        celltypes = [pv.CellType.TRIANGLE]
        vtk_data = pv.UnstructuredGrid(cells, celltypes, points)
        vertices, edges, faces = m_mesh.get_mesh_data_from_vtk(vtk_data)
        n_vert_edge_face = (
            len(vertices),
            len(edges),
            len(faces)
        )
        assert n_vert_edge_face == (3, 0, 1)
        
