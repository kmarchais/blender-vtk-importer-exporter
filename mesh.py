"""Mesh module."""

from __future__ import annotations

import warnings
from typing import TypeAlias

import bpy
import numpy as np
import pyvista as pv

from .attributes import initialize_material_attributes, update_material_attributes
from .material_panel import update_attributes_enum
from .nodes import convert_mesh_to_pointcloud, create_attribute_material_nodes

VTK_data: TypeAlias = pv.PolyData | pv.UnstructuredGrid


def update_mesh_frame(scene: bpy.types.Scene) -> None:
    """Update mesh frame."""
    if (
        "vtk_files" not in bpy.context.scene
        and "vtk_directory" not in bpy.context.scene
    ):
        return

    frame: int = scene.frame_current

    files: list[str] = bpy.context.scene["vtk_files"]
    directory: str = bpy.context.scene["vtk_directory"]
    frame_sep: str = bpy.context.scene["vtk_frame_sep"]

    if (
        not isinstance(files, list)
        or not isinstance(directory, str)
        or not isinstance(frame_sep, str)
    ):
        raise TypeError

    for file in files:
        mesh_name = file[0].split(".")[0].split(frame_sep)[0]

        if len(file) > 1:
            polydata = pv.read(f"{directory}/{file[frame]}")

            mesh = bpy.data.meshes[mesh_name]
            if len(polydata.points) == mesh.vertices:  # update mesh
                mesh.attributes["position"].data.foreach_set(
                    "vector",
                    np.ravel(polydata.points),
                )
                mat = bpy.data.materials[f"{mesh_name}_attributes"]

                for attr_name, values in polydata.point_data.items():
                    update_material_attributes(attr_name, values, mesh, mat, "POINT")

                for attr_name, values in polydata.cell_data.items():
                    update_material_attributes(attr_name, values, mesh, mat, "FACE")

                mesh.update()
            else:  # create new mesh
                # need to replace the current mesh by a new one
                # because of number of attributes
                err_msg = "Number of vertices is different."
                raise NotImplementedError(err_msg)


def get_mesh_data_from_vtk(
    vtk_data: VTK_data,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Get mesh data from VTK data."""
    edges = []
    faces = []

    if isinstance(vtk_data, pv.PolyData):
        if not vtk_data.is_all_triangles:
            vtk_data = vtk_data.triangulate()
        faces = np.reshape(vtk_data.faces, (vtk_data.n_cells, 4))[:, 1:]

    if isinstance(vtk_data, pv.UnstructuredGrid):
        faces = []
        for cell_type, cells in vtk_data.cells_dict.items():
            if cell_type == pv.CellType.LINE.value:
                edges = cells
            elif pv.CellType.TRIANGLE.value <= cell_type <= pv.CellType.QUAD.value:
                faces += cells
            else:
                warnings.warn(f"Unsupported cell type: {cell_type} yet.", stacklevel=2)

    return vtk_data.points, edges, faces


def update_mesh_from_vtk(
    mesh: bpy.types.Mesh,
    vtk_data: VTK_data,
    *,
    update_attributes: bool = True,
) -> None:
    """Update mesh from VTK data."""
    vertices, edges, faces = get_mesh_data_from_vtk(vtk_data)

    mesh.clear_geometry()
    mesh.from_pydata(vertices=vertices, edges=edges, faces=faces)

    if update_attributes:
        set_mesh_attributes(mesh, vtk_data)


def vtk_to_mesh(vtk_data: VTK_data, mesh_name: str) -> bpy.types.Mesh:
    """Convert VTK data to Blender mesh."""
    vertices, edges, faces = get_mesh_data_from_vtk(vtk_data)

    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(vertices=vertices, edges=edges, faces=faces)
    mesh.update()

    return mesh


def set_mesh_attributes(_: bpy.types.Mesh, __: VTK_data) -> None:
    """Set mesh attributes."""
    # create mesh attributes
    return


def create_object(
    context: bpy.types.Context,
    vtk_data: VTK_data,
    mesh_name: str,
) -> bpy.types.Object:
    """Create object from VTK data."""
    # convert vtk mesh to blender mesh
    # if attributes exist
    # - create material for attributes
    # - set vtk data into mesh attributes
    # create blender object
    # convert mesh to point cloud if it is point cloud
    mesh = vtk_to_mesh(vtk_data, mesh_name)

    mesh_name = mesh.name
    obj = bpy.data.objects.new(mesh_name, mesh)
    obj["data_range"] = {}
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    if vtk_data.point_data or vtk_data.cell_data:
        mat = bpy.data.materials.new(name=f"{mesh_name}_attributes")
        mat["attributes"] = {}

        for attr_name, values in vtk_data.point_data.items():
            initialize_material_attributes(attr_name, values, mesh, mat, "POINT")

        for attr_name, values in vtk_data.cell_data.items():
            initialize_material_attributes(attr_name, values, mesh, mat, "FACE")

        create_attribute_material_nodes(mesh_name)
        update_attributes_enum(mat, context)

    is_point_cloud = (
        len(mesh.polygons) + len(mesh.edges) == 0 and "rad" in vtk_data.point_data
    )
    if is_point_cloud:
        convert_mesh_to_pointcloud(mesh_name)

    return obj
