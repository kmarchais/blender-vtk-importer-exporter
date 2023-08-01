import bpy
import matplotlib.pyplot as plt

def create_attribute_material_nodes(mesh_name):
    mat = bpy.data.materials[f"{mesh_name}_attributes"]
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes["Principled BSDF"]
    material_output_node = mat.node_tree.nodes["Material Output"]


    attr_name = list(mat["attributes"].to_dict().keys())[0]

    attribute_node = mat.node_tree.nodes.new("ShaderNodeAttribute")
    attribute_node.attribute_name = attr_name

    length_node = mat.node_tree.nodes.new("ShaderNodeVectorMath")
    length_node.operation = "LENGTH"
    mat.node_tree.links.new(
        attribute_node.outputs["Vector"],
        length_node.inputs["Vector"]
    )

    separate_node = mat.node_tree.nodes.new("ShaderNodeSeparateXYZ")
    mat.node_tree.links.new(
        attribute_node.outputs["Vector"],
        separate_node.inputs["Vector"]
    )

    map_range_node = mat.node_tree.nodes.new("ShaderNodeMapRange")
    map_range_node.label = "Data range"
    
    colormap = bpy.context.scene.default_colormap
    mat.vtk_colormaps = colormap
    n_colors = bpy.context.scene.number_elem_cmap
    color_ramp_node = mat.node_tree.nodes.new("ShaderNodeValToRGB")
    cmap = plt.get_cmap(colormap)
    color_ramp_node.color_ramp.elements.remove(color_ramp_node.color_ramp.elements[-1]) # remove to create it again in the last iteration to have it selected
    for i in range(n_colors):
        location = i / (n_colors - 1)
        if i != 0:
            color_ramp_node.color_ramp.elements.new(location)
        color_ramp_node.color_ramp.elements[i].color = [c**2.2 for c in cmap(location)] # sRGB to Linear RGB

    color_ramp_node.select = False
    color_ramp_node.location = (bsdf.location.x - color_ramp_node.width - 50,
                                bsdf.location.y)
    color_ramp_node.label = colormap

    bsdf.select = False

    attribute_node.select = False
    length_node.select = False
    separate_node.select = False
    map_range_node.select = False

    map_range_node.location = (color_ramp_node.location.x - map_range_node.width - 50,
                                    bsdf.location.y)

    length_node.location = (map_range_node.location.x - length_node.width - 50,
                                    bsdf.location.y - 150)

    separate_node.location = (map_range_node.location.x - separate_node.width - 50,
                                    bsdf.location.y - 300)

    attribute_node.location = (length_node.location.x - attribute_node.width - 50,
                                    bsdf.location.y)

    mat.node_tree.links.new(map_range_node.outputs["Result"], color_ramp_node.inputs["Fac"])
    mat.node_tree.links.new(color_ramp_node.outputs["Color"], bsdf.inputs["Base Color"])
    mat.node_tree.links.new(bsdf.outputs["BSDF"], material_output_node.inputs["Surface"])

    bpy.data.objects[mesh_name].data.materials.append(mat)

    if "global_min" in mat["attributes"][attr_name].to_dict().keys():
        map_range_node.inputs["From Min"].default_value = mat["attributes"][attr_name]["global_min"]
        map_range_node.inputs["From Max"].default_value = mat["attributes"][attr_name]["global_max"]
    else:
        component = mat.vtk_attribute_component
        attr_stats = mat["attributes"][attr_name][component]
        map_range_node.inputs["From Min"].default_value = attr_stats["global_min"]
        map_range_node.inputs["From Max"].default_value = attr_stats["global_max"]


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
