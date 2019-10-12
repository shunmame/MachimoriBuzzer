// タイル関係
var t_pale = L.tileLayer('http://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png', {
    attribution: "<a href='http://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html' target='_blank'>国土地理院</a>"
});

var t_ort = L.tileLayer('http://cyberjapandata.gsi.go.jp/xyz/ort/{z}/{x}/{y}.jpg', {
    attribution: "<a href='http://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html' target='_blank'>国土地理院</a>"
});

var o_std = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
});

var Map_BaseLayer = {
    // "MIERUNE地図 color": m_color,
    // "MIERUNE地図 mono": m_mono,
    "地理院地図 淡色": t_pale,
    "地理院地図 航空写真": t_ort,
    "OpenStreetMap 標準": o_std
};

var map; //  マップ用のタイル

var user_lat = 32.504405;  // ユーザー緯度
var user_lon = 130.604782; // ユーザー経度
var user_num = 10001;      // ユーザー番号

var occur_info = []; // 不審者出没マーカー情報
var occur_lat = [];  // 不審者出没緯度
var occur_lon = [];  // 不審者出没経度
var occur_time = [];     // 不審者出没時刻
var occur_address = [];  // 不審者出没住所
var occur_case = [];     // 事案
var buzzer_num = []; // ブザー番号

var safeguard_info = []; // まもるいえマーカー情報
var safeguard_lat = [];  // まもるいえ緯度
var safeguard_lon = [];  // まもるいえ経度
var safeguard_name = [];     // まもるいえ名前
var safeguard_address = [];  // まもるいえ住所
var safeguard_img = [];      // まもるいえ写真


var occur_flag = 0;
var safeguard_flag = 0;
var danger_flag = 0;

var occur_tile;
var safeguard_tile;
var danger_tile = [];

var occur_popOpt = {
    'className': 'occur_pop'
}
var safeguard_popOpt = {
    'className': 'safeguard_pop'
}

var edit_time;
var edit_address;
var edit_case;

// var occur_pop_title = '<div class="occur_pop_title">不審者出没地点</div>';
// var safeguard_pop_title = '<div class="safeguard_pop_title">こどもをまもるいえ</div>';

var edit_mark = "<img src='../static/map_display/img/edit.png' class='edit_mark' onclick='img_click();'><label for='pop11'></label></img>";

function img_click(){
    var modaltext = document.getElementById('modaltext');
    modaltext.innerHTML = edit_time + '<br>' + edit_address + '<br>' + edit_case;
    document.getElementById("btn1").click();  // 強制的にクリック
}

function submit_clicked(){
    //alert("回答を受け付けました");
    document.getElementsByClassName("leaflet-popup-close-button")[0].click();  // 強制的にクリック
}

/*
$.getJSON({ url: 'map_data.json', cache: false, }) // json読み込み開始
    .done(function (data) { // jsonの読み込みに成功した時
        console.log('成功');
        len = data.length;
        for (var i = 0; i < len; i++) {
            if (data[i].kind == 0) {
                occur_lat.push(data[i].lat);
                occur_lon.push(data[i].lon);
                occur_time.push(data[i].time);
                occur_address.push(data[i].address);
                occur_case.push(data[i].case);
                buzzer_num.push(data[i].buzzer_num);
            }
            else{
                safeguard_lat.push(data[i].lat);
                safeguard_lon.push(data[i].lon);
                safeguard_name.push(data[i].name);
                safeguard_address.push(data[i].address);
                safeguard_img.push(data[i].img);
            }
        }
        data_load();
        map_load();
    })
    .fail(function () { // jsonの読み込みに失敗した時
        console.log('失敗');
    }
);*/


function get_data(data){
    console.log('成功');
    len = data.length;
    for (var i = 0; i < len; i++) {
        if (data[i].kind == 0) {
            occur_lat.push(data[i].lat);
            occur_lon.push(data[i].lon);
            occur_time.push(data[i].time);
            occur_address.push(data[i].address);
            occur_case.push(data[i].case);
             buzzer_num.push(data[i].buzzer_num);
        }
        else{
            safeguard_lat.push(data[i].lat);
            safeguard_lon.push(data[i].lon);
            safeguard_name.push(data[i].name);
            safeguard_address.push(data[i].address);
            safeguard_img.push(data[i].img);
        }
    }
    data_load();
    map_load();
    occur_appear();
    safeguard_appear();
    danger_appear();
}


// マップ読み込み
function map_load(){
    map = L.map('map', {
        center: [user_lat, user_lon],  // ユーザー住所を中心に設定
        zoom: 13,
        zoomControl: true,
        layers: [t_pale]
    });
    
    L.control.layers(Map_BaseLayer, null, {
        collapsed: true
    }).addTo(map)
    
    L.control.scale({imperial:false}).addTo(map);
}

// データ読み込み
function data_load(){
    // GeoJSON形式で複数個のマーカーを設定する
    // 不審者出没
    for (var i = 0; i < occur_lat.length; i++) {
        if(buzzer_num[i] == user_num){  // ブザー番号が一致したら
            occur_info.push({
                "type": "Feature",
                "properties": {
                    "occur_pop_title" : '<div class="occur_pop_title">不審者出没地点' + edit_mark + '</div>',
                    "popupContent": occur_time[i] + "<br>" + occur_address[i] + "<br>" + occur_case[i]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [occur_lon[i], occur_lat[i]]
                }
            });
            edit_time = occur_time[i];
            edit_address = occur_address[i];
            edit_case = occur_case[i];
        }
        else{
            occur_info.push({
                "type": "Feature",
                "properties": {
                    "occur_pop_title" : '<div class="occur_pop_title">不審者出没地点</div>',
                    "popupContent": occur_time[i] + "<br>" + occur_address[i] + "<br>" + occur_case[i]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [occur_lon[i], occur_lat[i]]
                }
            });
        }
    }

    // こどもをまもるいえ
    for (var i = 0; i < safeguard_lat.length; i++) {
        var img_info = "<div class='img_tag'><img src=" + safeguard_img[0] + "width='80%' height='80%' text-align:center;></img></div>";
        safeguard_info.push({     // 1つのマーカーの情報を格納する
            "type": "Feature",
            "properties": {
                "safeguard_pop_title" : '<div class="safeguard_pop_title">こどもをまもるいえ</div>',
                "popupContent": safeguard_name[i] + "<br>" + safeguard_address[i] + "<br>" + img_info
            },
            "geometry": {
                "type": "Point",
                "coordinates": [safeguard_lon[i], safeguard_lat[i]]
            }
        });
    }
}

// 不審者出没表示
function occur_appear() {
    if (occur_flag == 1) {
        occur_flag = 0;
        occur_disappear();
    }
    else {
        occur_flag = 1;
        // クリックしたらポップアップが出るように設定する
        occur_tile = L.geoJson(occur_info,
            {
                onEachFeature: function (feature, layer) {
                    if (feature.properties && feature.properties.popupContent) {
                        layer.bindPopup(feature.properties.occur_pop_title + feature.properties.popupContent, occur_popOpt);  // popupOptions : class名を振る
                    }
                },
                // オリジナル画像を設定する
                pointToLayer: function (feature, latlng) {
                    var myIcon = L.icon({
                        iconUrl: '../static/map_display/img/marker-red.png',  // 画像のURI
                        iconSize: [25, 41],         // 画像のサイズ設定
                        iconAnchor: [12, 40],       // 画像の位置設定
                        popupAnchor: [0, -40]       // ポップアップの表示を開始する位置設定
                    });
                    return L.marker(latlng, { icon: myIcon });  // マーカーに画像情報を設定
                }
            });
        occur_tile.addTo(map);
    }
}

// 不審者出没非表示
function occur_disappear() {
    map.removeLayer(occur_tile);
}

// まもるいえ表示
function safeguard_appear() {
    if (safeguard_flag == 1) {
        safeguard_flag = 0;
        safeguard_disappear();
    }
    else {
        safeguard_flag = 1;
        // クリックしたらポップアップが出るように設定する
        safeguard_tile = L.geoJson(safeguard_info,
            {
                onEachFeature: function (feature, layer) {
                    if (feature.properties && feature.properties.popupContent) {
                        layer.bindPopup(feature.properties.safeguard_pop_title + feature.properties.popupContent, safeguard_popOpt);
                    }
                },
                // オリジナル画像を設定する
                pointToLayer: function (feature, latlng) {
                    var myIcon = L.icon({
                        iconUrl: '../static/map_display/img/mamoruie.png',  // 画像のURI
                        iconSize: [40, 40],         // 画像のサイズ設定
                        iconAnchor: [12, 40],       // 画像の位置設定
                        popupAnchor: [0, -40]       //　　ポップアップの表示を開始する位置設定
                    });
                    return L.marker(latlng, { icon: myIcon });  // マーカーに画像情報を設定
                }
            });
        safeguard_tile.addTo(map);
    }
}

// まもるいえ非表示
function safeguard_disappear() {
    map.removeLayer(safeguard_tile);
}

// 危険エリア表示
function danger_appear() {
    if (danger_flag == 1) {
        danger_flag = 0;
        danger_disappear();
    }
    else {
        danger_flag = 1;

        for (var i = 0; i < occur_lat.length; i ++ ){
            danger_tile[i] = L.circle([occur_lat[i], occur_lon[i]], 200,{ // 位置と半径
                // radius: 1000,
                color: 'blue',
                fillColor: '#399ade',
                fillOpacity: 0.5,
                weight: 0  // 枠線の太さ
            }).addTo(map);
        }
    }
}

// 危険エリア非表示
function danger_disappear() {
    for (var i = 0; i < occur_lat.length; i++) {
        map.removeLayer(danger_tile[i]);
    }
}

// ページ読み込み時に実行
window.onload = function () {
    occur_appear();
    safeguard_appear();
    danger_appear();
}
