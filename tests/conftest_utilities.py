# Functions shared by fixtures

import os

import numpy as np
import pyvista as pv
from vtk import vtkDataSetAttributes as vtkAttributeTypes


# Add attributes to a dataset
#   See https://docs.pyvista.org/api/core/_autosummary/pyvista.dataset
#       https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetattributes
def set_attributes(dataset, fields):
    for data, suffix, scale in (
        (dataset.cell_data,  "_cell", -1),  # Cell values are set negative
        (dataset.point_data, "_point", 1)): # Point values are set positive
        
        n = data.valid_array_len
        if n > len(fields[0][2]):
            msg = (f"The size of fields must be at least equal to {n}. "
                   "See manufactured_fields() in conftest_fixtures.py.")
            raise ValueError(msg)
            
        for f_name, f_type, f_array in fields:
            f_data = f_array[:n] * scale
            match f_type:
                case vtkAttributeTypes.NORMALS:
                    data.active_normals = f_data
                case vtkAttributeTypes.TCOORDS:
                    data.active_texture_coordinates = f_data
                case _:
                    f_name += suffix
                    data.set_array(f_data, f_name)
                    match f_type:
                        case vtkAttributeTypes.SCALARS:
                            dataset.active_scalars_name = f_name
                        case vtkAttributeTypes.VECTORS:
                            dataset.active_vectors_name = f_name
                        case vtkAttributeTypes.TENSORS:
                            dataset.active_tensors_name = f_name
                        case _:
                            msg = f"Unsupported vtkDataSetAttributes type: {f_type}."
                            raise ValueError(msg)

    return
    

# Name of the directory to dump the manufactured datasets,
#   relative to the directory "tests"
dumpdir_name="data"


# Dump to disk a dataset
def dump_dataset(dataset, request):
    if request.config.getoption("dump"):
        filename = os.path.join(
            dumpdir_name,
            request.fixturename + ".vtk"
        )
        dataset.save(filename)
    return
    

# Name of the attribute indicating the cells to be deleted,
#   to manufacture the datasets with a single cell
to_remove_key = ".to_remove" # Hidden from Blender UI


# Add attributes to a dataset, tag the cells to be deleted
#   and dump it to disk
def finalize_dataset(dataset, fields, request):
    set_attributes(dataset, fields)
    
    to_remove = np.full(dataset.cell_data.valid_array_len, True)
    to_remove[0] = False # To keep only the first cell
    dataset.cell_data[to_remove_key] = to_remove
    
    dump_dataset(dataset, request)
    return
    

# Manufacture a PolyData dataset
def make_PolyData(
    request,
    points, fields,
    verts=None, lines=None, faces=None, strips=None
):
    dataset = pv.PolyData(
        points,
        verts=verts, lines=lines, faces=faces, strips=strips
    )
    finalize_dataset(dataset, fields, request)
    return dataset
    

# Manufacture an UnstructuredGrid dataset
def make_UnstructuredGrid(
    request,
    points, fields,
    cells, celltypes
):
    dataset = pv.UnstructuredGrid(
        cells, celltypes, points
    )
    finalize_dataset(dataset, fields, request)
    return dataset
    

# Merge datasets and reset attributes
def merge_datasets(
    request, fields,
    dataset_list=None, name_list=None
):
    if dataset_list is None:
        dataset_list = list()
    if name_list: # Extend the list of datasets to merge
        for name in name_list:
            dataset_list.append(request.getfixturevalue(name))
    
    dataset = pv.merge(dataset_list)
    
    # Reset the attributes, preserving the cells to be deleted
    to_remove = dataset.cell_data[to_remove_key] # Backup
    dataset.point_data.clear()
    dataset.cell_data.clear()
    set_attributes(dataset, fields)
    dataset.cell_data[to_remove_key] = to_remove # Restore
    
    return dataset
    

# Remove cells from a dataset
def remove_cells(dataset, invert_selection=False):
    to_remove = dataset.cell_data[to_remove_key].astype(np.bool_)
    if invert_selection:
        to_remove = np.logical_not(to_remove)
    return dataset.remove_cells(to_remove)
    

# Manufacture a dataset by removing cells
def strip_dataset(full_dataset, request):
    strip_dataset = remove_cells(full_dataset)
    dump_dataset(strip_dataset, request)
    return strip_dataset
    
