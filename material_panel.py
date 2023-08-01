import bpy
import matplotlib.pyplot as plt

from typing import Literal

from .colorbar import create_colorbar, remove_colorbar, update_colorbar

def update_data_range(context, frame_range: Literal["global", "current_frame"]):
    mat = context.object.active_material
    vtk_attribute = mat.vtk_attributes
    if vtk_attribute in mat["attributes"]:
        map_range_node = mat.node_tree.nodes["Map Range"]
        
        obj = context.object
        mesh = obj.data
        attr_type = mesh.attributes[mat.vtk_attributes].data.data.data_type
        if attr_type == 'FLOAT':
            min_value = mat["attributes"][vtk_attribute][f"{frame_range}_min"]
            max_value = mat["attributes"][vtk_attribute][f"{frame_range}_max"]
            map_range_node.inputs["From Min"].default_value = min_value
            map_range_node.inputs["From Max"].default_value = max_value
        elif attr_type in ['FLOAT2', 'FLOAT_VECTOR']:
            component = mat.vtk_attribute_component
            min_value = mat["attributes"][vtk_attribute][component][f"{frame_range}_min"]
            max_value = mat["attributes"][vtk_attribute][component][f"{frame_range}_max"]
            map_range_node.inputs["From Min"].default_value = min_value
            map_range_node.inputs["From Max"].default_value = max_value


class VTK_OT_Data_range_all_frames(bpy.types.Operator):
    bl_idname = "vtk.button_all_frames"
    bl_label = "Data range over all time steps"
    bl_description = "Data range over all time steps"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        update_data_range(context, "global")
        update_colorbar(self, context)

        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class VTK_OT_Data_range_current_frame(bpy.types.Operator):
    bl_idname = "vtk.button_current_frame"
    bl_label = "Data range of the current frame"
    bl_description = "Data range of the current frame"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        update_data_range(context, "current_frame")
        update_colorbar(self, context)

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

        update_colorbar(self, context)

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
        if "attributes" not in mat:
            return False
        if mat["attributes"] is None:
            return False
        return True

    def draw(self, context):
        layout = self.layout

        material = context.object.active_material

        row = layout.row()
        row.label(text="Attribute")
        row.prop(data=material, property="vtk_attributes", text="", icon_value=0, emboss=True)
        row.prop(data=material, property="vtk_attribute_component", text="", icon_value=0, emboss=True)

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

        layout.prop(material, "vtk_show_scalar_bar", text="Show Scalar Bar")
        if material.vtk_show_scalar_bar:
            box = layout.box()
            row = box.row()
            row.label(text="Labels color")
            row.prop(material, "vtk_scalar_bar_labels_color", text="")
            row = box.row()
            row.label(text="Attribute name")
            row.prop(material, "vtk_scalar_bar_attribute_name", text="")
            row = box.row()
            row.label(text="Scale numbers")
            row.prop(material, "vtk_scalar_bar_scale_numbers", text="")
            row = box.row()
            row.label(text="Number format")
            row.prop(material, "vtk_scalar_bar_number_format", text="")

def get_availbale_colormaps():
    colormaps = list(filter(lambda cmap: cmap[-2:] != "_r", plt.colormaps()))
    return sorted(colormaps, key=lambda s: s.split('.')[-1].lower())

def vtk_enum_colormaps(self, context):
    # https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
    return [(cmap, cmap.split('.')[-1], cmap) for cmap in get_availbale_colormaps()]

def vtk_enum_attributes(self, context):
    # https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
    mat = context.object.active_material
    if mat is None:
        return []
    if "attributes" not in mat:
        return []
    attributes = list(mat["attributes"].to_dict().keys())
    return [(rf"{attribute}",)*3 for attribute in attributes]

def vtk_enum_attribute_component(self, context):
    # https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
    mat = context.object.active_material
    if mat is None:
        return []
    if "attributes" not in mat:
        return []
    obj = context.object
    mesh = obj.data
    attr_type = mesh.attributes[mat.vtk_attributes].data.data.data_type

    components = [] # 'FLOAT'
    if attr_type == 'FLOAT_VECTOR':
        components = ["Magnitude", "X", "Y", "Z"]
    elif attr_type == 'FLOAT2':
        components = ["Magnitude", "X", "Y"]

    return [(rf"{component}",)*3 for component in components]

def update_colormap_enum(self, context):
    if "Color Ramp" not in self.node_tree.nodes:
        return
    color_ramp_node = self.node_tree.nodes["Color Ramp"]
    cmap = plt.get_cmap(self.vtk_colormaps)
    n_colors = len(color_ramp_node.color_ramp.elements)
    for i in range(n_colors):
        location = i / (n_colors - 1)
        sRGB = cmap(location)
        linear_rgb = [c**2.2 for c in sRGB]
        color_ramp_node.color_ramp.elements[i].color = linear_rgb
    color_ramp_node.label = self.vtk_colormaps

    update_colorbar(self, context)


def update_attributes_enum(self, context):
    attribute_node = self.node_tree.nodes["Attribute"]
    attribute_node.attribute_name = self.vtk_attributes

    map_range_node = self.node_tree.nodes["Map Range"]
    mesh = context.object.data
    attr_type = mesh.attributes[self.vtk_attributes].data.data.data_type
    if attr_type == 'FLOAT':
        self.node_tree.links.new(attribute_node.outputs["Fac"], map_range_node.inputs["Value"])
    elif attr_type in ['FLOAT_VECTOR', 'FLOAT2']:
        if self.vtk_attribute_component == "Magnitude":
            length_node = self.node_tree.nodes["Vector Math"]
            self.node_tree.links.new(
                attribute_node.outputs["Vector"],
                length_node.inputs["Vector"]
            )
            self.node_tree.links.new(
                length_node.outputs["Value"],
                map_range_node.inputs["Value"]
            )
        elif self.vtk_attribute_component in ["X", "Y", "Z"]:
            separate_node = self.node_tree.nodes["Separate XYZ"]
            component = self.vtk_attribute_component
            self.node_tree.links.new(
                attribute_node.outputs["Vector"],
                separate_node.inputs["Vector"]
            )
            self.node_tree.links.new(
                separate_node.outputs[component],
                map_range_node.inputs["Value"]
            )

    update_data_range(context, 'global')

    update_colorbar(self, context)


def show_scalar_bar(self, context):
    if self.vtk_show_scalar_bar:
        create_colorbar(context)
    else:
        remove_colorbar(context)


def register():
    bpy.utils.register_class(MATERIAL_PT_VTK_Attributes)
    bpy.types.Material.vtk_colormaps = bpy.props.EnumProperty(
        name='Colormaps',
        description='',
        items=vtk_enum_colormaps,
        update=update_colormap_enum
    )
    bpy.types.Material.vtk_attributes = bpy.props.EnumProperty(
        name='Attributes',
        description='',
        items=vtk_enum_attributes,
        update=update_attributes_enum
    )
    bpy.types.Material.vtk_attribute_component = bpy.props.EnumProperty(
        name='Component',
        description='',
        items=vtk_enum_attribute_component,
        update=update_attributes_enum
    )
    bpy.types.Material.vtk_show_scalar_bar = bpy.props.BoolProperty(
        default=False,
        update=show_scalar_bar
    )

    bpy.types.Material.vtk_scalar_bar_labels_color = bpy.props.FloatVectorProperty(
        name="Scalar Bar Labels Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        update=update_colorbar
    )

    bpy.types.Material.vtk_scalar_bar_attribute_name = bpy.props.StringProperty(
        name="Attribute Name",
        update=update_colorbar
    )

    bpy.types.Material.vtk_scalar_bar_scale_numbers = bpy.props.FloatProperty(
        name="Scale Numbers",
        default=1.0,
        update=update_colorbar
    )

    bpy.types.Material.vtk_scalar_bar_number_format = bpy.props.StringProperty(
        name="Number Format",
        # default="{:.2f}",
        update=update_colorbar
    )

    bpy.utils.register_class(VTK_OT_Data_range_all_frames)
    bpy.utils.register_class(VTK_OT_Data_range_current_frame)
    bpy.utils.register_class(VTK_OT_Data_range_custom)


def unregister():
    del bpy.types.Material.vtk_colormaps
    del bpy.types.Material.vtk_attributes
    del bpy.types.Material.vtk_attribute_component
    del bpy.types.Material.vtk_show_scalar_bar
    del bpy.types.Material.vtk_scalar_bar_labels_color
    del bpy.types.Material.vtk_scalar_bar_attribute_name
    del bpy.types.Material.vtk_scalar_bar_scale_numbers
    del bpy.types.Material.vtk_scalar_bar_number_format

    bpy.utils.unregister_class(MATERIAL_PT_VTK_Attributes)
    bpy.utils.unregister_class(VTK_OT_Data_range_all_frames)
    bpy.utils.unregister_class(VTK_OT_Data_range_current_frame)
    bpy.utils.unregister_class(VTK_OT_Data_range_custom)
