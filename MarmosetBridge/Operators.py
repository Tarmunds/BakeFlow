import bpy, os, subprocess, tempfile, textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional
from bl_operators.presets import AddPresetBase
from .Functions import ensure, build_marmoset_script, get_prefs, get_path_abs, next_unused_enum
from .Properties import MarmoConfig

class BF_MT_HelpURL(bpy.types.Operator):
    bl_idname = "object.bf_mt_openurl"
    bl_label = "Open Marmoset Naming Conventions"
    bl_description = "Open the Marmoset Toolbag naming conventions documentation"
    url: bpy.props.StringProperty()
    def execute(self, context):
        bpy.ops.wm.url_open(url=self.url)
        return {'FINISHED'}

# ===================== Ui List Operators =====================

class BF_MT_Map_add(bpy.types.Operator):
    bl_idname = "ui_list.bf_mt_map_add"
    bl_label = "Add Item"
    bl_description = "Add a new map to bake"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ui_container = context.scene.BF_MT_MapContainer
        new_item = ui_container.maps.add()
        new_item.map_enable = True                              
        new_item.map_type = next_unused_enum(ui_container)      
        ui_container.active_map_index = len(ui_container.maps) - 1
        return {'FINISHED'}

class BF_MT_Map_remove(bpy.types.Operator):
    bl_idname = "ui_list.bf_mt_map_remove"
    bl_label = "Remove Item"
    bl_description = "Remove the selected map"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ui_container = context.scene.BF_MT_MapContainer
        index = context.scene.BF_MT_MapContainer.active_map_index
        if ui_container.maps:
            ui_container.maps.remove(index)
            if ui_container.active_map_index >= len(ui_container.maps):
                ui_container.active_map_index = min(max(0, index - 1), len(ui_container.maps) - 1)
        return {'FINISHED'}

class BF_MT_Map_move(bpy.types.Operator):
    bl_idname = "ui_list.bf_mt_map_move"
    bl_label = "Move Item"
    bl_description = "Move the selected map up or down"
    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""), ('DOWN', 'Down', "")))
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ui_container = context.scene.BF_MT_MapContainer
        index = ui_container.active_map_index
        if self.direction == 'UP' and index > 0:
            ui_container.maps.move(index, index - 1)
            ui_container.active_map_index -= 1
        elif self.direction == 'DOWN' and index < len(ui_container.maps) - 1:
            ui_container.maps.move(index, index + 1)
            ui_container.active_map_index += 1
        return {'FINISHED'}

# ===================== Presets =====================

class PresetRegistry:
    _reg: Dict[str, Callable[[MarmoConfig], None]] = {}

    @classmethod
    def register(cls, name: str):
        def deco(fn):
            cls._reg[name] = fn
            return fn
        return deco

    @classmethod
    def apply(cls, name: Optional[str], cfg: MarmoConfig):
        if name and name in cls._reg:
            cls._reg[name](cfg)

@PresetRegistry.register("asset_default")
def _asset_default(cfg: MarmoConfig):
    cfg.enable_ao = True
    cfg.enable_curvature = True
    cfg.enable_thickness = False
    cfg.normal_flip_y = False
    cfg.extra["dilate_pixels"] = 8

@PresetRegistry.register("tileable")
def _tileable(cfg: MarmoConfig):
    cfg.tile_mode = 1
    cfg.ignore_backfaces = True
    cfg.enable_thickness = False
    cfg.extra["dilate_pixels"] = 16

# ===================== Export and Launch =====================

class ExportService:
    @staticmethod
    def selection_probe(context):
        objs = context.selected_objects
        high_sel = any("_high" in o.name for o in objs)
        low_sel  = any("_low" in o.name for o in objs)
        return high_sel, low_sel

    @staticmethod
    def export_if_needed(context):
        high_sel, low_sel = ExportService.selection_probe(context)
        if high_sel:
            bpy.ops.object.export_selected_operator(suffix_to_export="_high")
        if low_sel:
            bpy.ops.object.export_selected_operator(suffix_to_export="_low")

class Launcher:
    @staticmethod
    def write_temp_script(code: str) -> str:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py")
        with open(tmp.name, "w", encoding="utf-8") as f:
            f.write(code)
        return tmp.name

    @staticmethod
    def launch(marmoset_path: str, script_path: str):
        subprocess.Popen([marmoset_path, "-py", script_path], shell=True)

# ===================== Blender Operator =====================

class BF_MT_ExportToMarmoset(bpy.types.Operator):
    bl_idname = "object.bf_mt_export_to_marmoset"
    bl_label = "Export and Launch Marmoset"
    bl_description = "Export selected high and/or low meshes and launch Marmoset Toolbag with baking setup"

    # Optional: let user pick a preset by name via Operator property
    preset_name: bpy.props.StringProperty(
        name="Preset", description="Preset name to apply", default="asset_default"
    )

    def _make_config(self, context) -> MarmoConfig:
        scene = context.scene
        #addon_mod = bpy.context.preferences.addons.get(__package__)

        marmoset_path = bpy.path.abspath(get_prefs().marmoset_path)
        ensure(marmoset_path and os.path.exists(marmoset_path),
               f"Marmoset Toolbag not found at: {marmoset_path}. Set the correct path in Preferences.")

        ensure(bool(context.scene.BF_BS_Properties.Name.strip()), "Appellation cannot be empty. Please provide a name.")

        #ref to Properties
        properties = scene.BF_MT_Properties
        properties_bs = scene.BF_BS_Properties

        # Pick the mesh path base
        meshes_folder = properties_bs.ExportPath.strip() if properties_bs.ExportPath.strip() else os.path.dirname(bpy.data.filepath)
        high_fbx = os.path.abspath(os.path.join(meshes_folder, f"{properties_bs.Name}_high.fbx"))
        low_fbx  = os.path.abspath(os.path.join(meshes_folder, f"{properties_bs.Name}_low.fbx"))

        # ensure at least one of high or low is selected
        high_sel, low_sel = ExportService.selection_probe(context)
        ensure(high_sel or low_sel, "No selected objects with '_high' or '_low' in their names.")

        # Choose bake output path
        if properties.SamePathAsMesh:
            if properties_bs.ExportPath:
                base_path = properties_bs.ExportPath.strip()
            else :
                base_path = os.path.dirname(bpy.data.filepath)
        else:
            ensure(bool(properties.BakingPath.strip()), "No custom path set for the Baking.")
            base_path = properties.BakingPath.strip()

        
        export_path = os.path.join(base_path, f"{properties_bs.Name.strip()}.{properties.FileFormat.lower()}").replace("/", "\\")

        cfg = MarmoConfig(
            marmoset_path=marmoset_path,
            export_path=export_path,
            width=properties.ResolutionX,
            height=properties.ResolutionY,
            pixel_bits=properties.PixelDepth,
            samples=properties.Samples,
            low_fbx=low_fbx if low_sel else None,
            high_fbx=high_fbx if high_sel else None,
            normal_flip_y=False,
            quick_bake=properties.DirectBake,
        )

        # Apply a named preset if available
        PresetRegistry.apply(self.preset_name, cfg)
        return cfg

    def execute(self, context):
        try:
            cfg = self._make_config(context)
        except RuntimeError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        # Export meshes if needed
        ExportService.export_if_needed(context)

        # Build script and launch Toolbag
        code = build_marmoset_script(cfg)
        script_path = Launcher.write_temp_script(code)
        Launcher.launch(cfg.marmoset_path, script_path)
        self.report({'INFO'}, "Marmoset Toolbag launched and setup.")
        return {'FINISHED'}


# ===================== Preset Operator =====================

class BF_MT_MapProperties_AddPreset(AddPresetBase, bpy.types.Operator):
    bl_idname = 'mbmt.mapproperties_addpreset'
    bl_label = 'Add preset'
    bl_description = "Add a new preset"
    preset_menu = 'BF_MT_MapPanel_Presets'

    preset_defines = [ 'mapcontainer = bpy.context.scene.BF_MT_MapContainer',
                       'normalsettings = bpy.context.scene.BF_MT_NormalSettings',
                       'normalobjsettings = bpy.context.scene.BF_MT_NormalOBJSettings',
                       'heightsettings = bpy.context.scene.BF_MT_HeightSettings',
                       'positionsettings = bpy.context.scene.BF_MT_PositionSettings',
                       'curvesettings = bpy.context.scene.BF_MT_CurveSettings',
                       'thicknesssettings = bpy.context.scene.BF_MT_ThicknessSettings',
                       'aosettings = bpy.context.scene.BF_MT_AOSettings',
                       'ao2settings = bpy.context.scene.BF_MT_AO2Settings',
                       ]
    preset_values = [
        'mapcontainer.maps',
        'mapcontainer.active_map_index',
        'normalsettings.suffix',
        'normalsettings.flip_x',
        'normalsettings.flip_y',
        'normalsettings.flip_z',
        'normalobjsettings.suffix',
        'normalobjsettings.flip_x',
        'normalobjsettings.flip_y',
        'normalobjsettings.flip_z',
        'heightsettings.suffix',
        'heightsettings.inner_distance',
        'heightsettings.outer_distance',
        'positionsettings.suffix',
        'positionsettings.normalization',
        'curvesettings.suffix',
        'curvesettings.strength',
        'thicknesssettings.suffix',
        'thicknesssettings.ray_count',
        'thicknesssettings.search_distance',
        'thicknesssettings.scale',
        'thicknesssettings.ignore_groups',
        'thicknesssettings.gamma',
        'aosettings.suffix',
        'aosettings.ray_count',
        'aosettings.search_distance',
        'aosettings.cavity_weight',
        'aosettings.floor_occlusion',
        'aosettings.floor_strength',
        'aosettings.ignore_groups',
        'aosettings.two_sided',
        'ao2settings.suffix',
        'ao2settings.ray_count',
        'ao2settings.search_distance',
        'ao2settings.cavity_weight',
        'ao2settings.floor_occlusion',
        'ao2settings.floor_strength',
        'ao2settings.ignore_groups',
        'ao2settings.two_sided',
    ]

    preset_subdir = 'MapPresets'
    
_classes = (
    BF_MT_Map_add,
    BF_MT_Map_remove,
    BF_MT_Map_move,
    BF_MT_ExportToMarmoset,
    BF_MT_MapProperties_AddPreset,
    BF_MT_HelpURL,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
