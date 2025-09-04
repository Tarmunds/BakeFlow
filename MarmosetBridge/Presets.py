import bpy
from bpy.types import Menu, Panel, Operator
from bpy.props import BoolProperty
from bl_operators.presets import AddPresetBase, PresetMenu, PresetPanel


PROP_ACCESS_LIST = [
    "bpy.context.scene.MB_MT_MapContainer",
    "bpy.context.scene.MB_MT_NormalSettings",
    "bpy.context.scene.MB_MT_NormalOBJSettings",
    "bpy.context.scene.MB_MT_HeightSettings",
    "bpy.context.scene.MB_MT_PositionSettings",
    "bpy.context.scene.MB_MT_CurveSettings",
    "bpy.context.scene.MB_MT_ThicknessSettings",
    "bpy.context.scene.MB_MT_AOSettings",
    "bpy.context.scene.MB_MT_AO2Settings",
]

PRESET_SUBDIR = "MapPresets"

def _resolve_prop_access():
    """Returns the live PropertyGroup instance from PROP_ACCESS."""
    # Safe eval limited to bpy + context only
    _globals = {"bpy": bpy}
    return eval(PROP_ACCESS, _globals, {})

def _collect_preset_value_paths():
    names = []
    _globals = {"bpy": bpy}
    for access in PROP_ACCESS_LIST:
        pg = eval(access, _globals, {})
        rna = pg.bl_rna
        for p in rna.properties:
            if p.is_readonly or p.identifier in {"rna_type"}:
                continue
            if p.type in {'POINTER', 'COLLECTION'}:
                continue
            names.append(f"{access}.{p.identifier}")
    return names


# ------------------------------
# Menu shown in the panel header
# ------------------------------
class MB_MT_MainPanel_Presets(PresetMenu, Menu):
    bl_label = "DATA Baker Presets"
    preset_subdir = PRESET_SUBDIR
    preset_operator = "script.execute_preset"   # This loads the selected preset
    draw = Menu.draw_preset


# ------------------------------
# Add / Remove preset operator
# ------------------------------
class MB_MT_AddPreset(AddPresetBase, Operator):
    """Add or remove a preset capturing all fields from your Map Properties"""
    bl_idname = "gametools.databaker_addpreset"
    bl_label = "Add DataBaker Preset"
    preset_menu = "DATABAKER_MT_MainPanel_Presets"

    # Where preset files live
    preset_subdir = PRESET_SUBDIR

    # We will *fill these at runtime* in execute()
    preset_defines = []
    preset_values = []

    # When True, pressing the operator deletes the active preset
    remove_active: BoolProperty(default=False)

    def execute(self, context):
        # Define the 'props' symbol in the preset file so assignments are readable if needed.
        # (We actually serialize via preset_values below.)
        self.preset_defines = [f"props = {PROP_ACCESS}"]

        # Dynamically list every storable field on the property group
        self.preset_values = _collect_preset_value_paths()

        # AddPresetBase handles add/remove depending on remove_active
        return super().execute(context)


# ------------------------------
# Optional Preset Panel (header helper)
# ------------------------------
class MB_MT_DataBaker_Preset(PresetPanel, Panel):
    """Gives you draw_panel_header() to show the menu + + / - buttons."""
    bl_label = "DATA Baker Presets"
    bl_space_type = 'VIEW_3D'         # Match your main panel
    bl_region_type = 'UI'             # Match your main panel
    bl_category = "DataBaker"         # Match your tab
    # These three connect the UI to our menu/operator
    preset_subdir = PRESET_SUBDIR
    preset_operator = "script.execute_preset"
    preset_add_operator = "gametools.databaker_addpreset"


# ------------------------------
# Registration
# ------------------------------
classes = (
    MB_MT_MainPanel_Presets,
    MB_MT_AddPreset,
    MB_MT_DataBaker_Preset,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
