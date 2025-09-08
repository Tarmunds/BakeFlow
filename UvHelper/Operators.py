import bpy
from .Functions import *
class BF_UH_EdgesByNormal(bpy.types.Operator):
    bl_idname = "object.bf_uh_edges_by_normal"
    bl_label = "Select Edges by Normal Difference"
    bl_description = "Select edges based on the angle between adjacent face normals"

    @classmethod
    def poll(cls, context):
        # Prevent running outside edit mode entirely
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        select_edges_by_normal_difference(self, context)
        return {'FINISHED'}
    
class BF_UH_ContourSelect(bpy.types.Operator):
    bl_idname = "object.bf_uh_contour_select"
    bl_label = "Select Contour Edges"
    bl_description = "Select contour edges of the selection"
    
    @classmethod
    def poll(cls, context):
        # Prevent running outside edit mode entirely
        return context.mode == 'EDIT_MESH'
    
    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        return {'FINISHED'}
    
class BF_UH_SeamSharpEdges(bpy.types.Operator):
    bl_idname = "object.bf_uh_seam_sharp_edges"
    bl_label = "Tag Seam and Sharp Edges"
    bl_description = "Tag or Clean selected edges of seam and sharp"
    bl_options = {'REGISTER', 'UNDO'}

    tag: bpy.props.BoolProperty(name="Tag", default=True)
    
    @classmethod
    def poll(cls, context):
        # Prevent running outside edit mode entirely
        return context.mode == 'EDIT_MESH'
    
    def execute(self, context):
        if self.tag:
            tag_seam_sharp_edges()
        else:
            clear_seam_sharp_edges()
        return {'FINISHED'}
    
class BF_UH_ClearSplitNormals(bpy.types.Operator):
    bl_idname = "object.bf_uh_clear_split_normals"
    bl_label = "Clear Split Normals"
    bl_description = "Clear custom split normals from selected meshes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Prevent running outside object mode entirely
        return context.mode == 'OBJECT'
        
    def execute(self, context):
        clear_custom_split_normals(context)
        return {'FINISHED'}

class BF_UH_AddModifier(bpy.types.Operator):
    bl_idname = "object.bf_uh_add_modifier"
    bl_label = "Add Modifier to Selected"
    bl_description = "Add a Trangulate and a Weighted Normals modifier to selected meshes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Prevent running outside object mode entirely
        return context.mode == 'OBJECT'
    
    def execute(self, context):
        add_modifier(context)
        return {'FINISHED'}
    
class BF_UH_Ngon(bpy.types.Operator):
    bl_idname = "object.bf_uh_ngon"
    bl_label = "Select Ngon Faces"
    bl_description = "Detect and select ngons in the mesh range"
   
    def execute(self, context):
        ngon_detector(self, context)
        return {'FINISHED'}

      
_classes = (
    BF_UH_EdgesByNormal,
    BF_UH_ContourSelect,
    BF_UH_SeamSharpEdges,
    BF_UH_ClearSplitNormals,
    BF_UH_AddModifier,
    BF_UH_Ngon,
)
def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)