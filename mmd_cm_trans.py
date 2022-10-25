# Copyright (c) 2022 mugi
import bpy

from bpy.types import Panel, UIList
from bpy.props import *

translat = bpy.app.translations

class Prop_mmd_cm_trans_setting(bpy.types.PropertyGroup):
# PropertyGroupの定義は”＝”でなく”：”に
    #use_regex = bpy.props.BoolProperty(
    max_bl      : FloatProperty(default = 0,name = "bl(Max_H)")                  # 選択オブジェクトの一番高いとこ
    min_bl      : FloatProperty(default = 0,name = "bl(Min_H)")                  # 選択オブジェクトの一番低いとこ
    maxmin_bl   : FloatProperty(default = 0,name = "MMD(Max-Min_H)cm")           # 選択オブジェクトの高低差
    max_cm      : FloatProperty(default = 0,name = "MMD(Max_H)cm")               # 選択オブジェクトの一番高いとこ(MMDcm換算)
    min_cm      : FloatProperty(default = 0,name = "MMD(Min_H)cm")               # 選択オブジェクトの一番低いとこ(MMDcm換算)
    maxmin_cm   : FloatProperty(default = 0,name = "MMD(Max-Min_H)cm")           # 選択オブジェクトの高低差(MMDcm換算)
    mmd_bool    : BoolProperty(default = True,name = "MMD_trans",                # MMDcm換算フラグ   
                              description = "Convert blender dim to MMD dim")

    mmd_ajf     : BoolProperty(default = False,name = "MMD_ajust",               # MMDcm換算調整込みフラグ   
                              description = "MMD dim_ajust_Flags")
    mmd_ajam    : FloatProperty(default = 2.0,min = -25.0,max = 25.0,step = 50,  # MMDcm調整量   
                              name = "MMD dim_ajust",
                              description = "Adjustment_amount" )
    maxmin_aj   : FloatProperty(default = 0,name = "MMD(Max-Min_H)cm")           # 選択オブジェクトの高低差調整込み(MMDcm換算)

class OBJECT_OT_mmd_cm_trans_maxmin(bpy.types.Operator):
    bl_idname = "object.mmd_cm_trans_maxmin"
    bl_label = "mmd_cm_trans_maxmin"
    bl_description = "mmdのcm単位の表示"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT':            # objectモードで実行させるのでモード確認
            for slctobj in bpy.context.selected_objects:
                if slctobj.type in {'MESH'}:        #　選択オブジェクトにメッシュがあるか？
                    return True
        else:
            return False

    def execute(self, context):
        slctobjlist = []    # 測るいじるリスト
        nonlist =[]         # はじいたオブジェクトリスト
        vz = []
        obj = bpy.context.active_object.data
        gl_obj = bpy.context.active_object.matrix_world # test用に指定してるだけ、実際はあとで変数入れ直し
        mmdtrans = 0.12595                              # MMD(cm)に変換ようの係数　158cm基準
        mmdcm = bpy.context.scene.cm_props_setting      # __init__で設定済みPropertyGroup：変数受け渡し用

        for slctobj in bpy.context.selected_objects:
            if slctobj.type in {'MESH'}:                # 選択オブジェクトからメッシュを取り出してリスト化
                slctobjlist.append(slctobj)
                for listobj in slctobjlist:             # リストから一個ずつメッシュオブジェクトの取り出し
                    print(listobj)
                    for v in listobj.data.vertices:     # リストから一個ずつ頂点の取り出し
                        gl_obj =listobj.matrix_world    # ローカル座標じゃこまるので".matrix_world"でグローバル換算
                        gl_vtx = gl_obj @ v.co          # オブジェクト内の座標をグローバル換算
                        #print("test---->",test[2],"\n",test)
                        vz.append(gl_vtx[2])            #Vectorで取り出してるのでZ座標だけ抽出（[0]:X座標 [1]:Y座標 [0]:Z座標）
        mmdcm.max_bl = max(vz)
        mmdcm.min_bl = min(vz) 
        mmdcm.maxmin_bl = (max(vz) -  min(vz))
        mmdcm.max_cm = max(vz) / mmdtrans
        mmdcm.min_cm = min(vz) / mmdtrans
        mmdcm.maxmin_cm = (max(vz) -  min(vz)) / mmdtrans
        mmdcm.maxmin_aj = ((max(vz) -  min(vz)) / mmdtrans) - mmdcm.mmd_ajam

        # print("max-->",mmdcm.max_cm,"cm","max_bl-->",mmdcm.max_bl)
        # print("min-->",mmdcm.min_cm,"cm","min_bl-->",mmdcm.min_bl)
        # print("mmd",mmdcm.maxmin_cm,"cm")


        return{'FINISHED'}


class VIEW3D_PT__mmd_cm_trans_mugi(Panel):
    bl_space_type = "VIEW_3D"          # パネルを登録するスペース
    bl_region_type = "UI"              # パネルを登録するリージョン
    bl_category = "mugiTOOLS"          # パネルを登録するタブ名
    bl_label = "MMD_unit_conversion"   # パネルのヘッダに表示される文字列
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context

    def draw(self, context):
        mmdcm = bpy.context.scene.cm_props_setting
        ### ↓ bpy.context.scene.cm_props_setting　のプロパティの中身memo ↓　###
        # max_bl     : FloatProperty 選択オブジェクトの一番高いとこ
        # min_bl     : FloatProperty 選択オブジェクトの一番低いとこ
        # maxmin_bl  : FloatProperty 選択オブジェクトの高低差
        # max_cm     : FloatProperty 選択オブジェクトの一番高いとこ(MMDcm換算)
        # min_cm     : FloatProperty 選択オブジェクトの一番低いとこ(MMDcm換算)
        # maxmin_cm  : FloatProperty 選択オブジェクトの高低差(MMDcm換算)
        # mmd_bool   : BoolProperty  MMDcm換算フラグ   
        # mmd_ajf    : BoolProperty  MMDcm換算調整込みフラグ   
        # mmd_ajam   : FloatProperty MMDcm調整量   
        # maxmin_aj  : FloatProperty 選択オブジェクトの高低差調整込み(MMDcm換算)

        # row = 横並び : col = 縦並び : box = 囲む : split :分割
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.alignment = "RIGHT"
        row.prop(mmdcm,"mmd_ajf",text = "Ajust_Flags(cm)")         # 調整用checkボックス
        row = col.row(align=True)
        row.label(text = "Adj_amount",icon = "MOD_HUE_SATURATION")
        row.prop(mmdcm,"mmd_ajam",text = "mmd")                    # MMD変換するかのcheckボックス
        #row = col.row(align=True)
        row = layout.row()
        row.alignment = "RIGHT"
        row.prop(mmdcm,"mmd_bool",text = "MMD(cm)")
        col = layout.column(align=True)
        row = col.row(align=True)


        if not mmdcm.mmd_bool:               #blender(m)をMMD(cm)に換算するかのcheck(False)
            row = col.row(align=True)
            row.label(text = "OBJ_TOP",icon = "TRIA_UP_BAR")
            row.prop(mmdcm,"max_bl",text = "blnd")
            row = col.row(align=True)
            row.label(text = "OBJ_BOTTOM",icon = "TRIA_DOWN_BAR")
            row.prop(mmdcm,"min_bl",text = "blnd")
            row = col.row(align=True)
            row.label(text = "DifferenceH/L",icon = "OUTLINER_DATA_ARMATURE")
            row.prop(mmdcm,"maxmin_bl",text = "blnd")
        else:                                 #blender(m)をMMD(cm)に換算するかのcheck(True)
            row = col.row(align=True)
            row.label(text = "OBJ_TOP",icon = "TRIA_UP_BAR")
            row.prop(mmdcm,"max_cm",text = "mmd")
            row = col.row(align=True)
            row.label(text = "OBJ_BOTTOM",icon = "TRIA_DOWN_BAR")
            row.prop(mmdcm,"min_cm",text = "mmd")
            if not (mmdcm.mmd_ajf):            # 調整フラグ(False):高低差を表示
                row = col.row(align=True)
                row.label(text = "DifferenceH/L" ,icon = "OUTLINER_DATA_ARMATURE")
                row.prop(mmdcm,"maxmin_cm",text = "mmd")
            else:                              # 調整フラグ(True):（高低差-調整）を表示
                row = col.row(align=True)
                row.label(text = "Difference-ajust" ,icon = "OUTLINER_DATA_ARMATURE")
                row.prop(mmdcm,"maxmin_aj",text = "mmd")    
        col.separator()
        col.operator(OBJECT_OT_mmd_cm_trans_maxmin.bl_idname, text = translat.pgettext("Calculation!"))

