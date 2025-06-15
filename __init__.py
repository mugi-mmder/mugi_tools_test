# Copyright (c) 2022 mugi
import bpy
from bpy.props import *

import os
import urllib.request
import zipfile
import shutil
from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty

from .OBJECT_OT_vertex_groups_weight import OBJECT_OT_vertex_groups_weight_round_the_weight,VIEW3D_PT_CustomPanel_mugi
from .VIEW3D_PT_CustomPanel import VIEW3D_PT_3D_cursor_Panel_mugi,OBJECT_OT_cursor_to_XlocZero,OBJECT_OT_PoseReset_OBJmode
from .TEXTURE_OT_BRUSH import TEXTURE_OT_BRUSHSize,TEXTURE_OT_BRUSHSize_Ajust,TEXTURE_PT_BrushPanel_mugi
from .mmd_cm_trans import Prop_mmd_cm_trans_setting,OBJECT_OT_mmd_cm_trans_maxmin,VIEW3D_PT__mmd_cm_trans_mugi
from .MESH_OT_change_vtxselect_shapekey import MESH_OT_change_vtxslct_shapekey,VIEW3D_PT_CustomPanel_mugi_change_vtx4skey
from .OBJECT_OT_vertex_groups_remove0 import OBJECT_OT_vertex_groups_weightZero_remove,VIEW3D_PT_CustomPanel_mugi_weightZero_remove
from .OBJECT_OT_shape_keys_tiny_DEL import OBJECT_OT_remove_tiny_shape_keys,OBJECT_OT_clean_and_fix_mirror_X0,\
                                            VIEW3D_PT_CustomPanel_mugi_tiny_shape_key

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





# GitHubリポジトリのZIP URL（mainブランチ）
GITHUB_ZIP_URL = "https://github.com/mugi-mmder/mugi_tools_test/archive/refs/heads/main.zip"
ADDON_FOLDER_NAME = "mugi_tools_test-main"

# モジュールのインポート（必要なモジュールを追記）
from . import VIEW3D_PT_CustomPanel
from . import OBJECT_OT_vertex_groups_weight

# -------------------- 更新処理 --------------------

class MUGI_OT_UpdateAddon(Operator):
    bl_idname = "mugi.update_addon"
    bl_label = "アドオンを更新"
    bl_description = "GitHubから最新版をダウンロードして上書きします"
    
    def execute(self, context):
        addon_path = bpy.utils.user_resource('SCRIPTS') + "/addons"
        zip_path = os.path.join(addon_path, "mugi_tools_latest.zip")

        try:
            # ZIPをダウンロード
            urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)

            # 一時展開フォルダ
            temp_dir = os.path.join(addon_path, "temp_mugi")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            # 解凍
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # 古いアドオン削除
            old_addon = os.path.join(addon_path, ADDON_FOLDER_NAME)
            if os.path.exists(old_addon):
                shutil.rmtree(old_addon)

            # 解凍したアドオンを移動
            extracted_folder = os.path.join(temp_dir, ADDON_FOLDER_NAME)
            shutil.move(extracted_folder, old_addon)

            # 後片付け
            os.remove(zip_path)
            shutil.rmtree(temp_dir)

            self.report({'INFO'}, "更新完了しました。再起動してください。")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"更新失敗: {str(e)}")
            return {'CANCELLED'}

# -------------------- プリファレンス --------------------

class MUGI_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.label(text="GitHubからアドオンを自動更新できます。")
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

    OBJECT_OT_remove_tiny_shape_keys,
    OBJECT_OT_clean_and_fix_mirror_X0,
    VIEW3D_PT_CustomPanel_mugi_tiny_shape_key,


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
         #OBJECT_OT_shape_keys_tiny_DEL
         ("*", "Finishing Shape Keys") : "ｼｪｲﾌﾟｷｰ仕上げ機能",
         ("*", "tiny_shape_key_DELL") : "微小移動ｼｪｲﾌﾟｷｰ頂点削除",
         ("*", "shape_key_X0") : "X=0強制",
         

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
