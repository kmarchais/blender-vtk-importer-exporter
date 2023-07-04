from __future__ import annotations
import importlib
import subprocess
import sys

import bpy

from . import dependencies
from .material_panel import vtk_enum_colormaps, get_availbale_colormaps

COLORMAP = "viridis"

def get_dependencies_versions():
    for dependency, dep_dict in dependencies.items():
        try:
            module = importlib.import_module(dependency)
            dep_dict["module"] = module
            dep_dict["version"] = module.__version__
        except ModuleNotFoundError:
            dep_dict["version"] = "Not installed"

get_dependencies_versions()


class VTK_OT_Upgrade_Dependencies(bpy.types.Operator):
    bl_idname = "vtk.upgrade_dependencies"
    bl_label = "Upgrade dependencies"
    bl_description = "Upgrade dependencies"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for dependency, dep_dict in dependencies.items():
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", dependency])
            importlib.reload(dep_dict["module"])
        get_dependencies_versions()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class VtkImporterPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    expand_dependencies: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout : bpy.types.UILayout = self.layout
        box = layout.box()
        row = box.row()
        icon = 'DISCLOSURE_TRI_DOWN' if self.expand_dependencies else 'DISCLOSURE_TRI_RIGHT'
        row.prop(self, "expand_dependencies", text="", icon=icon, emboss=False, icon_only=True)

        column = row.column()
        column.label(text="Dependencies")

        if self.expand_dependencies:
            for dependency, dep_dict in dependencies.items():
                row = box.row().split(factor=0.5)
                split = row.split(factor=0.5)
                split.label(text=dependency)

                split.label(text=f"v{dep_dict['version']}")

                if "url" in dep_dict:
                    row.operator(operator="wm.url_open", text=dep_dict["url"].split("//")[-1], icon="URL").url = dep_dict["url"]

            box.operator(operator="vtk.upgrade_dependencies", text="Upgrade dependencies",
                         icon_value=0, emboss=True, depress=False)

        box = layout.box()
        box.prop(context.scene, "default_colormap", icon_value=0, emboss=True)

def register():
    colormaps = get_availbale_colormaps()
    default_cmap_index = colormaps.index(COLORMAP)

    bpy.types.Scene.default_colormap = bpy.props.EnumProperty(
        name='Default Colormap',
        description='Select the default colormap',
        items=vtk_enum_colormaps,
        default=default_cmap_index
    )
    bpy.utils.register_class(VTK_OT_Upgrade_Dependencies)
    bpy.utils.register_class(VtkImporterPreferences)


def unregister():
    del bpy.types.Scene.default_colormap
    bpy.utils.unregister_class(VTK_OT_Upgrade_Dependencies)
    bpy.utils.unregister_class(VtkImporterPreferences)
