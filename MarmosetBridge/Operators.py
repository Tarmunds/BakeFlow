import bpy, os, subprocess, tempfile

class MB_MT_ExportToMarmoset(bpy.types.Operator):
    """Exports mesh to Marmoset Toolbag"""
    bl_idname = "object.mb_mt_export_to_marmoset"
    bl_label = "Export & Launch Marmoset"

    def execute(self, context):
        scene = context.scene
        addon_prefs = bpy.context.preferences.addons.get(__package__)
        properities = context.scene.MB_MT_Properties

        if not addon_prefs:
            self.report({'ERROR'}, "Failed to retrieve Baking Supply addon preferences.")
            return {'CANCELLED'}

        marmoset_path = addon_prefs.preferences.marmoset_path
        custompreset_path = addon_prefs.preferences.custompreset_path

        if not marmoset_path or not os.path.exists(marmoset_path):
            self.report({'ERROR'}, f"Marmoset Toolbag not found at: {marmoset_path}. Please set the correct path in Preferences.")
            return {'CANCELLED'}

        if not scene.appelation.strip():
            self.report({'ERROR'}, "Appellation cannot be empty. Please provide a name.")
            return {'CANCELLED'}

        addon_folder = os.path.dirname(os.path.abspath(__file__))
        asset_preset_path = os.path.join(addon_folder, "Tarmunds_Asset.tbbake")
        tileable_preset_path = os.path.join(addon_folder, "Tarmunds_Tileable.tbbake")

        export_dir = scene.mesh_path.strip() if scene.mesh_path.strip() else os.path.dirname(bpy.data.filepath)
        high_fbx = os.path.abspath(os.path.join(export_dir, f"{scene.appelation}_high.fbx"))
        low_fbx = os.path.abspath(os.path.join(export_dir, f"{scene.appelation}_low.fbx"))

        high_selected = any(obj for obj in context.selected_objects if "_high" in obj.name)
        low_selected = any(obj for obj in context.selected_objects if "_low" in obj.name)

        if not high_selected and not low_selected:
            self.report({'ERROR'}, "No selected objects with '_high' or '_low' in their names.")
            return {'CANCELLED'}

        if high_selected:
            bpy.ops.object.export_selected_operator_high()
        if low_selected:
            bpy.ops.object.export_selected_operator_low()

        high_fbx_safe = high_fbx.replace("\\", "\\\\") if high_selected else None
        low_fbx_safe = low_fbx.replace("\\", "\\\\") if low_selected else None
        asset_preset_safe = asset_preset_path.replace("\\", "\\\\")
        tileable_preset_safe = tileable_preset_path.replace("\\", "\\\\")
        custom_preset_safe = custompreset_path.replace("\\", "\\\\")

        if scene.BS_PathBakeAsMeshes:
            base_path = scene.mesh_path.strip()
        else:
            base_path = scene.BS_BakePath.strip()

        if not base_path:
            base_path = os.path.dirname(bpy.data.filepath)

        output_path = os.path.join(
            base_path,
            f"{scene.appelation.strip()}.{scene.BS_FileFormat}"
        ).replace("/", "\\")


        output_bits = 8
        output_samples = scene.BS_Sample
        output_width = scene.BS_ResX
        output_height = scene.BS_ResY
        output_single_psd = scene.BS_SinglePSD
        use_preset = scene.BS_UsePreset
        if scene.BS_Preset == "ASSETS":
            preset = "ASSETS"
        elif scene.BS_Preset == "TILEABLE":
            preset = "TILEABLE"
        elif scene.BS_Preset == "CUSTOM":
            preset = "CUSTOM"
        NormalDirection = False if scene.BS_NormalDirection == "OPENGL" else True
        quickbake = scene.BS_DirectBake
        output_depth = 8 if scene.BS_PixelDepth == "8Bits" else 16

        marmoset_script = tempfile.NamedTemporaryFile(delete=False, suffix=".py").name

        with open(marmoset_script, "w") as script_file:
            script_file.write(f"""
import mset

mset.newScene()
baker = mset.BakerObject()

{f'baker.importModel(r"{low_fbx_safe}")' if low_selected else ''}
{f'baker.importModel(r"{high_fbx_safe}")' if high_selected else ''}

baker.outputPath = r"{output_path}"
baker.outputBits = {output_bits}
baker.outputSamples = {output_samples}
baker.edgePadding = "Moderate"
baker.outputSoften = 0
baker.useHiddenMeshes = True
baker.ignoreTransforms = False
baker.smoothCage = True
baker.ignoreBackfaces = True
baker.tileMode = 0
#baker.outputSinglePsd = {output_single_psd}
baker.outputBits = {output_depth}

baker.outputWidth = {output_width}
baker.outputHeight = {output_height}

if {use_preset}:
    if "{preset}" == "ASSETS":
        baker.loadPreset(r"{asset_preset_safe}")
    elif "{preset}" == "TILEABLE":
        baker.loadPreset(r"{tileable_preset_safe}")
    elif "{preset}" == "CUSTOM":
        baker.loadPreset(r"{custom_preset_safe}")
#else:
#    baker.loadPreset(r"%appdata%\Local\Marmoset Toolbag 5\baker\Default.tbbake")

normal_map = None
for map in baker.getAllMaps():
    if isinstance(map, mset.NormalBakerMap):  # Check class type instead of `type` attribute
        normal_map = map
        break

all_objects = mset.getAllObjects()

# Filter materials
materials = [obj for obj in all_objects if isinstance(obj, mset.Material)]

# Find the material named "Default"
default_material = next((mat for mat in materials if mat.name == "Default"), None)


if normal_map:
    normal_map.flipY = {NormalDirection}
    if default_material:
        default_material.setProperty("normalFlipY", True)
        print("Flip Y for normals enabled on Default material.")
    else:
        print("Default material not found.")


print("Marmoset bake project created and models loaded.")

if {quickbake}:
    baker.bake()
    baker.applyPreviewMaterial()
""")

        subprocess.Popen([marmoset_path, "-py", marmoset_script], shell=True)
        self.report({'INFO'}, "Marmoset Toolbag launched and setup.")
        return {'FINISHED'}