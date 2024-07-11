import os
import warnings

import bpy
import numpy as np
import pyvista as pv


def initialize_material_attributes(attr_name, attr_values, mesh, material, domain):
    if attr_name == "id":
        attr_name = "id_"  # id is a reserved keyword

    value_type = "FLOAT"
    if len(attr_values.shape) == 2:
        if attr_values.shape[1] == 3:
            value_type = "FLOAT_VECTOR"
        elif attr_values.shape[1] == 2:
            value_type = "FLOAT2"
        # elif attr_values.shape[1] == 4:
        #     value_type = 'FLOAT_COLOR'
        else:
            warnings.warn(
                f"Unsupported attribute shape: {attr_values.shape} for attribute {attr_name}",
                stacklevel=2,
            )
    attr = mesh.attributes.new(attr_name, type=value_type, domain=domain)

    if len(attr_values.shape) == 1:
        attr_type = "value"
        attr.data.foreach_set(attr_type, attr_values)

        min_value = np.min(attr_values).item()
        max_value = np.max(attr_values).item()

        material["attributes"][attr_name] = {
            "current_frame_min": min_value,
            "current_frame_max": max_value,
            "global_min": min_value,
            "global_max": max_value,
        }
    elif len(attr_values.shape) == 2:
        if attr_values.shape[1] in [2, 3]:
            attr_type = "vector"
            attr.data.foreach_set(attr_type, attr_values.flatten())
            # elif attr_values.shape[1] == 4:
            #     attr_type = 'color'

            magnitude = np.linalg.norm(attr_values, axis=1)
            min_value = np.min(magnitude).item()
            max_value = np.max(magnitude).item()

            material["attributes"][attr_name] = {}

            material["attributes"][attr_name]["Magnitude"] = {
                "current_frame_min": min_value,
                "current_frame_max": max_value,
                "global_min": min_value,
                "global_max": max_value,
            }

            components = ["X", "Y", "Z"] if attr_values.shape[1] == 3 else ["X", "Y"]
            for component in components:
                index = components.index(component)
                min_value = np.min(attr_values[:, index]).item()
                max_value = np.max(attr_values[:, index]).item()

                material["attributes"][attr_name][component] = {
                    "current_frame_min": min_value,
                    "current_frame_max": max_value,
                    "global_min": min_value,
                    "global_max": max_value,
                }
        else:
            warnings.warn(
                f"Unsupported attribute shape: {attr_values.shape} for attribute {attr_name}",
                stacklevel=2,
            )
    else:
        warnings.warn(
            f"Unsupported attribute shape: {attr_values.shape} for attribute {attr_name}",
            stacklevel=2,
        )


def update_material_attributes(attr_name, attr_values, mesh, material, domain):
    frame_min = np.min(attr_values).item()
    frame_max = np.max(attr_values).item()

    if attr_name == "id":
        attr_name = "id_"
    if attr_name not in mesh.attributes.keys():
        value_type = "FLOAT"
        if len(attr_values.shape) == 2:
            if attr_values.shape[1] == 3:
                value_type = "FLOAT_VECTOR"
            elif attr_values.shape[1] == 2:
                value_type = "FLOAT2"
            # elif attr_values.shape[1] == 4:
            #     value_type = 'FLOAT_COLOR'
            else:
                warnings.warn(
                    f"Unsupported attribute shape: {attr_values.shape} for attribute {attr_name}",
                    stacklevel=2,
                )

            component = "Magnitude"
            if component == "Magnitude":
                array = np.linalg.norm(attr_values, axis=1)
            # elif component in ['X', 'Y', 'Z']:
            #     index = ['X', 'Y', 'Z'].index(component)
            #     array = attr_values[:, index]
            frame_min = np.min(array).item()
            frame_max = np.max(array).item()

        mesh.attributes.new(attr_name, type=value_type, domain=domain)

        if value_type == "FLOAT":
            material["attributes"][attr_name] = {
                "current_frame_min": frame_min,
                "current_frame_max": frame_max,
                "global_min": frame_min,
                "global_max": frame_max,
            }
        elif value_type in {"FLOAT_VECTOR", "FLOAT2"}:
            material["attributes"][attr_name] = {}
            component = "Magnitude"
            material["attributes"][attr_name][component] = {
                "current_frame_min": frame_min,
                "current_frame_max": frame_max,
                "global_min": frame_min,
                "global_max": frame_max,
            }

    if len(attr_values.shape) == 1:
        attr_type = "value"
        mesh.attributes[attr_name].data.foreach_set(attr_type, attr_values)

        global_min = material["attributes"][attr_name]["global_min"]
        global_max = material["attributes"][attr_name]["global_max"]

        material["attributes"][attr_name]["current_frame_min"] = frame_min
        material["attributes"][attr_name]["current_frame_max"] = frame_max
        material["attributes"][attr_name]["global_min"] = min(frame_min, global_min)
        material["attributes"][attr_name]["global_max"] = max(frame_max, global_max)
    elif len(attr_values.shape) == 2:
        if attr_values.shape[1] in [2, 3]:
            attr_type = "vector"
            mesh.attributes[attr_name].data.foreach_set(
                attr_type, attr_values.flatten()
            )

            component = "Magnitude"
            global_min = material["attributes"][attr_name][component]["global_min"]
            global_max = material["attributes"][attr_name][component]["global_max"]

            material["attributes"][attr_name][component]["current_frame_min"] = (
                frame_min
            )
            material["attributes"][attr_name][component]["current_frame_max"] = (
                frame_max
            )
            material["attributes"][attr_name][component]["global_min"] = min(
                frame_min, global_min
            )
            material["attributes"][attr_name][component]["global_max"] = max(
                frame_max, global_max
            )
        # elif attr_values.shape[1] == 4:
        #     attr_type = 'color'
        else:
            warnings.warn(
                f"Unsupported attribute shape: {attr_values.shape} for attribute {attr_name}",
                stacklevel=2,
            )
    else:
        warnings.warn(
            f"Unsupported attribute shape: {attr_values.shape} for attribute {attr_name}",
            stacklevel=2,
        )


def update_attributes_from_vtk(scene):
    if (
        "vtk_files" not in bpy.context.scene
        and "vtk_directory" not in bpy.context.scene
    ):
        return

    frame = scene.frame_current

    files = bpy.context.scene["vtk_files"]
    directory = bpy.context.scene["vtk_directory"]
    frame_sep = bpy.context.scene["vtk_frame_sep"]

    for file in files:
        mesh_name = file[0].split(".")[0].split(frame_sep)[0]

        if len(file) > 1:
            polydata = pv.read(f"{directory}/{file[frame]}")
            mesh = bpy.data.meshes[mesh_name]

            mesh.attributes["position"].data.foreach_set(
                "vector", np.ravel(polydata.points)
            )
            mat = bpy.data.materials[f"{mesh_name}_attributes"]

            for attr_name, values in polydata.point_data.items():
                update_material_attributes(attr_name, values, mesh, mat, "POINT")

            for attr_name, values in polydata.cell_data.items():
                update_material_attributes(attr_name, values, mesh, mat, "FACE")

            mesh.update()
