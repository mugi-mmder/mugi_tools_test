# Copyright (c) 2022 mugi
import bpy
from bpy.props import *
from .OBJECT_OT_vertex_groups_weight import OBJECT_OT_vertex_groups_weight_round_the_weight,VIEW3D_PT_CustomPanel_mugi
from .VIEW3D_PT_CustomPanel import VIEW3D_PT_3D_cursor_Panel_mugi,OBJECT_OT_cursor_to_XlocZero
from .TEXTURE_OT_BRUSH import TEXTURE_OT_BRUSHSize,TEXTURE_OT_BRUSHSize_Ajust,TEXTURE_PT_BrushPanel_mugi
from .mmd_cm_trans import Prop_mmd_cm_trans_setting,OBJECT_OT_mmd_cm_trans_maxmin,VIEW3D_PT__mmd_cm_trans_mugi
from .MESH_OT_change_vtxselect_shapekey import MESH_OT_change_vtxslct_shapekey,VIEW3D_PT_CustomPanel_mugi_change_vtx4skey


bl_info = {
    "name": "test mugiTOOLs",
    "author": "mugi",
    "version": (1, 0),
    "blender": (3, 1, 0),
    "location": "VIEW3D > Sidebar",
    "description": "実験用のむぎの遊び場.",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "User Interface"
}

classes = (
    # コレクションクラスのインポートの順番に注意
    OBJECT_OT_vertex_groups_weight_round_the_weight,
    VIEW3D_PT_CustomPanel_mugi,

    VIEW3D_PT_3D_cursor_Panel_mugi,
    OBJECT_OT_cursor_to_XlocZero,

    TEXTURE_OT_BRUSHSize,
    TEXTURE_OT_BRUSHSize_Ajust,
    TEXTURE_PT_BrushPanel_mugi,

    Prop_mmd_cm_trans_setting,
    OBJECT_OT_mmd_cm_trans_maxmin,
    VIEW3D_PT__mmd_cm_trans_mugi,

    MESH_OT_change_vtxslct_shapekey,
    VIEW3D_PT_CustomPanel_mugi_change_vtx4skey,

     )

# 翻訳用辞書
translation_dict = {
    "ja_JP" :
        {#OBJECT_OT_vertex_groups_weight
         ("*", "round_the_weight") : "ウェイトを丸める",
         ("*", "clean_weights") : "値以下のｳｪｲﾄ削除",
         ("*", "Round_weights_of_selected_objects") : "選択オブジェクトのウェイト丸め＆正規化",
         #VIEW3D_PT_CustomPanel
         ("*", "3D_cursor_Item") : "3Dカーソル(アイテム欄用)",
         ("*", "cursor_to_selected") : "3Dカーソル→選択物",
         ("*", "selected_to_cursor") : "選択物→3Dカーソル",
         ("*", "cursor_to_center") : "3Dカーソル→原点",
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
