# Copyright (c) 2023 mugi
import bpy

from bpy.types import Panel, UIList
from bpy.props import *


translat = bpy.app.translations

class OBJECT_OT_vertex_groups_weightZero_remove(bpy.types.Operator):
    bl_idname = "object.vg_weightzero_remove"
    bl_label = "vg_weightzero_remove."
    bl_description = "ウェイトがのってない頂点グループ削除"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT'           : # objectモードで実行させるのでモード確認
            for slctobj in bpy.context.selected_objects:
                if slctobj.type in {'MESH'}:        #　選択オブジェクトにメッシュがあるか？
                    if slctobj.parent != None:      #　ペアレントがあるか？ウェイトボーンチェック前の簡易チェック
                            return True
        else:
            return False
        
    def execute(self, context):    #複数メッシュオブジェクト対応したかったが、エラー回避方法ができずに断念・・・単独のみ対応でお茶濁し
        
        act_obj = bpy.context.active_object
        slct_obj = bpy.context.selected_objects
        #print(slct_obj)
        
        slctobjlist = []    # 選択オブジェクトリスト
        nonlist =[]         # はじいたオブジェクトリスト

        modilist  = []      # モディのリスト
        modi_typelist  = [] # モディのタイプリスト

        remlist =[]         # 削除リスト
        remlis_name =[]     # 削除リスト(名称)
        LRlist =[]          # 左右checkリスト

        for modilist in act_obj.modifiers:
              #print(slctobjlist.type)
              modi_typelist.append(modilist.type)
        print("-------モディ--------\n",modi_typelist ,"ARMATURE"  in modi_typelist) 
        if not ("ARMATURE"  in modi_typelist):
            self.report({'ERROR'}, "not_ARMATURE_Modifier!!!") 
            print("not ARMATURE Modifier!!!")
            return {'CANCELLED'}

        for slctobj in bpy.context.selected_objects:
            if slctobj.type in {'MESH'}:                                        #　選択オブジェクトからメッシュを取り出してリスト化
                if len(slctobj.vertex_groups) != 0 and slctobj.parent != None and\
                    'ARMATURE'  in slctobj.parent.type:                         #　頂点グループがあるか,ペアレントがあるかチェック 
                        prt_bones = [b.name for b in slctobj.parent.pose.bones] #　アーマチュアからボーンリスト作成 
                        vtx_groups =[v.name for v in slctobj.vertex_groups]     #　オブジェクトから頂点グループリスト作成 
                        if len(set(prt_bones) & set(vtx_groups)) != 0:          #　ウェイトボーンがあるかチェック 
                            slctobjlist.append(slctobj)
                        else:
                            nonlist.append(slctobj)           
                else:
                    nonlist.append(slctobj)
            else:
                nonlist.append(slctobj)
        if  len(slctobjlist) == 1:
            print("========  slctobjlist  ==========\n", slctobjlist ,"\n----------------------\n")
            print("========  nonlist  ==========\n", nonlist ,"\n----------------------\n")

            for listobj in slctobjlist:                                   # リストから一個ずつメッシュオブジェクトの取り出し
                print("----実行OBJ--------->",listobj.name)
                print("vertex_groups--->",listobj.vertex_groups)
                bpy.context.view_layer.objects.active = listobj           # リストから一個ずつメッシュオブジェクトを選択
                # print("remlist check 1---",remlist)

                for vg in listobj.vertex_groups:                          # 選択オブジェクトから一個ずつ頂点グループを取得
                    remlis_name.append(vg.name)                           # メッシュに含まれる頂点グループ(名称)
                    remlist.append(vg)                                    # メッシュに含まれる頂点グループ

                for vg in listobj.vertex_groups:                          # 選択オブジェクトから一個ずつ頂点グループを取得
                    print("vg.name===    ",vg.name)

                    for vtx in listobj.data.vertices:                     # 選択オブジェクトから頂点取得
                        try:                                              # ウェイト0を拾うとエラー？なんかランタイムエラーでるんで利用
                            print("vg----",vg," ===weight(vert.index)----",vg.weight(vtx.index))

                            if vg.name.endswith((".L" , "-L" , "_L" )):   # 左右判定がある場合、一旦保留
                                LRlist.append(vg.name[0:-2])              #
                                print(vg.name,"   ==左右判定===    L")
                                
                            elif vg.name.endswith((".R" , "-R" , "_R" )): # 左右判定がある場合、一旦保留
                                LRlist.append(vg.name[0:-2])              
                                print(vg.name,"   ==左右判定===    R")
                            else:
                                print(vg.name,"   ==左右判定なし")

                            remlis_name.remove(vg.name)                    # ウェイトが0以外なら削除リストから除外
                            remlist.remove(vg)
                            print("break")
                            break                                          # ウェイト0以外が一個でもプリント処理が走るんで処理停止

                        except RuntimeError:                               # ランタイムエラーでたらウェイトが0っぽいのでパス
                            pass
                    else:                                                  # 正常終了時の処理
                        print("   ===",vg.name,"はウェイト0===")
                    
                for vgLR in remlist:
                    if vgLR.name[0:-2] in LRlist:                          #　左右判定checkに引っかかった頂点グループは左右とも削除リストから除外
                        remlist.remove(vgLR)
                infoVG = len(remlist)
                if infoVG > 0:
                    for remVG in remlist:                                  #　残った頂点グループを削除
                            print("  ",remVG.name,"を削除")
                            act_obj.vertex_groups.remove(remVG)
                else:
                    print("頂点グループの削除なし")
                    self.report({'INFO'}, "頂点グループの削除なし") 
                    return {'FINISHED'}


                remlist.clear()     
                remlis_name.clear()  
                LRlist.clear()


        else:
            self.report({'ERROR'}, "メッシュオブジェクトを1つだけ選択してね!!!") 
            return {'CANCELLED'}

        self.report({'INFO'}, f"{infoVG}個の頂点グループを削除") 
        return {'FINISHED'}


class VIEW3D_PT_CustomPanel_mugi_weightZero_remove(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "mugiTOOLS"               # パネルを登録するタブ名
    bl_label = "weightZero_remove"             # パネルのヘッダに表示される文字列
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
        # row = 横並び : col = 縦並び : box = 囲む : split :分割
        layout = self.layout
        row = layout.split(align=True)
        row.label(text = "weightZero_remove")
        row.operator(OBJECT_OT_vertex_groups_weightZero_remove.bl_idname, text = translat.pgettext("weightZero_remove"))
