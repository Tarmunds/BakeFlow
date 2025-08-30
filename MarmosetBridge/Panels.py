import bpy
from .Functions import GoToLine
class MB_MT_Panel(bpy.types.Panel):
    """Panel for the low and high mesh operations"""
    bl_label = "MB Marmoset Toolbag Bridge"
    bl_idname = "VIEW3D_PT_MB_MT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tarmunds Addons'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properities = context.scene.MB_MT_Properties
        
        row = layout.row()
        row.scale_y = 2
        row.label(text="Marmoset Toolbag Bridge", icon='MONKEY')
    def draw_header_preset(self, context):
        layout = self.layout
        layout.label(icon='MONKEY')
        layout.label(text="")
    
_classes = (
    MB_MT_Panel,
)
def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)