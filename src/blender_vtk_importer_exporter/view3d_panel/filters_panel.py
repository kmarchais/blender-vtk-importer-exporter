from __future__ import annotations

import bpy
import pyvista as pv
from bpy.types import Context
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from ..mesh import create_object, set_mesh_attributes, vtk_to_mesh
from .view3d_panel import View3D_VTK_Panel


def update_filters(scene: bpy.types.Scene) -> None:
    if (
        "vtk_files" not in bpy.context.scene
        and "vtk_directory" not in bpy.context.scene
    ):
        return

    frame = scene.frame_current

    files = bpy.context.scene["vtk_files"]
    directory = bpy.context.scene["vtk_directory"]
    frame_sep = bpy.context.scene["frame_sep"]

    for file in files:
        if len(file) > 1:
            obj_name = file[0].split(".")[0].split(frame_sep)[0]
            obj = bpy.data.objects[obj_name]
            if "vtk_filters" in obj:
                vtk_data = pv.read(f"{directory}/{file[frame]}")
                for vtk_filter in obj["vtk_filters"]:
                    if vtk_filter == "clip":
                        clip_filter = obj["vtk_filters"]["clip"]
                        normal = clip_filter["normal"]
                        origin = clip_filter["origin"]
                        invert = clip_filter["invert"]
                        vtk_data = vtk_data.clip(
                            normal=normal,
                            origin=origin,
                            invert=invert,
                        )

                        for child in obj.children:
                            if "clip" in child.name:
                                mesh = vtk_to_mesh(vtk_data, child.name)
                                set_mesh_attributes(mesh, vtk_data)
                                # update_mesh_from_vtk(child.data, vtk_data, update_attributes=True)
                                child.data = mesh
                                # child.data.clear_geometry()
                                # child.data.from_pydata(vertices, [], triangles)


# class VTK_OT_Clip(bpy.types.Operator):
#     bl_idname = "vtk.clip"
#     bl_label = "Clip"
#     bl_description = "Clip"

#     def execute(self, context):
#         obj = context.object
#         obj.clip_active = not obj.clip_active
#         name = f"{obj.name}_clipped"

#         if obj.clip_active:
#             vtk_file_path = obj["vtk_file_path"]
#             vtk_data = pv.read(vtk_file_path)
#             normal = obj.clip_normal
#             origin = obj.clip_origin
#             invert = obj.clip_invert
#             if "vtk_block_name" in obj:
#                 vtk_data = vtk_data[obj["vtk_block_name"]]
#             clipped = vtk_data.clip(normal=normal, origin=origin, invert=invert)

#             create_object(context, clipped, name)
#             obj.hide_set(True)
#             bpy.data.objects[name].parent = obj
#         else:
#             obj.hide_set(False)
#             bpy.data.meshes.remove(bpy.data.meshes[name])

#         return {'FINISHED'}


class VTK_OT_Clip(bpy.types.Operator):
    bl_idname = "vtk.clip"
    bl_label = "Clip"
    bl_description = "Clip"
    bl_options = {"REGISTER", "UNDO"}

    obj_name: bpy.props.StringProperty(
        name="Object Name",
        description="Object Name",
        default="",
    )

    normal: bpy.props.FloatVectorProperty(
        name="Normal",
        subtype="XYZ",
        description="",
        default=(1.0, 0.0, 0.0),
    )
    origin: bpy.props.FloatVectorProperty(
        name="Origin",
        subtype="XYZ",
        description="",
        default=(0.0, 0.0, 0.0),
    )
    invert: bpy.props.BoolProperty(
        name="Invert",
        description="",
        default=False,
    )

    def execute(self, context: Context) -> set[str]:
        obj = context.object

        # name = f"{obj.name}_clipped"

        # vtk_file_path = obj["vtk_file_path"]
        # vtk_data = pv.read(vtk_file_path)
        # if "vtk_block_name" in obj:
        #     vtk_data = vtk_data[obj["vtk_block_name"]]

        if "vtk_filters" not in obj:
            obj["vtk_filters"] = {}
        if "clip" not in obj["vtk_filters"]:
            obj["vtk_filters"]["clip"] = {}
        obj["vtk_filters"]["clip"]["normal"] = self.normal
        obj["vtk_filters"]["clip"]["origin"] = self.origin
        obj["vtk_filters"]["clip"]["invert"] = self.invert

        clipped = self.vtk_data.clip(
            normal=self.normal, origin=self.origin, invert=self.invert
        )
        if clipped.n_points == 0:
            return {"FINISHED"}

        clipped_obj = create_object(context, clipped, self.clip_name)
        # context.view_layer.objects.active = obj
        # obj.hide_set(True)
        clipped_obj.parent = obj

        # object_data_add(context, bpy.data.meshes[name], operator=self)

        return {"FINISHED"}

    def invoke(self, context: Context, _: bpy.types.Event) -> set[str]:
        obj = context.object
        self.clip_name = f"{obj.name}_clipped"
        vtk_file_path = obj["vtk_file_path"]
        self.vtk_data = pv.read(vtk_file_path)
        if "vtk_block_name" in obj:
            self.vtk_data = self.vtk_data[obj["vtk_block_name"]]
        return context.window_manager.invoke_props_dialog(self)

    # def draw(self, context):
    #     layout = self.layout
    #     layout.prop(self, "normal", text="Normal")
    #     layout.prop(self, "origin", text="Origin")
    #     layout.prop(self, "invert", text="Invert")


class VTK_OT_Warp(bpy.types.Operator):
    bl_idname = "vtk.warp"
    bl_label = "Warp"
    bl_description = "Warp"

    def execute(self, _: Context) -> set[str]:
        return {"FINISHED"}


class VIEW3D_PT_filters(View3D_VTK_Panel, bpy.types.Panel):
    bl_label = "Filters"
    bl_idname = "VIEW3D_PT_VTK_Filters"

    @classmethod
    def poll(cls, context: Context) -> bool:
        if context.object is not None:
            if "vtk_file_path" in context.object:
                return True
            elif context.object.parent is not None:
                if "vtk_file_path" in context.object.parent:
                    return True
        return False

    def draw(self, _: Context) -> None:
        layout = self.layout

        # layout.label(text="Clip")
        # layout.prop(context.object, "clip_normal", text="")
        # layout.prop(context.object, "clip_origin", text="")
        # layout.prop(context.object, "clip_invert", text="Invert")
        layout.operator("vtk.clip", text="Clip")

        layout.separator()

        layout.operator("vtk.warp", text="Warp")


def register() -> None:
    bpy.utils.register_class(VIEW3D_PT_filters)
    bpy.utils.register_class(VTK_OT_Clip)
    bpy.utils.register_class(VTK_OT_Warp)

    # bpy.types.Object.clip_active = bpy.props.BoolProperty(
    #     name='Active',
    #     description='',
    #     default=False,
    # )
    # bpy.types.Object.clip_normal = bpy.props.FloatVectorProperty(
    #     name='Normal',
    #     subtype='XYZ',
    #     description='',
    #     default=(1.0, 0.0, 0.0),
    # )
    # bpy.types.Object.clip_origin = bpy.props.FloatVectorProperty(
    #     name='Origin',
    #     subtype='XYZ',
    #     description='',
    #     default=(0.0, 0.0, 0.0),
    # )
    # bpy.types.Object.clip_invert = bpy.props.BoolProperty(
    #     name='Invert',
    #     description='',
    #     default=False,
    # )


def unregister() -> None:
    # del bpy.types.Object.clip_active
    # del bpy.types.Object.clip_normal
    # del bpy.types.Object.clip_origin
    # del bpy.types.Object.clip_invert

    bpy.utils.unregister_class(VIEW3D_PT_filters)
    bpy.utils.unregister_class(VTK_OT_Clip)
    bpy.utils.unregister_class(VTK_OT_Warp)
