dependencies = {
    "pip": {},
    "pyvista": {"url": "https://github.com/pyvista/pyvista"},
    "cmcrameri": {"url": "https://www.fabiocrameri.ch/colourmaps/"},
}

for dependency in dependencies:
    if dependency != "pip":
        try:
            __import__(dependency)
        except ImportError:
            import subprocess
            import sys

            subprocess.call([sys.executable, "-m", "pip", "install", dependency])

import bpy
from bpy.app.handlers import persistent

from . import exporter, importer, material_panel, preferences, view3d_panel
from .attributes import update_attributes_from_vtk
from .view3d_panel.filters_panel import update_filters

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


@persistent
def update_frame(scene):
    update_attributes_from_vtk(scene)
    update_filters(scene)


def register():
    exporter.register()
    importer.register()
    material_panel.register()
    preferences.register()
    view3d_panel.register()

    bpy.types.WindowManager.on_frame_change = update_frame
    bpy.app.handlers.frame_change_post.append(bpy.types.WindowManager.on_frame_change)


def unregister():
    exporter.unregister()
    importer.unregister()
    preferences.unregister()
    material_panel.unregister()
    view3d_panel.unregister()

    bpy.app.handlers.frame_change_post.remove(bpy.types.WindowManager.on_frame_change)
    del bpy.types.WindowManager.on_frame_change
