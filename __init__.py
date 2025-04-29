# Copyright (c) 2022 mugi
import bpy
from bpy.props import *

import urllib.request
import os
import zipfile
import shutil


from .OBJECT_OT_vertex_groups_weight import OBJECT_OT_vertex_groups_weight_round_the_weight,VIEW3D_PT_CustomPanel_mugi
from .VIEW3D_PT_CustomPanel import VIEW3D_PT_3D_cursor_Panel_mugi,OBJECT_OT_cursor_to_XlocZero,OBJECT_OT_PoseReset_OBJmode
from .TEXTURE_OT_BRUSH import TEXTURE_OT_BRUSHSize,TEXTURE_OT_BRUSHSize_Ajust,TEXTURE_PT_BrushPanel_mugi
from .mmd_cm_trans import Prop_mmd_cm_trans_setting,OBJECT_OT_mmd_cm_trans_maxmin,VIEW3D_PT__mmd_cm_trans_mugi
from .MESH_OT_change_vtxselect_shapekey import MESH_OT_change_vtxslct_shapekey,VIEW3D_PT_CustomPanel_mugi_change_vtx4skey
from .OBJECT_OT_vertex_groups_remove0 import OBJECT_OT_vertex_groups_weightZero_remove,VIEW3D_PT_CustomPanel_mugi_weightZero_remove

bl_info = {
    "name": "test mugiTOOLs",
    "author": "mugi",
    "version": (1, 1),
    "blender": (3, 1, 0),
    "location": "VIEW3D > Sidebar",
    "description": "実験用のむぎの遊び場.",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "User Interface"
}




class MUGI_OT_UpdateAddon(bpy.types.Operator):
    bl_idname = "mugi.update_addon"
    bl_label = "Mugi Tools を更新"
    bl_description = "GitHub から最新版をダウンロードして更新します"

    def execute(self, context):
        url = "https://github.com/mugi-mmder/mugi_tools_test/archive/refs/heads/main.zip"
        addon_folder = os.path.join(bpy.utils.user_resource('SCRIPTS'), "addons")
        zip_path = os.path.join(addon_folder, "mugi_tools_test_update.zip")

        try:
            self.report({'INFO'}, "アドオンをダウンロード中...")
            urllib.request.urlretrieve(url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(addon_folder)

            old_path = os.path.join(addon_folder, "mugi_tools_test")
            if os.path.exists(old_path):
                shutil.rmtree(old_path)

            extracted_path = os.path.join(addon_folder, "mugi_tools_test-main")
            os.rename(extracted_path, old_path)

            os.remove(zip_path)
            self.report({'INFO'}, "更新完了！Blenderを再起動してください。")
        except Exception as e:
            self.report({'ERROR'}, f"更新に失敗しました: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


class MUGI_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Mugi Tools アップデーター")
        layout.operator("mugi.update_addon", icon="FILE_REFRESH")



classes = (
    # コレクションクラスのインポートの順番に注意
    OBJECT_OT_vertex_groups_weight_round_the_weight,
    VIEW3D_PT_CustomPanel_mugi,

    VIEW3D_PT_3D_cursor_Panel_mugi,
    OBJECT_OT_cursor_to_XlocZero,
    OBJECT_OT_PoseReset_OBJmode,

    TEXTURE_OT_BRUSHSize,
    TEXTURE_OT_BRUSHSize_Ajust,
    TEXTURE_PT_BrushPanel_mugi,

    Prop_mmd_cm_trans_setting,
    OBJECT_OT_mmd_cm_trans_maxmin,
    VIEW3D_PT__mmd_cm_trans_mugi,

    MESH_OT_change_vtxslct_shapekey,
    VIEW3D_PT_CustomPanel_mugi_change_vtx4skey,

    OBJECT_OT_vertex_groups_weightZero_remove,
    VIEW3D_PT_CustomPanel_mugi_weightZero_remove,
    MUGI_OT_UpdateAddon,
    MUGI_AddonPreferences,

     )

# 翻訳用辞書
translation_dict = {
    "ja_JP" :
        {#OBJECT_OT_vertex_groups_weight
         ("*", "round_the_weight") : "ウェイトを丸める",
         ("*", "clean_weights") : "値以下のｳｪｲﾄ削除",
         ("*", "Round_weights_of_selected_objects") : "選択オブジェクトのウェイト丸め＆正規化",
         #VIEW3D_PT_CustomPanel
         ("*", "little＿shortcut") : "ちょっとしたショトカ",
         ("*", "cursor_to_selected") : "3Dカーソル→選択物",
         ("*", "selected_to_cursor") : "選択物→3Dカーソル",
         ("*", "cursor_to_center") : "3Dカーソル→原点",
         ("*", "Pose_Reset2Item") : "ポーズリセット(アイテム欄用)",
         ("*", "select_bone_Pose_Reset") : "選択ボーンのポーズリセット",
         ("*", "Pose_Reset_OBJmode") : "ポーズリセット(OBJモード用)",
         #TEXTURE_PT_BrushPanel
         ("*", "Unified_Brush_setting") : "共通ペイントブラシ設定",
         ("*", "Unified_Brush_size") : "共通ブラシサイズ",
         ("*", "Unified_Brush_strength") : "共通ブラシ強さ",
         ("*", "Brush_size") : "ブラシサイズ",
         ("*", "Brush_strength") : "ブラシ強さ",
         #mmd_cm_trans
         ("*", "Ajust_Flags(cm)") : "調整(cm)",
         ("*", "Adj_amount") : "調整量",
         ("*", "MMD_unit_conversion") : "MMD(cm)単位換算",
         ("*", "OBJ_TOP") : "一番高いとこ",
         ("*", "OBJ_BOTTOM") : "一番低いとこ",
         ("*", "DifferenceH/L") : "高低差",
         ("*", "Difference-ajust") : "高低差 - (調整)",
         ("*", "Calculation!") : "計算！",
         #MESH_OT_change_vtxselect_shapekey
         ("*", "change_vtx4skey_select") : "選択ｼｪｲﾌﾟｷｰの変更頂点選択",
         ("*", "change_vertex_selection") : "変更頂点選択",
         #OBJECT_OT_vertex_groups_weight0_remove
         ("*", "weightZero_remove") : "ウェイトなし頂点ｸﾞﾙｰﾌﾟ削除",
        },
}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.translations.register(__name__, translation_dict)   # 辞書の登録
    bpy.types.Scene.cm_props_setting = bpy.props.PointerProperty(type=Prop_mmd_cm_trans_setting) # mmd_cm_trans



def unregister():
    del bpy.types.Scene.cm_props_setting        # mmd_cm_trans
    bpy.app.translations.unregister(__name__)   # 辞書の削除
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
