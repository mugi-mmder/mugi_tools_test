# Copyright (c) 2025 mugi
import bpy

from bpy.types import Panel, UIList
from bpy.props import *
from mathutils import Vector

translat = bpy.app.translations

class OBJECT_OT_remove_tiny_shape_keys(bpy.types.Operator):
    bl_idname = "object.fix_tiny_shape_keys_all"
    bl_label = "Remove Tiny Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    threshold: bpy.props.FloatProperty(name="Threshold",default=0.001,min=0.0,max = 0.1,step = 1,
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


class OBJECT_OT_clean_and_fix_mirror_X0(bpy.types.Operator):
    """単一メッシュオブジェクト専用：微小移動削除+グローバルX=0固定"""
    bl_idname = "object.clean_and_fix_mirror_x0"
    bl_label = "Fix Mirror X0"
    bl_description = "アクティブメッシュの微小移動削除後、BasisでグローバルX=0の頂点を全シェイプキーでX=0に固定"
    bl_options = {'REGISTER', 'UNDO'}

    threshold: bpy.props.FloatProperty(
        name="Threshold",
        default=0.001,
        min=0.0,
        max=0.1,
        step=1,
        description="微小移動の閾値"
    )
    
    x_tolerance: bpy.props.FloatProperty(
        name="X=0 Tolerance",
        default=0.0001,
        min=0.0,
        max=0.01,
        step=0.1,
        description="X=0判定の許容誤差"
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and 
                obj.type == 'MESH' and 
                obj.data.shape_keys and
                context.mode == 'OBJECT')

    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "アクティブオブジェクトがメッシュではありません")
            return {'CANCELLED'}
            
        mesh = obj.data
        shape_keys = mesh.shape_keys
        
        if not shape_keys:
            self.report({'ERROR'}, "シェイプキーが存在しません")
            return {'CANCELLED'}
        
        world_matrix = obj.matrix_world
        world_matrix_inv = world_matrix.inverted()
        
        # Step 1: 微小移動量削除
        basis = shape_keys.key_blocks.get("Basis")
        if not basis:
            self.report({'ERROR'}, "Basisシェイプキーが見つかりません")
            return {'CANCELLED'}
        
        print(f"処理開始: オブジェクト '{obj.name}' - {len(shape_keys.key_blocks)}個のシェイプキー")
        
        tiny_fixed_vertices = 0
        tiny_fixed_shape_keys = 0
        
        # 微小移動削除
        for key_block in shape_keys.key_blocks:
            if key_block.name == "Basis":
                continue
                
            shape_modified = False
            for i, vert in enumerate(key_block.data):
                if i >= len(basis.data):
                    break
                delta = (vert.co - basis.data[i].co).length
                if delta < self.threshold:
                    key_block.data[i].co = basis.data[i].co
                    tiny_fixed_vertices += 1
                    shape_modified = True
            
            if shape_modified:
                tiny_fixed_shape_keys += 1
                print(f"微小移動削除: {key_block.name}")
        
        # Step 2: BasisでグローバルX≈0の頂点を特定
        center_vertices = []
        for i, vert in enumerate(basis.data):
            global_pos = world_matrix @ vert.co
            if abs(global_pos.x) <= self.x_tolerance:
                center_vertices.append(i)
                print(f"中央頂点発見: インデックス{i}, グローバルX={global_pos.x:.6f}")
        
        print(f"中央頂点数: {len(center_vertices)}個")
        
        # Step 3: 中央頂点を全シェイプキーでX=0に固定
        mirror_fixed_vertices = 0
        mirror_fixed_shape_keys = 0
        
        if center_vertices:
            for shape_key in shape_keys.key_blocks:
                shape_modified = False
                fixed_count_this_shape = 0
                
                for vert_idx in center_vertices:
                    if vert_idx < len(shape_key.data):
                        # 現在の座標を取得
                        current_local = shape_key.data[vert_idx].co.copy()
                        current_global = world_matrix @ current_local
                        
                        # グローバルX座標が0でない場合は修正
                        if abs(current_global.x) > self.x_tolerance:
                            # グローバル座標でX=0に設定
                            fixed_global = Vector((0.0, current_global.y, current_global.z))
                            # ローカル座標に変換して設定
                            fixed_local = world_matrix_inv @ fixed_global
                            shape_key.data[vert_idx].co = fixed_local
                            
                            mirror_fixed_vertices += 1
                            fixed_count_this_shape += 1
                            shape_modified = True
                            
                            print(f"修正: {shape_key.name} 頂点{vert_idx} "
                                  f"X: {current_global.x:.6f} → 0.0")
                
                if shape_modified:
                    mirror_fixed_shape_keys += 1
                    print(f"シェイプキー '{shape_key.name}': {fixed_count_this_shape}個の頂点を修正")
        
        # Step 4: メッシュ更新
        mesh.update()
        
        # 結果報告
        message = (f"完了 - 微小削除: {tiny_fixed_vertices}頂点/{tiny_fixed_shape_keys}キー, "
                  f"ミラー固定: {mirror_fixed_vertices}頂点/{mirror_fixed_shape_keys}キー "
                  f"(中央頂点: {len(center_vertices)}個)")
        
        self.report({'INFO'}, message)
        print(f"[{obj.name}] {message}")
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.use_property_split = True
        row.prop(self, "threshold")

        
class OBJECT_OT_clean_and_fix_mirror_X0(bpy.types.Operator):
    """単一メッシュオブジェクト専用：微小移動削除+グローバルX=0固定"""
    bl_idname = "object.clean_and_fix_mirror_x0"
    bl_label = "Fix Mirror X0"
    bl_description = "アクティブメッシュの微小移動削除後、BasisでグローバルX=0の頂点を全シェイプキーでX=0に固定"
    bl_options = {'REGISTER', 'UNDO'}

    threshold: bpy.props.FloatProperty(name="Threshold",default=0.001,min=0.0,max=0.1, step=1,
                                        description="微小移動の閾値" )
    
    x_tolerance: bpy.props.FloatProperty(name="X=0 Tolerance", default=0.0001, min=0.0, max=0.01, step=0.1,
                                          description="X=0判定の許容誤差" )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and 
                obj.type == 'MESH' and 
                obj.data.shape_keys and
                context.mode == 'OBJECT')

    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "アクティブオブジェクトがメッシュではありません")
            return {'CANCELLED'}
            
        mesh = obj.data
        shape_keys = mesh.shape_keys
        
        if not shape_keys:
            self.report({'ERROR'}, "シェイプキーが存在しません")
            return {'CANCELLED'}
        
        world_matrix = obj.matrix_world
        world_matrix_inv = world_matrix.inverted()
        
        # Step 1: 微小移動量削除
        basis = shape_keys.key_blocks.get("Basis")
        if not basis:
            self.report({'ERROR'}, "Basisシェイプキーが見つかりません")
            return {'CANCELLED'}
        
        print(f"処理開始: オブジェクト '{obj.name}' - {len(shape_keys.key_blocks)}個のシェイプキー")
        
        tiny_fixed_vertices = 0
        tiny_fixed_shape_keys = 0
        
        # 微小移動削除
        for key_block in shape_keys.key_blocks:
            if key_block.name == "Basis":
                continue
                
            shape_modified = False
            for i, vert in enumerate(key_block.data):
                if i >= len(basis.data):
                    break
                delta = (vert.co - basis.data[i].co).length
                if delta < self.threshold:
                    key_block.data[i].co = basis.data[i].co
                    tiny_fixed_vertices += 1
                    shape_modified = True
            
            if shape_modified:
                tiny_fixed_shape_keys += 1
                print(f"微小移動削除: {key_block.name}")
        
        # Step 2: BasisでグローバルX≈0の頂点を特定
        center_vertices = []
        for i, vert in enumerate(basis.data):
            global_pos = world_matrix @ vert.co
            if abs(global_pos.x) <= self.x_tolerance:
                center_vertices.append(i)
                print(f"中央頂点発見: インデックス{i}, グローバルX={global_pos.x:.6f}")
        
        print(f"中央頂点数: {len(center_vertices)}個")
        
        # Step 3: 中央頂点を全シェイプキーでX=0に固定
        mirror_fixed_vertices = 0
        mirror_fixed_shape_keys = 0
        
        if center_vertices:
            for shape_key in shape_keys.key_blocks:
                shape_modified = False
                fixed_count_this_shape = 0
                
                for vert_idx in center_vertices:
                    if vert_idx < len(shape_key.data):
                        # 現在の座標を取得
                        current_local = shape_key.data[vert_idx].co.copy()
                        current_global = world_matrix @ current_local
                        
                        # グローバルX座標が0でない場合は修正
                        if abs(current_global.x) > self.x_tolerance:
                            # グローバル座標でX=0に設定
                            fixed_global = Vector((0.0, current_global.y, current_global.z))
                            # ローカル座標に変換して設定
                            fixed_local = world_matrix_inv @ fixed_global
                            shape_key.data[vert_idx].co = fixed_local
                            
                            mirror_fixed_vertices += 1
                            fixed_count_this_shape += 1
                            shape_modified = True
                            
                            print(f"修正: {shape_key.name} 頂点{vert_idx} "
                                  f"X: {current_global.x:.6f} → 0.0")
                
                if shape_modified:
                    mirror_fixed_shape_keys += 1
                    print(f"シェイプキー '{shape_key.name}': {fixed_count_this_shape}個の頂点を修正")
        
        # Step 4: メッシュ更新
        mesh.update()
        
        # 結果報告
        message = (f"完了 - 微小削除: {tiny_fixed_vertices}頂点/{tiny_fixed_shape_keys}キー, "
                  f"ミラー固定: {mirror_fixed_vertices}頂点/{mirror_fixed_shape_keys}キー "
                  f"(中央頂点: {len(center_vertices)}個)")
        
        self.report({'INFO'}, message)
        print(f"[{obj.name}] {message}")
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "threshold")




class VIEW3D_PT_CustomPanel_mugi_tiny_shape_key(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "mugiTOOLS"          # パネルを登録するタブ名
    bl_label = "Finishing Shape Keys"       # パネルのヘッダに表示される文字列
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
       # row = 横並び : col = 縦並び : box = 囲む : split :分割
      layout = self.layout
    
     # 既存のボタン（横並び）
      col = layout.column(align=True)
      row = layout.row(align=True)
      col.label(text = "tiny_shape_key_DELL")
      col.operator(OBJECT_OT_remove_tiny_shape_keys.bl_idname, text = translat.pgettext("tiny_shape_key_DELL"))

    
      # 縦並びで新しいボタンを追加

      col.label(text = "shape_key_X0")
      col.operator(OBJECT_OT_clean_and_fix_mirror_X0.bl_idname, text="shape_key_X0")