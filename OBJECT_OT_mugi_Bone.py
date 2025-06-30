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
    """選択されたボーンチェーンを浮かせた状態で連番リネーム"""
    bl_idname = "armature.rename_bone_chains_vglink"
    bl_label = "チェーン連番リネーム（VG自動追従）"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'EDIT_ARMATURE' and
            context.object and
            context.object.type == 'ARMATURE' and
            len([b for b in context.object.data.edit_bones if b.select]) >= 2
        )

    def execute(self, context):
        arm_obj = context.object
        edit_bones = arm_obj.data.edit_bones
        selected = [b for b in edit_bones if b.select]

        root_bones = [b for b in selected if not b.parent or b.parent not in selected]
        total_renamed = 0

        for chain_index, root in enumerate(root_bones):
            suffix_match = re.search(r"(\.[LR])$", root.name)
            suffix = suffix_match.group(1) if suffix_match else ""
            base_name = re.sub(r"(\.[LR])$", "", root.name)
            prefix_match = re.match(r"(.*-)\d+$", base_name)
            if not prefix_match:
                self.report({'WARNING'}, f"{root.name} は '名前-番号.L' の形式ではありません。スキップ")
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

            # 仮リネーム
            for i, bone in enumerate(chain):
                bone.name = f"TMP_{chain_index}_{i}"

            # 本リネーム
            for i, bone in enumerate(chain):
                new_name = f"{prefix}{i:0{digits}d}{suffix}"
                bone.name = new_name

            total_renamed += len(chain)

        # ボーン名に応じて VG を自動追従させる（浮かせた状態）
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, f"{len(root_bones)}列、{total_renamed}本のボーンをリネームしました（VG追従）")
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
