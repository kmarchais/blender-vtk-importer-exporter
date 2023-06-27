import os
import glob

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
import bpy
from bpy.app.handlers import persistent

import pyvista as pv
import numpy as np

from .nodes import convert_mesh_to_pointcloud, create_attribute_material

def sort_files(file_list):
    sorted_file_list = []
    patterns = []
    for file in file_list:
        pattern = file.name.split('.')[0].split('-')[0]
        if pattern not in patterns:
            patterns.append(pattern)
            sorted_file_list.append([file.name])
        else:
            sorted_file_list[patterns.index(pattern)].append(file.name)

    for i, sequence in enumerate(sorted_file_list):
        if len(sequence) > 1:
            sorted_file_list[i] = sorted(
                sequence,
                key=lambda x: int(x.split('.')[0].split('-')[-1])
            )

    return sorted_file_list

def create_mesh(data_object, mesh_name):
    faces = []
    if isinstance(data_object, pv.UnstructuredGrid):
        data_object = data_object.extract_geometry()
        # faces = np.reshape(data_object.cells, (data_object.n_cells, 4))[:, 1:]

    if not data_object.is_all_triangles():
        data_object = data_object.triangulate()
    faces = np.reshape(data_object.faces, (data_object.n_faces, 4))[:, 1:]

    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(vertices=data_object.points, edges=[], faces=faces)
    mesh.update()

    obj = bpy.data.objects.new(mesh_name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    attributes = []

    for key, value in data_object.point_data.items():
        if key == "id":
            key = "id_" # id is a reserved keyword
        value_type = 'FLOAT'
        if len(value.shape) == 2:
            value_type = 'FLOAT_VECTOR'
        attr = bpy.data.meshes[obj.name].attributes.new(key, type=value_type, domain='POINT')
        attr.data.foreach_set('value', value)
        
        attributes.append({"name": key, "min_value": np.min(value), "max_value": np.max(value)})
    
    
    for key, value in data_object.cell_data.items():
        if key == "id":
            key = "id_" # id is a reserved keyword
        value_type = 'FLOAT'
        if len(value.shape) == 2:
            value_type = 'FLOAT_VECTOR'
        attr = bpy.data.meshes[obj.name].attributes.new(key, type=value_type, domain='FACE')
        attr.data.foreach_set('value', value)
        
        attributes.append({"name": key, "min_value": np.min(value), "max_value": np.max(value)})
    
    if attributes:
        create_attribute_material(mesh_name, attributes)

    if data_object.n_faces == 0 and "radius" in data_object.point_data.keys():
        convert_mesh_to_pointcloud(mesh_name)

@persistent
def update_attributes(scene):
    frame = scene.frame_current
    print(f"\nframe : {frame}")

    files = bpy.context.scene["vtk_files"]
    directory = bpy.context.scene["vtk_directory"]

    for file in files:
        mesh_name = file[0].split(".")[0].split("-")[0]
        print(f"\nmesh : {mesh_name}")

        if len(file) > 1:
            polydata = pv.read(f"{directory}/{file[frame]}")
            mesh = bpy.data.meshes[mesh_name]

            mesh.attributes["position"].data.foreach_set('vector', np.ravel(polydata.points))

            for key, value in polydata.point_data.items():
                print(f"attribute : {key}\tmin : {np.min(value)}\tmax : {np.max(value)}")
                if key == "id":
                    key = "id_"
                if key not in mesh.attributes.keys():
                    value_type = 'FLOAT'
                    if len(value.shape) == 2:
                        value_type = 'FLOAT_VECTOR'
                    mesh.attributes.new(key, type=value_type, domain='POINT')
                mesh.attributes[key].data.foreach_set('value', value)

            for key, value in polydata.cell_data.items():
                print(f"attribute : {key}\tmin : {np.min(value)}\tmax : {np.max(value)}")
                if key == "id":
                    key = "id_"
                if key not in mesh.attributes.keys():
                    value_type = 'FLOAT'
                    if len(value.shape) == 2:
                        value_type = 'FLOAT_VECTOR'
                    mesh.attributes.new(key, type=value_type, domain='FACE')
                mesh.attributes[key].data.foreach_set('value', value)

            mesh.update()

    print("-" * os.get_terminal_size().columns)


class ImportVTK(bpy.types.Operator, ImportHelper):
    """Load a VTK file"""
    bl_idname = "import.vtk"
    bl_label = "Import VTK"

    filename_ext = ".vtk"
    filter_glob: StringProperty(
        default="*.vtk;*.vtu;*.vtp;*.vtm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement,
                                         options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        # global files, directory

        files = sort_files(self.files)

        directory = os.path.dirname(self.filepath)

        bpy.context.scene["vtk_files"] = files
        bpy.context.scene["vtk_directory"] = directory

        for file in files:
            data = pv.read(f"{directory}/{file[0]}")
            mesh_name = file[0].split('.')[0].split('-')[0]

            if isinstance(data, pv.MultiBlock):
                for key in data.keys():
                    create_mesh(data[key], f"{mesh_name} : {key}")
            else:
                create_mesh(data, mesh_name)

        max_frame = 0
        for file in files:
            max_frame = max(max_frame, len(file) - 1)

        if max_frame != 0:
            # while len(bpy.app.handlers.frame_change_pre) > 1:
            #     bpy.app.handlers.frame_change_pre.pop()
            bpy.app.handlers.frame_change_post.append(update_attributes)

            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_end = max_frame
            bpy.context.scene.frame_current = 0


        return {'FINISHED'}
