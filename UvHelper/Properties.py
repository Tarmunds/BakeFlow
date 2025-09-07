import bpy

class BF_UH_Properties(bpy.types.PropertyGroup):
    angle_threshold: bpy.props.FloatProperty(
        name="Angle Threshold",
        description="Minimum angle (in degrees) to select edges",
        default=30,
        min=0,
        max=180,
    )
    ngon_detect_range: bpy.props.EnumProperty(
        name="Ngon Detection Range",
        description="Select ngons within this range of meshes",
        items=[
            ('SELECTED', "Selected", "Detect Ngon on the selected objects"),
            ('VISIBLE', "Visible", "Detect Ngon on all visible objects"),
            ('ALL', "All", "Detect Ngon on all object, including hidden. Warning: can be slow"),
        ],
        default='SELECTED',
    )
    
_classes = (
    BF_UH_Properties,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.BF_UH_Properties = bpy.props.PointerProperty(type=BF_UH_Properties)

def unregister():
    del bpy.types.Scene.BF_UH_Properties
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)