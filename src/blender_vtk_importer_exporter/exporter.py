import csv

import bpy
import numpy as np
import pyvista as pv
from bpy_extras.io_utils import ExportHelper


class ExportVTK(bpy.types.Operator, ExportHelper):
    """Export mesh to a VTK file"""

    bl_idname = "export.vtk"
    bl_label = "Export VTK"

    filename_ext = ".vtk"
    filter_glob: bpy.props.StringProperty(
        default="*.vtk;*.vtu;*.vtp;*.vtm",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement, options={"HIDDEN", "SKIP_SAVE"}
    )

    def execute(self, context):
        obj = bpy.context.active_object
        mesh = obj.data

        vertices = np.ones(len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", vertices)
        vertices = vertices.reshape(-1, 3)

        faces = []
        for face in mesh.polygons:
            faces.append(len(face.vertices))
            faces.extend(face.vertices)

        vtk_mesh = pv.PolyData(vertices, faces)

        for attr in mesh.attributes:
            if attr.domain == "POINT":
                array_length = len(mesh.vertices)
            elif attr.domain == "FACE":
                array_length = len(mesh.polygons)
            else:
                continue

            if attr.data_type in ["FLOAT", "INT"]:
                attr_type = "value"
            elif attr.data_type == "FLOAT_VECTOR":
                attr_type = "vector"
                array_length *= 3
            else:
                continue

            array = np.zeros(array_length)
            attr.data.foreach_get(attr_type, array)

            array = array.reshape(-1, 3) if attr_type == "vector" else array

            vtk_mesh[attr.name] = array

        vtk_mesh.save(self.filepath)

        return {"FINISHED"}


class ExportCSV(bpy.types.Operator, ExportHelper):
    """Export mesh attributes to a CSV file"""

    bl_idname = "export.csv"
    bl_label = "Export CSV"

    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(
        default="*.csv",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement, options={"HIDDEN", "SKIP_SAVE"}
    )

    def execute(self, context):
        obj = bpy.context.active_object
        mesh = obj.data

        vertices = np.ones(len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", vertices)
        vertices = vertices.reshape(-1, 3)
        attributes = {
            "position X": vertices[:, 0],
            "position Y": vertices[:, 1],
            "position Z": vertices[:, 2],
        }

        for attr in mesh.attributes:
            if attr.domain == "POINT":
                array_length = len(mesh.vertices)
            elif attr.domain == "FACE":
                array_length = len(mesh.polygons)
            else:
                continue

            if attr.data_type in ["FLOAT", "INT"]:
                attr_type = "value"
            elif attr.data_type == "FLOAT_VECTOR":
                attr_type = "vector"
                array_length *= 3
            else:
                continue

            array = np.zeros(array_length)
            attr.data.foreach_get(attr_type, array)

            if attr_type == "vector":
                array = array.reshape(-1, 3)
                attributes[f"{attr.name} X"] = array[:, 0]
                attributes[f"{attr.name} Y"] = array[:, 1]
                attributes[f"{attr.name} Z"] = array[:, 2]
            else:
                attributes[attr.name] = array

        with open(self.filepath, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(attributes.keys())
            writer.writerows(zip(*attributes.values()))

        return {"FINISHED"}
