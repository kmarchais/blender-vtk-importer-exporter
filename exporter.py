import bpy

from bpy_extras.io_utils import ExportHelper

import pyvista as pv
import numpy as np

class ExportVTK(bpy.types.Operator, ExportHelper):
    """Export mesh to a VTK file"""
    bl_idname = "export.vtk"
    bl_label = "Export VTK"

    filename_ext = ".vtk"
    filter_glob: bpy.props.StringProperty(
        default="*.vtk;*.vtu;*.vtp;*.vtm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement,
                                         options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        obj = bpy.context.active_object
        mesh = obj.data

        vertices = np.ones(len(mesh.vertices)*3)
        mesh.vertices.foreach_get("co", vertices)
        vertices = vertices.reshape(-1, 3)

        faces = []
        for face in mesh.polygons:
            faces.append(len(face.vertices))
            faces.extend(face.vertices)

        vtk_mesh = pv.PolyData(vertices, faces)

        for attr in mesh.attributes:
            if attr.domain == 'POINT':
                array_length = len(mesh.vertices)
            elif attr.domain == 'FACE':
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

        return {'FINISHED'}
