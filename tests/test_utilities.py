# Unit tests of utilities

import bpy

from utilities import *


class TestClass_unique_name:

    def test_empty(self):
        keys = list()
        name = unique_name("pytest_", keys)
        assert len(name) > 0
        

    def test_no_match(self):
        keys = list("Cube")
        name = unique_name("pytest_", keys)
        assert len(name) > 0
        

    def test_matching(self):
        prefix = "pytest_"
        keys = list()
        name_1 = unique_name(prefix, keys)
        keys += [name_1]
        name_2 = unique_name(prefix, keys)
        assert name_1 != name_2
        

    def test_mesh(self):
        mesh_name = unique_mesh_name()
        assert bpy.data.meshes.find(mesh_name) == -1
        
