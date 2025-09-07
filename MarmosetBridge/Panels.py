import bpy, os
from .Properties import MB_MT_MapItem
from bl_ui.utils import PresetPanel
from .Functions import GoToLine
from .Operators import MB_MT_MapProperties_AddPreset
from .MapProperties import MAP_TYPE_TO_SETTINGS, MB_MT_NoSettings
from pathlib import Path
#from .Presets import MB_MT_DataBaker_PresetHeader

ADDON_ROOT = Path(__file__).resolve().parent.parent
# packaged presets live at: <addon_root>/presets/MapPresets
PKG_DIR = ADDON_ROOT / "presets" / "MapPresets"

class MB_MT_MapPanel_Presets(bpy.types.Menu):
    bl_label = 'Map Presets'
    preset_subdir = 'MapPresets'
    preset_operator = 'script.execute_preset'
    draw = bpy.types.Menu.draw_preset

class MB_MT_Panel(bpy.types.Panel):
    """Panel for the low and high mesh operations"""
    bl_label = "Marmoset Toolbag Bridge"
    bl_idname = "VIEW3D_PT_BF_3_MT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BakeFlow'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properties = context.scene.MB_MT_Properties
        
        row = layout.row()
        row.scale_y = 2
        row.operator("object.mb_mt_export_to_marmoset", text="Export & Launch Marmoset", icon='MONKEY')
        layout.separator()

        row = GoToLine(layout, align=False)
        row.prop(properties, "DirectBake", text="Quick Bake", toggle=True)
        row.prop(properties, "SendProperties", text="Send Properties", toggle=True)
        row = GoToLine(layout)
        row.prop(properties, "SamePathAsMesh")
        sub = row.row()
        sub.enabled = not properties.SamePathAsMesh
        sub.prop(properties, "BakingPath")
        row = GoToLine(layout)
        row.prop(properties, "Samples")
        row = GoToLine(layout)
        row.prop(properties, "PixelDepth")
        row = GoToLine(layout)
        row.prop(properties, "FileFormat")
        row = GoToLine(layout)
        row.prop(properties, "TileMode")
        row = GoToLine(layout)
        row.prop(properties, "NormalOrientation", expand=True)
        row = GoToLine(layout)
        row.prop(properties, "NonSquareTextures",text="Non Square Texture" , toggle=True)
        row.prop(properties, "ResolutionX", text="   X")
        sub = row.row()
        sub.enabled = properties.NonSquareTextures
        sub.prop(properties, "ResolutionY", text="   Y")


        
    def draw_header_preset(self, context):
        layout = self.layout
        layout.label(icon='MONKEY')
        layout.label(text="")

class  MB_MT_MapsPanel(bpy.types.Panel):
    """Panel for the low and high mesh operations"""
    bl_label = "Marmoset Toolbag Bridge - Maps"
    bl_idname = "VIEW3D_PT_BF_4_MT_MapsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BakeFlow'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        map_container = context.scene.MB_MT_MapContainer
        properties = context.scene.MB_MT_Properties
        send_map = properties.SendMapSettings
        
        row = GoToLine(layout, align=False)
        row.label(text="Texture Maps to Bake:")
        row.prop(properties, "SendMapSettings", toggle=True)
        
        row = GoToLine(layout, align=False)
        row.enabled = send_map
        row.menu("MB_MT_MapPanel_Presets", text="Map Presets", icon="PRESET")

        row.operator(MB_MT_MapProperties_AddPreset.bl_idname, text="", icon='ADD')
        row.operator(MB_MT_MapProperties_AddPreset.bl_idname, text="", icon='REMOVE').remove_active = True
        


        # List UI
        row = layout.row()
        row.enabled = send_map
        row.template_list("MB_MT_map_list", "", map_container, "maps", map_container, "active_map_index", rows=5)
        # Operators
        col = row.column(align=True)
        col.operator("ui_list.mb_mt_map_add", icon='ADD', text="")
        col.operator("ui_list.mb_mt_map_remove", icon='REMOVE', text="")
        col.separator()
        col.operator("ui_list.mb_mt_map_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("ui_list.mb_mt_map_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        # --- Active map settings block under the list ---
        if map_container.maps and 0 <= map_container.active_map_index < len(map_container.maps) and send_map:
            item = map_container.maps[map_container.active_map_index]

            # Resolve settings class from map_type
            settings_cls = MAP_TYPE_TO_SETTINGS.get(item.map_type, MB_MT_NoSettings)

            # Scene stores a PointerProperty per settings class with the same name as the class
            settings_attr_name = settings_cls.__name__
            settings_ptr = getattr(scene, settings_attr_name, None)

            layout.separator()
            if settings_ptr is not None and hasattr(settings_ptr, "draw"):
                settings_ptr.draw(layout)
            else:
                layout.label(text="No settings available for this map.")
        elif send_map:
            layout.label(text="No map selected.")
        else :
            layout.label(text="Send Map settings is disabled.")
            
            
    def draw_header_preset(self, context):
        layout = self.layout
        layout.label(icon='TEXTURE')
        layout.label(text="")

def _sync_presets():
    import os, shutil, bpy
    addon_presets = ADDON_ROOT / "presets" / "MapPresets"
    if not addon_presets.is_dir():
        return
    user_presets = bpy.utils.user_resource("SCRIPTS", path="presets/MapPresets", create=True)
    os.makedirs(user_presets, exist_ok=True)
    for fn in os.listdir(addon_presets):
        if fn.lower().endswith(".py"):
            src = str(addon_presets / fn)
            dst = os.path.join(user_presets, fn)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)


_classes = (
    MB_MT_MapPanel_Presets,
    MB_MT_Panel,
    MB_MT_MapsPanel,
)
def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    _sync_presets()

def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)