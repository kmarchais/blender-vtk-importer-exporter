"""Register Crameri color tables without importing its plotting helpers."""

from importlib.metadata import distribution

from matplotlib import colormaps
from matplotlib.colors import ListedColormap
import numpy as np


def register_crameri_colormaps():
    # Read the installed package's data without executing cmcrameri.__init__.
    data_dir = distribution("cmcrameri").locate_file("cmcrameri/cmaps")
    for path in sorted(data_dir.glob("*.txt")):
        name = f"cmc.{path.stem}"
        cmap = ListedColormap(np.loadtxt(path), name=path.stem)
        if name not in colormaps:
            colormaps.register(cmap, name=name)
        if not path.stem.endswith("S") and f"{name}_r" not in colormaps:
            colormaps.register(cmap.reversed(), name=f"{name}_r")
