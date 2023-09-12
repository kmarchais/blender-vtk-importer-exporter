from typing import Union

import bpy
import numpy as np
import pyvista as pv
from .nodes import convert_mesh_to_pointcloud, create_attribute_material_nodes
from .attributes import initialize_material_attributes
from .material_panel import update_attributes_enum

VTK_data = Union[pv.PolyData, pv.UnstructuredGrid]

def get_mesh_data_from_vtk(vtk_data: VTK_data):
    edges = []
    faces = []

    if isinstance(vtk_data, pv.PolyData):
        if not vtk_data.is_all_triangles:
            vtk_data = vtk_data.triangulate()
        faces = np.reshape(vtk_data.faces, (vtk_data.n_faces, 4))[:, 1:]

    if isinstance(vtk_data, pv.UnstructuredGrid):
        faces = []
        for cell_type, cells in vtk_data.cells_dict.items():
            if cell_type == pv.CellType.LINE.value:
                edges = cells
            elif pv.CellType.TRIANGLE.value <= cell_type <= pv.CellType.QUAD.value:
                faces += cells
            else:
                print(f"Unsupported cell type: {cell_type} yet.")

    return vtk_data.points, edges, faces

def update_mesh_from_vtk(mesh: bpy.types.Mesh, vtk_data: VTK_data, update_attributes: bool = True):
    vertices, edges, faces = get_mesh_data_from_vtk(vtk_data)

    mesh.clear_geometry()
    mesh.from_pydata(vertices=vertices, edges=edges, faces=faces)

    if update_attributes:
        set_mesh_attributes(mesh, vtk_data)

def vtk_to_mesh(vtk_data, mesh_name):
    vertices, edges, faces = get_mesh_data_from_vtk(vtk_data)

    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(vertices=vertices, edges=edges, faces=faces)
    mesh.update()

    return mesh

def set_mesh_attributes(mesh, vtk_data):
    # create mesh attributes
    pass

    # for attr_name, values in data_object.point_data.items():
    #     initialize_material_attributes(attr_name, values, mesh, mesh.materials[0], 'POINT')

    # for attr_name, values in data_object.cell_data.items():
    #     initialize_material_attributes(attr_name, values, mesh, mesh.materials[0], 'FACE')

def create_object(context, vtk_data, mesh_name) -> bpy.types.Object:
    # convert vtk mesh to blender mesh
    # if attributes exist
    # - create material for attributes
    # - set vtk data into mesh attributes
    # create blender object
    # convert mesh to point cloud if it is point cloud
    mesh = vtk_to_mesh(vtk_data, mesh_name)

    mesh_name = mesh.name
    obj = bpy.data.objects.new(mesh_name, mesh)
    # obj.location = vtk_data.center
    obj["data_range"] = {}
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    if vtk_data.point_data or vtk_data.cell_data:
        mat = bpy.data.materials.new(name=f"{mesh_name}_attributes")
        mat["attributes"] = {}

        for attr_name, values in vtk_data.point_data.items():
            initialize_material_attributes(attr_name, values, mesh, mat, 'POINT')

        for attr_name, values in vtk_data.cell_data.items():
            initialize_material_attributes(attr_name, values, mesh, mat, 'FACE')

        create_attribute_material_nodes(mesh_name)
        update_attributes_enum(mat, context)

    is_point_cloud = len(mesh.polygons) + len(mesh.edges) == 0 and "radius" in vtk_data.point_data
    if is_point_cloud:
        convert_mesh_to_pointcloud(mesh_name)

    return obj
