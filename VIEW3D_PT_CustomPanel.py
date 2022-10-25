# Copyright (c) 2022 mugi
import bpy

from bpy.types import Panel, UIList
from bpy.props import *

translat = bpy.app.translations

class OBJECT_OT_cursor_to_XlocZero(bpy.types.Operator):
    bl_idname = "object.cursor_to_xloczero"
    bl_label = "cursor_to_X_loc=0."
    bl_description = "3DカーソルのX位置を0に"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context


    def execute(self, context):
        bpy.context.scene.cursor.location[0] = 0
        return {'FINISHED'}


class VIEW3D_PT_3D_cursor_Panel_mugi(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "Item"               # パネルを登録するタブ名
    bl_label = "3D_cursor_Item"             # パネルのヘッダに表示される文字列
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
        # row = 横並び : col = 縦並び : box = 囲む : split :分割
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text = "cursor<->selected",icon = "ARROW_LEFTRIGHT")
        box = layout.box()
        box_col = box.column(align=True)
        box_row = box_col.row(align=True)
        box_row.operator("view3d.snap_cursor_to_selected", text = translat.pgettext("cursor_to_selected"), icon = "SNAP_VOLUME")
        box_row.separator()
        box_row.operator("view3d.snap_selected_to_cursor", text = translat.pgettext("selected_to_cursor"), icon = "ORIENTATION_CURSOR")
        box_col = box.column(align=True)
        box_row = box_col.row(align=True)
        box_row.operator("view3d.snap_cursor_to_center", text = translat.pgettext("cursor_to_center"), icon = "ORIENTATION_GLOBAL")
        box_row.separator()
        box_row.operator(OBJECT_OT_cursor_to_XlocZero.bl_idname, text = "X = 0", icon = "CENTER_ONLY")
