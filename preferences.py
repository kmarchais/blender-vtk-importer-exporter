"""Manage the preferences of the VTK Importer add-on."""

from __future__ import annotations

import importlib
import subprocess
import sys
from typing import ClassVar

import bpy
import pip

from . import dependencies
from .material_panel import get_availbale_colormaps, vtk_enum_colormaps

COLORMAP = "viridis"


def get_dependencies_versions() -> None:
    """Get the dependencies versions."""
    for dependency, dep_dict in dependencies.items():
        module_spec = importlib.util.find_spec(dependency)
        dep_dict["module"] = dependency
        if module_spec is not None:
            module = importlib.import_module(dependency)
            dep_dict["version"] = getattr(module, "__version__", "Unknown version.")
        else:
            dep_dict["version"] = "Not installed."


get_dependencies_versions()


class VTK_OT_Upgrade_Dependencies(bpy.types.Operator):  # noqa: N801
    """Upgrade dependencies."""

    bl_idname = "vtk.upgrade_dependencies"
    bl_label = "Upgrade dependencies"
    bl_description = "Upgrade dependencies"
    bl_options: ClassVar = {"REGISTER", "UNDO"}

    def execute(self, _: bpy.types.Context) -> set[str]:
        """Upgrade dependencies."""
        for dependency, dep_dict in dependencies.items():
            pip.main(["install", dependency, "--upgrade"])
            importlib.reload(dep_dict["module"])
        get_dependencies_versions()
        return {"FINISHED"}

    def invoke(self, context: bpy.types.Context, _: bpy.types.Event) -> set[str]:
        """Invoke the operator."""
        return self.execute(context)


class VtkImporterPreferences(bpy.types.AddonPreferences):
    """VTK Importer preferences."""

    bl_idname = __package__

    expand_dependencies: bpy.props.BoolProperty(default=False)

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the preferences."""
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
            for dependency, dep_dict in dependencies.items():
                row = box.row().split(factor=0.5)
                split = row.split(factor=0.5)
                split.label(text=dependency)

                split.label(text=f"v{dep_dict['version']}")

                if "url" in dep_dict:
                    row.operator(
                        operator="wm.url_open",
                        text=dep_dict["url"].split("//")[-1],
                        icon="URL",
                    ).url = dep_dict["url"]

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


def register() -> None:
    """Register the preferences."""
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


def unregister() -> None:
    """Unregister the preferences."""
    del bpy.types.Scene.default_colormap
    del bpy.types.Scene.number_elem_cmap
    bpy.utils.unregister_class(VTK_OT_Upgrade_Dependencies)
    bpy.utils.unregister_class(VtkImporterPreferences)
