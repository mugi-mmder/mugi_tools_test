# Copyright (c) 2022 mugi
import bpy

from bpy.types import Panel, UIList, Operator
from bpy.props import *
import bmesh
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

from mathutils import Vector



translat = bpy.app.translations


class OBJECT_OT_vertex_groups_weight_round_the_weight(bpy.types.Operator):
    bl_idname = "object.vertex_groups_round_the_weight_mugitest"
    bl_label = "round_the_weight"
    bl_description = "選択メッシュオブジェクトのウェイトの0.01以下を丸めて正規化"
    bl_options = {'REGISTER', 'UNDO'}

    limit : FloatProperty(default = 0.01, min = 0.0, max = 1.0, step = 1,
                          name = "clean_weights",
                          description = "clean vertex_group weights")

    @staticmethod
    def get_armature_parent(obj):
        """オブジェクトの親チェーンをたどり、アーマチュアオブジェクトを返す。"""
        parent = obj.parent
        while parent:
            if parent.type == 'ARMATURE':
                return parent
            parent = parent.parent
        return None

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':           # objectモードで実行させるのでモード確認
            for slctobj in context.selected_objects:
                if slctobj.type == 'MESH':     # 選択オブジェクトにメッシュがあるか？
                    if cls.get_armature_parent(slctobj) is not None:  # 親階層にアーマチュアがあるかチェック
                        return True
        return False

    def execute(self, context):
        original_active = bpy.context.active_object  # 元のアクティブオブジェクトを保存
        slct_obj = bpy.context.selected_objects
        
        slctobjlist = []    # ウェイトいじるリスト
        nonlist = []        # はじいたオブジェクトリスト

        for slctobj in bpy.context.selected_objects:
            if slctobj.type in {'MESH'}:                                # 選択オブジェクトからメッシュを取り出してリスト化
                armature_parent = self.get_armature_parent(slctobj)          # 親階層からアーマチュアを取得
                if len(slctobj.vertex_groups) != 0 and armature_parent is not None:  # 頂点グループとアーマチュアがあるかチェック
                        prt_bones = [b.name for b in armature_parent.pose.bones]  # アーマチュアからボーンリスト作成 
                        vtx_groups = [v.name for v in slctobj.vertex_groups]     # オブジェクトから頂点グループリスト作成 
                        if len(set(prt_bones) & set(vtx_groups)) != 0:          # ウェイトボーンがあるかチェック 
                            slctobjlist.append(slctobj)
                        else:
                            nonlist.append(slctobj)           
                else:
                    nonlist.append(slctobj)
            else:
                nonlist.append(slctobj)
                
        if not len(slctobjlist) == 0:
            print("========  slctobjlist  ==========\n", slctobjlist ,"\n----------------------\n")
            print("========  nonlist  ==========\n", nonlist ,"\n----------------------\n")
            self.report({'INFO'}, "Round_weights_of_selected_objects") 

            for current_obj in slctobjlist:    # リストから一個ずつメッシュオブジェクトの取り出し
                print("Processing object:", current_obj.name)
                bpy.context.view_layer.objects.active = current_obj     # リストから一個ずつメッシュオブジェクトを選択

                # アーマチュアモディファイアのチェック（現在のオブジェクトで）
                has_armature = any(mod.type == 'ARMATURE' for mod in current_obj.modifiers)
                if not has_armature:
                    self.report({'INFO'}, f"{current_obj.name}にアーマチュアモディファイアが付いていません")
                    continue  # 次のオブジェクトに進む

                # 現在のオブジェクトのアーマチュア親とボーンリストを取得
                armature_parent = self.get_armature_parent(current_obj)
                if armature_parent is None:
                    self.report({'INFO'}, f"{current_obj.name}にアーマチュア親が見つかりません")
                    continue
                    
                current_prt_bones = [b.name for b in armature_parent.pose.bones]

                bpy.ops.object.mode_set(mode='EDIT', toggle = False)  # EDITmodeにはいって全頂点選択
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT', toggle = False)

                # ウェイト処理
                try:
                    bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM',
                                                        limit = self.limit, keep_single=True)
                except TypeError as e:
                    if "enum \"BONE_DEFORM\" not found" in str(e):
                        self.report({'INFO'}, "なんかエラー。もっかい試してみて")
                        return {'CANCELLED'}
                    else:
                        raise e  
                        
                bpy.ops.object.vertex_group_limit_total(group_select_mode='BONE_DEFORM', limit = 4)
                bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM',
                                                    limit = self.limit, keep_single=True)             
                bpy.ops.object.vertex_group_quantize(group_select_mode='BONE_DEFORM', steps = 100)
                bpy.ops.object.vertex_group_normalize_all(group_select_mode='BONE_DEFORM',
                                                                lock_active=False)
                bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM',
                                                    limit = self.limit, keep_single=True)
                bpy.ops.object.vertex_group_quantize(group_select_mode='BONE_DEFORM', steps = 100)

                # 手動で丸める処理（現在のオブジェクトを使用）
                ctrl_bmsh = bmesh.new()
                ctrl_bmsh.from_mesh(current_obj.data)  # 現在のオブジェクトのメッシュを使用
                bm_Df_Lay = ctrl_bmsh.verts.layers.deform.active 
                print("bm_Df_Lay---->", bm_Df_Lay)

                if not bm_Df_Lay:
                    print("not bm_Df_Lay!!!")
                    ctrl_bmsh.free()
                    continue  # 次のオブジェクトに進む

                for vm_vert in ctrl_bmsh.verts:
                    i = 0
                    last_v_ind = None
                    
                    for v_ind, v_weight in vm_vert[bm_Df_Lay].items():   
                        # 現在のオブジェクトの頂点グループを使用
                        if v_ind < len(current_obj.vertex_groups) and current_obj.vertex_groups[v_ind].name in current_prt_bones:
                            quan = Decimal(str(v_weight)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
                            vm_vert[bm_Df_Lay][v_ind] = float(quan)
                            i += vm_vert[bm_Df_Lay][v_ind]
                            last_v_ind = v_ind

                    # 正規化チェックと修正
                    i = round(i, 2)
                    def_i = 1 - i
                    if (abs(def_i) > 0.001) and (last_v_ind is not None) and (last_v_ind in vm_vert[bm_Df_Lay]):
                       vm_vert[bm_Df_Lay][last_v_ind] = (vm_vert[bm_Df_Lay][last_v_ind] + def_i)

                ctrl_bmsh.to_mesh(current_obj.data)  # 現在のオブジェクトのメッシュに適用
                ctrl_bmsh.free()
                print("Processing completed:", current_obj.name)

        else:
            self.report({'WARNING'}, "処理可能なオブジェクトがありません")
            
        # 元のアクティブオブジェクトを復元
        if original_active:
            bpy.context.view_layer.objects.active = original_active
            
        return {'FINISHED'}
    
    def invoke(self, context, event):  # ポップアップ表示
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.use_property_split = True
        row.prop(self, "limit")


class MESH_OT_vertex_weight_copy_normalize(Operator):

    bl_idname = "mesh.vertex_weight_copy_normalize"
    bl_label = "copy_weights_from_nearby_vertices"
    bl_description = "選択頂点を非選択の最近傍頂点からウェイトコピー＆正規化"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.active_object.type == 'MESH' and
                context.mode == 'EDIT_MESH')

    def execute(self, context):
        try:
            obj = context.active_object
            bm = bmesh.from_edit_mesh(obj.data)
            
            # 選択頂点と非選択頂点
            selected_verts = [v for v in bm.verts if v.select]
            unselected_verts = [v for v in bm.verts if not v.select]

            if not selected_verts:
                self.report({'ERROR'}, "No vertices selected")
                return {'CANCELLED'}
            if not unselected_verts:
                self.report({'ERROR'}, "No unselected vertices to copy from")
                return {'CANCELLED'}



            # 処理対象の頂点を記録
            processed_verts = []
            
            for base_vert in selected_verts:
                # 一番近い非選択頂点を探す
                nearest_vert = min(unselected_verts, key=lambda u: (u.co - base_vert.co).length)

                # コピー方向を逆に：nearestがアクティブ、baseがターゲット
                base_vert.select = True
                nearest_vert.select = True
                bm.select_history.clear()
                bm.select_history.add(nearest_vert)
                
                # メッシュ更新
                bmesh.update_edit_mesh(obj.data)
                
                # コピー（アクティブ = nearest、選択 = base）
                bpy.ops.object.vertex_weight_copy()
                
                # 処理済み頂点として記録
                processed_verts.append(base_vert)
                
                # 選択解除
                base_vert.select = False
                nearest_vert.select = False

            # 処理済み頂点を全選択
            for vert in processed_verts:
                vert.select = True
            
            # メッシュ更新
            bmesh.update_edit_mesh(obj.data)
            
            # デフォームボーンウェイトのみを一括正規化
            bpy.ops.object.vertex_group_normalize_all(group_select_mode='BONE_DEFORM')
            
            # 選択解除
            for vert in processed_verts:
                vert.select = False

            bmesh.update_edit_mesh(obj.data)
            self.report({'INFO'}, f"Copied and normalized deform weights for {len(selected_verts)} vertices")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error during operation: {str(e)}")
            return {'CANCELLED'}
            
class VIEW3D_PT_CustomPanel_mugi(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "Item"               # パネルを登録するタブ名
    bl_label = "Weight Tools"             # パネルのヘッダに表示される文字列
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
        # row = 横並び : col = 縦並び : box = 囲む : split :分割
        layout = self.layout
        col = layout.column(align=True)  # 縦に積む


        # 1段目

        col.label(text="copy_weights_from_nearby_vertices")
        col.operator(MESH_OT_vertex_weight_copy_normalize.bl_idname,text="実行" )

        # 2段目

        col.label(text="round_the_weight")
        col.operator(OBJECT_OT_vertex_groups_weight_round_the_weight.bl_idname,text="実行" )