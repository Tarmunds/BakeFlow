import bpy, textwrap, subprocess, tempfile, os
from pathlib import Path
from .Properties import MarmoConfig, Map_Types
from typing import Callable, Dict, List, Optional

def GoToLine(layout, *, scale_y=1.2, align=True):
    row = layout.row(align=align)
    row.scale_y = scale_y
    return row

#ensure no error when wirte the path with 4 backslashes
def win_raw(path: str) -> str:
    return str(Path(path)).replace("\\", "\\\\")

# ensure condition is true, otherwise raise a RuntimeError with the given message
def ensure(cond: bool, msg: str):
    if not cond:
        raise RuntimeError(msg)


ADDON_KEY = (__package__ or __name__).split(".")[0]
def get_prefs() -> bpy.types.AddonPreferences:
    return bpy.context.preferences.addons[ADDON_KEY].preferences

def get_path_abs() -> str:
    """Return the absolute, Blender-evaluated path."""
    return bpy.path.abspath(get_prefs().marmoset_path)

def next_unused_enum(container):
    if len(container.maps)==1:
        return Map_Types[0][0]
    used_types = {item.map_type for item in container.maps}
    for enum_value, _, _ in Map_Types:
        if enum_value not in used_types:
            return enum_value
    # fallback: reuse first entry
    return Map_Types[0][0]


# ===================== Builder =====================

# A simple utility class to build scripts or code snippets dynamically
class ScriptBuilder:
    def __init__(self):
        self.parts: List[str] = []
    def line(self, s: str): self.parts.append(s)
    def line_if(self, cond: bool, s: str):
        if cond: self.parts.append(s)
    def assign(self, target: str, value_code: str):
        self.parts.append(f"{target} = {value_code}")
    def assign_if(self, cond: bool, target: str, value_code: str):
        if cond: self.parts.append(f"{target} = {value_code}")
    def section(self, text: str):
        self.parts.append(textwrap.dedent(text).strip("\n"))
    def build(self) -> str:
        return "\n".join(self.parts) + "\n"

# ===================== Sections =====================

def sec_header(sb: ScriptBuilder):
    sb.section("""
    import mset
    mset.newScene()
    baker = mset.BakerObject()
    """)

def sec_imports(sb: ScriptBuilder, cfg: MarmoConfig):
    if cfg.low_fbx:
        sb.line_if(bool(cfg.low_fbx),  f'baker.importModel(r"{win_raw(cfg.low_fbx)}")')
    if cfg.high_fbx:
        sb.line_if(bool(cfg.high_fbx), f'baker.importModel(r"{win_raw(cfg.high_fbx)}")')

def sec_core_params(sb: ScriptBuilder, cfg: MarmoConfig):
    sb.assign("baker.outputPath",      f'r"{win_raw(cfg.export_path)}"')
    sb.assign("baker.outputBits",      str(cfg.pixel_bits))
    sb.assign("baker.outputSamples",   str(cfg.samples))
    sb.assign("baker.outputWidth",     str(cfg.width))
    sb.assign("baker.outputHeight",    str(cfg.height))
    sb.assign("baker.edgePadding",     f'"{cfg.edge_padding}"')
    sb.assign("baker.outputSoften",    str(cfg.soften))
    sb.assign("baker.useHiddenMeshes", str(cfg.use_hidden_meshes))
    sb.assign("baker.ignoreTransforms",str(cfg.ignore_transforms))
    sb.assign("baker.smoothCage",      str(cfg.smooth_cage))
    sb.assign("baker.ignoreBackfaces", str(cfg.ignore_backfaces))
    sb.assign("baker.tileMode",        str(cfg.tile_mode))


def sec_maps(sb: ScriptBuilder, cfg: MarmoConfig):
    #sb.section("""
    #normal_map = None
    #for _map in baker.getAllMaps():
    #    if isinstance(_map, mset.NormalBakerMap):
    #        normal_map = _map
    #        break
    #""")
    #sb.line_if(True, f"if normal_map: normal_map.flipY = {cfg.normal_flip_y}")

    #sb.line_if(cfg.enable_ao,        "ao = mset.AmbientOcclusionBakerMap()")
    #sb.line_if(cfg.enable_curvature, "curv = mset.CurvatureBakerMap()")
    #sb.line_if(cfg.enable_thickness, "thick = mset.ThicknessBakerMap()")
    sb.section("""
    # Clear existing maps
    existing_maps = baker.getAllMaps()
    for m in existing_maps:
        m.enabled = False
    """)

def sec_material_sync(sb: ScriptBuilder, cfg: MarmoConfig):
    sb.section(f"""
    all_objects = mset.getAllObjects()
    materials = [obj for obj in all_objects if isinstance(obj, mset.Material)]
    default_material = next((mat for mat in materials if mat.name == "Default"), None)
    if default_material:
        default_material.setProperty("normalFlipY", {str(cfg.normal_flip_y)})
    """)

def sec_finalize(sb: ScriptBuilder, cfg: MarmoConfig):
    sb.line_if(cfg.quick_bake, "baker.bake()")
    sb.line_if(cfg.quick_bake, "baker.applyPreviewMaterial()")
    sb.line('print("Marmoset bake project created and models loaded.")')

def build_marmoset_script(cfg: MarmoConfig) -> str:
    sb = ScriptBuilder()
    sec_header(sb)
    sec_imports(sb, cfg)
    sec_core_params(sb, cfg)
    sec_maps(sb, cfg)
    #sec_material_sync(sb, cfg)
    sec_finalize(sb, cfg)
    return sb.build()