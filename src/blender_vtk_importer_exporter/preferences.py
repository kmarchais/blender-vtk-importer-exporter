from __future__ import annotations

import importlib
import importlib.metadata
import subprocess
import sys

import bpy
import pip

from blender_vtk_importer_exporter.material_panel import (
    get_availbale_colormaps,
    vtk_enum_colormaps,
)

COLORMAP = "viridis"
DEPENDENCIES = importlib.metadata.requires(__package__)


def get_dependencies_versions():
    if __package__ is None:
        return
    dep_dict = {}
    for dependency in DEPENDENCIES:
        name = dependency.split("==")[0].split(">")[0].split("<")[0].split(";")[0]
        dep_dict["module"] = name
        try:
            module = importlib.import_module(name)
            dep_dict["version"] = module.__version__
        except ModuleNotFoundError:
            dep_dict["version"] = "Not installed."


get_dependencies_versions()


class VTK_OT_Upgrade_Dependencies(bpy.types.Operator):
    bl_idname = "vtk.upgrade_dependencies"
    bl_label = "Upgrade dependencies"
    bl_description = "Upgrade dependencies"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if __package__ is None:
            return {"CANCELLED"}
        for dependency in DEPENDENCIES:
            name = dependency.split("==")[0].split(">")[0].split("<")[0].split(";")[0]
            pip.main(["install", "--upgrade", name])
            # importlib.reload(name)
            importlib.import_module(name)
        get_dependencies_versions()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class VtkImporterPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    expand_dependencies: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        box = layout.box()
        row = box.row()
        icon = (
            "DISCLOSURE_TRI_DOWN"
            if self.expand_dependencies
            else "DISCLOSURE_TRI_RIGHT"
        )
        row.prop(
            self,
            "expand_dependencies",
            text="",
            icon=icon,
            emboss=False,
            icon_only=True,
        )

        column = row.column()
        column.label(text="Dependencies")

        if self.expand_dependencies:
            for dependency in DEPENDENCIES:
                dep_name = (
                    dependency.split("==")[0].split(">")[0].split("<")[0].split(";")[0]
                )
                row = box.row().split(factor=0.5)
                split = row.split(factor=0.5)
                split.label(text=dependency)

                version = importlib.metadata.version(dep_name)
                split.label(text=f"v{version}")

                # if "url" in dep_dict:
                #     row.operator(
                #         operator="wm.url_open",
                #         text=dep_dict["url"].split("//")[-1],
                #         icon="URL",
                #     ).url = dep_dict["url"]

            box.operator(
                operator="vtk.upgrade_dependencies",
                text="Upgrade dependencies",
                icon_value=0,
                emboss=True,
                depress=False,
            )

        box = layout.box()
        box.prop(context.scene, "default_colormap", icon_value=0, emboss=True)
        row = box.row()
        row.label(text="Color map discretization")
        row.prop(context.scene, "number_elem_cmap", text="")


def register():
    colormaps = get_availbale_colormaps()
    default_cmap_index = colormaps.index(COLORMAP)

    bpy.types.Scene.default_colormap = bpy.props.EnumProperty(
        name="Default Colormap",
        description="Select the default colormap",
        items=vtk_enum_colormaps,
        default=default_cmap_index,
    )
    bpy.types.Scene.number_elem_cmap = bpy.props.IntProperty(
        name="Color map discretization",
        description="Number of color map elements",
        default=9,
        min=2,
        max=32,
    )
    bpy.utils.register_class(VTK_OT_Upgrade_Dependencies)
    bpy.utils.register_class(VtkImporterPreferences)


def unregister():
    del bpy.types.Scene.default_colormap
    del bpy.types.Scene.number_elem_cmap
    bpy.utils.unregister_class(VTK_OT_Upgrade_Dependencies)
    bpy.utils.unregister_class(VtkImporterPreferences)
