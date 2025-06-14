# Copyright (c) 2022 mugi
import bpy

from bpy.types import Panel, UIList
from bpy.props import *

from bl_ui.space_view3d_toolbar import View3DPaintPanel


class TEXTURE_OT_BRUSHSize(bpy.types.Operator):
    bl_idname = "tool_settings.brush_size_select"
    bl_label = "text"
    bl_options = {'REGISTER', 'UNDO'}

    size: IntProperty(default = 1, min = 1, max = 100, name = "size")


    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'PAINT_TEXTURE': #Texture Paintモードで実行させるのでモード確認
            return True
        return False
        
    def execute(self, context):
        test = self.size
        print(test)
        bpy.context.scene.tool_settings.unified_paint_settings.size = self.size

        return{'FINISHED'}

class TEXTURE_OT_BRUSHSize_Ajust(bpy.types.Operator):
    bl_idname = "tool_settings.brush_size_ajust"
    bl_label = "text"
    bl_options = {'REGISTER', 'UNDO'}

    ajsize: IntProperty(default = 1, min = -5, max = 5,  name = "size")

    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'PAINT_TEXTURE': #Texture Paintモードで実行させるのでモード確認
            return True
        return False
        
    def execute(self, context):
        bpy.context.scene.tool_settings.unified_paint_settings.size += self.ajsize
        return{'FINISHED'}


class TEXTURE_PT_BrushPanel_mugi(View3DPaintPanel,Panel):
    bl_context = "imagepaint"  
    bl_label = "Unified_Brush_setting"
    bl_options = {'DEFAULT_CLOSED'}
    """
    bl_label = "Brushes_Size"             # パネルのヘッダに表示される文字列
    bl_space_type = "PROPERTIES"          # パネルを登録するスペース
    bl_region_type = "WINDOW"              # パネルを登録するリージョン
    bl_category = "Brushes_Size"               # パネルを登録するタブ名
    """


    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'PAINT_TEXTURE': #Texture Paintモードで実行させるのでモード確認
            return True
        return False
    def draw(self, context):
        # row = 横並び : col = 縦並び : box = 囲む : split :分割
        layout = self.layout
        layout.label(text = "Unified_Brush_size")
        
        row = layout.row(align=True)
        
        size_bool = bpy.context.scene.tool_settings.unified_paint_settings.size # 現在のブラシサイズ取得
        
        b_set = bpy.context.scene.tool_settings.unified_paint_settings

        #depressはUILayout.operator()の引数
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "1", depress=(size_bool == 1)).size = 1
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text =" 3", depress=(size_bool == 3)).size = 3
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "5", depress=(size_bool == 5)).size = 5
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "7", depress=(size_bool == 7)).size = 7
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "10", depress=(size_bool == 10)).size = 10
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "12", depress=(size_bool == 12)).size = 12
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "15", depress=(size_bool == 15)).size = 15
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "20", depress=(size_bool == 20)).size = 20
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "25", depress=(size_bool == 25)).size = 25
        row.operator(TEXTURE_OT_BRUSHSize.bl_idname, text = "30", depress=(size_bool == 30)).size = 30

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator(TEXTURE_OT_BRUSHSize_Ajust.bl_idname, text="+1",).ajsize = (1)
        row.operator(TEXTURE_OT_BRUSHSize_Ajust.bl_idname, text="-1",).ajsize = (-1)
        
        col.prop(b_set,"size",text = "Brush_size",slider = True)
        row = col.row(align=True)
        row.label(text = "Unified_Brush_strength")
        col.prop(b_set,"strength",text = "Brush_strength",slider = True)

