import bpy
import numpy as np
import pyvista as pv
from .nodes import convert_mesh_to_pointcloud, create_attribute_material_nodes
from .attributes import initialize_material_attributes

def create_mesh(data_object, mesh_name):
    edges = []
    faces = []

    if isinstance(data_object, pv.PolyData):
        if not data_object.is_all_triangles:
            data_object = data_object.triangulate()
        faces = np.reshape(data_object.faces, (data_object.n_faces, 4))[:, 1:]

    if isinstance(data_object, pv.UnstructuredGrid):
        for cell_type, cells in data_object.cells_dict.items():
            if cell_type == pv.CellType.LINE.value:
                edges = cells
            elif cell_type == pv.CellType.TRIANGLE.value:
                faces = cells
            else:
                print(f"Unsupported cell type: {cell_type} yet.")

    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(vertices=data_object.points, edges=edges, faces=faces)
    mesh.update()

    obj = bpy.data.objects.new(mesh_name, mesh)
    obj["data_range"] = {}
    bpy.context.scene.collection.objects.link(obj)

    if len(data_object.point_data.keys()) or len(data_object.cell_data.keys()):
        mat = bpy.data.materials.new(name=f"{mesh_name}_attributes")
        mat["attributes"] = {}

        for attr_name, values in data_object.point_data.items():
            initialize_material_attributes(attr_name, values, mesh, mat, 'POINT')

        for attr_name, values in data_object.cell_data.items():
            initialize_material_attributes(attr_name, values, mesh, mat, 'FACE')

        create_attribute_material_nodes(mesh_name)

    if len(faces) == 0 and len(edges) == 0 and "radius" in data_object.point_data.keys():
        convert_mesh_to_pointcloud(mesh_name)
