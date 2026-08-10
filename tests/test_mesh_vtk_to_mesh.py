# Unit tests of mesh.vtk_to_mesh()

import bpy

from utilities import *


m_mesh = import_submodule("mesh")


class TestClass:

    def test_bpy_data_meshes_update(self, pvPD_one_point):
        mesh_name = unique_mesh_name()
        mesh = m_mesh.vtk_to_mesh(
            pvPD_one_point,
            mesh_name
        )
        assert bpy.data.meshes.find(mesh_name) != -1 # "find != -1" means "found"
        

    def test_one_triangle(self, pvUG_one_triangle):
        mesh = m_mesh.vtk_to_mesh(
            pvUG_one_triangle,
            unique_mesh_name()
        )
        assert len(mesh.vertices) == 3
        assert len(mesh.edges)    == 3
        assert len(mesh.polygons) == 1
        
