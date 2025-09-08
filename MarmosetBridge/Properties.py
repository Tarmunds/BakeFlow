import bpy, os, shutil
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from .MapProperties import *
from .MapProperties import _MB_SYNC_GUARD

# ===================== Update Functions =====================
def _sync_res_y(self, context):
    # self is the PropertyGroup instance
    self.ResolutionY = self.ResolutionX

def _UpdateFormat(self, context):
    Format = self.FileFormat
    Depth = int(self.PixelDepth)

    match Format:
        case 'JPG':
            if Depth in {16, 32}:
                self.PixelDepth = '8'
                try:
                    self.report({'WARNING'}, f"{Format} format only supports 8-bit depth. Pixel Depth has been set to 8-bit.")
                except AttributeError:
                    bpy.context.window_manager.popup_menu(
                        lambda s, c: s.layout.label(text="JPG: 8-bits only. Set to 8-bits.", icon='ERROR'),
                        title="Warning"
                    )
        case 'TGA':
            if Depth in {16, 32}:
                self.PixelDepth = '8'
                try:
                    self.report({'WARNING'}, f"{Format} format only supports 8-bit depth. Pixel Depth has been set to 8-bit.")
                except AttributeError:
                    bpy.context.window_manager.popup_menu(
                        lambda s, c: s.layout.label(text="TGA: 8-bits only. Set to 8-bits.", icon='ERROR'),
                        title="Warning"
                    )
        case 'PNG':
            if Depth == 32:
                self.PixelDepth = '16'
                try:
                    self.report({'WARNING'}, f"{Format} format only supports 8 and 16-bit depth. Pixel Depth has been set to 16-bit.")
                except AttributeError:
                    bpy.context.window_manager.popup_menu(
                        lambda s, c: s.layout.label(text="JPG: 8 and 16-bits only. Set to 16-bits.", icon='ERROR'),
                        title="Warning"
                    )
        case _:
            pass

def _UpdateDepth(self, context):
    Format = self.FileFormat
    Depth = int(self.PixelDepth)

    match Depth:
        case 32 if Format != 'PSD':
            self.FileFormat = 'PSD'
            try:
                self.report({'WARNING'}, "32-bit depth is only supported with PSD. File Format set to PSD.")
            except AttributeError:
                bpy.context.window_manager.popup_menu(
                    lambda s, c: s.layout.label(text="32-bit: PSD only. Set to PSD.", icon='ERROR'),
                    title="Warning"
                )

        case 16 if Format not in {'PSD', 'PNG'}:
            self.FileFormat = 'PNG'
            try:
                self.report({'WARNING'}, "16-bit depth is only supported with PNG or PSD. File Format set to PNG.")
            except AttributeError:
                bpy.context.window_manager.popup_menu(
                    lambda s, c: s.layout.label(text="16-bit: PNG or PSD. Set to PNG.", icon='ERROR'),
                    title="Warning"
                )

        case _:
            pass
    
def _UpdateNormalOrientation(self, context):
    if _MB_SYNC_GUARD["busy"]:
        return
    try:
        _MB_SYNC_GUARD["busy"] = True
        context.scene.BF_MT_NormalSettings.flip_y = (self.NormalOrientation == 'DIRECTX')
    finally:
        _MB_SYNC_GUARD["busy"] = False



# ===================== Addon Preferences & Properties =====================

ADDON_KEY = (__package__ or __name__).split(".")[0]
class BF_MT_Preferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_KEY

    marmoset_path: bpy.props.StringProperty(
        name="Marmoset Toolbag Path",
        default=r"C:\Program Files\Marmoset\Toolbag 5\Toolbag.exe",
        subtype='FILE_PATH'
    )
    use_tarmundsaddons_panel: bpy.props.BoolProperty(
        name="Use Tarmunds Addons Panel",
        description="Integrate Marmoset Toolbag Bridge into the Tarmunds Addons panel",
        default=False,
        update=lambda self, context: bpy.ops.wm.restart_addon()  # Restart the addon to apply changes
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Marmoset Toolbag Bridge Preferences")
        layout.prop(self, "marmoset_path")

class BF_MT_Properties(bpy.types.PropertyGroup):
    #-----------Exporter-----------#
    DirectBake: bpy.props.BoolProperty(
        name="Direct Bake",
        description="Toggle to enable or disable direct baking",
        default=False
    )
    SendProperties: bpy.props.BoolProperty(
        name="Send Properties",
        description="Toggle to send or not Baker properties",
        default=True
    )
    SendMapSettings: bpy.props.BoolProperty(
        name="Send Map Settings",
        description="Toggle to send or not Map properties",
        default=True
    )
    #-----------Baker-----------#
    BakingPath: bpy.props.StringProperty(
        name="Export Path",
        description="Path to export the selected objects",
        default="",
        subtype='DIR_PATH'
    )
    SamePathAsMesh: bpy.props.BoolProperty(
        name="Same Path as Mesh",
        description="Use the same path as the mesh for baking",
        default=False
    )
    Samples: bpy.props.EnumProperty(
        name="Samples",
        description="Number of samples for baking",
        items=[
            ('1', "1", "1 sample"),
            ('2', "2", "2 samples"),
            ('4', "4", "4 samples"),
            ('8', "8", "8 samples"),
            ('16', "16", "16 samples"),
            ('32', "32", "32 samples"),
            ('64', "64", "64 samples")
        ],
        default='16'
    )
    PixelDepth: bpy.props.EnumProperty(
        name="Pixel Depth",
        description="Bit depth for the baked textures",
        items=[
            ('8', "8-bit", "8-bit per channel"),
            ('16', "16-bit", "16-bit per channel"),
            ('32', "32-bit", "32-bit per channel")
        ],
        default='8',
        update= _UpdateDepth
    )
    TileMode: bpy.props.EnumProperty(
        name="Tile Mode",
        description="Tile mode for baking",
        items=[
            ('SINGLE', "Single Texture Set", "Bake to a single texture set"),
            ('MULTI', "Multiple Texture Sets", "Bake to multiple texture sets")
        ],
        default='SINGLE'
    )
    NonSquareTextures: bpy.props.BoolProperty(
        name="Non-Square Textures",
        description="Allow non-square textures",
        default=False
    )
    ResolutionX: bpy.props.EnumProperty(
        name="Resolution X",
        description="Width of the baked texture",
        items=[
            ('256', "256", "256 pixels"),
            ('512', "512", "512 pixels"),
            ('1024', "1024", "1024 pixels"),
            ('2048', "2048", "2048 pixels"),
            ('4096', "4096", "4096 pixels"),
            ('8192', "8192", "8192 pixels")
        ],
        default='2048',
        update= _sync_res_y
    )
    ResolutionY: bpy.props.EnumProperty(
        name="Resolution Y",
        description="Height of the baked texture",
        items=[
            ('256', "256", "256 pixels"),
            ('512', "512", "512 pixels"),
            ('1024', "1024", "1024 pixels"),
            ('2048', "2048", "2048 pixels"),
            ('4096', "4096", "4096 pixels"),
            ('8192', "8192", "8192 pixels")
        ],
        default='2048'
    )
    FileFormat: bpy.props.EnumProperty(
        name="File Format",
        description="File format for the baked textures",
        items=[
            ('PNG', "PNG", "Portable Network Graphics"),
            ('JPG', "JPG", "Joint Photographic Experts Group"),
            ('TGA', "TGA", "Targa"),
            ('PSD', "PSD", "Photoshop Document"),
        ],
        default='PNG',
        update= _UpdateFormat
    )
    #-----------Texture-----------#
    NormalOrientation: bpy.props.EnumProperty(
        name="Normal Map Orientation",
        description="Orientation of the normal map",
        items=[
            ('OPENGL', "OpenGL", "OpenGL normal map orientation"),
            ('DIRECTX', "DirectX", "DirectX normal map orientation")
        ],
        default='OPENGL',
        update= _UpdateNormalOrientation
    )
    #-----------BakeGroup-----------#
    OverideMaxOffset: bpy.props.BoolProperty(
        name="Override Max Offset",
        description="Override the maximum offset for baking",
        default=False
    )
    MaxOffset: bpy.props.FloatProperty(
        name="Max Offset",
        description="Maximum offset for baking",
        default=4.0,
        min=0.0,
        max=64.0,
        step=0.1,
        precision=3
    )
    

# ===================== Ui List =====================

Map_Types = [
    ('NORMAL', 'Normal', 'Normal Map'),
    ('NORMAL_OBJ', 'Normal Obj', 'World SPace Normal Map'),
    ('HEIGHT', 'Height', 'Height Map'),
    ('POSITION', 'Position', 'Position Map'),
    ('CURVATURE', 'Curvature', 'Curvature Map'),
    ('THICKNESS', 'Thickness', 'Thickness Map'),
    ('AMBIANT_OCCLUSION', 'AO', 'Ambient Occlusion Map'),
    ('AMBIANT_OCCLUSION_2', 'AO 2', 'Ambient Occlusion Map'),
    ('OBJECT_ID', 'Object ID', 'Object ID Map'),
    ('MATERIAL_ID', 'Material ID', 'Material ID Map'),
]

class BF_MT_MapItem(bpy.types.PropertyGroup):
    map_enable: bpy.props.BoolProperty(
        name="Enable",
        description="Enable or disable this map for baking",
        default=True
    )
    map_type: bpy.props.EnumProperty(
        name="Map Type",
        description="Type of map to bake",
        items=Map_Types,
        default='NORMAL'
    )
            

class BF_MT_MapContainer(bpy.types.PropertyGroup):
    maps: bpy.props.CollectionProperty(type=BF_MT_MapItem)
    active_map_index: bpy.props.IntProperty(name="Active Index", default=0)
    
class BF_MT_MapList(bpy.types.UIList):
    """UIList to display and manage baking maps"""
    bl_idname = "BF_MT_map_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        map_item = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(map_item, "map_enable", text="")
            row.label(text="")
            row.prop(map_item, "map_type", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(map_item, "map_type", text="")



# ===================== Config =====================
@dataclass
class MarmoConfig:
    # Required
    marmoset_path: str
    export_path: str
    width: int
    height: int
    pixel_bits: int
    samples: int

    # Optional scene inputs
    low_fbx: Optional[str] = None
    high_fbx: Optional[str] = None
    cage_fbx: Optional[str] = None

    # Common toggles
    edge_padding: str = "Moderate"
    soften: int = 0
    use_hidden_meshes: bool = True
    ignore_transforms: bool = False
    smooth_cage: bool = True
    ignore_backfaces: bool = True
    tile_mode: int = 0
    normal_flip_y: bool = False
    quick_bake: bool = False

    # Maps toggles
    enable_ao: bool = True
    enable_curvature: bool = False
    enable_thickness: bool = False

    # Extensible bag for future one-offs
    extra: Dict[str, object] = field(default_factory=dict)


# ===================== Registration =====================


_classes = (
    BF_MT_Properties,
    BF_MT_Preferences,
    BF_MT_MapItem,
    BF_MT_MapContainer,
    BF_MT_MapList,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.BF_MT_Properties = bpy.props.PointerProperty(type=BF_MT_Properties)
    bpy.types.Scene.BF_MT_MapContainer = bpy.props.PointerProperty(type=BF_MT_MapContainer)



def unregister():
    del bpy.types.Scene.BF_MT_MapContainer
    del bpy.types.Scene.BF_MT_Properties
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)