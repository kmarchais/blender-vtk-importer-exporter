"""Import VTK files into Blender."""

from __future__ import annotations

from pathlib import Path

import bpy
import pyvista as pv
from bpy.props import StringProperty  # noqa: TCH002
from bpy_extras.io_utils import ImportHelper

from .mesh import create_object


def sort_files(
    file_list: list[bpy.types.OperatorFileListElement],
    frame_sep: str = "_",
) -> list[list[str]]:
    """Sort files by frame."""
    sorted_file_list: list[str] = []
    patterns: list[str] = []
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
                sequence,
                key=lambda x: int(x.split(".")[0].split(frame_sep)[-1]),
            )

    return sorted_file_list


class ImportVTK(bpy.types.Operator, ImportHelper):
    """Load a VTK file."""

    bl_idname = "import.vtk"
    bl_label = "Import VTK"

    filename_ext = ".vtk"
    filter_glob: StringProperty(
        default="*.vtk;*.vtu;*.vtp;*.vtm",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={"HIDDEN", "SKIP_SAVE"},
    )

    frame_sep = "_"

    def execute(self, context: bpy.types.Context) -> set[str]:
        """Import the VTK file."""
        files = sort_files(self.files, frame_sep=self.frame_sep)

        directory = Path(self.filepath).parent

        bpy.context.scene["vtk_files"] = files
        bpy.context.scene["vtk_directory"] = str(directory)
        bpy.context.scene["mesh_attributes"] = {}
        bpy.context.scene["vtk_frame_sep"] = self.frame_sep

        for file in files:
            file_path = f"{directory}/{file[0]}"
            vtk_data = pv.read(file_path)
            mesh_name = file[0].split(".")[0].split(self.frame_sep)[0]

            if isinstance(vtk_data, pv.MultiBlock):
                for block_name in vtk_data:
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
