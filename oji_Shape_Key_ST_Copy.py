import bpy
from bpy.types import Operator
from bpy.app.translations import pgettext

class OBJECT_OT_copy_shape_key_structure(Operator):
    bl_idname = "object.copy_shape_key_structure"
    bl_label = "Copy Shape Key Structure"
    bl_description = "アクティブオブジェクトのシェイプキー構造（名前と順序）を他の選択オブジェクトにコピーします"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        selected_meshes = [o for o in context.selected_objects if o.type == 'MESH']
        return obj and obj.type == 'MESH' and obj.data.shape_keys and len(selected_meshes) >= 2

    def execute(self, context):
        active_obj = context.active_object
        selected_objects = [obj for obj in context.selected_objects if obj != active_obj]

        if not selected_objects:
            self.report({'WARNING'}, "コピー先のオブジェクトが選択されていません")
            return {'CANCELLED'}

        source_keys = active_obj.data.shape_keys
        source_names = [k.name for k in source_keys.key_blocks]

        updated_count = 0

        for target_obj in selected_objects:
            if target_obj.type != 'MESH':
                continue

            shape_keys = target_obj.data.shape_keys
            if not shape_keys:
                # Basis を追加してシェイプキー構造を初期化
                target_obj.shape_key_add(name="Basis", from_mix=False)
                shape_keys = target_obj.data.shape_keys

            target_names = [k.name for k in shape_keys.key_blocks]

            # 不足分を追加
            for name in source_names:
                if name not in target_names:
                    target_obj.shape_key_add(name=name, from_mix=False)

            # 並べ替え：Basisは常に最初なので除いて処理
            for index, name in enumerate(source_names[1:], start=1):
                current_index = shape_keys.key_blocks.find(name)
                if current_index != index:
                    while current_index > index:
                        bpy.context.view_layer.objects.active = target_obj
                        bpy.ops.object.shape_key_move(type='UP')
                        current_index -= 1
                    while current_index < index:
                        bpy.context.view_layer.objects.active = target_obj
                        bpy.ops.object.shape_key_move(type='DOWN')
                        current_index += 1

            updated_count += 1

        self.report({'INFO'}, f"{updated_count} 個のオブジェクトにシェイプキー構造をコピーしました")
        return {'FINISHED'}

# ▼ Basisと選択シェイプキーを入れ替え、シェイプキーで元形状に戻す
class OBJECT_OT_invert_shape_key(bpy.types.Operator):
    bl_idname = "object.invert_shape_key"
    bl_label = "Invert Shape Key (Overwrite Basis)"
    bl_description = "選択シェイプキーをBasisにし、反転シェイプキーに(表情/隠しモーフ用)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj and obj.type == 'MESH' and obj.data.shape_keys and
            len(obj.data.shape_keys.key_blocks) > 1 and
            obj.active_shape_key_index > 0
        )

    def invoke(self, context, event):
        # カスタム確認ダイアログを画面中央に表示
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        #layout.alert = True  # 全体を警告色にする
        
        obj = context.active_object
        active_shape = obj.data.shape_keys.key_blocks[obj.active_shape_key_index]
        
        # 大きな警告アイコンとタイトル
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="", icon='ERROR')
        row.label(text="危険な操作")
        row.label(text="", icon='ERROR')
        
        layout.separator()
        
        # 中央揃えで操作対象を表示
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text=f"Basisを、シェイプキー: '{active_shape.name}'に入れ替えます")

        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=f"実行前に[ mugiToolS 微小移動ｼｪｲﾌﾟｷｰ削除 ]を行ってください")
        
        layout.separator()
        
        # 警告ボックス
        box = layout.box()
        #box.alert = True
        col = box.column()
        col.label(text="⚠️ この操作は Basis を永続的に変更します", icon='CANCEL')
        col.separator(factor=0.5)
        col.label(text="実行されること:")
        col.label(text="  • Basis が選択シェイプキーの形状に変更される")
        col.label(text="  • 元の Basis に戻すシェイプキーが新規作成される")
        col.label(text="  • 元のシェイプキーは削除される")
        
        layout.separator()
        
        # 最終警告
        row = layout.row()
        row.alignment = 'CENTER'
        row.alert = True
        row.label(text="🔴 この操作は取り消せない場合があります 🔴")
        
        layout.separator()

    def execute(self, context):
        try:
            obj = context.active_object
            shape_keys = obj.data.shape_keys
            active_index = obj.active_shape_key_index
            original_shape = shape_keys.key_blocks[active_index]
            original_name = original_shape.name
            
            # 現在のモードを保存
            original_mode = obj.mode
            
            # オブジェクトモードに切り換え
            if original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            # スライダー範囲変更と逆変形
            original_shape.slider_min = -1.000
            original_shape.value = -1.0

            # 逆状態を複製
            bpy.ops.object.shape_key_add(from_mix=True)
            new_shape = shape_keys.key_blocks[-1]

            # Basisに戻してBlend From Shape
            obj.active_shape_key_index = 0
            # メッシュを強制更新
            obj.data.update()
            bpy.context.view_layer.update()

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.blend_from_shape(shape=original_name, blend=1.0, add=False)
            bpy.ops.object.mode_set(mode='OBJECT')

            # 元を削除、名前上書き
            obj.active_shape_key_index = active_index
            bpy.ops.object.shape_key_remove()
            new_shape.name = original_name
            
            # 元のモードに戻る
            if original_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=original_mode)

            self.report({'INFO'}, f"{original_name} を逆方向で置き換えました")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"操作に失敗しました: {str(e)}")
            # エラーが発生した場合、可能な限り元のモードに戻す
            try:
                if 'original_mode' in locals() and obj.mode != original_mode:
                    bpy.ops.object.mode_set(mode=original_mode)
            except:
                pass
            return {'CANCELLED'}

class OBJECT_OT_add_inverted_shape_key(bpy.types.Operator):
    bl_idname = "object.add_inverted_shape_key"
    bl_label = "Add Inverted Shape Key"
    bl_description = "選択中のシェイプキーを逆方向にしたものを新しく追加します（Basisは変更しません）"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj and obj.type == 'MESH' and obj.data.shape_keys and
            len(obj.data.shape_keys.key_blocks) > 1 and
            obj.active_shape_key_index > 0
        )

    def execute(self, context):
        obj = context.active_object
        shape_keys = obj.data.shape_keys
        active_index = obj.active_shape_key_index
        original_shape = shape_keys.key_blocks[active_index]
        original_name = original_shape.name

        # 選択シェイプキーの値を -1.0 にして反転状態に
        original_shape.slider_min = -1.000
        original_shape.value = -1.0

        # 現在の反転状態を複製
        bpy.ops.object.shape_key_add(from_mix=True)
        new_shape = shape_keys.key_blocks[-1]

        # 新しい名前に "_inv" を付けてリネーム
        new_shape.name = original_name + "_inv"

        # 元のシェイプキーの値を元に戻す
        original_shape.value = 0.0
        original_shape.slider_min = 0.0

        self.report({'INFO'}, f"{new_shape.name} を追加しました（Basisは変更なし）")
        return {'FINISHED'}