from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import numpy as np
from matplotlib import colormaps
import cmcrameri
names = sorted(name for name in colormaps if name.startswith("cmc."))
values = np.linspace(0, 1, 513)
before = {name: colormaps[name](values) for name in names}
for name in names:
    colormaps.unregister(name)
spec = spec_from_file_location("addon_colormaps", Path(__file__).resolve().parents[1] / "colormaps.py")
module = module_from_spec(spec)
spec.loader.exec_module(module)
module.register_crameri_colormaps()
assert sorted(name for name in colormaps if name.startswith("cmc.")) == names
for name in names:
    np.testing.assert_array_equal(colormaps[name](values), before[name])
module.register_crameri_colormaps()
print(f"PASS: all {len(names)} Crameri maps match cmcrameri exactly at 513 samples; repeat registration passes")
