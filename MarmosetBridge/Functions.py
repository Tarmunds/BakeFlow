import bpy

def GoToLine(layout, *, scale_y=1.2, align=True):
    row = layout.row(align=align)
    row.scale_y = scale_y
    return row

def _sync_res_y(self, context):
    # self is the PropertyGroup instance
    self.ResolutionY = self.ResolutionX