import bpy
import matplotlib.pyplot as plt
from .cmap import coolwarm, viridis


def create_attribute_material(mesh_name, attributes):
    mat = bpy.data.materials.new(name=f"{mesh_name}_attributes")
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes["Principled BSDF"]
    material_output_node = mat.node_tree.nodes["Material Output"]

    attribute_nodes = []
    map_range_nodes = []
    for attribute in attributes:
        attribute_node = mat.node_tree.nodes.new("ShaderNodeAttribute")
        attribute_node.attribute_name = attribute["name"]
        attribute_node.label = attribute["name"]

        map_range_node = mat.node_tree.nodes.new("ShaderNodeMapRange")
        map_range_node.label = "Data range"
        map_range_node.inputs["From Min"].default_value = attribute["min_value"]
        map_range_node.inputs["From Max"].default_value = attribute["max_value"]

        attribute_nodes.append(attribute_node)
        map_range_nodes.append(map_range_node)


    colormaps = ["viridis", "plasma", "inferno", "magma", "cividis", "Greys", "Purples", "Blues", "Greens", "Oranges"]
    color_ramp_nodes = []
    for index, colormap in enumerate(colormaps):
        color_ramp_node = mat.node_tree.nodes.new("ShaderNodeValToRGB")
        n_colors = 32
        cmap = plt.get_cmap(colormap)
        for i in range(n_colors):
            location = i / (n_colors - 1)
            if i != 0 and i != n_colors - 1:
                color_ramp_node.color_ramp.elements.new(location)
            color_ramp_node.color_ramp.elements[i].color = cmap(location)

        color_ramp_node.select = False
        color_ramp_node.location = (bsdf.location.x - color_ramp_node.width - 50,
                                    bsdf.location.y - index * 250)
        color_ramp_node.label = colormap

        color_ramp_nodes.append(color_ramp_node)

    bsdf.select = False

    for i, (attribute_node, map_range_node) in enumerate(zip(attribute_nodes, map_range_nodes)):
        attribute_node.select = False
        map_range_node.select = False

        map_range_node.location = (color_ramp_nodes[0].location.x - map_range_node.width - 50,
                                       bsdf.location.y - i * 300)
        attribute_node.location = (map_range_nodes[i].location.x - attribute_node.width - 50,
                                       bsdf.location.y - i * 300)

        mat.node_tree.links.new(attribute_node.outputs["Fac"], map_range_node.inputs["Value"])

    mat.node_tree.links.new(map_range_nodes[0].outputs["Result"], color_ramp_nodes[0].inputs["Fac"])
    mat.node_tree.links.new(color_ramp_nodes[0].outputs["Color"], bsdf.inputs["Base Color"])
    mat.node_tree.links.new(bsdf.outputs["BSDF"], material_output_node.inputs["Surface"])


def convert_mesh_to_pointcloud(mesh_name):
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'

    obj = bpy.data.objects[mesh_name]
    modifier = obj.modifiers.new(name=f"modifier_{mesh_name}", type='NODES')
    geo_node = bpy.data.node_groups.new(f"node_{mesh_name}", 'GeometryNodeTree')
    geo_node.inputs.new('NodeSocketGeometry', 'Geometry')
    geo_node.outputs.new('NodeSocketGeometry', 'Geometry')

    input_node = geo_node.nodes.new('NodeGroupInput')
    output_node = geo_node.nodes.new('NodeGroupOutput')
    output_node.is_active_output = True

    modifier.node_group = geo_node

    radius_node = geo_node.nodes.new("GeometryNodeInputRadius")
    mesh_to_points_node = geo_node.nodes.new("GeometryNodeMeshToPoints")

    set_material_node = geo_node.nodes.new("GeometryNodeSetMaterial")
    set_material_node.inputs[2].default_value = bpy.data.materials[f"{mesh_name}_attributes"]

    radius_node.select = False
    set_material_node.select = False
    output_node.select = False
    input_node.select = False
    mesh_to_points_node.select = False

    input_node.location = (-300, 0)
    radius_node.location = (-300, -100)
    mesh_to_points_node.location = (-100, 0)
    set_material_node.location = (100, 0)
    output_node.location = (300, 0)

    geo_node.links.new(input_node.outputs[0], mesh_to_points_node.inputs["Mesh"])
    geo_node.links.new(radius_node.outputs["Radius"], mesh_to_points_node.inputs["Radius"])
    geo_node.links.new(mesh_to_points_node.outputs["Points"], set_material_node.inputs["Geometry"])
    geo_node.links.new(set_material_node.outputs["Geometry"], output_node.inputs["Geometry"])
