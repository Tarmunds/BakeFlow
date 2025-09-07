import importlib
from importlib import import_module

bl_info = {
    "name": "BakeFlow",
    "author": "Tarmunds",
    "version": (0, 9, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Tarmunds Addons > Marmoset Bridge",
    "description": "Tool",
    "tracker_url": "https://discord.gg/h39W5s5ZbQ",
    "category": "Import-Export",
}
  
_SUBMODULES = (
    "UvHelper.Functions",
    "UvHelper.Properties",
    "UvHelper.Operators",
    "UvHelper.Panels",
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
