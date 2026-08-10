# Unit tests of utilities

import bpy

from utilities import *


class TestClass_modules:

    def test_get_current_module(self):
        module_name, module_path = get_current_module()
        assert len(module_name) > 0
        assert len(module_path) > 0
        

    def test_import_submodule_root(self):
        assert import_submodule() is not None
        

    def test_import_submodule_known(self):
        assert import_submodule("mesh") is not None
        

    def test_import_submodule_unknown(self):
        assert import_submodule("--unknown--") is None
        

    def test_reload_modules(self):
        assert reload_modules() > 0
        

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
        
