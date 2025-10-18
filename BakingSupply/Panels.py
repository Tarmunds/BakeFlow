import bpy
from .Functions import GoToLine

class BF_BS_Panel(bpy.types.Panel):
    """Panel for the low and high mesh operations"""
    bl_label = "Baking Supply"
    bl_idname = "VIEW3D_PT_BF_2_BS_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BakeFlow'
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properities = context.scene.BF_BS_Properties

        #Hide/Show Buttons
        row = GoToLine(layout)
        row.operator("object.bf_bs_hide_high_meshes", text="Hide High")
        row.operator("object.bf_bs_hide_low_meshes", text="Hide Low")
        row = GoToLine(layout)
        row.operator("object.bf_bs_show_high_meshes", text="Show High")
        row.operator("object.bf_bs_show_low_meshes", text="Show Low")
        #Suffix Buttons
        layout.separator()
        
        row = GoToLine(layout, align=False)
        row.operator("object.bf_bs_renaming_operator", text="Rename")
        row.prop(properities, "RenameName", text="")
        row.operator("object.bf_mt_openurl", text="", icon='HELP').url = "https://docs.marmoset.co/docs/baking-attributes/#quick-loader"
        
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator("object.bf_bs_add_suffix", text="Add _high").rename_type = "high"
        row.operator("object.bf_bs_add_suffix", text="Add _low").rename_type = "low"
        
        row = GoToLine(layout, align=False)
        row.operator("object.bf_bs_switch_suffix", text="High <> Low")
        row.operator("object.bf_bs_transfer_name_suffix", text="Transfer Name")
        #Export Buttons
        layout.separator()
        row = GoToLine(layout, align=False)
        row.prop(properities, "Name", text="Files Name")
        row.prop(properities, "exported_in_pose", text="Export In Pose Mode", toggle=True)
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("object.export_selected_operator", text="Export High").suffix_to_export = "_high"
        row.operator("object.export_selected_operator", text="Export Low").suffix_to_export = "_low"

               
        col= self.layout.column()
        if not properities.ShowPathOptions:
            row = col.row()
            row.prop(properities, "ShowPathOptions", icon='TRIA_RIGHT', text="", emboss=False, toggle=True)
            row.label(text="Mesh Output Path")
            if not properities.ExportPath:
                row.label(text="Current: Mesh export at blend files location")
            else:
                row.label(text=f"Current: {properities.ExportPath}")
        else :
            box = layout.box()
            row = box.row()
            row.prop(properities, "ShowPathOptions", icon='TRIA_DOWN', text="", emboss=False, toggle=True)
            row.label(text="Mesh Output Path")
            if not properities.ExportPath:
                row.label(text="Current: Mesh export at blend files location")
            else:
                row.label(text=f"Current: {properities.ExportPath}")
            row = GoToLine(box)
            row.prop(properities, "ExportPath", text="Mesh Export Path")

    def draw_header_preset(self, context):
        layout = self.layout
        layout.label(icon='TOOL_SETTINGS')
        layout.label(text="")
    
        
        
        
def register():
    bpy.utils.register_class(BF_BS_Panel)
    
def unregister():
    bpy.utils.unregister_class(BF_BS_Panel)

       