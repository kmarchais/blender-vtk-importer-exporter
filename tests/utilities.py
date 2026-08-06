# Functions shared by unit tests

import bpy


def unique_name(prefix_val=str(), keys=list()):
    prefix_len = len(prefix_val)
    highest_suffix = 0
    for name in keys:
        if name.startswith(prefix_val):
            highest_suffix = max(
                highest_suffix,
                float(name[prefix_len:]) # float() is required to handle e.g. 2.001
            )
    return f"{prefix_val}{int(highest_suffix)+1}"


def unique_mesh_name():
    return unique_name("pytest_mesh_", bpy.data.meshes.keys())
    
