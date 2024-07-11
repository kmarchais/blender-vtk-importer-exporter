import math

import bpy

from .view3d_panel import View3D_VTK_Panel


class VTK_OT_View_Isometric(bpy.types.Operator):
    bl_idname = "vtk.view_isometric"
    bl_label = "Isometric"
    bl_description = "Set isometric view"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type="RIGHT")
        angle = math.radians(45)
        bpy.ops.view3d.view_orbit(angle=angle, type="ORBITRIGHT")
        # something weird with orbit up and down
        bpy.ops.view3d.view_orbit(angle=angle, type="ORBITUP")

        return {"FINISHED"}


class VTK_OT_View_XY(bpy.types.Operator):
    bl_idname = "vtk.view_xy"
    bl_label = "XY"
    bl_description = "Set XY view"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type="TOP")
        return {"FINISHED"}


class VTK_OT_View_XZ(bpy.types.Operator):
    bl_idname = "vtk.view_xz"
    bl_label = "XZ"
    bl_description = "Set XZ view"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type="BACK")
        return {"FINISHED"}


class VTK_OT_View_YX(bpy.types.Operator):
    bl_idname = "vtk.view_yx"
    bl_label = "YX"
    bl_description = "Set YX view"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type="BOTTOM")
        return {"FINISHED"}


class VTK_OT_View_YZ(bpy.types.Operator):
    bl_idname = "vtk.view_yz"
    bl_label = "YZ"
    bl_description = "Set YZ view"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type="RIGHT")
        return {"FINISHED"}


class VTK_OT_View_ZX(bpy.types.Operator):
    bl_idname = "vtk.view_zx"
    bl_label = "ZX"
    bl_description = "Set ZX view"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type="FRONT")
        return {"FINISHED"}


class VTK_OT_View_ZY(bpy.types.Operator):
    bl_idname = "vtk.view_zy"
    bl_label = "ZY"
    bl_description = "Set ZY view"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type="LEFT")
        return {"FINISHED"}


class VTK_OT_Rotate_90(bpy.types.Operator):
    bl_idname = "vtk.rotate_90"
    bl_label = "Rotate 90°"
    bl_description = "Rotate view 90°"

    def execute(self, context):
        bpy.ops.view3d.view_roll(angle=math.radians(90))
        return {"FINISHED"}


class VTK_OT_Rotate_90_Inv(bpy.types.Operator):
    bl_idname = "vtk.rotate_90_inv"
    bl_label = "Rotate -90°"
    bl_description = "Rotate view -90°"

    def execute(self, context):
        bpy.ops.view3d.view_roll(angle=math.radians(-90))
        return {"FINISHED"}


class VIEW3D_PT_VTK_view(View3D_VTK_Panel, bpy.types.Panel):
    bl_label = "View"
    bl_idname = "VIEW3D_PT_VTK_View"

    def draw(self, context):
        layout = self.layout
        layout.operator("vtk.view_isometric", text="Isometric")
        row = layout.row()
        row.operator("vtk.view_xy", text="XY")
        row.operator("vtk.view_xz", text="XZ")
        row.operator("vtk.view_yx", text="YX")
        row.operator("vtk.view_yz", text="YZ")
        row.operator("vtk.view_zx", text="ZX")
        row.operator("vtk.view_zy", text="ZY")
        row = layout.row()
        row.operator("vtk.rotate_90", text="+90°")
        row.operator("vtk.rotate_90_inv", text="-90*")


def register():
    bpy.utils.register_class(VIEW3D_PT_VTK_view)
    bpy.utils.register_class(VTK_OT_View_Isometric)
    bpy.utils.register_class(VTK_OT_View_XY)
    bpy.utils.register_class(VTK_OT_View_XZ)
    bpy.utils.register_class(VTK_OT_View_YX)
    bpy.utils.register_class(VTK_OT_View_YZ)
    bpy.utils.register_class(VTK_OT_View_ZX)
    bpy.utils.register_class(VTK_OT_View_ZY)
    bpy.utils.register_class(VTK_OT_Rotate_90)
    bpy.utils.register_class(VTK_OT_Rotate_90_Inv)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_VTK_view)
    bpy.utils.unregister_class(VTK_OT_View_Isometric)
    bpy.utils.unregister_class(VTK_OT_View_XY)
    bpy.utils.unregister_class(VTK_OT_View_XZ)
    bpy.utils.unregister_class(VTK_OT_View_YX)
    bpy.utils.unregister_class(VTK_OT_View_YZ)
    bpy.utils.unregister_class(VTK_OT_View_ZX)
    bpy.utils.unregister_class(VTK_OT_View_ZY)
    bpy.utils.unregister_class(VTK_OT_Rotate_90)
    bpy.utils.unregister_class(VTK_OT_Rotate_90_Inv)
