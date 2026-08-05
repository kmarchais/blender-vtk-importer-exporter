# Unitary tests of mesh.vtk_to_mesh()

import importlib

import numpy as np
import pyvista as pv

import bpy


m_mesh = importlib.import_module("blender-vtk-importer-exporter-main.mesh")


def unique_mesh_name():
    prefix_val = "pytest_mesh_"
    prefix_len = len(prefix_val)
    highest_suffix = 0
    for mesh_name in bpy.data.meshes.keys():
        if mesh_name.startswith(prefix_val):
            highest_suffix = max(
                highest_suffix,
                float(mesh_name[prefix_len:]) # float() is required to handle e.g. 2.001
            )
    return f"{prefix_val}{int(highest_suffix)+1}"


class TestClass:

    def test_bpy_data_meshes_update(self):
        vtk_data = pv.PolyData([1.0, 2.0, 3.0])
        mesh_name = unique_mesh_name()
        mesh = m_mesh.vtk_to_mesh(vtk_data, mesh_name)
        assert (bpy.data.meshes.find(mesh_name) != -1)
        

    def test_one_triangle(self):
        points = np.asarray(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0]]
        )
        cells = np.asarray([3, 0, 1, 2])
        celltypes = [pv.CellType.TRIANGLE]
        vtk_data = pv.UnstructuredGrid(cells, celltypes, points)
        mesh_name = unique_mesh_name()
        mesh = m_mesh.vtk_to_mesh(vtk_data, mesh_name)
        assert (
            (len(mesh.vertices), len(mesh.edges), len(mesh.polygons)) == 
            (                 3,               3,                  1)
        )
        
