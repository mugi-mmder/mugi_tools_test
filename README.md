# mugi_tools_test


## Description

「mugiTOOLs」は、Blenderのアドオンです。
気が向いたときに気が向いた機能を実験してます。
blender 3.1以降に対応してます。



## Download
GitHuｂの画面右上にある［Code ▼］ ＞ ［Dwonload ZIP］の順にクリックして、ZIPファイルをダウンロードしてください。

discordのモデラー鯖「MMDキャラモデルをつくろ」の、mmdtools関連のZIPファイルをダウンロードしてください。（試作版）
※気分で更新/削除するのであったりなかったりする


## Install

1. Blenderの［Blenderプリファレンス］画面を開きます。
2. ［アドオン］タブにある［インストール］ボタンを押して、ダウンロードしたZIPファイルを選択しインストールします。
3. ［サポートレベル］にある［テスト中］を押して、テスト中のアドオンを表示します。
4. ［test mugiTOOLs］の左にあるチェックをつけて、アドオンを有効にします。


## Caution
個人用の実験/遊び用なので、気分次第で機能も増えたり消したりする

## Usage

・OBJECT_OT_vertex_groups_weight
□　サイドバー　→　アイテム　→　ウェイト丸め　：

　ウェイト指定値でｸﾘｰﾝ　＆　0.01以下ウェイト丸め　＆正規化
　左下にでるウィンドは使う予定はないが、消し方が分からないので放置
※注意.1　アーマチュアのみや、頂点グループのないメッシュオブジェクトだけを選んで無理やり実行すると落ちる！※
※注意.2　SDEFウェイトは保持されないので、PMXファイルを読み込んでの実行時は注意※


・VIEW3D_PT_CustomPanel
□　サイドバー　→　アイテム　→　3Dカーソル(アイテム欄用)：

　よく使う3Dカーソル関連をまとめたやつ



・TEXTURE_OT_BRUSH
□　プロパティ　→　ツール　→　共通ペイントブラシ設定：

　ブラシサイズをボタンで操作できるようにしてるだけ


・mmd_cm_trans
□　サイドバー　→　mugiTOOLS　→　MMD(cm)単位換算　：

　選択オブジェクト（複数可）のblender内高さを158ｃｍプラグイン換算で計算する
※選択オブジェクトの、一番高い頂点と一番低い頂点をリストから選ぶので、全オブジェクト選択でも可能だが、負荷軽減のため
　一番高いオブジェクトと一番低いオブジェクトの2、3個ほど選んで実行するが吉



・MESH_OT_change_vtxselect_shapekey
□ サイドバー　→　mugiTOOLS　→　選択ｼｪｲﾌﾟｷｰの変更頂点選択：

メッシュオブジェクトの編集モードで、選択中のシェイプキー（Basisを除く）で変更した頂点を選択状態にする



・OBJECT_OT_shape_keys_tiny_DEL
□ サイドバー　→　mugiTOOLS　→　ｼｪｲﾌﾟｷｰ仕上げ機能：

①微小移動ｼｪｲﾌﾟｷｰ頂点削除
オブジェクトモードで、選択中のメッシュオブジェクトのシェイプキー（Basisを除く）から微小量だけ動いている
頂点移動を削除し初期位置（Basis）位置に戻す

②X=0強制
オブジェクトモードで、選択中のメッシュオブジェクトのシェイプキー（Basisを除く）のX＝0の頂点は、すべての
シェイプキーでX＝0を強制する

・oji_Shape_Key_ST_Copy
□ プロパティ　→　データ　→　ｼｪｲﾌﾟｷｰｽﾍﾟｼｬﾙ：

①複数選択したメッシュオブジェクトのシェイプキーの名称枠をコピー
②選択シェイプキーとBasisを入替、表情モーフや隠しモーフ用。元のシェイプキーで旧Basis位置に戻る（取扱注意)
③選択シェイプキーを反転を元ｼｪｲﾌﾟｷｰ+inv名称で追加

・OBJECT_OT_mugi_Bone
□ サイドバー　→　mugiTOOLS　→　mugi_bone_panel：

①選択ボーン整列
アーマチュアオブジェクトの編集モードで、接続設定している連続したボーンを直線に整える

②先頭ボーンで改名
アーマチュアオブジェクトの編集モードで、接続設定している連続したボーンを最上位の名称からの連番でリネーム



## Licence

[MIT License](./LICENCE)

## Author　mugi

GitHub:[mugi-mmder](https://github.com/mugi-mmder) 
Twitter:[###](https://twitter.com/####)
