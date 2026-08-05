# Unit tests of utilities

import bpy

from utilities import *


class TestClass:

    def test_unique_mesh_name_empty(self):
        keys = list()
        mesh_name = unique_mesh_name(keys)
        assert len(mesh_name) > 0
        

    def test_unique_mesh_name_no_match(self):
        keys = list("Cube")
        mesh_name = unique_mesh_name(keys)
        assert len(mesh_name) > 0
        

    def test_unique_mesh_name_matching(self):
        keys = list()
        mesh_name_1 = unique_mesh_name(keys)
        keys += [mesh_name_1]
        mesh_name_2 = unique_mesh_name(keys)
        assert mesh_name_1 != mesh_name_2
        

    def test_unique_mesh_name_bpy(self):
        mesh_name = unique_mesh_name(bpy.data.meshes.keys())
        assert bpy.data.meshes.find(mesh_name) == -1
        
