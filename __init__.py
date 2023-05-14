bl_info = {
    "name": "VTK Importer",
    "author": "kmarchais",
    "version": (0, 1),
    "blender": (3, 5, 0),
    "location": "File > Import-Export",
    "description": "Import VTK files",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty

import os
import glob

import pyvista as pv
import numpy as np


filepath = ""
files_pattern = ""
file_list = []


class ImportVTK(bpy.types.Operator, ImportHelper):
    """Load a VTK file"""
    bl_idname = "import.vtk"
    bl_label = "Import VTK"

    filename_ext = ".vtk"
    filter_glob: StringProperty(
        default="*.vtk;*.vtu;*.vtp",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    import_sequence: BoolProperty(
        name="Import Sequence?",
        description="Import a single file or a sequence of files",
        default=False,
    )

    pattern: StringProperty(
        name="Sequence Pattern",
        default="",
        description="example: filename-*.vtk",
    )

    def execute(self, context):
        global filepath, files_pattern, file_list

        filepath = self.filepath
        files_pattern = self.pattern
        
        polydata = pv.read(filepath)
        mesh_name = os.path.basename(filepath)
        if self.import_sequence:
            mesh_name = files_pattern

        faces = []
        if isinstance(polydata, pv.PolyData) and polydata.n_faces > 0:
            if not polydata.is_all_triangles():
                polydata = polydata.triangulate()
            faces = np.reshape(polydata.faces, (polydata.n_faces, 4))[:, 1:]
        elif isinstance(polydata, pv.UnstructuredGrid) and polydata.n_cells > 0:
            faces = np.reshape(polydata.cells, (polydata.n_cells, 4))[:, 1:]

        mesh = bpy.data.meshes.new(mesh_name)
        mesh.from_pydata(vertices=polydata.points, edges=[], faces=faces)
        mesh.update()

        obj = bpy.data.objects.new(mesh_name, mesh)
        bpy.context.scene.collection.objects.link(obj)

        for key, value in polydata.point_data.items():
            if key == "id":
                key = "id_" # id is a reserved keyword
            attr = bpy.data.meshes[obj.name].attributes.new(key, type='FLOAT', domain='POINT')
            attr.data.foreach_set('value', value)

        if self.import_sequence:
            bpy.app.handlers.frame_change_pre.append(update_attributes)
            file_list = glob.glob(os.path.join(os.path.dirname(filepath), files_pattern))
            file_list = sorted(file_list, key=lambda x: int(os.path.basename(x).split('.')[0].split('-')[-1]))
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_end = len(file_list) - 1

        return {'FINISHED'}


def update_attributes(scene):
    global filepath, file_list, files_pattern
    frame = scene.frame_current
    mesh_name = files_pattern

    polydata = pv.read(file_list[frame])
    mesh = bpy.data.meshes[mesh_name]
    mesh.attributes["position"].data.foreach_set('vector', np.ravel(polydata.points))
    for key, value in polydata.point_data.items():
        if key == "id":
            key = "id_"
        if key not in mesh.attributes.keys():
            mesh.attributes.new(key, type='FLOAT', domain='POINT')
        mesh.attributes[key].data.foreach_set('value', value)
    mesh.update()

    
def menu_func_import(self, context):
    self.layout.operator(ImportVTK.bl_idname, text="VTK (.vtk, .vtu, .vtp)")

def register():
    bpy.utils.register_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportVTK)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
