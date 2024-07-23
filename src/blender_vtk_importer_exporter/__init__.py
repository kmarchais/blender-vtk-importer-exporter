import bpy
from bpy.app.handlers import persistent

from . import exporter, importer, material_panel, preferences, view3d_panel
from .mesh import update_mesh
from .view3d_panel.filters_panel import update_filters


@persistent
def update_frame(scene: bpy.types.Scene) -> None:
    """Update the mesh and filters when the frame changes."""
    update_mesh(scene)
    update_filters(scene)


def register() -> None:
    """Register the addon."""
    exporter.register()
    importer.register()
    material_panel.register()
    preferences.register()
    view3d_panel.register()

    bpy.types.WindowManager.on_frame_change = update_frame
    bpy.app.handlers.frame_change_post.append(bpy.types.WindowManager.on_frame_change)


def unregister() -> None:
    """Unregister the addon."""
    exporter.unregister()
    importer.unregister()
    preferences.unregister()
    material_panel.unregister()
    view3d_panel.unregister()

    bpy.app.handlers.frame_change_post.remove(bpy.types.WindowManager.on_frame_change)
    del bpy.types.WindowManager.on_frame_change
