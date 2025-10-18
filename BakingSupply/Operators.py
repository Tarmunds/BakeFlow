import bpy, re, os


#-----------Naming Operators-----------#
# renmaing operators

class BF_BS_Renaming(bpy.types.Operator):
    bl_idname = "object.bf_bs_renaming_operator"
    bl_label = "Renaming Operator"
    bl_description = "Rename selected mesh objects with a base name and an index"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Prevent running outside object mode entirely
        return context.mode == 'OBJECT'    

    def execute(self, context):
        NameOfMeshes = bpy.context.scene.BF_BS_Properties.RenameName
        count = 1
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected. Please select at least one mesh object.")
            return {'CANCELLED'}
        
        if not NameOfMeshes.strip():
            self.report({'ERROR'}, "Name cannot be empty. Please provide a name.")
            return {'CANCELLED'}
        
        if len(selected_objects) == 1:
            selected_objects[0].name = NameOfMeshes
            return {'FINISHED'}
        
        for obj in selected_objects:
            if obj.type == 'MESH':
                obj.name = f"{NameOfMeshes}_{count:02}"
                count += 1

        return {'FINISHED'}



# Operator to replace "_high" with "_low" and vice versa
class BF_BS_SwitchSuffix(bpy.types.Operator):
    bl_idname = "object.bf_bs_switch_suffix"
    bl_label = "High <> Low"
    bl_description = "Switch '_high' to '_low' and vice versa in selected object names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Prevent running outside object mode entirely
        return context.mode == 'OBJECT'

    def execute(self, context):
        pattern = re.compile(r'(_high|_low)', re.IGNORECASE)

        def replace_case(match):
            text = match.group(1).lower()
            return '_low' if text == '_high' else '_high'

        for obj in bpy.context.selected_objects:
            obj.name = pattern.sub(replace_case, obj.name)

        return {'FINISHED'}

# Operator to add "_high" or "_low" to object names, preventing duplicate suffixes
class BF_BS_AddSuffix(bpy.types.Operator):
    bl_idname = "object.bf_bs_add_suffix"
    bl_label = "Add Suffix"
    bl_description = "Add '_high' or '_low' suffix to selected object names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Prevent running outside object mode entirely
        return context.mode == 'OBJECT'

    rename_type: bpy.props.StringProperty(name="Rename Type")

    def execute(self, context):
        rename_type = self.rename_type.lower()
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                name = obj.name.rstrip("_high_low")  # Remove existing suffix if present
                obj.name = f"{name}_{rename_type}"

        return {'FINISHED'}

# Operator to transfer names between _high and _low meshes with indexing
class BF_BS_TransferName(bpy.types.Operator):
    bl_idname = "object.bf_bs_transfer_name_suffix"
    bl_label = "Transfer Name"
    bl_description = "Transfer names between from active to rest of the selection, taking care of the suffix"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Prevent running outside object mode entirely
        return context.mode == 'OBJECT'

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
                    new_name = f"{base_name}_{count:02}"
                    count += 1
                obj.name = new_name
                existing_names.add(new_name)

        self.report({'INFO'}, "Names transferred successfully")
        return {'FINISHED'}


#-----------Visibility Operators-----------#

#show low
class BF_BS_ShowLow(bpy.types.Operator):
    """Operator to show or hide meshes with '_low' in their name"""
    bl_idname = "object.bf_bs_show_low_meshes"
    bl_label = "Show Low"
    bl_description = "Show meshes with '_low' in their name"

    def execute(self, context):
        for obj in context.view_layer.objects:
            if "_low" in obj.name:
                obj.hide_set(False)
        return {'FINISHED'}


#Hide low
class BF_BS_HideLow(bpy.types.Operator):
    """Operator to hide meshes with '_low' in their name"""
    bl_idname = "object.bf_bs_hide_low_meshes"
    bl_label = "Hide Low"
    bl_description = "Hide meshes with '_low' in their name"

    def execute(self, context):
        for obj in context.view_layer.objects:
            if "_low" in obj.name:
                obj.hide_set(True)
        return {'FINISHED'}


#show High
class BF_BS_ShowHigh(bpy.types.Operator):
    """Operator to show or hide meshes with '_high' in their name"""
    bl_idname = "object.bf_bs_show_high_meshes"
    bl_label = "Show High"
    bl_description = "Show meshes with '_high' in their name"

    def execute(self, context):
        for obj in context.view_layer.objects:
            if "_high" in obj.name:
                obj.hide_set(False)
        return {'FINISHED'}


#Hide high
class BF_BS_HideHigh(bpy.types.Operator):
    """Operator to hide meshes with '_high' in their name"""
    bl_idname = "object.bf_bs_hide_high_meshes"
    bl_label = "Hide High"
    bl_description = "Hide meshes with '_high' in their name"

    def execute(self, context):
        for obj in context.view_layer.objects:
            if "_high" in obj.name:
                obj.hide_set(True)
        return {'FINISHED'}
    
#-----------Exporter-----------#


class BF_BS_Export(bpy.types.Operator):
    bl_idname = "object.export_selected_operator"
    bl_label = "Export Selected To Files"
    bl_description = "Export selected objects with a specific suffix to FBX files"
    
    suffix_to_export: bpy.props.StringProperty(name="Suffix to Export")

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def _resolve_export_path(self, properties, suffix_to_export: str):
        if properties.ExportPath:
            return os.path.join(properties.ExportPath.strip(), f"{properties.Name}{suffix_to_export}.fbx")
        return os.path.join(os.path.dirname(bpy.data.filepath), f"{properties.Name}{suffix_to_export}.fbx")

    def _validate(self, properties, selected_objects, export_path):
        if not selected_objects:
            self.report({'WARNING'}, "No selected objects match the suffix filter.")
            return False
        if not properties.Name.strip():
            self.report({'ERROR'}, "Name cannot be empty. Please provide a name.")
            return False
        export_dir = os.path.dirname(export_path)
        if not os.path.exists(export_dir):
            self.report({'ERROR'}, f"Directory does not exist: {export_dir}")
            return False
        return True

    def _export_original_workflow(self, selected_objects, export_path):
        # Store and adjust selection
        original_selection = list(bpy.context.selected_objects)
        original_active = bpy.context.view_layer.objects.active

        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            obj.select_set(True)

        try:
            bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True)
        except PermissionError:
            self.report({'ERROR'}, f"Permission denied: Unable to write to {export_path}.")
            return {'CANCELLED'}
        finally:
            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for o in original_selection:
                if o and o.name in bpy.data.objects:
                    o.select_set(True)
            if original_active and original_active.name in bpy.data.objects:
                bpy.context.view_layer.objects.active = original_active

        return {'FINISHED'}

    def _export_baked_pose_meshes(self, selected_objects, export_path, context):
        # Build temp posed meshes from depsgraph
        depsgraph = context.evaluated_depsgraph_get()

        original_selection = list(bpy.context.selected_objects)
        original_active = context.view_layer.objects.active

        temp_objects = []
        try:
            bpy.ops.object.select_all(action='DESELECT')

            for obj in selected_objects:
                if obj.type != 'MESH':
                    continue

                eval_obj = obj.evaluated_get(depsgraph)
                new_me = bpy.data.meshes.new_from_object(
                    eval_obj,
                    preserve_all_data_layers=True,
                    depsgraph=depsgraph
                )

                new_obj = bpy.data.objects.new(f"{obj.name}_POSEBAKED", new_me)
                new_obj.matrix_world = obj.matrix_world

                link_target = obj.users_collection[0] if obj.users_collection else context.collection
                link_target.objects.link(new_obj)

                for m in list(new_obj.modifiers):
                    new_obj.modifiers.remove(m)

                new_obj.select_set(True)
                temp_objects.append(new_obj)

            if not temp_objects:
                self.report({'ERROR'}, "No mesh objects to export after baking.")
                return {'CANCELLED'}

            try:
                bpy.ops.export_scene.fbx(
                    filepath=export_path,
                    use_selection=True,
                    object_types={'MESH'},
                    use_mesh_modifiers=False,  # geometry is already baked
                    bake_anim=False,
                    add_leaf_bones=False,
                    apply_unit_scale=True,
                    apply_scale_options='FBX_SCALE_ALL',
                    path_mode='AUTO'
                )
            except PermissionError:
                self.report({'ERROR'}, f"Permission denied: Unable to write to {export_path}.")
                return {'CANCELLED'}

        finally:
            # Cleanup temp objects
            if temp_objects:
                bpy.ops.object.select_all(action='DESELECT')
                for o in temp_objects:
                    if o and o.name in bpy.data.objects:
                        o.select_set(True)
                bpy.ops.object.delete()

            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for o in original_selection:
                if o and o.name in bpy.data.objects:
                    o.select_set(True)
            if original_active and original_active.name in bpy.data.objects:
                context.view_layer.objects.active = original_active

        return {'FINISHED'}

    def execute(self, context):
        properties = context.scene.BF_BS_Properties
        if properties is None:
            self.report({'ERROR'}, "Scene properties 'BF_BS_Properties' not found.")
            return {'CANCELLED'}

        suffix_to_export = (self.suffix_to_export or "").lower()

        # Filter currently selected objects by suffix
        selected_objects = [
            obj for obj in context.selected_objects
            if suffix_to_export in obj.name.lower()
        ]

        export_path = self._resolve_export_path(properties, suffix_to_export)
        self.report({'INFO'}, f"Export Path: {export_path}")

        if not self._validate(properties, selected_objects, export_path):
            return {'CANCELLED'}

        # Toggle based on BF_BS_Properties.exported_in_pose
        exported_in_pose = properties.exported_in_pose

        if exported_in_pose:
            result = self._export_baked_pose_meshes(selected_objects, export_path, context)
        else:
            result = self._export_original_workflow(selected_objects, export_path)

        if result == {'FINISHED'}:
            self.report({'INFO'}, f"Exported successfully to: {export_path}")
        return result


#-----------Register-----------#

_classes = (
    BF_BS_Renaming,
    BF_BS_SwitchSuffix,
    BF_BS_AddSuffix,
    BF_BS_TransferName,
    BF_BS_ShowLow,
    BF_BS_HideLow,
    BF_BS_ShowHigh,
    BF_BS_HideHigh,
    BF_BS_Export,
)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)