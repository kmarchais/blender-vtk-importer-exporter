from pathlib import Path

from blender_vtk_importer_exporter.importer import sort_files


def test_sort_files() -> None:
    files = [
        Path("file-2.vtk"),
        Path("file-5.vtk"),
        Path("file-3.vtk"),
        Path("file-1.vtk"),
        Path("file-4.vtk"),
    ]
    sorted_files = sort_files(files)
    assert sorted_files[0] == [file.name for file in sorted(files)]
