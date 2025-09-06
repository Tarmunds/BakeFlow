import bpy
from .Functions import GoToLine

class MB_UH_Panel(bpy.types.Panel):
    bl_label = "MB UV Helper"
    bl_idname = "VIEW3D_PT_MB_UH_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tarmunds Addons'
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properities = context.scene.MB_UH_Properties

        row = GoToLine(layout, align=False)
        row.operator("object.mb_uh_edges_by_normal", text="Select Edges by Angle")
        row.prop(properities, "angle_threshold", text="Angle")
        row = GoToLine(layout, align=False)
        row.operator("object.mb_uh_contour_select", text="Select Contour Edges")
        row = GoToLine(layout)
        row.operator("object.mb_uh_seam_sharp_edges", text="Tag Seam and Sharp").tag = True
        row.operator("object.mb_uh_seam_sharp_edges", text="Clear Seam and Sharp").tag = False
        row = GoToLine(layout, align=False)
        row.operator("object.mb_uh_clear_split_normals", text="Clear Split Normals")
        row.operator("object.mb_uh_add_modifier", text="Add Modifiers")
        row = GoToLine(layout, align=False)
        row.operator("object.mb_uh_ngon", text="Detect Ngons")
        row = GoToLine(layout)
        row.enabled = (context.mode == 'OBJECT')
        row.label(text="Range:")
        row.prop(properities, "ngon_detect_range", expand=True)
        
        
    def draw_header_preset(self, context):
        layout = self.layout
        layout.label(icon='UV')
        layout.label(text="")
        
_classes = (
    MB_UH_Panel,
)
def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)