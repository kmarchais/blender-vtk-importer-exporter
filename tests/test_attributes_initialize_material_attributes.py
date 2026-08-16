# Unit tests of attributes.initialize_material_attributes()
#   TODO: Check the setup of the "mat" argument also (only the setup of the "mesh" argument is checked).

import numpy as np

import bpy

import pytest

from utilities import *


m_attributes = import_submodule("attributes")
m_mesh       = import_submodule("mesh")


# Parametrization of the type of data stored in attribute
#   name:      Name of a manufactured field, based on vtkDataSetAttributes
#              see conftest_fixtures.manufactured_fields()
#   data_type: Type of data manipulated by Blender
#              see https://docs.blender.org/api/current/bpy_types_enum_items/attribute_type_items.html
@pytest.mark.parametrize(
    "name, data_type",
    [
        pytest.param(
            "int_scalars",         "INT",          id="int_scalars_2_INT",           marks=pytest.mark.xfail
        ),
        pytest.param(
            "int_vectors",         "FLOAT_VECTOR", id="int_vectors_2_FLOAT_VECTOR"
        ),
        pytest.param(
            "int_tensors",         "FLOAT4X4",     id="int_tensors_2_FLOAT4X4",      marks=pytest.mark.xfail
        ),
        pytest.param(
            "flt_scalars",         "FLOAT",        id="float_scalars_2_FLOAT"
        ),
        pytest.param(
            "flt_vectors",         "FLOAT_VECTOR", id="float_vectors_2_FLOAT_VECTOR"
        ),
        pytest.param(
            "Normals",             "FLOAT_VECTOR", id="Normals_2_FLOAT_VECTOR"
        ),
        pytest.param(
            "Texture Coordinates", "FLOAT2",       id="Texture_Coordinates_2_FLOAT2"
        ),
        pytest.param(
            "flt_tensors",         "FLOAT4X4",     id="float_tensors_2_FLOAT4X4",    marks=pytest.mark.xfail
        ),
    ]
)

# Parametrization of the domain of an attribute
#   t_domain: Name of domain manipulated by PyVista
#             see https://docs.pyvista.org/api/core/_autosummary/pyvista.dataset
#   b_domain: Name of domain manipulated by Blender
#             see https://docs.blender.org/api/current/bpy_types_enum_items/attribute_domain_items.html
#   suffix:   Suffix of the name of a manufactured field, based on PyVista
#             see conftest_utilities.set_attributes()
@pytest.mark.parametrize(
    "t_domain, b_domain, suffix",
    [
        pytest.param(
            "point_data", "POINT", "_point", id="point_data_2_POINT"
        ),
        pytest.param(
            "cell_data",  "FACE",  "_cell",  id="cell_data_2_FACE"
        ),
    ]
)

class TestClass:
    
    def test_domain_type(
        self,
        pvUG_one_triangle, # PyVista DataSet with attributes
        t_domain, b_domain, suffix, # Domain of the attribute
        name, data_type # Type of data stored in attribute 
    ):
        # Mesh and Material setup
        mesh_name = unique_mesh_name()
        mesh = m_mesh.vtk_to_mesh(pvUG_one_triangle, mesh_name)
        mat = bpy.data.materials.new(name=f"{mesh_name}_attributes")
        mat["attributes"] = {}
        
        # Collect of test data
        t_name = name
        if name not in ("Texture Coordinates", "Normals"):
            t_name += suffix
        t_data = getattr(pvUG_one_triangle, t_domain)
        if t_data.get(t_name) is None:
            pytest.skip("Irrelevant attribute")
        t_values = t_data[t_name]
        
        m_attributes.initialize_material_attributes(t_name, t_values, mesh, mat, b_domain)
        
        # Test if the attribute is set correctly
        assert mesh.attributes.find(t_name)      != -1
        assert mesh.attributes[t_name].data_type == data_type
        assert mesh.attributes[t_name].domain    == b_domain
        
        # Test if the values are set correctly
        if data_type in ("FLOAT2", "FLOAT_VECTOR"):
            # See https://docs.blender.org/api/current/bpy.types.Float2AttributeValue.html
            #     https://docs.blender.org/api/current/bpy.types.FloatVectorAttributeValue.html
            property_name = "vector"
        else:
            # See https://docs.blender.org/api/current/bpy.types.Float4x4AttributeValue.html
            #     https://docs.blender.org/api/current/bpy.types.FloatAttributeValue.html
            #     https://docs.blender.org/api/current/bpy.types.IntAttributeValue.html
            property_name = "value"
        b_values = np.zeros_like(t_values) # To store the values returned by Blender
        mesh.attributes[t_name].data.foreach_get(property_name, np.ravel(b_values))
        assert b_values == pytest.approx(t_values)
        
    