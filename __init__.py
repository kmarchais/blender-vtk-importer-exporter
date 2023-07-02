import bpy

def install_dependencies():
    import sys, subprocess
    for dependency in dependencies.keys():
        if dependency != 'pip':
            subprocess.call([sys.executable, "-m", "pip", "install", *dependencies])

dependencies = {'pip': {}, 'pyvista': {}, 'cmcrameri': {}}
install_dependencies()

from . import preferences, material_panel
from .importer import ImportVTK, update_attributes_from_vtk

bl_info = {
    "name": "VTK importer",
    "author": "kmarchais",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "File > Import-Export",
    "description": "Import VTK files",
    "warning": "",
    "doc_url": "https://github.com/kmarchais/blender-vtk-importer",
    "category": "Import-Export",
}

def menu_func_import(self, context):
    self.layout.operator(ImportVTK.bl_idname, text="VTK (.vtk, .vtu, .vtp, .vtm)")

def register():
    bpy.utils.register_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    material_panel.register()
    preferences.register()

    bpy.types.WindowManager.on_frame_change = update_attributes_from_vtk
    bpy.app.handlers.frame_change_post.append(bpy.types.WindowManager.on_frame_change)

def unregister():
    bpy.utils.unregister_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    preferences.unregister()
    material_panel.unregister()

    bpy.app.handlers.frame_change_post.remove(bpy.types.WindowManager.on_frame_change)
    del bpy.types.WindowManager.on_frame_change
