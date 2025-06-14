# Copyright (c) 2025 mugi
import bpy

from bpy.types import Panel, UIList
from bpy.props import *

translat = bpy.app.translations


class OBJECT_OT_remove_tiny_shape_keys(bpy.types.Operator):
    bl_idname = "object.fix_tiny_shape_keys_all"
    bl_label = "Remove Tiny Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    threshold: bpy.props.FloatProperty(name="Threshold",default=0.0001,min=0.0,max = 0.01,step = 1,
                                       description="Threshold" )



    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT'           : # objectモードで実行させるのでモード確認
            for slctobj in bpy.context.selected_objects:
                if slctobj.type in {'MESH'}:        #　選択オブジェクトにメッシュがあるか？
                            return True
        else:
            return False


    # クラス内関数：シェイプキーが微小か判定

    def execute(self, context):
        total_modified_vertices = 0
        affected_shape_keys = 0
        selected_objects = context.selected_objects

        for obj in selected_objects:
            if obj.type != 'MESH':
                continue

            shape_keys = obj.data.shape_keys
            if not shape_keys:
                continue

            basis = shape_keys.key_blocks.get("Basis")
            if not basis:
                continue

            for key_block in shape_keys.key_blocks:
                if key_block.name == "Basis":
                    continue

                modified_this_key = False

                for i, vert in enumerate(key_block.data):
                    delta = (vert.co - basis.data[i].co).length
                    if delta < self.threshold:
                        vert.co = basis.data[i].co
                        total_modified_vertices += 1
                        modified_this_key = True

                if modified_this_key:
                    affected_shape_keys += 1

        self.report(
            {'INFO'},
            f"Corrected {total_modified_vertices} vertices in {affected_shape_keys} shape key(s)"
        )
        return {'FINISHED'}

    def invoke(self, context, event):# ポップアップ表示
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.use_property_split = True
        row.prop(self, "threshold")

        

class VIEW3D_PT_CustomPanel_mugi_tiny_shape_key(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "mugiTOOLS"          # パネルを登録するタブ名
    bl_label = "tiny_shape_key_DELL"       # パネルのヘッダに表示される文字列
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
        # row = 横並び : col = 縦並び : box = 囲む : split :分割
        layout = self.layout
        row = layout.split(align=True)
        row.label(text = "tiny_shape_key_DELL")
        row.operator(OBJECT_OT_remove_tiny_shape_keys.bl_idname, text = translat.pgettext("tiny_shape_key_DELL"))