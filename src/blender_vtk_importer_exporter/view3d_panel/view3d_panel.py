import bpy


class View3D_VTK_Panel:
    bl_idname = "VIEW3D_PT_VTK"
    bl_label = "VTK"
    bl_category = "VTK"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.object is not None
