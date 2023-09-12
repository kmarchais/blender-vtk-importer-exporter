import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
import bpy

import pyvista as pv

from .mesh import create_object

def sort_files(file_list):
    sorted_file_list = []
    patterns = []
    for file in file_list:
        pattern = file.name.split('.')[0].split('-')[0]
        if pattern not in patterns:
            patterns.append(pattern)
            sorted_file_list.append([file.name])
        else:
            sorted_file_list[patterns.index(pattern)].append(file.name)

    for i, sequence in enumerate(sorted_file_list):
        if len(sequence) > 1:
            sorted_file_list[i] = sorted(
                sequence,
                key=lambda x: int(x.split('.')[0].split('-')[-1])
            )

    return sorted_file_list


class ImportVTK(bpy.types.Operator, ImportHelper):
    """Load a VTK file"""
    bl_idname = "import.vtk"
    bl_label = "Import VTK"

    filename_ext = ".vtk"
    filter_glob: StringProperty(
        default="*.vtk;*.vtu;*.vtp;*.vtm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement,
                                         options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        # global files, directory

        files = sort_files(self.files)

        directory = os.path.dirname(self.filepath)

        bpy.context.scene["vtk_files"] = files
        bpy.context.scene["vtk_directory"] = directory
        bpy.context.scene["mesh_attributes"] = {}

        for file in files:
            file_path = f"{directory}/{file[0]}"
            vtk_data = pv.read(file_path)
            mesh_name = file[0].split('.')[0].split('-')[0]

            if isinstance(vtk_data, pv.MultiBlock):
                for block_name in vtk_data.keys():
                    name = f"{mesh_name} : {block_name}"
                    obj = create_object(context, vtk_data[block_name], name)
                    obj["vtk_file_path"] = file_path
                    obj["vtk_block_name"] = block_name
            else:
                obj = create_object(context, vtk_data, mesh_name)
                obj["vtk_file_path"] = file_path

        max_frame = 0
        for file in files:
            max_frame = max(max_frame, len(file) - 1)

        if max_frame != 0:
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_end = max_frame
            bpy.context.scene.frame_current = 0

        return {'FINISHED'}
