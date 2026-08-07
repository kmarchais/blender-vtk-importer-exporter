# How to run unit tests

Unit testing is based on the `pytest` framework (see https://docs.pytest.org/en/stable/index.html).

All test files are in the `tests` directory, the main script being `run_pytest_in_blender.py`. Two modes are supported, without or with graphical display. Both require to launch Blender from the command line (see https://docs.blender.org/manual/en/latest/advanced/command_line/launch/index.html). Before launching Blender, go to the `tests` directory. The tests output is printed in the terminal. By default, all tests are run, with the lowest verbosity.

## Without graphical display

In the terminal, execute:

```
blender --python-use-system-env --background --python run_pytest_in_blender.py
```

## With graphical display

In the terminal, execute:

```
blender --python-use-system-env
```

Then open the `Scripting` workspace, and use `Text > Open` to read the file `run_pytest_in_blender.py`. It can be executed more than one time using `Text > Run Script`.

*Side note: the "--python-use-system-env" flag is required if some packages, including `pytest`, are not installed along with others provided with Blender.*

# How to configure a test session

All `pytest` command-line flags can be specified (see https://docs.pytest.org/en/stable/reference/reference.html#command-line-flags). 

To facilitate the management of verbosity, the option `[-d or --details LEVEL]` is added, with the level of details between 0 and 3:

- 0 : Shows only the counts of failed, passed and deselected tests (default)

- 1 : Adds the name of each processed file, with successes and failures

- 2 : Shows the result of each individual test, passed or failed

- 3 : Prints on stdout/stderr are no longer captured



The following example increases the level of details to 2, and runs only the tests in the file `test_mesh_get_mesh_data_from_vtk.py`.

## Without graphical display

In the terminal, execute:

```
blender --python-use-system-env --background --python run_pytest_in_blender.py -- -d 2 -k get_mesh_data_from_vtk
```

Take notice that the `pytest` command-line flags along with the level of details option are all positioned **after** the `--` symbol.

## With graphical display

In the `Text Editor`, edit the bottom of the file `run_pytest_in_blender.py` and modify the arguments of the calling sequence to the `main()` function as:

```
main(details=2, pytest_args=["-k get_mesh_data_from_vtk"])
```

Then use `Text > Save` and rerun the script.

# Known issues

- On quitting Blender GUI, an exception is raised in module `unregister()`. It is related to reloading modules before running `pytest`. However, it does not seem to affect the results of `pytest`.

- Due to the caching mechanism of Python import system, renamed or deleted tests are still run when Blender GUI is used. One workaround is to restart Blender. An other one is to purge the `tests/__pycache__` directory.
