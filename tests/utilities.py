# Functions shared by unit tests

import os
import sys
import pathlib
import importlib

import bpy


def get_current_module():
    this_file   = pathlib.Path(__file__).resolve() # Full path to this script
    module_name = os.path.basename(this_file.parents[1]) # Directory cloned from the repository
    module_path = str(this_file.parents[2]) # Directory above the cloned directory
    return module_name, module_path
    

def import_submodule(submodule_name=str()):
    module_name, module_path = get_current_module()
    if module_path not in sys.path:
        sys.path.append(module_path)
    name = module_name
    if submodule_name:
        name += "." + submodule_name
    module = sys.modules.copy().get(name)
    if not module:
        try:
            module = importlib.import_module(name)
        except:
            module = None
    return module
    

# Reload python scripts possibly modified during development and testing
#   see: https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts
#   see: https://docs.python.org/3/library/importlib.html#importlib.reload
def reload_modules(verbose=False):
    module_name, module_path = get_current_module()
    count = 0
    for name, module in sys.modules.copy().items():
        if name.startswith((module_name, "utilities", "test_")):
            if verbose:
                print(f"Reloading {name}")
            importlib.reload(module)
            count += 1
    return count
    

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
    
