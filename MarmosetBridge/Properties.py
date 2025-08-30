import bpy
from .Functions import _sync_res_y

class MB_MT_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Marmoset Toolbag Bridge Preferences")
        marmoset_path: bpy.props.StringProperty(
            name="Marmoset Toolbag Path",
            default=r"C:\\Program Files\\Marmoset\\Toolbag 5\\Toolbag.exe",
            subtype='FILE_PATH'
        )
        

class MB_MT_Properties(bpy.types.PropertyGroup):
    #-----------Exporter-----------#
    DirectBake: bpy.props.BoolProperty(
        name="Direct Bake",
        description="Toggle to enable or disable direct baking",
        default=False
    )
    SendProperties: bpy.props.BoolProperty(
        name="Send Properties",
        description="Toggle to show or hide send properties",
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
        default='8'
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
        default='PNG'
    )
    #-----------Texture-----------#

_classes = (
    MB_MT_Properties,
    MB_MT_Preferences,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.MB_MT_Properties = bpy.props.PointerProperty(type=MB_MT_Properties)

def unregister():
    del bpy.types.Scene.MB_MT_Properties
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)