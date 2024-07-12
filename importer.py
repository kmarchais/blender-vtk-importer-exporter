import os

import bpy
import pyvista as pv
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from .mesh import create_object


def sort_files(file_list, frame_sep):
    sorted_file_list = []
    patterns = []
    for file in file_list:
        pattern = file.name.split(".")[0].split(frame_sep)[0]
        if pattern not in patterns:
            patterns.append(pattern)
            sorted_file_list.append([file.name])
        else:
            sorted_file_list[patterns.index(pattern)].append(file.name)

    for i, sequence in enumerate(sorted_file_list):
        if len(sequence) > 1:
            sorted_file_list[i] = sorted(
                sequence, key=lambda x: int(x.split(".")[0].split(frame_sep)[-1])
            )

    return sorted_file_list


class ImportVTK(bpy.types.Operator, ImportHelper):
    """Load a VTK file"""

    bl_idname = "import.vtk"
    bl_label = "Import VTK"

    filename_ext = ".vtk"
    filter_glob: StringProperty(
        default="*.vtk;*.vtu;*.vtp;*.vtm",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement, options={"HIDDEN", "SKIP_SAVE"}
    )

    frame_sep: bpy.props.StringProperty(
        name="Frame Separator",
        description="Separator for frame numbers in file names",
        default="-",
    )

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        split = layout.split(factor=0.5)

        col = split.column()
        col.label(text="Frame Separator")

        col = split.column()
        col.prop(operator, "frame_sep", text="")

    def execute(self, context):
        # global files, directory

        files = sort_files(self.files, self.frame_sep)

        directory = os.path.dirname(self.filepath)

        bpy.context.scene["vtk_files"] = files
        bpy.context.scene["vtk_directory"] = directory
        bpy.context.scene["mesh_attributes"] = {}
        bpy.context.scene["frame_sep"] = self.frame_sep

        for file in files:
            file_path = f"{directory}/{file[0]}"
            vtk_data = pv.read(file_path)
            mesh_name = file[0].split(".")[0].split(self.frame_sep)[0]

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

        return {"FINISHED"}


class VTK_PT_import(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        print(operator.bl_idname)

        return operator.bl_idname == "IMPORT_MESH_OT_vtk"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "frame_sep")


def menu_func_import(self, context):
    self.layout.operator(ImportVTK.bl_idname, text="VTK (.vtk, .vtu, .vtp, .vtm)")


def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(ImportVTK)
    bpy.utils.register_class(VTK_PT_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ImportVTK)
    bpy.utils.unregister_class(VTK_PT_import)
