import bpy, textwrap, subprocess, tempfile, os
from pathlib import Path
from .Properties import MarmoConfig, Map_Types
from .MapProperties import MAP_TYPE_TO_SETTINGS
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
    properties = bpy.context.scene.MB_MT_Properties #get the properties from the context
    map_container = bpy.context.scene.MB_MT_MapContainer
    enable_map_types = [item.map_type for item in map_container.maps if item.map_enable]
    
    sb.section("""
    # Clear existing maps
    existing_maps = baker.getAllMaps()
    for m in existing_maps:
        m.enabled = False
    """)

    if 'NORMAL' in enable_map_types:
        sb.section(f"""
        for map in baker.getAllMaps():
            if isinstance(map, mset.NormalBakerMap):  # Check class type instead of `type` attribute due to flip y issue
                normal_map = map
                break
        #normal_map = baker.getMap("Normals")
        normal_map.enabled = True
        normal_map.suffix = "{str(bpy.context.scene.MB_MT_NormalSettings.suffix)[1:]}"
                
        normal_map.flipX = {bpy.context.scene.MB_MT_NormalSettings.flip_x}
        normal_map.flipY = True #{bpy.context.scene.MB_MT_NormalSettings.flip_y}
        normal_map.flipZ = {bpy.context.scene.MB_MT_NormalSettings.flip_z}
        
        print(dir(normal_map))
        """) #bug of flipping normal due to error in the api, Request made on marmoset server

    
    if 'NORMAL_OBJ' in enable_map_types:
        sb.section(f"""
        normal_obj_map = baker.getMap("Normals (Object)")
        normal_obj_map.enabled = True
        normal_obj_map.suffix = "{str(bpy.context.scene.MB_MT_NormalOBJSettings.suffix)[1:]}"
        
        normal_obj_map.flipX = {bpy.context.scene.MB_MT_NormalOBJSettings.flip_x}
        normal_obj_map.flipY = {bpy.context.scene.MB_MT_NormalOBJSettings.flip_y}
        normal_obj_map.flipZ = {bpy.context.scene.MB_MT_NormalOBJSettings.flip_z}
        """) #bug of flipping normal due to error in the api, Request made on marmoset server
    
    if 'HEIGHT' in enable_map_types:
        sb.section(f"""
        height_map = baker.getMap("Height")
        height_map.enabled = True
        height_map.suffix = "{str(bpy.context.scene.MB_MT_HeightSettings.suffix)[1:]}"
        height_map.innerDistance = {bpy.context.scene.MB_MT_HeightSettings.inner_distance}
        height_map.outerDistance = {bpy.context.scene.MB_MT_HeightSettings.outer_distance}
        """)
    
    if 'POSITION' in enable_map_types:
        sb.section(f"""
        position_map = baker.getMap("Position")
        position_map.enabled = True
        position_map.suffix = "{str(bpy.context.scene.MB_MT_PositionSettings.suffix)[1:]}"
        normalization_properities = "{str(bpy.context.scene.MB_MT_PositionSettings.normalization)}"
        match normalization_properities:
            case "BOUNDINGBOX":
                position_map.normalization = "Bounding Box"
            case "BOUNDINGSPHERE":
                position_map.normalization = "Bounding Sphere"
            case "DISABLED":
                position_map.normalization = "Disabled"
        """)
            

    
    if 'CURVATURE' in enable_map_types:
        sb.section(f"""
        curvature_map = baker.getMap("Curvature")
        curvature_map.enabled = True
        curvature_map.suffix = "{str(bpy.context.scene.MB_MT_CurveSettings.suffix)[1:]}"
        curvature_map.strength = {bpy.context.scene.MB_MT_CurveSettings.strength}
        """)
    
    if 'THICKNESS' in enable_map_types:
        sb.section(f"""
        thickness_map = baker.getMap("Thickness")
        thickness_map.enabled = True
        thickness_map.suffix = "{str(bpy.context.scene.MB_MT_ThicknessSettings.suffix)[1:]}"
        thickness_map.rayCount = {bpy.context.scene.MB_MT_ThicknessSettings.ray_count}
        """)
    
    if 'AMBIANT_OCCLUSION' in enable_map_types:
        sb.section(f"""
        ao_map = baker.getMap("Ambient Occlusion")
        ao_map.enabled = True
        ao_map.suffix = "{str(bpy.context.scene.MB_MT_AOSettings.suffix)[1:]}"
        ao_map.rayCount = {bpy.context.scene.MB_MT_AOSettings.ray_count}
        ao_map.searchDistance = {bpy.context.scene.MB_MT_AOSettings.search_distance}
        ao_map.cosineWeight = {bpy.context.scene.MB_MT_AOSettings.cavity_weight}
        ao_map.floorOcclusion = {bpy.context.scene.MB_MT_AOSettings.floor_occlusion}
        ao_map.floor = {bpy.context.scene.MB_MT_AOSettings.floor_strength}
        ao_map.twoSided = {bpy.context.scene.MB_MT_AOSettings.two_sided}
        ao_map.ignoreGroups = {bpy.context.scene.MB_MT_AOSettings.ignore_groups}
        
        """)
    
    if 'AMBIANT_OCCLUSION_2' in enable_map_types:
        sb.section(f"""
        ao2_map = baker.getMap("Ambient Occlusion (2)")
        ao2_map.enabled = True
        ao2_map.suffix = "{str(bpy.context.scene.MB_MT_AO2Settings.suffix)[1:]}"
        ao2_map.rayCount = {bpy.context.scene.MB_MT_AO2Settings.ray_count}
        ao2_map.searchDistance = {bpy.context.scene.MB_MT_AO2Settings.search_distance}
        ao2_map.cosineWeight = {bpy.context.scene.MB_MT_AO2Settings.cavity_weight}
        ao2_map.floorOcclusion = {bpy.context.scene.MB_MT_AO2Settings.floor_occlusion}
        ao2_map.floor = {bpy.context.scene.MB_MT_AO2Settings.floor_strength}
        ao2_map.twoSided = {bpy.context.scene.MB_MT_AO2Settings.two_sided}
        ao2_map.ignoreGroups = {bpy.context.scene.MB_MT_AO2Settings.ignore_groups}
        """)
    
    if 'OBJECT_ID' in enable_map_types:
        sb.section(f"""
        object_id_map = baker.getMap("Object ID")
        object_id_map.enabled = True
        """)
        
    if 'MATERIAL_ID' in enable_map_types:
        sb.section(f"""
        material_id_map = baker.getMap("Material ID")
        material_id_map.enabled = True
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