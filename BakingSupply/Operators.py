import bpy, re, os


#-----------Naming Operators-----------#

# Operator to replace "_high" with "_low" and vice versa
class MB_BS_SwitchSuffix(bpy.types.Operator):
    bl_idname = "object.mb_bs_switch_suffix"
    bl_label = "High <> Low"

    def execute(self, context):
        pattern = re.compile(r'(_high|_low)', re.IGNORECASE)

        def replace_case(match):
            text = match.group(1).lower()
            return '_low' if text == '_high' else '_high'

        for obj in bpy.context.selected_objects:
            obj.name = pattern.sub(replace_case, obj.name)

        return {'FINISHED'}

# Operator to add "_high" or "_low" to object names, preventing duplicate suffixes
class MB_BS_AddSuffix(bpy.types.Operator):
    bl_idname = "object.mb_bs_add_suffix"
    bl_label = "Add Suffix"

    rename_type: bpy.props.StringProperty(name="Rename Type")

    def execute(self, context):
        rename_type = self.rename_type.lower()
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                name = obj.name.rstrip("_high_low")  # Remove existing suffix if present
                obj.name = f"{name}_{rename_type}"

        return {'FINISHED'}

# Operator to transfer names between _high and _low meshes with indexing
class MB_BS_TransferName(bpy.types.Operator):
    bl_idname = "object.mb_bs_transfer_name_suffix"
    bl_label = "Transfer Name"

    def execute(self, context):
        active_obj = context.active_object

        if not active_obj:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}

        name = active_obj.name
        base_name = None

        if "_high" in name:
            base_name = name.replace("_high", "_low")
        elif "_low" in name:
            base_name = name.replace("_low", "_high")

        if not base_name:
            self.report({'WARNING'}, "Active object's name does not contain '_high' or '_low'")
            return {'CANCELLED'}

        existing_names = {obj.name for obj in bpy.data.objects}  # Collect existing names
        count = 1

        for obj in context.selected_objects:
            if obj != active_obj and obj.type == 'MESH':
                new_name = base_name
                while new_name in existing_names:
                    new_name = f"{base_name}_{count}"
                    count += 1
                obj.name = new_name
                existing_names.add(new_name)

        self.report({'INFO'}, "Names transferred successfully")
        return {'FINISHED'}


#-----------Visibility Operators-----------#

#show low
class MB_BS_ShowLow(bpy.types.Operator):
    """Operator to show or hide meshes with '_low' in their name"""
    bl_idname = "object.mb_bs_show_low_meshes"
    bl_label = "Show Low"

    def execute(self, context):
        for obj in bpy.data.objects:
            if "_low" in obj.name:
                obj.hide_set(False)
        return {'FINISHED'}


#Hide low
class MB_BS_HideLow(bpy.types.Operator):
    """Operator to hide meshes with '_low' in their name"""
    bl_idname = "object.mb_bs_hide_low_meshes"
    bl_label = "Hide Low"

    def execute(self, context):
        for obj in bpy.data.objects:
            if "_low" in obj.name:
                obj.hide_set(True)
        return {'FINISHED'}


#show High
class MB_BS_ShowHigh(bpy.types.Operator):
    """Operator to show or hide meshes with '_high' in their name"""
    bl_idname = "object.mb_bs_show_high_meshes"
    bl_label = "Show High"

    def execute(self, context):
        for obj in bpy.data.objects:
            if "_high" in obj.name:
                obj.hide_set(False)
        return {'FINISHED'}


#Hide high
class MB_BS_HideHigh(bpy.types.Operator):
    """Operator to hide meshes with '_high' in their name"""
    bl_idname = "object.mb_bs_hide_high_meshes"
    bl_label = "Hide High"

    def execute(self, context):
        for obj in bpy.data.objects:
            if "_high" in obj.name:
                obj.hide_set(True)
        return {'FINISHED'}
    
#-----------Exporter-----------#

class MB_BS_Export(bpy.types.Operator):
    bl_idname = "object.export_selected_operator"
    bl_label = "Export Selected To Files"
    
    suffix_to_export: bpy.props.StringProperty(name="Suffix to Export")

    def execute(self, context):
        scene = context.scene
        properities = context.scene.MB_BS_Properties
        suffix_to_export = self.suffix_to_export.lower()
        selected_objects = [obj for obj in context.selected_objects if suffix_to_export in obj.name]

        if properities.ExportPath:
            export_path = os.path.join(properities.ExportPath.strip(), f"{properities.Name}{suffix_to_export}.fbx")
        else :
            export_path = os.path.join(os.path.dirname(bpy.data.filepath), f"{properities.Name}{suffix_to_export}.fbx")
        
        self.report({'INFO'}, f"Export Path: {export_path}")
         
        if not selected_objects:
            self.report({'WARNING'}, f"No selected objects with {suffix_to_export} in their names.")
            return {'CANCELLED'}

        if not properities.Name.strip():
            self.report({'ERROR'}, "Name cannot be empty. Please provide a name.")
            return {'CANCELLED'}

        if not os.path.exists(os.path.dirname(export_path)):
            self.report({'ERROR'}, f"Directory does not exist: {os.path.dirname(export_path)}")
            return {'CANCELLED'}

        # Store the original selection
        original_selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select only selected objects
        for obj in selected_objects:
            obj.select_set(True)

        try:
            bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True)
        except PermissionError:
            self.report({'ERROR'}, f"Permission denied: Unable to write to {export_path}.")
            return {'CANCELLED'}
        finally:
            # Restore original selection
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_selection:
                obj.select_set(True)

        self.report({'INFO'}, f"Exported successfully to: {export_path}")
        return {'FINISHED'}

#-----------Register-----------#

_classes = (
    MB_BS_SwitchSuffix,
    MB_BS_AddSuffix,
    MB_BS_TransferName,
    MB_BS_ShowLow,
    MB_BS_HideLow,
    MB_BS_ShowHigh,
    MB_BS_HideHigh,
    MB_BS_Export,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)