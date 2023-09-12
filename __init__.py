dependencies = {'pip': {},
                'pyvista': {"url": "https://github.com/pyvista/pyvista"},
                'cmcrameri': {"url": "https://www.fabiocrameri.ch/colourmaps/"}}

for dependency in dependencies:
    if dependency != 'pip':
        try:
            __import__(dependency)
        except ImportError:
            import sys, subprocess
            subprocess.call([sys.executable, "-m", "pip", "install", dependency])

import bpy
from bpy.app.handlers import persistent

from . import preferences, material_panel
from .importer import ImportVTK
from .exporter import ExportVTK
from .attributes import update_attributes_from_vtk
from .view3d_panel.filters_panel import update_filters
from . import view3d_panel

bl_info = {
    "name": "VTK import/Export",
    "author": "kmarchais",
    "version": (0, 1),
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

@persistent
def update_frame(scene):
    update_attributes_from_vtk(scene)
    update_filters(scene)

def register():
    bpy.utils.register_class(ImportVTK)
    bpy.utils.register_class(ExportVTK)
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
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    preferences.unregister()
    material_panel.unregister()
    view3d_panel.unregister()

    bpy.app.handlers.frame_change_post.remove(bpy.types.WindowManager.on_frame_change)
    del bpy.types.WindowManager.on_frame_change
