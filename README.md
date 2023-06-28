# blender-vtk-importer
- Import VTK files (VTK, VTU, VTP, VTM)
- Store data as attributes
- Import sequence of files 

<p align="center">
  <img src="tpms.gif" width="50%"/>
</p>

# Installation
- Download the ZIP file from this repository
- In Blender, Edit > Preferences > Add-ons > Install... find the zip file that you just downloaded and click Install Add-on
- Enable the add-on by clicking the checkbox
- Install the PyVista package with Python:
  - In the python console copy paste and run the following line: 
  - `import sys, subprocess; subprocess.call([sys.executable, '-m', 'pip', 'install', 'pyvista'])`

# TODO
- Fix real colors of the colormaps
- Preferences panel