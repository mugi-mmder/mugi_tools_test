# Copyright (c) 2022 mugi
import bpy

from bpy.types import Panel, UIList
from bpy.props import *

translat = bpy.app.translations


class MESH_OT_change_vtxslct_shapekey(bpy.types.Operator):
    bl_idname = "object.change_vtxselect_shapekey"
    bl_label = "change_vtxselect_shapekey"
    bl_description = "編集モードで選択ｼｪｲﾌﾟｷｰの変更頂点選択"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'EDIT_MESH':                               # EDITモードで実行させるのでモード確認
            if bpy.context.active_object.data.shape_keys != None:         # ｼｪｲﾌﾟｷｰが0じゃない
                if bpy.context.active_object.active_shape_key_index != 0: # index=0は基準になるので動作させない               
                     return True
        else:
            return False

    def execute(self, context):
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')  # 選択モードを頂点に
        act_obj   = bpy.context.active_object
        act_obj_d = bpy.context.active_object.data

        # if act_obj_d.shape_keys == None:
        #    return {'CANCELLED'}
        # shpk_base = bpy.context.active_object.data.shape_keys.key_blocks[0]


        vlist = []          # 頂点リスト
        nonlist =[]         # はじいたリスト
        
        shpk_base = bpy.context.object.active_shape_key.relative_key.data # 基準対象ｼｪｲﾌﾟｷｰ(基本はbasisのはず)
        shpk_act  = bpy.context.object.active_shape_key.data              # 選択中のｼｪｲﾌﾟｷｰ

        for base_s, act_s in zip(shpk_base, shpk_act):
            print(base_s.co == act_s.co)
            # print(base_s.co,"---",act_s.co)
            if base_s.co != act_s.co:                                      # シェイプキーで変わった頂点検出
                vlist.append(base_s.co)                                    # 変更頂点リスト化    
            else:
                nonlist.append(base_s.co)                                  # はじいた頂点リスト化  
                
        # print(len(vlist),"\n",vlist)
        bpy.ops.mesh.select_all(action='DESELECT')                         # 頂点選択全解除
 
        bpy.ops.object.mode_set(mode='OBJECT', toggle = False)             # EDITmodeじゃ上手くいかないのでOBJECTmodeに
        for vtx in act_obj_d.vertices:                                     # 変更頂点リスト化にある頂点を選択
            if vtx.co in vlist:                                            # 変更前基準の座標位置で検索 
                vtx.select = True
        bpy.ops.object.mode_set(mode='EDIT', toggle = False)               # EDITmodeに戻す

        return{'FINISHED'}

class VIEW3D_PT_CustomPanel_mugi_change_vtx4skey(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "mugiTOOLS"          # パネルを登録するタブ名
    bl_label = "change_vtx4skey_select"       # パネルのヘッダに表示される文字列
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
        # row = 横並び : col = 縦並び : box = 囲む : split :分割
        layout = self.layout
        row = layout.split(align=True)
        row.label(text = "change_vertex_selection")
        row.operator(MESH_OT_change_vtxslct_shapekey.bl_idname, text = translat.pgettext("change_vertex_selection"))