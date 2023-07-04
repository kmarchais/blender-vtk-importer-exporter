import bpy
import matplotlib.pyplot as plt

class VTK_OT_Data_range_all_frames(bpy.types.Operator):
    bl_idname = "vtk.button_all_frames"
    bl_label = "Data range over all time steps"
    bl_description = "Data range over all time steps"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mat = context.object.active_material
        vtk_attribute = mat.vtk_attributes
        if vtk_attribute in mat["attributes"]:
            map_range_node = mat.node_tree.nodes["Map Range"]
            global_min = mat["attributes"][vtk_attribute]["global_min"]
            global_max = mat["attributes"][vtk_attribute]["global_max"]
            map_range_node.inputs["From Min"].default_value = global_min
            map_range_node.inputs["From Max"].default_value = global_max
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class VTK_OT_Data_range_current_frame(bpy.types.Operator):
    bl_idname = "vtk.button_current_frame"
    bl_label = "Data range of the current frame"
    bl_description = "Data range of the current frame"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        mat = context.object.active_material
        vtk_attribute = mat.vtk_attributes
        if vtk_attribute in mat["attributes"]:
            map_range_node = mat.node_tree.nodes["Map Range"]
            current_frame_min = mat["attributes"][vtk_attribute]["current_frame_min"]
            current_frame_max = mat["attributes"][vtk_attribute]["current_frame_max"]
            map_range_node.inputs["From Min"].default_value = current_frame_min
            map_range_node.inputs["From Max"].default_value = current_frame_max
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class VTK_OT_Data_range_custom(bpy.types.Operator):
    bl_idname = "vtk.button_custom_data_range"
    bl_label = "Custom data range"
    bl_description = "Custom data range"
    bl_options = {"REGISTER", "UNDO"}

    min_value: bpy.props.FloatProperty(name="Min Value")
    max_value: bpy.props.FloatProperty(name="Max Value")

    def execute(self, context):
        mat = context.object.active_material
        mat.node_tree.nodes["Map Range"].inputs["From Min"].default_value = self.min_value
        mat.node_tree.nodes["Map Range"].inputs["From Max"].default_value = self.max_value
        return {"FINISHED"}

    def invoke(self, context, event):
        mat = context.object.active_material
        self.min_value = mat.node_tree.nodes["Map Range"].inputs["From Min"].default_value
        self.max_value = mat.node_tree.nodes["Map Range"].inputs["From Max"].default_value
        return context.window_manager.invoke_props_dialog(self)

class MATERIAL_PT_VTK_Attributes(bpy.types.Panel):
    bl_label = "VTK attributes"
    bl_idname = "MATERIAL_PT_VTK_Attributes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        mat = context.object.active_material
        if mat is None:
            return False
        if mat["attributes"] is None:
            return FalseA
        return True

    def draw(self, context):
        layout = self.layout

        material = context.object.active_material

        row = layout.row()
        row.label(text="Attribute")
        row.prop(data=material, property="vtk_attributes", text="", icon_value=0, emboss=True)

        row = layout.row(align=True)
        row.label(text="Data range")
        row.operator("vtk.button_all_frames", text="All frames",
                     icon_value=0, emboss=True, depress=False)
        row.operator("vtk.button_current_frame", text="Current",
                     icon_value=0, emboss=True, depress=False)
        row.operator("vtk.button_custom_data_range", text="Custom",
                     icon_value=0, emboss=True, depress=False)

        row = layout.row()
        row.label(text="Color Map")
        row.prop(material, "vtk_colormaps", text="", icon_value=0, emboss=True)
        color_ramp_node = material.node_tree.nodes["Color Ramp"]
        box = layout.box()
        box.template_color_ramp(color_ramp_node, "color_ramp", expand=True)

def get_availbale_colormaps():
    colormaps = list(filter(lambda cmap: cmap[-2:] != "_r", plt.colormaps()))
    return sorted(colormaps, key=lambda s: s.split('.')[-1].lower())

def vtk_enum_colormaps(self, context):
    # https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
    return [(cmap, cmap.split('.')[-1], cmap) for cmap in get_availbale_colormaps()]

def vtk_enum_attributes(self, context):
    # https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
    mat = context.object.active_material
    attributes = list(mat["attributes"].to_dict().keys())
    return [(rf"{attribute}",)*3 for attribute in attributes]

def update_colormap_enum(self, context):
    obj = context.object
    if obj is None:
        return
    mat = context.object.active_material
    color_ramp_node = mat.node_tree.nodes["Color Ramp"]
    cmap = plt.get_cmap(self.vtk_colormaps)
    n_colors = 32
    for i in range(n_colors):
        location = i / (n_colors - 1)
        sRGB = cmap(location)
        linear_rgb = [c**2.2 for c in sRGB]
        color_ramp_node.color_ramp.elements[i].color = linear_rgb
    color_ramp_node.label = self.vtk_colormaps

def update_attributes_enum(self, context):
    mat = context.object.active_material
    attribute_node = mat.node_tree.nodes["Attribute"]
    attribute_node.attribute_name = self.vtk_attributes

def register():
    bpy.utils.register_class(MATERIAL_PT_VTK_Attributes)
    bpy.types.Material.vtk_colormaps = bpy.props.EnumProperty(name='Colormaps',
                                                              description='',
                                                              items=vtk_enum_colormaps,
                                                              update=update_colormap_enum)
    bpy.types.Material.vtk_attributes = bpy.props.EnumProperty(name='Attributes',
                                                               description='',
                                                               items=vtk_enum_attributes,
                                                               update=update_attributes_enum)

    bpy.utils.register_class(VTK_OT_Data_range_all_frames)
    bpy.utils.register_class(VTK_OT_Data_range_current_frame)
    bpy.utils.register_class(VTK_OT_Data_range_custom)


def unregister():
    del bpy.types.Material.vtk_colormaps
    del bpy.types.Material.vtk_attributes
    bpy.utils.unregister_class(MATERIAL_PT_VTK_Attributes)
    bpy.utils.unregister_class(VTK_OT_Data_range_all_frames)
    bpy.utils.unregister_class(VTK_OT_Data_range_current_frame)
    bpy.utils.unregister_class(VTK_OT_Data_range_custom)
