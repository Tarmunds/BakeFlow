# BakeFlow

BakeFlow is a Blender add-on that streamlines the workflow from retopology and UV preparation to baking and Marmoset Toolbag integration.  
It combines three modules into one cohesive toolset:

- **UV Helper** – mesh and UV preparation utilities
- **Baking Supply** – naming, visibility, and export management
- **Marmoset Bridge** – one-click handoff to Marmoset Toolbag with map presets

---

## ✨ Features Overview

### UV Helper
Tools to clean meshes, detect issues, and speed up UV preparation.
- **Select Edges by Angle** – find edges based on normal differences (customizable threshold).
- **Select Contour Edges** – create contour loops from selected faces.
- **Tag/Clear Seam & Sharp** – quickly assign or remove seams and sharp edges.
- **Clear Split Normals** – remove custom split normals.
- **Add Modifiers** – add Triangulate and Weighted Normal modifiers in one click.
- **Detect Ngons** – locate n-gons (across selected, visible, or all meshes).

### Baking Supply
Automates high/low mesh naming, organization, and export.
- **Renaming** – batch rename with sequential numbering.
- **Suffix Management** – add `_high` or `_low`, swap suffixes, or transfer names.
- **Visibility Controls** – hide/show all high or low meshes.
- **Export to FBX** – export selected `_high` or `_low` meshes with proper naming and folder options.

### Marmoset Bridge
Direct integration with Marmoset Toolbag for baking.
- **Export & Launch** – send selected meshes to Toolbag and launch with bake setup.
- **Direct Bake** – optional quick bake execution from Blender.
- **Bake Settings** – resolution, samples, pixel depth, file format, tile mode, and max offset.
- **Map Settings** – per-map controls for Normals, AO, Curvature, Height, Position, Thickness, etc.
- **Presets** – save and reuse common bake setups.

---

## 📂 Panels

After enabling the add-on, you’ll find a new **BakeFlow** category in the `N` sidebar of the 3D View:

- **UV Helper** – mesh/UV preparation tools
- **Baking Supply** – naming, suffix, export options
- **Marmoset Bridge** – bake configuration and Toolbag launcher

---

## ⚙️ Installation

1. Download the `.zip` of the add-on.
2. In Blender, open **Edit → Preferences → Add-ons → Install…**
3. Select the `.zip` file and enable **BakeFlow**.
4. Panels will appear in the `N` sidebar under **BakeFlow**.

---

## 🔧 Properties

### UV Helper
- **Angle Threshold** – minimum angle to detect edges (default 30°).
- **Ngon Detection Range** – scan scope (Selected / Visible / All).

### Baking Supply
- **Export Path** – folder to export FBX files.
- **Name** – base name for exports.
- **Rename Name** – new base name for batch renaming.

### Marmoset Bridge
- **Direct Bake** – toggle to trigger bake immediately.
- **Send Properties / Map Settings** – decide what is sent to Toolbag.
- **Resolution (X/Y)** – bake output size.
- **Pixel Depth** – 8/16/32-bit.
- **File Format** – PNG, JPG, TGA, or PSD.
- **Normal Orientation** – OpenGL or DirectX.
- **Override Max Offset** – manual max ray offset.

---

## 🚀 Typical Workflow

1. **Prepare Meshes** with UV Helper
    - Detect ngons, mark seams, clear split normals, apply modifiers.

2. **Organize & Export** with Baking Supply
    - Rename and suffix meshes, show/hide high/low, export FBX files.

3. **Bake in Toolbag** with Marmoset Bridge
    - Export to Toolbag, configure map settings, bake directly, and pull results.

---

## 👤 Author

**BakeFlow** by **Tarmunds**  
Community & support: [Discord](https://discord.gg/h39W5s5ZbQ)

---

## 📝 License

Distributed under the same license as the repository. Please check the repo for details.

