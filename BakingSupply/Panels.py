import bpy
from .Functions import GoToLine

class MB_BS_Panel(bpy.types.Panel):
    """Panel for the low and high mesh operations"""
    bl_label = "Baking Supply"
    bl_idname = "VIEW3D_PT_BF_2_BS_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BakeFlow'
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properities = context.scene.MB_BS_Properties

        #Hide/Show Buttons
        row = GoToLine(layout)
        row.operator("object.mb_bs_hide_high_meshes", text="Hide High")
        row.operator("object.mb_bs_hide_low_meshes", text="Hide Low")
        row = GoToLine(layout)
        row.operator("object.mb_bs_show_high_meshes", text="Show High")
        row.operator("object.mb_bs_show_low_meshes", text="Show Low")
        #Suffix Buttons
        layout.separator()
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator("object.mb_bs_add_suffix", text="Add _high").rename_type = "high"
        row.operator("object.mb_bs_add_suffix", text="Add _low").rename_type = "low"
        col.operator("object.mb_bs_switch_suffix", text="High <> Low")
        col.operator("object.mb_bs_transfer_name_suffix", text="Transfer Name")
        #Export Buttons
        layout.separator()
        row = GoToLine(layout)
        row.prop(properities, "Name", text="Name of the files")
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("object.export_selected_operator", text="Export High").suffix_to_export = "_high"
        row.operator("object.export_selected_operator", text="Export Low").suffix_to_export = "_low"
               
        col= self.layout.column()
        if not properities.ShowPathOptions:
            row = col.row()
            row.prop(properities, "ShowPathOptions", icon='TRIA_RIGHT', text="", emboss=False, toggle=True)
            row.label(text="Path Option")
        else :
            box = layout.box()
            row = box.row()
            row.prop(properities, "ShowPathOptions", icon='TRIA_DOWN', text="", emboss=False, toggle=True)
            row.label(text="Path Option")
            row = GoToLine(box)
            row.prop(properities, "ExportPath", text="Export Path")

    def draw_header_preset(self, context):
        layout = self.layout
        layout.label(icon='TOOL_SETTINGS')
        layout.label(text="")
    
        
        
        
def register():
    bpy.utils.register_class(MB_BS_Panel)
    
def unregister():
    bpy.utils.unregister_class(MB_BS_Panel)

       