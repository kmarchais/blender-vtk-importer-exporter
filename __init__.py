try:
    import blender_vtk_importer_exporter
except ImportError:
    import importlib
    import site
    import subprocess
    import sys
    from pathlib import Path

    # install the blender_tpms package in blender's python environment
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        str(Path(__file__).parent),
    ]
    subprocess.check_call(cmd)

    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.append(user_site)

    importlib.import_module("blender_tpms")


bl_info = {
    "name": "VTK import/Export",
    "author": "kmarchais",
    "version": (0, 1),
    "blender": (3, 6, 0),
    "location": "File > Import-Export",
    "description": "Import/Export VTK files",
    "warning": "",
    "doc_url": "https://github.com/kmarchais/blender-vtk-importer-exporter",
    "category": "Import-Export",
}

import blender_vtk_importer_exporter


def register() -> None:
    """Register the addon."""
    blender_vtk_importer_exporter.register()


def unregister() -> None:
    """Unregister the addon."""
    blender_vtk_importer_exporter.unregister()
