"""View3D panel."""

import bpy


class View3D_VTK_Panel:  # noqa: N801
    """Base class for VTK panels."""

    bl_idname = "VIEW3D_PT_VTK"
    bl_label = "VTK"
    bl_category = "VTK"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Poll the panel."""
        return context.object is not None
