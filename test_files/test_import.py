import pyvista as pv
import numpy as np

def remove_1d_elements(mesh: pv.PolyData) -> pv.PolyData:
    faces = mesh.faces
    n_faces = mesh.n_faces
    j = 0
    while j < n_faces:
        n_points = faces[j]
        if n_points == 2:
            faces = np.delete(faces, slice(j, j + n_points + 1))
            n_faces -= 1
        else:
            j += n_points + 1
    return pv.PolyData(mesh.points, faces=faces)

vtk = pv.read("test_files/blade.vtk")
vtk.plot()
if isinstance(vtk, pv.UnstructuredGrid):
    print(len(vtk.cells), vtk.n_cells)
    vtk = vtk.extract_surface()
    
    if not vtk.is_all_triangles:
        vtk = vtk.triangulate()
    faces = np.reshape(vtk.faces, (vtk.n_faces, 4))[:, 1:]

    # faces = np.reshape(vtk.cells, (vtk.n_cells, 4))[:, 1:]


vtk.plot()