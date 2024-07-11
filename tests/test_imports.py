from blender_vtk_importer_exporter.importer import sort_files

def test_sort_files() -> None:
    files = ["file-2.vtk", "file-5.vtk", "file-3.vtk", "file-1.vtk", "file-4.vtk"]
    sorted_files = sort_files(files)
    assert sorted_files == sorted(files)

if __name__ == "__main__":
    test_sort_files()