# Unitary tests of mesh.get_mesh_data_from_vtk()
# HowTo: In Blender/Scripting workspace, use "Text > Open" to read this script, then "Text > Run Script" to execute it

import importlib
import sys
import inspect
import traceback
import numpy as np
import pyvista as pv

# Reload modified python scripts during development and testing
#   see: https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts
#   see: https://docs.python.org/3/library/importlib.html#importlib.reload
current_package_prefix = "blender-vtk-importer-exporter-main"
for name, module in sys.modules.copy().items():
    if name.startswith(current_package_prefix):
        print(f"Reloading {name}")
        importlib.reload(module)
mesh = importlib.import_module(current_package_prefix+".mesh")

# Wrapper
def test_get_mesh_data_from_vtk(vtk_data):
    print("TEST: " + inspect.currentframe().f_back.f_code.co_name)
    try:
        vertices, edges, faces = mesh.get_mesh_data_from_vtk(vtk_data)
    except:
        print("..... FAILED")
        print(traceback.format_exc())
    else:
        print("..... PASS")
        
# Unstructured grid with a single triangle
def test_UnstructuredGrid_one_triangle():
    points = np.asarray([[0.0, 0.0, 0.0],
                         [1.0, 0.0, 0.0],
                         [0.0, 1.0, 0.0]])
    cells = np.asarray([3, 0, 1, 2])
    celltypes = [pv.CellType.TRIANGLE]
    vtk_data = pv.UnstructuredGrid(cells, celltypes, points)
    test_get_mesh_data_from_vtk(vtk_data)
        
def main():
    print()
    test_UnstructuredGrid_one_triangle()
    
if __name__ == "__main__":
    main()
