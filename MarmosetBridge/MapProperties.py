import bpy

_MB_SYNC_GUARD = {"busy": False}

def _guarded(fn):
    def wrapper(self, context):
        if _MB_SYNC_GUARD["busy"]:
            return
        try:
            _MB_SYNC_GUARD["busy"] = True
            fn(self, context)
        finally:
            _MB_SYNC_GUARD["busy"] = False
    return wrapper

@_guarded
def _update_flip_y(self, context):
    # Example: mirror flip_y into a scene property for other tools
    if self.flip_y:
        context.scene.MB_MT_Properties.NormalOrientation = 'DIRECTX'
    else:
        context.scene.MB_MT_Properties.NormalOrientation = 'OPENGL'
class MB_MT_NormalSettings(bpy.types.PropertyGroup):
    suffix: bpy.props.StringProperty(name="Suffix", default="_normal")
    flip_x: bpy.props.BoolProperty(name="Flip X", default=False)
    flip_y: bpy.props.BoolProperty(name="Flip Y", default=False, update=_update_flip_y)
    flip_z: bpy.props.BoolProperty(name="Flip Z", default=False)


    def draw(self, layout):
        box = layout.box()
        box.label(text="Normal Map Settings")
        row = box.row(align=True)
        row.prop(self, "suffix")
        col = box.column(align=True)
        col.label(text="Flip Channels")
        flips = col.row(align=True)
        flips.enabled = True #disable due to marmoset issue
        sub = flips.row()
        sub.enabled = False #disable due to marmoset issue
        sub.prop(self, "flip_x")
        sub = flips.row()
        sub.prop(self, "flip_y")
        sub = flips.row()
        sub.enabled = False #disable due to marmoset issue
        sub.prop(self, "flip_z")
        row = box.row()
        row.alert = True
        row.label(text="Note: Normal map flipping might not work due to a bug in Marmoset Toolbag API.", icon='ERROR')
        row = box.row()
        row.alert = True
        row.label(text="Request has been made to Marmoset support to fix this issue.")

class MB_MT_NormalOBJSettings(bpy.types.PropertyGroup):
    suffix: bpy.props.StringProperty(name="Suffix", default="_normalobj")
    flip_x: bpy.props.BoolProperty(name="Flip X", default=False)
    flip_y: bpy.props.BoolProperty(name="Flip Y", default=False)
    flip_z: bpy.props.BoolProperty(name="Flip Z", default=False)


    def draw(self, layout):
        box = layout.box()
        box.label(text="Normal OBJ Map Settings")
        row = box.row(align=True)
        row.prop(self, "suffix")
        col = box.column(align=True)
        col.label(text="Flip Channels")
        flips = col.row(align=True)
        flips.prop(self, "flip_x")
        flips.prop(self, "flip_y")
        flips.prop(self, "flip_z")

class MB_MT_HeightSettings(bpy.types.PropertyGroup):
    suffix: bpy.props.StringProperty(name="Suffix", default="_height")
    inner_distance: bpy.props.FloatProperty(name="Inner Distance", default=-0.5, min=-100.0, max=100.0)
    outer_distance: bpy.props.FloatProperty(name="Outer Distance", default=0.5, min=-100.0, max=100.0)

    def draw(self, layout):
        box = layout.box()
        box.label(text="Height Map Settings")
        row = box.row(align=True)
        row.prop(self, "suffix")
        col = box.column(align=True)
        col.prop(self, "inner_distance")
        col.prop(self, "outer_distance")

class MB_MT_PositionSettings(bpy.types.PropertyGroup):
    suffix: bpy.props.StringProperty(name="Suffix", default="_position")
    normalization: bpy.props.EnumProperty(
        name="Normalization",
        items=[
            ('BOUNDINGBOX', "Bounding Box", ""),
            ('BOUNDINGSPHERE', "Bounding Sphere", ""),
            ('DISABLED', "Disabled", ""),
        ],
        default='BOUNDINGSPHERE'
    )

    def draw(self, layout):
        box = layout.box()
        box.label(text="Position Map Settings")
        row = box.row(align=True)
        row.prop(self, "suffix")
        col = box.column(align=True)
        col.prop(self, "normalization")

class MB_MT_CurveSettings(bpy.types.PropertyGroup):
    suffix: bpy.props.StringProperty(name="Suffix", default="_curve")
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0, max=4.0)

    def draw(self, layout):
        box = layout.box()
        box.label(text="Curvature Map Settings")
        row = box.row(align=True)
        row.prop(self, "suffix")
        col = box.column(align=True)
        col.prop(self, "strength")

class MB_MT_ThicknessSettings(bpy.types.PropertyGroup):
    suffix: bpy.props.StringProperty(name="Suffix", default="_thickness")
    ray_count: bpy.props.IntProperty(name="RayCount", default=256, min=32, max=4096)
    search_distance: bpy.props.FloatProperty(name="Search Distance", default=0.0, min=0.0, max=100.0)
    scale: bpy.props.FloatProperty(name="Scale", default=0.5, min=0.0, max=1.0)
    ignore_groups: bpy.props.BoolProperty(name="Ignore Groups", default=True)
    gamma: bpy.props.BoolProperty(name="Gamma", default=False)

    def draw(self, layout):
        box = layout.box()
        box.label(text="Thickness Map Settings")
        row = box.row(align=True)
        row.prop(self, "suffix")
        col = box.column(align=True)
        col.prop(self, "ray_count")
        row = box.row()
        row.enabled = False #disable due to marmoset issue
        row.prop(self, "search_distance")
        row = box.row()
        row.enabled = False #disable due to marmoset issue
        row.prop(self, "scale")
        row = box.row(align=True)
        row.enabled = False #disable due to marmoset issue
        row.prop(self, "ignore_groups")
        row.prop(self, "gamma")
        row = box.row()
        row.alert = True
        row.label(text="Note: Except ray count all other attribute will not work due to a bug in Marmoset Toolbag API.", icon='ERROR')
        row = box.row()
        row.alert = True
        row.label(text="Request has been made to Marmoset support to fix this issue.")

class MB_MT_AOSettings(bpy.types.PropertyGroup):
    suffix: bpy.props.StringProperty(name="Suffix", default="_ao")
    ray_count: bpy.props.IntProperty(name="Ray Count", default=512, min=32, soft_max=4096)
    search_distance: bpy.props.FloatProperty(name="Search Distance", default=0.0, min=0.0, soft_max=100.0)
    cavity_weight: bpy.props.FloatProperty(name="Cavity Weight", default=0.0, min=-1.0, max=1.0)
    floor_occlusion: bpy.props.BoolProperty(name="Floor Occlusion", default=False)
    floor_strength: bpy.props.FloatProperty(name="Floor Strength", default=0.8, min=0.0, max=1.0)
    ignore_groups: bpy.props.BoolProperty(name="Ignore Groups", default=True)
    two_sided: bpy.props.BoolProperty(name="Two Sided", default=False)

    def draw(self, layout):
        box = layout.box()
        box.label(text="Ambiant Occlusion Map Settings")
        row = box.row(align=True)
        row.prop(self, "suffix")
        col = box.column(align=True)
        col.prop(self, "ray_count")
        col.prop(self, "search_distance")
        col.prop(self, "cavity_weight")
        row = box.row(align=True)
        row.prop(self, "floor_occlusion")
        sub = row.row()
        sub.enabled = self.floor_occlusion
        sub.prop(self, "floor_strength")
        row = box.row(align=True)
        row.prop(self, "ignore_groups")
        row.prop(self, "two_sided")


class MB_MT_AO2Settings(bpy.types.PropertyGroup):
    suffix: bpy.props.StringProperty(name="Suffix", default="_ao2")
    ray_count: bpy.props.IntProperty(name="Ray Count", default=512, min=32, soft_max=4096)
    search_distance: bpy.props.FloatProperty(name="Search Distance", default=0.0, min=0.0, soft_max=100.0)
    cavity_weight: bpy.props.FloatProperty(name="Cavity Weight", default=0.0, min=-1.0, max=1.0)
    floor_occlusion: bpy.props.BoolProperty(name="Floor Occlusion", default=False)
    floor_strength: bpy.props.FloatProperty(name="Floor Strength", default=0.8, min=0.0, max=1.0)
    ignore_groups: bpy.props.BoolProperty(name="Ignore Groups", default=True)
    two_sided: bpy.props.BoolProperty(name="Two Sided", default=False)

    def draw(self, layout):
        box = layout.box()
        box.label(text="Ambiant Occlusion 2 Map Settings")
        row = box.row(align=True)
        row.prop(self, "suffix")
        col = box.column(align=True)
        col.prop(self, "ray_count")
        col.prop(self, "search_distance")
        col.prop(self, "cavity_weight")
        row = box.row(align=True)
        row.prop(self, "floor_occlusion")
        sub = row.row()
        sub.enabled = self.floor_occlusion
        sub.prop(self, "floor_strength")
        row = box.row(align=True)
        row.prop(self, "ignore_groups")
        row.prop(self, "two_sided")

class MB_MT_NoSettings(bpy.types.PropertyGroup):
    def draw(self, layout):
        box = layout.box()
        box.label(text="No Settings Available")

MAP_TYPE_TO_SETTINGS = {
    'NORMAL': MB_MT_NormalSettings,
    'NORMAL_OBJ': MB_MT_NormalOBJSettings,
    'HEIGHT': MB_MT_HeightSettings,
    'POSITION': MB_MT_PositionSettings,
    'CURVATURE': MB_MT_CurveSettings,
    'THICKNESS': MB_MT_ThicknessSettings,
    'AMBIANT_OCCLUSION': MB_MT_AOSettings,
    'AMBIANT_OCCLUSION_2': MB_MT_AO2Settings,

}

_classes = (
    MB_MT_NormalSettings,
    MB_MT_NormalOBJSettings,
    MB_MT_HeightSettings,
    MB_MT_PositionSettings,
    MB_MT_CurveSettings,
    MB_MT_ThicknessSettings,
    MB_MT_AOSettings,
    MB_MT_AO2Settings,
    MB_MT_NoSettings,
)

_MapsSettings = (
    MB_MT_NormalSettings,
    MB_MT_NormalOBJSettings,
    MB_MT_HeightSettings,
    MB_MT_PositionSettings,
    MB_MT_CurveSettings,
    MB_MT_ThicknessSettings,
    MB_MT_AOSettings,
    MB_MT_AO2Settings,
    MB_MT_NoSettings,
)



def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    for ms in _classes:
        prop_name = ms.__name__
        if not hasattr(bpy.types.Scene, prop_name):
            setattr(
                bpy.types.Scene,
                prop_name,
                bpy.props.PointerProperty(type=ms)
            )

def unregister():
    for ms in _MapsSettings:
        prop_name = ms.__name__
        if hasattr(bpy.types.Scene, prop_name):
            delattr(bpy.types.Scene, prop_name)
            
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
        
