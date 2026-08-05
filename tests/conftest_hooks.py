# Configuration of pytest hooks
#   see https://docs.pytest.org/en/stable/reference/reference.html#hooks

import os

import pytest


# Specify the order of tests
#   see https://stackoverflow.com/questions/17571438/how-to-control-test-case-execution-order-in-pytest

# Ordered list of substring expressions to match
#   The tests that do not match any expression are run last
ordered_list_of_tests = [
    "utilities",
    "mesh_get_mesh_data_from_vtk",
    "mesh_vtk_to_mesh"
]

def tests_order(item: pytest.Item) -> int:
    long_name = (
        os.path.basename(item.path) + "::" + # Module where the test was collected from
        item.parent.name            + "::" + # Class in which the test is defined
        item.name                            # Function coding the test
    )
    for rank, expression in enumerate(ordered_list_of_tests):
        if expression in long_name:
            break
    return rank

def pytest_collection_modifyitems(items):
    items.sort(key=tests_order)
    
