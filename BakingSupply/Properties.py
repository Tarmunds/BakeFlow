import bpy
class BF_BS_Properties(bpy.types.PropertyGroup):
    ExportPath: bpy.props.StringProperty(
        name="Export Path",
        description="Path to export the selected objects",
        default="",
        subtype='DIR_PATH'
    )
    Name: bpy.props.StringProperty(
        name="Name of the files",
        description="Base name for the exported files",
        default=""
    )
    ShowPathOptions: bpy.props.BoolProperty(
        name="Show Path Options",
        description="Toggle to show or hide path options",
        default=False
    )
    RenameName: bpy.props.StringProperty(
        name="Rename Name",
        description="New base name for renaming objects",
        default=""
    )
    exported_in_pose: bpy.props.BoolProperty(
        name="Exported In Pose",
        description="try to export in pose mode, warning, this will temporarily duplicate your mesh for the export so it's way more heavy on memory usage, especially with high poly meshes",
        default=False
    )
    
_classes = (BF_BS_Properties,)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.BF_BS_Properties = bpy.props.PointerProperty(type=BF_BS_Properties)

def unregister():
    del bpy.types.Scene.BF_BS_Properties
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)