import bpy

from . import preferences
from .importer import ImportVTK

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


DEPENDENCIES = ['pyvista', 'numpy']

def menu_func_import(self, context):
    self.layout.operator(ImportVTK.bl_idname, text="VTK (.vtk, .vtu, .vtp, .vtm)")

def register():
    bpy.utils.register_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    preferences.register()

def unregister():
    bpy.utils.unregister_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    preferences.unregister()
