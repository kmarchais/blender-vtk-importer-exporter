# Unit tests of mesh.get_mesh_data_from_vtk()

import importlib


m_mesh = importlib.import_module("blender-vtk-importer-exporter-main.mesh")


class TestClass_UnstructuredGrid:
    
    def test_three_segments(self, pvUG_three_segments):
        vertices, edges, faces = m_mesh.get_mesh_data_from_vtk(
            pvUG_three_segments
        )
        assert len(vertices) == 3
        assert len(edges)    == 3
        assert len(faces)    == 0
        

    def test_one_triangle(self, pvUG_one_triangle):
        vertices, edges, faces = m_mesh.get_mesh_data_from_vtk(
            pvUG_one_triangle
        )
        assert len(vertices) == 3
        assert len(edges)    == 0
        assert len(faces)    == 1
        
