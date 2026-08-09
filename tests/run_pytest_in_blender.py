# Run unit tests with pytest

import sys
import importlib
import argparse

import pytest

# Reload python scripts possibly modified during development and testing
#   see: https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts
#   see: https://docs.python.org/3/library/importlib.html#importlib.reload
def reload_modules(verbose=False):
    current_package_prefix = "blender-vtk-importer-exporter-main"
    for name, module in sys.modules.copy().items():
        if name.startswith((current_package_prefix, "utilities", "test_")):
            if verbose:
                print(f"Reloading {name}")
            importlib.reload(module)
            

# Get this script own arguments
#   see $BLENDER_HOME/scripts/templates_py/background_job.py
def get_args(argv):
    usage_text = (
        "Run blender in background mode with pytest:\n"
        "  blender --python-use-system-env --background --python run_pytest_in_blender.py -- [options] [pytest options]"
    )
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        description=usage_text
    )
    
    parser.add_argument(
        "-d", "--details", type=int, default=0, metavar="LEVEL",
        help="Level of details to print, from 0 to 3"
    )
    
    args, pytest_args = parser.parse_known_args(argv)
    
    return args.details, pytest_args


def main(details=0, pytest_args=[]):
    # Get comand-line flags to setup pytest in background mode
    #   see https://docs.pytest.org/en/stable/reference/reference.html#command-line-flags
    argv = sys.argv
    if "--" in argv:
        details, pytest_args = get_args(argv[argv.index("--") + 1:])
    
    # Format the level of details for pytest
    pytest_args += {
        0: ["-q"],      # Shows only the counts of failed, passed and deselected tests
        1: [],          # Adds the name of each processed file, with successes and failures
        2: ["-v"],      # Shows the result of each individual test, passed or failed
        3: ["-v", "-s"] # Prints on stdout/stderr are no longer captured
    }.get(details, ["-q"]) # Default same as 0
        
    # Reload modules in interactive mode
    background = "--background" in argv
    if not background:
        reload_modules()
        
    # Run pytest
    #   see https://docs.pytest.org/en/stable/reference/exit-codes.html
    exit_code = pytest.main(args=pytest_args)
    
    return exit_code, background
    

if __name__ == '__main__':
    exit_code, background = main() # Default: run all tests with minimal output
#    exit_code, background = main(details=2, pytest_args=["-k get_mesh_data_from_vtk"]) # Example running a single file of tests
    if background:
        sys.exit(exit_code)
