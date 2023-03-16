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

class OBJECT_OT_PoseReset_OBJmode(bpy.types.Operator):
    bl_idname = "object.pose_reset_objmode"
    bl_label = "pose_reset_objmode"
    bl_description = "あちこちでポーズリセット"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT':            # objectモードで実行させるのでモード確認
            if (bpy.context.active_object.type == 'ARMATURE'):
                    return True


    def execute(self, context):
        bpy.ops.object.mode_set(mode='POSE', toggle = False)    # POSEモードにしてポーズリセット
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle = False)  # OBJECTmodeに戻す

        return {'FINISHED'}






class VIEW3D_PT_3D_cursor_Panel_mugi(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "Item"               # パネルを登録するタブ名
    bl_label = "little＿shortcut"             # パネルのヘッダに表示される文字列
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

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text = "Pose_Reset2Item",icon = "OUTLINER_OB_ARMATURE")
        row = col.row(align=True)
        row.operator("pose.transforms_clear", text = translat.pgettext("select_bone_Pose_Reset"), icon = "OUTLINER_OB_ARMATURE")
        row = col.row(align=True)
        row.operator(OBJECT_OT_PoseReset_OBJmode.bl_idname, text = translat.pgettext("Pose_Reset_OBJmode"), icon = "OUTLINER_OB_ARMATURE")


