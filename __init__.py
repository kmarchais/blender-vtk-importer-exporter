"""Blender Addon initialization file."""

import importlib.util
from pathlib import Path

import pip

if importlib.util.find_spec("blender-vtk-importer-exporter") is None:
    pip.main(["install", str(Path(__file__).parent), "--upgrade"])

import bpy
from blender_vtk_importer_exporter import material_panel, preferences, view3d_panel
from blender_vtk_importer_exporter.attributes import update_attributes_from_vtk
from blender_vtk_importer_exporter.exporter import ExportCSV, ExportVTK
from blender_vtk_importer_exporter.importer import ImportVTK
from blender_vtk_importer_exporter.view3d_panel.filters_panel import update_filters
from bpy.app.handlers import persistent

bl_info = {
    "name": "VTK import/Export",
    "author": "kmarchais",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "File > Import-Export",
    "description": "Import/Export VTK files",
    "warning": "",
    "doc_url": "https://github.com/kmarchais/blender-vtk-importer-exporter",
    "category": "Import-Export",
}


def menu_func_import(self, context):
    self.layout.operator(ImportVTK.bl_idname, text="VTK (.vtk, .vtu, .vtp, .vtm)")


def menu_func_export(self, context):
    self.layout.operator(ExportVTK.bl_idname, text="VTK (.vtk)")
    self.layout.operator(ExportCSV.bl_idname, text="CSV (.csv)")


@persistent
def update_frame(scene):
    update_attributes_from_vtk(scene)
    update_filters(scene)


def register():
    bpy.utils.register_class(ImportVTK)
    bpy.utils.register_class(ExportVTK)
    bpy.utils.register_class(ExportCSV)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    material_panel.register()
    preferences.register()
    view3d_panel.register()

    bpy.types.WindowManager.on_frame_change = update_frame
    bpy.app.handlers.frame_change_post.append(bpy.types.WindowManager.on_frame_change)


def unregister():
    bpy.utils.unregister_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ExportVTK)
    bpy.utils.unregister_class(ExportCSV)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    preferences.unregister()
    material_panel.unregister()
    view3d_panel.unregister()

    bpy.app.handlers.frame_change_post.remove(bpy.types.WindowManager.on_frame_change)
    del bpy.types.WindowManager.on_frame_change
