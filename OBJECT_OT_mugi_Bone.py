import bpy
import re

from bpy.types import Panel, UIList
from mathutils import Vector

translat = bpy.app.translations


class OBJECT_OT_align_bones_line(bpy.types.Operator):
    """選択したボーンを、最初に選んだボーンヘッドから最後に選んだボーンテールを結ぶ直線に整列させる"""
    bl_idname = "object.align_bones_line"
    bl_label = "Align Bones on Line"
    bl_options = {'REGISTER', 'UNDO'}



    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_ARMATURE':
            return False
        obj = context.object
        if not obj or obj.type != 'ARMATURE':
            return False
        bones = obj.data.edit_bones
        selected = [b for b in bones if b.select]
        return len(selected) >= 2

    def execute(self, context):
        bones = context.object.data.edit_bones
        selected = [b for b in bones if b.select]

        # 親が非選択のボーン（最上流）を取得
        root = next((b for b in selected if not b.parent or b.parent not in selected), None)
        if not root:
            self.report({'ERROR'}, "親が非選択のボーンが見つかりません")
            return {'CANCELLED'}

        # チェーン取得
        chain = self.get_connected_chain(root, selected)

        if set(chain) != set(selected):
            self.report({'ERROR'}, "選択に接続されていないボーンが含まれています")
            return {'CANCELLED'}

        # 2本だけ選択されていた場合の簡易整列
        if len(chain) == 2:
            bone1, bone2 = chain
            start = bone1.head.copy()
            end = bone2.tail.copy()
            vec = end - start
            if vec.length == 0:
                self.report({'ERROR'}, "2本のボーンの開始と終了位置が同じです")
                return {'CANCELLED'}

            dir_vec = vec.normalized()

            # ボーン1：開始に合わせる
            len1 = (bone1.tail - bone1.head).length
            bone1.head = start
            bone1.tail = start + dir_vec * len1

            # ボーン2：終了に合わせる
            len2 = (bone2.tail - bone2.head).length
            bone2.tail = end
            bone2.head = end - dir_vec * len2

            self.report({'INFO'}, "2本のボーンを直線に整列しました")
            return {'FINISHED'}

        # 3本以上：中間ボーンの長さ比率を保って整列
        start = chain[0].head.copy()
        end = chain[-1].tail.copy()
        vec = end - start
        total_length = vec.length
        if total_length == 0:
            self.report({'ERROR'}, "開始と終了座標が同じです")
            return {'CANCELLED'}

        dir_vec = vec.normalized()
        middle_bones = chain[1:-1]

        # 元の中間ボーン長さ比率を取得
        original_lengths = [(b.tail - b.head).length for b in middle_bones]
        sum_length = sum(original_lengths)
        if sum_length == 0:
            self.report({'ERROR'}, "中間ボーンの長さがすべて0です")
            return {'CANCELLED'}

        ratios = [l / sum_length for l in original_lengths]
        usable_length = total_length - (chain[0].length + chain[-1].length)
        allocated_lengths = [r * usable_length for r in ratios]

        # 中間整列処理
        cursor = chain[0].tail.copy()
        for i, bone in enumerate(middle_bones):
            bone.head = cursor
            length = allocated_lengths[i]
            bone.tail = bone.head + dir_vec * length
            cursor = bone.tail

        self.report({'INFO'}, f"{len(middle_bones)} 本の中間ボーンを整列しました（端固定・比率維持）")
        return {'FINISHED'}

    def get_connected_chain(self, root, selected):
        """親→子で接続されたボーンを順にリストアップ"""
        chain = []
        current = root
        while current and current in selected:
            chain.append(current)
            children = [b for b in current.children if b in selected]
            current = children[0] if len(children) == 1 else None
        return chain


    

class OBJECT_OT_rename_multiple_chains_padded(bpy.types.Operator):
    """選択された接続チェーンを列ごとに連番リネーム（メッシュ→アーマチュア順でVGも更新）"""
    bl_idname = "armature.rename_multiple_chains_padded"
    bl_label = "接続チェーン連番リネーム（0埋め）"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_ARMATURE':
            return False
        obj = context.object
        if not obj or obj.type != 'ARMATURE':
            return False
        bones = obj.data.edit_bones
        selected = [b for b in bones if b.select]
        return len(selected) >= 2

    def execute(self, context):
        # アーマチュア取得
        arm_obj = next((obj for obj in context.selected_objects if obj.type == 'ARMATURE'), None)
        if arm_obj is None:
            self.report({'ERROR'}, "アーマチュアが選択されていません")
            return {'CANCELLED'}
        bpy.context.view_layer.objects.active = arm_obj

        edit_bones = arm_obj.data.edit_bones
        selected = [b for b in edit_bones if b.select]

        # メッシュオブジェクトを取得（アーマチュアモディファイアで関連づけられたもののみ）
        mesh_objects = [
            obj for obj in context.selected_objects
            if obj.type == 'MESH'
            and any(mod.type == 'ARMATURE' and mod.object == arm_obj for mod in obj.modifiers)
        ]

        # 親が非選択（＝列の先頭）のボーンから処理
        root_bones = [b for b in selected if not b.parent or b.parent not in selected]
        total_renamed = 0

        for chain_index, root in enumerate(root_bones):
            # 接尾辞（.L/.R）と接頭辞（prefix-）
            suffix_match = re.search(r"(\.[LR])$", root.name)
            suffix = suffix_match.group(1) if suffix_match else ""
            base_name = re.sub(r"(\.[LR])$", "", root.name)
            prefix_match = re.match(r"(.*-)\d+$", base_name)
            if not prefix_match:
                self.report({'WARNING'}, f"{root.name} は '名前-番号.L' の形式ではありません。スキップします")
                continue
            prefix = prefix_match.group(1)

            # チェーン構築
            chain = []
            current = root
            while current:
                chain.append(current)
                children = [b for b in current.children if b.select and b.use_connect]
                current = children[0] if len(children) == 1 else None

            digits = 2 if len(chain) >= 11 else 1

            # ボーン名 → 新ボーン名のマッピングを作成（仮名に変更する前に）
            bone_rename_map = {}  # {old_name: new_name}
            for i, bone in enumerate(chain):
                index_str = f"{i:0{digits}d}"
                new_name = f"{prefix}{index_str}{suffix}"
                bone_rename_map[bone.name] = new_name

            # 仮名に変更（衝突防止）
            for i, bone in enumerate(chain):
                bone.name = f"BONEkari_{i}_{chain_index}"

            # 本リネーム
            for bone in chain:
                for old_name, new_name in bone_rename_map.items():
                    if bone.name.startswith("BONEkari") and old_name not in [b.name for b in chain]:
                        continue
                    bone.name = new_name
                    break

            # 頂点グループも同様にリネーム
            for mesh in mesh_objects:
                for old_name, new_name in bone_rename_map.items():
                    vg = mesh.vertex_groups.get(old_name)
                    if vg:
                        vg.name = new_name

            total_renamed += len(chain)

        self.report({'INFO'}, f"{len(root_bones)} 列、{total_renamed} 本のボーンをリネームしました")
        return {'FINISHED'}
    

    
class VIEW3D_PT_CustomPanel_mugi_Bone_Panel(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "mugiTOOLS"          # パネルを登録するタブ名
    bl_label = "mugi_bone_panel"       # パネルのヘッダに表示される文字列
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
       # row = 横並び : col = 縦並び : box = 囲む : split :分割
      layout = self.layout

     # test1 + ボタン1
      row = layout.row(align=True)
      row.label(text="Align_selected_bones")
      row.operator(OBJECT_OT_align_bones_line.bl_idname, text = translat.pgettext("bones_line"))

     # test2 + ボタン2
      row = layout.row(align=True)
      row.label(text="Rename_at_the_top_bone")
      row.operator(OBJECT_OT_rename_multiple_chains_padded.bl_idname, text = translat.pgettext("bones_rename"))
