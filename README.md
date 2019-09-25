# MachimoriBuzzer

### Webサイト(↓Look here!↓)
http://machimori.japanwest.cloudapp.azure.com

### 概要  
まちもりブザーのソースコード

- app  
サーバーで動いているコード

- wio  
wioで動いているコード

### ファイル構成  
```
app/
 ├ app.py              ・ mainで動かすファイル
 ├ DB.py               ・ DB関連
 ├ addrestoik.py       ・ 住所を緯度経度変換
 ├ calc_distance.py    ・ 二点間の距離を求める
 ├ create_json.py      ・ map用のjson(dict)を作成する
 ├ knn.py              ・ 異常検知
 ├ mail.py             ・ mailを送信
 ├ templates/
 │     ├ index.html                   ・ login画面
 │     ├ map_display.html             ・ mapを表示する画面
 │     ├ registration_parent.html     ・ 保護者を登録する画面
 │     ├ registration_safehouse.html  ・ こどもをまもるいえを登録する画面
 │     ├ select_type.html             ・ どちらの登録者かを選択する画面
 │     ├ wio_form.html                ・ wioからデータが送られてきたことを偽る画面
 ├ static/
       ├ map_display/
             ├ jquery-3.3.1.min.js
             ├ map_display.css        ・ map表示ようのcss
             ├ map_display.js         ・ map表示ようのjavascript
             ├ img/
                 ├ *.png              ・ mapに表示している画像
                 ├ safeguard/
                       ├ *.png        ・ こどもをまもるいえの画像

wio/
 ├ wio_main.ino        ・ wioで動いているファイル
```
