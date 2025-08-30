import bpy, os, subprocess, tempfile

class MB_MT_ExportToMarmoset(bpy.types.Operator):
    """Exports mesh to Marmoset Toolbag"""
    bl_idname = "object.mb_mt_export_to_marmoset"
    bl_label = "Export & Launch Marmoset"

    def execute(self, context):
        scene = context.scene
        addon_prefs = bpy.context.preferences.addons.get(__package__)
        properties = context.scene.MB_MT_Properties
        properties_BS = context.scene.MB_BS_Properties
        marmoset_path = addon_prefs.preferences.marmoset_path

        #------------ Sanity Checks ------------#
        if not addon_prefs:
            self.report({'ERROR'}, "Failed to retrieve Baking Supply addon preferences.")
            return {'CANCELLED'}

        if not marmoset_path or not os.path.exists(marmoset_path):
            self.report({'ERROR'}, f"Marmoset Toolbag not found at: {marmoset_path}. Please set the correct path in Preferences.")
            return {'CANCELLED'}

        if not scene.appelation.strip():
            self.report({'ERROR'}, "Appellation cannot be empty. Please provide a name.")
            return {'CANCELLED'}
        
        #------------ End Sanity Checks ------------#    
        
        #Preset mbake
        #addon_folder = os.path.dirname(os.path.abspath(__file__))
        #asset_preset_path = os.path.join(addon_folder, "Tarmunds_Asset.tbbake")
        #tileable_preset_path = os.path.join(addon_folder, "Tarmunds_Tileable.tbbake")

        Meshes_Folder = properties_BS.ExportPath.strip() if properties_BS.ExportPath.strip() else os.path.dirname(bpy.data.filepath) #use export path or blend file path
        high_fbx = os.path.abspath(os.path.join(Meshes_Folder, f"{properties_BS.Name}_high.fbx"))
        low_fbx = os.path.abspath(os.path.join(Meshes_Folder, f"{properties_BS.Name}_low.fbx"))

        high_selected = any(obj for obj in context.selected_objects if "_high" in obj.name)
        low_selected = any(obj for obj in context.selected_objects if "_low" in obj.name)

        high_fbx_safe = high_fbx.replace("\\", "\\\\") if high_selected else None
        low_fbx_safe = low_fbx.replace("\\", "\\\\") if low_selected else None
        asset_preset_safe = asset_preset_path.replace("\\", "\\\\")
        tileable_preset_safe = tileable_preset_path.replace("\\", "\\\\")
        custom_preset_safe = custompreset_path.replace("\\", "\\\\")


        #------------ Export Selected High and Low ------------#
        if not high_selected and not low_selected:
            self.report({'ERROR'}, "No selected objects with '_high' or '_low' in their names.")
            return {'CANCELLED'}
        else:
            if high_selected:
                bpy.ops.object.export_selected_operator_high()
            if low_selected:
                bpy.ops.object.export_selected_operator_low()

        #------------ Select Path ------------#
        if properties.SamePathAsMesh:
            Original_path = properties_BS.ExportPath
        else:
            if properties.CustomBakePath.strip():
                Original_path = properties.CustomBakePath.strip()
            else:
                self.report({'ERROR'}, "No custom path set for the Baking")
                return {'CANCELLED'}
                
        MarmoBake_ExportPath = os.path.join(Original_path,f"{properties_BS.Name.strip()}.{properties.FileFormat}").replace("/", "\\")
        #------------ End Path ------------#

        MarmoBake_PixelDepth = properties.PixelDepth
        MarmoBake_samples = properties.Samples
        MarmoBake_width = properties.ResolutionX
        MarmoBake_height = properties.ResolutionY

        NormalDirection = False
        MarmoBake_QuickBake = properties.DirectBake


        marmoset_script = tempfile.NamedTemporaryFile(delete=False, suffix=".py").name

        with open(marmoset_script, "w") as script_file:
            script_file.write(f"""
import mset

mset.newScene()
baker = mset.BakerObject()

{f'baker.importModel(r"{low_fbx_safe}")' if low_selected else ''}
{f'baker.importModel(r"{high_fbx_safe}")' if high_selected else ''}

baker.outputPath = r"{MarmoBake_ExportPath}"
baker.outputBits = {MarmoBake_PixelDepth}
baker.outputSamples = {MarmoBake_samples}
baker.edgePadding = "Moderate"
baker.outputSoften = 0
baker.useHiddenMeshes = True
baker.ignoreTransforms = False
baker.smoothCage = True
baker.ignoreBackfaces = True
baker.tileMode = 0

baker.outputWidth = {MarmoBake_width}
baker.outputHeight = {MarmoBake_height}


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

if {MarmoBake_QuickBake}:
    baker.bake()
    baker.applyPreviewMaterial()
""")

        subprocess.Popen([marmoset_path, "-py", marmoset_script], shell=True)
        self.report({'INFO'}, "Marmoset Toolbag launched and setup.")
        return {'FINISHED'}
    
#------------ Register and Unregister ------------#
def register():
    bpy.utils.register_class(MB_MT_ExportToMarmoset)

def unregister():
    bpy.utils.unregister_class(MB_MT_ExportToMarmoset)