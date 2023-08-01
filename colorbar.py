import bpy
import numpy as np

import matplotlib.pyplot as plt

from .attributes import update_attributes_from_vtk

def create_colorbar(context):
    mat = context.object.active_material

    n_colors = len(mat.node_tree.nodes["Color Ramp"].color_ramp.elements)

    cbar_scale = 0.25
    y = np.linspace(0.0, cbar_scale, n_colors)

    grid = np.zeros(shape=(2 * n_colors, 3))
    grid[1::2, 0] = 0.1 * cbar_scale
    grid[0::2, 1] = y
    grid[1::2, 1] = y

    faces = [(i, i + 1, i + 3, i + 2) for i in range(0, 2 * (n_colors - 1), 2)]

    cbar_name = f"{mat.name}_cbar"
    cbar_mesh = bpy.data.meshes.new(cbar_name)
    cbar_mesh.from_pydata(vertices=grid, edges=[], faces=faces)

    cbar_obj = bpy.data.objects.new(cbar_name, cbar_mesh)
    bpy.context.scene.collection.objects.link(cbar_obj)

    attr_value = grid[:, 1]
    min_value = np.min(attr_value)
    max_value = np.max(attr_value)
    color_fac = (attr_value - min_value) / (max_value - min_value)

    cbar_mat = bpy.data.materials.new(name=cbar_name)
    attr = cbar_mesh.attributes.new("Color Fac", type='FLOAT', domain='POINT')
    attr.data.foreach_set('value', color_fac)

    cbar_mat.use_nodes = True
    bsdf = cbar_mat.node_tree.nodes["Principled BSDF"]
    cbar_mat.node_tree.nodes.remove(bsdf)

    emission_shader_node = cbar_mat.node_tree.nodes.new("ShaderNodeEmission")
    material_output_node = cbar_mat.node_tree.nodes["Material Output"]

    attribute_node = cbar_mat.node_tree.nodes.new("ShaderNodeAttribute")
    attribute_node.attribute_name = "Color Fac"

    #cbar_mat.vtk_colormaps = colormap
    color_ramp_node = cbar_mat.node_tree.nodes.new("ShaderNodeValToRGB")
    cmap = plt.get_cmap(mat.vtk_colormaps)

    # remove last element to create it again in the last iteration to have it selected
    last_elem = color_ramp_node.color_ramp.elements[-1]
    color_ramp_node.color_ramp.elements.remove(last_elem)

    for i in range(n_colors):
        location = i / (n_colors - 1)
        if i != 0:
            color_ramp_node.color_ramp.elements.new(location)

    cbar_mat.node_tree.links.new(
        attribute_node.outputs["Fac"],
        color_ramp_node.inputs["Fac"]
    )
    cbar_mat.node_tree.links.new(
        color_ramp_node.outputs["Color"],
        emission_shader_node.inputs["Color"]
    )
    cbar_mat.node_tree.links.new(
        emission_shader_node.outputs["Emission"],
        material_output_node.inputs["Surface"]
    )

    cbar_obj.data.materials.append(cbar_mat)


    scale = 0.1 * cbar_scale

    min_range_curve = bpy.data.curves.new(name=f"{mat.name}_min", type='FONT')
    min_range_obj = bpy.data.objects.new(name=f"{mat.name}_min", object_data=min_range_curve)
    min_range_obj.scale = (scale, scale, scale)
    min_range_obj.location = (0.15 * cbar_scale, 0, 0)

    max_range_curve = bpy.data.curves.new(name=f"{mat.name}_max", type='FONT')
    max_range_obj = bpy.data.objects.new(name=f"{mat.name}_max", object_data=max_range_curve)
    max_range_obj.scale = (scale, scale, scale)
    max_range_obj.location = (
        0.15 * cbar_scale,
        cbar_scale - scale * max_range_obj.dimensions[1],
        0
    )

    attribute_curve = bpy.data.curves.new(name=f"{mat.name}_attribute_name", type='FONT')
    attribute_obj = bpy.data.objects.new(
        name=f"{mat.name}_attribute_name",
        object_data=attribute_curve
    )
    attribute_obj.scale = (scale, scale, scale)
    attribute_obj.rotation_euler = (0, 0, np.pi / 2)
    attribute_obj.location = (
        0.2 * cbar_scale,
        0.25 * (cbar_scale - scale * attribute_obj.dimensions[1]),
        0
    )


    cbar_label_mat = bpy.data.materials.new(name=f"{cbar_name}_labels")

    cbar_label_mat.use_nodes = True

    bsdf = cbar_label_mat.node_tree.nodes["Principled BSDF"]
    cbar_label_mat.node_tree.nodes.remove(bsdf)

    combine_color_node = cbar_label_mat.node_tree.nodes.new("ShaderNodeCombineColor")
    emission_shader_node = cbar_label_mat.node_tree.nodes.new("ShaderNodeEmission")
    material_output_node = cbar_label_mat.node_tree.nodes["Material Output"]

    cbar_label_mat.node_tree.links.new(
        combine_color_node.outputs["Color"],
        emission_shader_node.inputs["Color"]
    )
    cbar_label_mat.node_tree.links.new(
        emission_shader_node.outputs["Emission"],
        material_output_node.inputs["Surface"]
    )

    min_range_obj.data.materials.append(cbar_label_mat)
    max_range_obj.data.materials.append(cbar_label_mat)
    attribute_obj.data.materials.append(cbar_label_mat)

    min_range_obj.parent = cbar_obj
    max_range_obj.parent = cbar_obj
    attribute_obj.parent = cbar_obj

    bpy.context.scene.collection.objects.link(min_range_obj)
    bpy.context.scene.collection.objects.link(max_range_obj)
    bpy.context.scene.collection.objects.link(attribute_obj)


    cbar_obj.parent = bpy.data.objects['Camera']
    cbar_obj.location = (-0.35, -0.2, -1)
    cbar_obj.select_set(False)

    update_colorbar(None, context)

def update_colorbar(self, context):
    mat = context.object.active_material

    if not mat.vtk_show_scalar_bar:
        return

    cbar_name = f"{mat.name}_cbar"
    cbar_mat = bpy.data.materials[cbar_name]
    cbar_label_mat = bpy.data.materials[f"{cbar_name}_labels"]

    color_ramp_node = cbar_mat.node_tree.nodes["Color Ramp"]
    cmap = plt.get_cmap(mat.vtk_colormaps)
    n_colors = len(color_ramp_node.color_ramp.elements)
    for i in range(n_colors):
        location = i / (n_colors - 1)
        rgb = [c**2.2 for c in cmap(location)] # sRGB to Linear RGB
        color_ramp_node.color_ramp.elements[i].color = rgb

    scale = mat.vtk_scalar_bar_scale_numbers
    numbers_format = "{" + mat.vtk_scalar_bar_number_format + "}"
    min_range_curve = bpy.data.curves[f"{mat.name}_min"]
    min_value = mat.node_tree.nodes["Map Range"].inputs["From Min"].default_value
    # min_value = mat["attributes"][mat.vtk_attributes]["global_min"]
    min_range_curve.body = numbers_format.format(min_value * scale)
    max_range_curve = bpy.data.curves[f"{mat.name}_max"]
    max_value = mat.node_tree.nodes["Map Range"].inputs["From Max"].default_value
    # max_value = mat["attributes"][mat.vtk_attributes]["global_max"]
    # mat.node_tree.nodes["Map Range"].inputs["From Max"].default_value = max_value
    max_range_curve.body = numbers_format.format(max_value * scale)
    attribute_curve = bpy.data.curves[f"{mat.name}_attribute_name"]
    attribute_curve.body = mat.vtk_attributes

    combine_color_node = cbar_label_mat.node_tree.nodes["Combine Color"]
    combine_color_node.inputs["Red"].default_value = mat.vtk_scalar_bar_labels_color[0]
    combine_color_node.inputs["Green"].default_value = mat.vtk_scalar_bar_labels_color[1]
    combine_color_node.inputs["Blue"].default_value = mat.vtk_scalar_bar_labels_color[2]

    mat.vtk_scalar_bar_attribute_name = mat.vtk_attributes

def remove_colorbar(context):
    mat = context.object.active_material

    cbar_mat = bpy.data.materials[f"{mat.name}_cbar"]
    cbar_label_mat = bpy.data.materials[f"{mat.name}_cbar_labels"]

    bpy.data.materials.remove(cbar_mat)
    bpy.data.materials.remove(cbar_label_mat)

    cbar_mesh = bpy.data.meshes[f"{mat.name}_cbar"]
    bpy.data.meshes.remove(cbar_mesh)

    min_range_curve = bpy.data.curves[f"{mat.name}_min"]
    bpy.data.curves.remove(min_range_curve)
    max_range_curve = bpy.data.curves[f"{mat.name}_max"]
    bpy.data.curves.remove(max_range_curve)
    attribute_curve = bpy.data.curves[f"{mat.name}_attribute_name"]
    bpy.data.curves.remove(attribute_curve)
