# Copyright (c) 2022 mugi
import bpy

from bpy.types import Panel, UIList
from bpy.props import *
import bmesh
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

translat = bpy.app.translations


class OBJECT_OT_vertex_groups_weight_round_the_weight(bpy.types.Operator):
    bl_idname = "object.vertex_groups_round_the_weight_mugitest"
    bl_label = "round_the_weight"
    bl_description = "選択メッシュオブジェクトのウェイトの0.01以下を丸めて正規化"
    bl_options = {'REGISTER', 'UNDO'}

    limit : FloatProperty(default = 0.01,min = 0.0,max = 1.0,step = 1,
                          name = "clean_weights",
                          description = "clean vertex_group weights")



    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT'           : # objectモードで実行させるのでモード確認
            for slctobj in bpy.context.selected_objects:
                if slctobj.type in {'MESH'}:        #　選択オブジェクトにメッシュがあるか？
                    if slctobj.parent != None:      #　ペアレントがあるか？ウェイトボーンチェック前の簡易チェック
                            return True
        else:
            return False

    def execute(self, context):
        obj = bpy.context.active_object
        slct_obj = bpy.context.selected_objects
        #print(slct_obj)
        
        slctobjlist = []    # ウェイトいじるリスト
        nonlist =[]         # はじいたオブジェクトリスト

        for slctobj in bpy.context.selected_objects:
            if slctobj.type in {'MESH'}:                                #　選択オブジェクトからメッシュを取り出してリスト化
                if len(slctobj.vertex_groups) != 0 and slctobj.parent != None and\
                    'ARMATURE'  in slctobj.parent.type:                 #　頂点グループがあるか,ペアレントがあるかチェック 
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
        if  not len(slctobjlist) == 0:
            print("========  slctobjlist  ==========\n", slctobjlist ,"\n----------------------\n")
            print("========  nonlist  ==========\n", nonlist ,"\n----------------------\n")
            self.report({'INFO'}, "Round_weights_of_selected_objects") 

            for listobj in slctobjlist:    #　リストから一個ずつメッシュオブジェクトの取り出し
                # print("listobj--->",listobj)
                print("test--->",listobj.name)
                bpy.context.view_layer.objects.active = listobj     #　リストから一個ずつメッシュオブジェクトを選択

                has_armature = any(mod.type == 'ARMATURE' for mod in obj.modifiers)
                if not has_armature:
                    self.report({'INFO'}, "アーマチュアモディファイアが付いていません")
                    return {'CANCELLED'}
                

                bpy.ops.object.mode_set(mode='EDIT', toggle = False)  #　EDITmodeにはいって全頂点選択
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT', toggle = False)

 

                #ごみｳｪｲﾄｸﾘｰﾝ -> ｳｪｲﾄ数4制限 -> 再度ｸﾘｰﾝ -> 変形ｳｪｲﾄのみ正規化 -> 0.01単位で量子化 -> 再度正規化(微小端数) -> 0.01単位で量子化

                bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM',                  # 指定値以下の変形ウェイトをクリーン
                                                    limit = self.limit, keep_single=True)
                bpy.ops.object.vertex_group_limit_total(group_select_mode='BONE_DEFORM', limit = 4)   # 変形ウェイトを4つに制限
                bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM',                  # 指定値以下の変形ウェイトをクリーン
                                                    limit = self.limit, keep_single=True)             
                bpy.ops.object.vertex_group_quantize(group_select_mode='BONE_DEFORM', steps = 100)    # 0.01単位で量子化
                bpy.ops.object.vertex_group_normalize_all(group_select_mode='BONE_DEFORM',
                                                                lock_active=False)  # 変形ウェイトの正規化,ｱｸﾃｨﾌﾞﾛｯｸは掛けない
                bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM',                  # 一回目で端数がでる場合があるので二回目突入
                                                    limit = self.limit, keep_single=True)
                bpy.ops.object.vertex_group_quantize(group_select_mode='BONE_DEFORM', steps = 100)    # 正規化時に微小端数がでるのを利用して整える

               # ～～～↓↓↓↓～～たまに処理できない頂点がでたので手動で一回丸める～～～↓↓↓↓～～ #
                ctrl_bmsh = bmesh.new()
                ctrl_bmsh.from_mesh(obj.data)
                bm_Df_Lay = ctrl_bmsh.verts.layers.deform.active 
                print("bm_Df_Lay---->",bm_Df_Lay)

                if not bm_Df_Lay:
                    print("not bm_Df_Lay!!!")
                    return {'CANCELLED'}

                for vm_vert in ctrl_bmsh.verts:   # 選択中のアクティブオブジェクトの頂点ウェイト（変形）取得する
                        # print("=====================" , vm_vert.index , "=======================")
                        # print("vm_vert---->",vm_vert)
                        # print("vm_vert[bm_Df_Lay].items()---->","len=",len(vm_vert[bm_Df_Lay].items()),"bm_Df_Lay:",bm_Df_Lay,"item:",vm_vert[bm_Df_Lay].items())
                        i = 0
                        for v_ind, v_wieht in vm_vert[bm_Df_Lay].items():   
                            # print("v_ind---->",v_ind,"    v_wieht---->",v_wieht)      
                            if obj.vertex_groups[v_ind].name in prt_bones:                # 選択中の頂点ウェイト（変形）取得する
                                # print(obj.vertex_groups[v_ind].name,"Weight==",v_wieht)
                                # quan = str(v_wieht)
                                
                                quan = Decimal(str(v_wieht)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
                                vm_vert[bm_Df_Lay][v_ind] = float(quan)
                                i = i + vm_vert[bm_Df_Lay][v_ind]                         # 丸め時切り捨て、切り上げで1じゃなくなってないかcheck用
                                # print(obj.vertex_groups[v_ind].name,"Weight==",vm_vert[bm_Df_Lay][v_ind])
                        i == round(i,2)                                                 
                        def_i = 1 - i
                        # print((abs(def_i) < 0.001), " TOTAL == ", i,"difference== ",def_i)
                        if (abs(def_i) > 0.001) and (v_ind in vm_vert[bm_Df_Lay]):                                            # 合計が1±0.001以内かcheck（内部的に微小端数は出る）
                           vm_vert[bm_Df_Lay][v_ind] =(vm_vert[bm_Df_Lay][v_ind] + def_i)   # 1じゃないなら最後にチェックしたボーンに誤差分吸収

                ctrl_bmsh.to_mesh(obj.data)
                #print("ctrl_bmsh--->",ctrl_bmsh)
                ctrl_bmsh.free()                                                            # bmshを破棄


                # ～～～↑↑↑↑～～たまに処理できない頂点がでたので手動で一回丸める～～～↑↑↑↑～～ #
                print("test--->",listobj.name,"--->end")

        else:
            print("erorr",obj)
        return {'FINISHED'}
    
            
    def invoke(self, context, event):# ポップアップ表示
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.use_property_split = True
        row.prop(self, "limit")




class VIEW3D_PT_CustomPanel_mugi(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "Item"               # パネルを登録するタブ名
    bl_label = "round_the_weight"             # パネルのヘッダに表示される文字列
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
        # row = 横並び : col = 縦並び : box = 囲む : split :分割
        layout = self.layout
        row = layout.split(align=True)
        row.label(text = "round_the_weight")
        row.operator(OBJECT_OT_vertex_groups_weight_round_the_weight.bl_idname, text = translat.pgettext("round_the_weight"))
