# Run unitary tests with pytest

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
        if name.startswith((current_package_prefix, "test_")):
            if verbose:
                print(f"Reloading {name}")
            importlib.reload(module)
            

# Get this script own arguments
#   see $BLENDER_HOME/scripts/templates_py/background_job.py
def get_args(argv):
    usage_text = (
        "Run blender in background mode with pytest:\n"
        "  blender --python-use-system-env --background --python run_pytest_in_blender.py -- [options]"
    )
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        description=usage_text
    )
    
    parser.add_argument(
        "-v", "--verbosity", type=int, default=0, metavar="LEVEL",
        help="Verbosity level, from 0 to 3"
    )
    parser.add_argument(
        "-k", "--keywords", default="", metavar="EXPRESSION",
        help="Only run tests which match the given substring expression"
    )
    
    args = parser.parse_args(argv)
    
    return args.verbosity, args.keywords


def main(verbosity=0, keywords=""):
    # Get comand line args to tune pytest in background mode
    argv = sys.argv
    if "--" in argv:
        verbosity, keywords = get_args(argv[argv.index("--") + 1:])
        
    # Reload modules in interactive mode
    if "--background" not in argv:
        reload_modules()
    
    # Format args for pytest
    pytest_args = {
        0: ["-q"],      # Shows only the counts of failed, passed and deselected tests
        1: [],          # Adds the name of each processed file, with successes and failures
        2: ["-v"],      # Shows the result of each individual test, passed or failed
        3: ["-v", "-s"] # Prints on stdout/stderr are no longer captured
    }.get(verbosity, ["-q"]) # Default same as 0
    if keywords:
        pytest_args += ["-k " + keywords]
        
    # Run pytest
    pytest.main(args=pytest_args)
    

if __name__ == '__main__':
    main() # Default: run all tests with minimal output
#    main(verbosity=2, keywords="get_mesh_data_from_vtk") # Example running a single file of tests
