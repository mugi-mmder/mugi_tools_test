import bpy
from bpy.types import Operator

class OBJECT_OT_copy_shape_key_structure(Operator):
    bl_idname = "object.copy_shape_key_structure"
    bl_label = "Copy Shape Key Structure"
    bl_description = "アクティブオブジェクトのシェイプキー構造（名前と順序）を他の選択オブジェクトにコピーします"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.shape_keys

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
