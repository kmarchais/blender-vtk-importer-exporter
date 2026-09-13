# Unit tests of mesh.vtk_to_mesh()

import bpy

import pytest

from utilities import *


m_mesh = import_submodule("mesh")


class TestClass:

    def test_bpy_data_meshes_update(self, PolyData_one_vertex):
        mesh_name = unique_mesh_name()
        mesh = m_mesh.vtk_to_mesh(
            PolyData_one_vertex,
            mesh_name
        )
        assert bpy.data.meshes.find(mesh_name) != -1 # "find != -1" means "found"
        

    # Parametrization of the type of PyVista DataSet
    @pytest.mark.parametrize("dataset_type", ["PolyData", "UnstructuredGrid"])
    def test_one_triangle(
        self,
        dataset_type,
        PolyData_one_triangle
    ):
        dataset = PolyData_one_triangle
        match dataset_type:
            case "PolyData":
                vtk_data = dataset
            case "UnstructuredGrid":
                vtk_data = dataset.cast_to_unstructured_grid()
            case _:
                msg = f"Unsupported PyVista DataSet type: {dataset_type}."
                raise ValueError(msg)
        
        mesh = m_mesh.vtk_to_mesh(
            vtk_data,
            unique_mesh_name()
        )
        
        assert len(mesh.vertices) == 3
        assert len(mesh.edges)    == 3
        assert len(mesh.polygons) == 1
        
