import bpy

from . import preferences
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


DEPENDENCIES = ['pyvista', 'numpy', 'matplotlib', 'cmcrameri']

def menu_func_import(self, context):
    self.layout.operator(ImportVTK.bl_idname, text="VTK (.vtk, .vtu, .vtp, .vtm)")

def register():
    bpy.utils.register_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    preferences.register()

    bpy.types.WindowManager.my_frame_change_post_handler = update_attributes_from_vtk
    bpy.app.handlers.frame_change_post.append(bpy.types.WindowManager.my_frame_change_post_handler)

def unregister():
    bpy.utils.unregister_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    preferences.unregister()

    bpy.app.handlers.frame_change_post.remove(bpy.types.WindowManager.my_frame_change_post_handler)
    del bpy.types.WindowManager.my_frame_change_post_handler
