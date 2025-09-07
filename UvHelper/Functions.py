import bpy, bmesh, math

def GoToLine(layout, *, scale_y=1.2, align=True):
    row = layout.row(align=align)
    row.scale_y = scale_y
    return row



def popup_message(context, message):
    def draw(self, context):
        self.layout.label(text=message)
    context.window_manager.popup_menu(draw, title="Info", icon='INFO')

def select_edges_by_normal_difference(self, context):
    properties = context.scene.BF_UH_Properties
    bpy.ops.mesh.select_all(action='DESELECT')

    total_selected_edges = 0


    for obj in context.objects_in_mode:
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        angle_threshold = properties.angle_threshold

        selected_edges = 0
        for edge in bm.edges:
            if len(edge.link_faces) == 2:
                dot_product = edge.link_faces[0].normal.dot(edge.link_faces[1].normal)
                if -1.0 <= dot_product <= 1.0:
                    angle = math.degrees(math.acos(dot_product))
                    if angle >= angle_threshold:
                        edge.select_set(True)
                        selected_edges += 1

        bmesh.update_edit_mesh(me)
        total_selected_edges += selected_edges
    
    if total_selected_edges == 0:
        info = "No edges found with the specified angle threshold"
        popup_message(context, info)
    bpy.ops.ed.undo_push(message="Select Edges by Normal")

def tag_seam_sharp_edges():
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.mark_seam(clear=False)
    bpy.ops.mesh.mark_sharp()

def clear_seam_sharp_edges():
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.mark_seam(clear=True)
    bpy.ops.mesh.mark_sharp(clear=True)

def clear_custom_split_normals(context):
    bpy.ops.object.mode_set(mode='OBJECT')
    selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
    
    for obj in selected_objects:
        context.view_layer.objects.active = obj
        bpy.ops.mesh.customdata_custom_splitnormals_clear()

    for obj in selected_objects:
        obj.select_set(True)

def add_modifier(context):
    selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

    for obj in selected_objects:
        # Add Triangulate modifier if not present
        if not any(mod.type == 'TRIANGULATE' for mod in obj.modifiers):
            obj.modifiers.new(name="Triangulate", type='TRIANGULATE')

        # Add Weighted Normal modifier if not present
        if not any(mod.type == 'WEIGHTED_NORMAL' for mod in obj.modifiers):
            mod = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
            mod.keep_sharp = True  # Optional: keep sharp edges

        bpy.ops.object.shade_auto_smooth(use_auto_smooth=True, angle=3.14159)

    popup_message(context, f"Added Triangulate, Weighted Normal, and enabled smooth shading for {len(selected_objects)} objects.")

def ngon_detector(self, context):
    properties = context.scene.BF_UH_Properties
    meshes_to_switch_to_edit = []  # will hold meshes with ngons
    ngon_count = 0
    range_option = properties.ngon_detect_range
    object_to_scan = []

    if context.mode == 'EDIT_MESH':
        bpy.ops.mesh.select_all(action='DESELECT')
    
        for obj in bpy.context.objects_in_mode:  # loop, not assign
            bm = bmesh.from_edit_mesh(obj.data)
            for face in bm.faces:
                if len(face.verts) > 4:
                    face.select_set(True)
                    meshes_to_switch_to_edit.append(obj)
                    ngon_count += 1
            bmesh.update_edit_mesh(obj.data)
    
        self.report({'INFO'}, f"Detected {ngon_count} N-Gons on current edit meshes")
        return {'FINISHED'}

    match range_option:
        case 'SELECTED':
            object_to_scan = [obj for obj in context.selected_objects if obj.type == 'MESH']
        case 'VISIBLE':
            object_to_scan = [obj for obj in context.visible_objects if obj.type == 'MESH']
        case 'ALL':
            object_to_scan = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    if not object_to_scan:
        self.report({'INFO'}, "No mesh objects to scan")
        return {'CANCELLED'}

    # --- NEW: remember original visibility if scanning ALL
    original_hidden = {}
    if range_option == 'ALL':
        for o in object_to_scan:
            # record whether the object itself was hidden (object-level)
            # hide_get() includes collection visibility; we use both so we can re-hide object-level cases
            original_hidden[o.name] = (o.hide_viewport or o.hide_get())
            # unhide object-level so we can enter edit mode and scan
            o.hide_viewport = False
            o.hide_set(False)

    # Ensure Object Mode before switching objects
    if context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all OBJECTS safely in Object Mode
    bpy.ops.object.select_all(action='DESELECT')

    for obj in object_to_scan:
        if obj.type != 'MESH':
            continue

        # If still not visible (e.g., hidden by a hidden collection), skip it safely
        if not obj.visible_get():
            continue

        # Make it active (and selected helps in some edge cases)
        obj.select_set(True)
        context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        bm = bmesh.from_edit_mesh(obj.data)

        found_on_this = 0
        for face in bm.faces:
            if len(face.verts) > 4:
                face.select_set(True)
                found_on_this += 1

        if found_on_this > 0:
            meshes_to_switch_to_edit.append(obj)
            ngon_count += found_on_this

        bmesh.update_edit_mesh(obj.data)

        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)

    # --- NEW: if ALL, re-hide only those that were hidden and have NO ngons
    if range_option == 'ALL' and original_hidden:
        ngons_set = {o.name for o in meshes_to_switch_to_edit}
        for o in object_to_scan:
            if original_hidden.get(o.name, False) and o.name not in ngons_set:
                # re-hide at object level
                o.hide_set(True)
                o.hide_viewport = True

    # Put all meshes with ngons into multi-object Edit Mode
    if meshes_to_switch_to_edit:
        # go to Object mode, select all targets, set one active, then enter Edit once
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        for o in meshes_to_switch_to_edit:
            if o.visible_get():
                o.select_set(True)
        # set active to the first visible one
        for o in meshes_to_switch_to_edit:
            if o.visible_get():
                context.view_layer.objects.active = o
                break

        # enter multi-object edit mode (their face selections will show)
        if context.view_layer.objects.active:
            bpy.ops.object.mode_set(mode='EDIT')

    self.report({'INFO'}, f"Detected {ngon_count} N-Gons and switched to Edit Mode for relevant meshes")
    return {'FINISHED'}