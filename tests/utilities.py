# Functions shared by unit tests

import bpy


def unique_mesh_name(keys=list()):
    prefix_val = "pytest_mesh_"
    prefix_len = len(prefix_val)
    highest_suffix = 0
    for mesh_name in keys:
        if mesh_name.startswith(prefix_val):
            highest_suffix = max(
                highest_suffix,
                float(mesh_name[prefix_len:]) # float() is required to handle e.g. 2.001
            )
    return f"{prefix_val}{int(highest_suffix)+1}"

