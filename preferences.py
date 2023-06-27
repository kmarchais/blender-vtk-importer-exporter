from __future__ import annotations

import bpy

pip_version = "Not installed"
numpy_version = "Not installed"
pyvista_version = "Not installed"
try:
    import pip
    pip_version = pip.__version__
except ModuleNotFoundError:
    pass
try:
    import numpy
    numpy_version = numpy.__version__
except ModuleNotFoundError:
    pass
try:
    import pyvista
    pyvista_version = pyvista.__version__
except ModuleNotFoundError:
    pass


class VtkImporterPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    pip : bpy.props.StringProperty(name="Pip")
    pip_update : bpy.props.BoolProperty(name="Update Pip")

    def draw(self, context):
        layout : bpy.types.UILayout = self.layout
        layout.label(text="Dependencies:")
        row = layout.row()
        row.label(text=f"Pip: \t {pip_version}")
        row.prop(self, "pip_update", text="Update Pip", toggle=True)
        row = layout.row()
        row.label(text=f"Numpy: \t {numpy_version}")
        row = layout.row()
        row.label(text=f"PyVista: \t {pyvista_version}")

# class VtkImporterPanel(bpy.types.Panel):
#     bl_idname = "vtk_importer.panel"
#     bl_label = "TEST"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "TEST"

#     def draw(self, context):
#         self.layout.operator("vtk_importer.execute_pip_update", text="Execute Pip Update")



def register():
    bpy.utils.register_class(VtkImporterPreferences)
    # bpy.utils.register_class(VtkImporterPanel)


def unregister():
    bpy.utils.unregister_class(VtkImporterPreferences)
    # bpy.utils.unregister_class(VtkImporterPanel)
