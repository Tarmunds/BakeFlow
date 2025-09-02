# marmoset_bridge/__init__.py
bl_info = {
    "name": "Marmoset Bridge",
    "author": "Tarmunds",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Tarmunds Addons > Marmoset Bridge",
    "description": "",
    "tracker_url": "https://discord.gg/h39W5s5ZbQ",
    "category": "Import-Export",
}

import importlib
from importlib import import_module

# List your submodules once, in the order you want them registered.
_SUBMODULES = (
    "BakingSupply.Functions",
    "BakingSupply.Properties",
    "BakingSupply.Operators",
    "BakingSupply.Panels",
    "MarmosetBridge.Functions",
    "MarmosetBridge.MapProperties",
    "MarmosetBridge.Properties",
    "MarmosetBridge.Operators",
    "MarmosetBridge.Panels",
)

# Import them relative to this package name
_modules = tuple(import_module(f".{name}", __name__) for name in _SUBMODULES)

for m in _modules:
    importlib.reload(m)

def register():    
    for m in _modules:
        if hasattr(m, "register"):
            m.register()

def unregister():
    for m in reversed(_modules):
        if hasattr(m, "unregister"):
            m.unregister()
