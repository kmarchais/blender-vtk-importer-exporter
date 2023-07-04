import os

import bpy
from bpy.app.handlers import persistent

import numpy as np
import pyvista as pv

def initialize_material_attributes(attr_name, attr_values, mesh, material, domain):
    if attr_name == "id":
        attr_name = "id_" # id is a reserved keyword
    value_type = 'FLOAT' if len(attr_values.shape) == 1 else 'FLOAT_VECTOR'
    attr = mesh.attributes.new(attr_name, type=value_type, domain=domain)
    attr.data.foreach_set('value', attr_values)

    min_value = np.min(attr_values).item()
    max_value = np.max(attr_values).item()
    material["attributes"][attr_name] = {
        "current_frame_min": min_value,
        "current_frame_max": max_value,
        "global_min": min_value,
        "global_max": max_value
    }

def update_material_attributes(attr_name, attr_values, mesh, material, domain):
    frame_min = np.min(attr_values).item()
    frame_max = np.max(attr_values).item()

    if attr_name == "id":
        attr_name = "id_"
    if attr_name not in mesh.attributes.keys():
        value_type = 'FLOAT' if len(attr_values.shape) == 1 else 'FLOAT_VECTOR'
        mesh.attributes.new(attr_name, type=value_type, domain=domain)
        material["attributes"][attr_name] = {
            "current_frame_min": frame_min,
            "current_frame_max": frame_max,
            "global_min": frame_min,
            "global_max": frame_max
        }
    mesh.attributes[attr_name].data.foreach_set('value', attr_values)

    global_min = material["attributes"][attr_name]["global_min"]
    global_max = material["attributes"][attr_name]["global_max"]
    print(f"attribute : {attr_name}\tmin : {frame_min}\tmax : {frame_max}\tglobal_min : {global_min}\tglobal_max : {global_max}")
    material["attributes"][attr_name]["current_frame_min"] = frame_min
    material["attributes"][attr_name]["current_frame_max"] = frame_max
    material["attributes"][attr_name]["global_min"] = min(frame_min, global_min)
    material["attributes"][attr_name]["global_max"] = max(frame_max, global_max)




@persistent
def update_attributes_from_vtk(scene):
    if "vtk_files" not in bpy.context.scene and "vtk_directory" not in bpy.context.scene:
        return

    frame = scene.frame_current
    print(f"\nframe : {frame}")

    files = bpy.context.scene["vtk_files"]
    directory = bpy.context.scene["vtk_directory"]

    for file in files:
        mesh_name = file[0].split(".")[0].split("-")[0]
        print(f"\nmesh : {mesh_name}")

        if len(file) > 1:
            polydata = pv.read(f"{directory}/{file[frame]}")
            mesh = bpy.data.meshes[mesh_name]

            mesh.attributes["position"].data.foreach_set('vector', np.ravel(polydata.points))
            mat = bpy.data.materials[f"{mesh_name}_attributes"]

            for attr_name, values in polydata.point_data.items():
                update_material_attributes(attr_name, values, mesh, mat, 'POINT')

            for attr_name, values in polydata.cell_data.items():
                update_material_attributes(attr_name, values, mesh, mat, 'FACE')

            mesh.update()

    print("-" * os.get_terminal_size().columns)
