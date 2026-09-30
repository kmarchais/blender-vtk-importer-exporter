"""Check add-on activation with unavailable Matplotlib font discovery."""
import importlib
import importlib.abc
from pathlib import Path
import sys

import bpy
import numpy as np


class BrokenFontDiscovery(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "matplotlib.font_manager":
            raise KeyError("_items")
        return None


assert "matplotlib.font_manager" not in sys.modules
sys.meta_path.insert(0, BrokenFontDiscovery())
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent))
module_name = root.name
assert bpy.ops.preferences.addon_enable(module=module_name) == {"FINISHED"}
addon = importlib.import_module(module_name)
assert bpy.context.scene.default_colormap == "viridis"
assert any(item[0] == "cmc.batlow" for item in addon.material_panel.vtk_enum_colormaps(None, None))
assert addon.preferences.dependencies["cmcrameri"]["version"] != "Not installed"

# Exercise color-map lookups in material creation and updates.
mesh = bpy.data.meshes.new("font_discovery_check")
mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
obj = bpy.data.objects.new(mesh.name, mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
mat = bpy.data.materials.new(f"{mesh.name}_attributes")
mat["attributes"] = {}
addon.attributes.initialize_material_attributes("value", np.array([0., 0.5, 1.]), mesh, mat, "POINT")
bpy.context.scene.default_colormap = "cmc.batlow"
addon.nodes.create_attribute_material_nodes(mesh.name)
mat.vtk_colormaps = "viridis"
addon.material_panel.update_colormap_enum(mat, bpy.context)
from matplotlib import colormaps
elements = mat.node_tree.nodes["Color Ramp"].color_ramp.elements
expected = colormaps["viridis"](np.linspace(0, 1, len(elements))) ** 2.2
np.testing.assert_allclose([element.color[:] for element in elements], expected, rtol=1e-6)
assert "matplotlib.pyplot" not in sys.modules
assert "matplotlib.font_manager" not in sys.modules
assert "cmcrameri" not in sys.modules
assert bpy.ops.preferences.addon_disable(module=module_name) == {"FINISHED"}
assert bpy.ops.preferences.addon_enable(module=module_name) == {"FINISHED"}
assert bpy.ops.preferences.addon_disable(module=module_name) == {"FINISHED"}
print("PASS: activation, reactivation and material ramps work with broken font discovery")
