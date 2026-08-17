# Functions shared by fixtures

from vtk import vtkDataSetAttributes as vtkAttributeTypes


# Add attributes to a DataSet
#   See https://docs.pyvista.org/api/core/_autosummary/pyvista.dataset
#       https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetattributes
def set_attributes(dataset, fields):
    for data, suffix, scale in (
        (dataset.cell_data,  "_cell", -1),  # Cell values are set negative
        (dataset.point_data, "_point", 1)): # Point values are set positive
        
        n = data.valid_array_len
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
    
