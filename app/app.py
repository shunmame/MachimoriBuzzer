from flask import Flask, request, redirect, render_template, url_for
from mail import My_Mail
from DB import DB
import create_json as cj
from flask_login import (
    login_user,
    logout_user,
    LoginManager,
    UserMixin,
    login_required,
    current_user,
)
import addrestoik as atik
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import pytz
from calc_distance import CalcDistance
from pygc import great_circle
import math
import json
import geocoder
from knn import KNN2d


# ログイン用のクラス
class User(UserMixin):
    pass


# 初期設定
app = Flask(__name__, static_url_path="/static")
upload_folder = os.environ['UPLOAD_FOLDER']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = upload_folder

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

# こどもをまもるいえ用の画像種類
allowed_extensions = set(['png', 'jpg', 'gif', 'jpeg'])


# 画像が適切かの判定
def allowed_file(filename):
    dotin = '.' in filename
    listin = filename.rsplit('.', 1)[1].lower() in allowed_extensions
    return dotin and listin

# ログインの確認用
@login_manager.user_loader
def load_user(sp_ID):
    db = DB()
    sql = 'select parent_ID from parent where parent_ID=%s;'
    data = db.select(sql, (sp_ID,))
    if not data:
        sql = 'select safeguard_ID from safeguard where safeguard_ID=%s;'
        data = db.select(sql, (sp_ID,))
    db.end_DB()
    if sp_ID not in data[0]:
        return
    user = User()
    user.id = sp_ID
    return user

# ログイン画面表示
@app.route('/')
def home():
    return render_template('index.html')

# ログイン処理
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = DB()
        sp_ID = request.form['ID']
        password = request.form['password']
        # parentのアカウントがあるか確認
        sql = ('select parent_password from parent'
               ' where parent_ID=%s;')
        data = db.select(sql, (sp_ID,))
        if not data:  # parentではないときsafeguardのログイン
            sql = ('select safeguard_password from safeguard'
                   ' where safeguard_ID=%s;')
            data = db.select(sql, (sp_ID,))
        db.end_DB()
        # ログインできたらmapへ
        for pas in data:
            if pas[0] == password:
                user = User()
                user.id = sp_ID
                login_user(user)
                return redirect(url_for('map'))
        # ログインできなかったらログイン画面へ
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

# ログアウト
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# 登録者選択画面
@app.route('/select_type')
def select_type():
    return render_template('select_type.html')

# parentの登録フォーム表示
@app.route('/registration_parent')
def registration_parent():
    return render_template('registration_parent.html')

# parentの登録処理
@app.route('/registration_parent_data', methods=['POST'])
def registration_parent_data():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mail_addres = request.form['mail_addres']
        password = request.form['password']
        check_pass = request.form['check_pass']
        addres1 = request.form['addr11']
        addres2 = request.form['Address2']
        buzer_number = request.form['buzer_number']
        school_name = request.form['school_name']

        if password != check_pass:
            return redirect(url_for('registration_parent'))

        # 緯度経度から住所を出す
        lat, lon = atik.address_to_latlon(addres1+addres2)
        # 学校名から緯度経度を出す
        school_latlon = geocoder.osm(school_name, timeout=5.0)
        # 学校名でヒットしなかった場合はとりあえず自宅の座標を入れる
        if school_latlon is None:
            school_lat = lat
            school_lon = lon
        school_lat = school_latlon.latlng[0]
        school_lon = school_latlon.latlng[1]

        db = DB()
        # parent_ID作成用に現在の登録者数取得
        sql = 'select * from parent'
        ID_count = len(db.select(sql))
        # parentに登録
        data = ('P'+str(10000+ID_count), buzer_number, addres1+addres2,
                lat, lon, first_name+last_name,
                mail_addres, password, school_name,
                school_lat, school_lon,)
        sql = 'insert into parent values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        db.insert_update(sql, data)
        db.end_DB()

        # 登録確認メール送信
        mail = My_Mail(app)
        mail.p_registration_mail([mail_addres],
                                 first_name+last_name,
                                 'P'+str(10000+ID_count))
        return redirect(url_for('home'))

# safeguardの登録フォーム表示
@app.route('/registration_safehouse')
def registration_safehouse():
    return render_template('registration_safehouse.html')

# safeguardの登録処理
@app.route('/registration_safehouse_data', methods=['POST'])
def registration_safehouse_data():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mail_addres = request.form['mail_address']
        password = request.form['password']
        check_pass = request.form['check_pass']
        addres1 = request.form['addr11']
        addres2 = request.form['address']

        if password != check_pass:
            return redirect(url_for('registration_parent'))

        # safeguardの画像保存
        img_path = None
        if 'uploadfile' in request.files:
            imgfile = request.files['uploadfile']
            if imgfile and allowed_file(imgfile.filename):
                filename = secure_filename(imgfile.filename)
                img_path = os.path.join(upload_folder, filename)
                imgfile.save(img_path)

        # 住所を緯度経度変換
        lat, lon = atik.address_to_latlon(addres1+addres2)
        db = DB()
        # safeguard_ID作成のために現在の登録数を取得
        sql = 'select * from safeguard'
        ID_count = len(db.select(sql))
        # safeguardの登録
        data = ('S'+str(10000+ID_count), addres1+addres2,
                lat, lon,
                first_name+last_name, mail_addres,
                password, img_path)
        sql = 'insert into safeguard values (%s,%s,%s,%s,%s,%s,%s,%s)'
        db.insert_update(sql, data)
        db.end_DB()

        # 登録確認メールの送信
        mail = My_Mail(app)
        mail.s_registration_mail([mail_addres],
                                 first_name+last_name,
                                 'S'+str(10000+ID_count))
        return redirect(url_for('home'))

# マップ表示
@app.route('/map')
@login_required
def map():
    user_flag = 0
    db = DB()
    # 今までに発生した事件を取得
    sql = 'select * from occur;'
    occurdata = db.select(sql)
    # safeguardの家の場所を取得
    sql = 'select * from safeguard;'
    safeguarddata = db.select(sql)
    # ログインしている(マップを見る)ユーザー情報取得(parent)
    sql = ('select buzzer_num,parent_lat,parent_lon,parent_name'
           ' from parent where parent_ID=%s;')
    inuserdata = db.select(sql, (current_user.id,))
    if not inuserdata:  # parentではないときsafeguardの処理
        user_flag = 1
        sql = ('select safeguard_ID,safeguard_lat,safeguard_lon,safeguard_name'
               ' from safeguard where safeguard_ID=%s;')
        inuserdata = db.select(sql, (current_user.id,))
    # map表示用(JavaScript)に渡す用のJson作成
    create_json = cj.My_Json()
    data = create_json.data_molding(0, occurdata,
                                    1, safeguarddata,
                                    inuserdata, user_flag)
    db.end_DB()
    error_text = None
    try:
        is_error = request.args.get('is_error')
        if int(is_error):
            error_text = "すべての項目を入力してください"
        # マップ表示
        return render_template('map_display.html',
                           data=data,
                           name=inuserdata[0][3],
                           error_text = error_text)
    except:
        return render_template('map_display.html',
                           data=data,
                           name='ログイン中 : ' + inuserdata[0][3] + 'さん')

@app.route('/ab_map', methods=['POST'])
def ab_map():
    if request.method == 'POST':
        buzzer_num = request.form['buzzer_num']
        nowtime = request.form['nowtime'].replace(' ','-')
    db = DB()
    regular_latlon_sql = ("select * from regular_data "
                          "where date_format(regular_time, \'%Y-%m-%d\')"
                          "=date_format(\'{0}\',\'%Y-%m-%d\') and "
                          "buzzer_num=\'{1}\'").format(nowtime, buzzer_num)
    regular_latlon = db.select(regular_latlon_sql)
    create_json = cj.My_Json()
    abjson = create_json.abnormal_json(regular_latlon)
    db.end_DB()
    return render_template('map_display.html',
                           data = abjson,
                           name = '異常検知')

@app.route('/occurmap', methods=['POST'])
def occurmap():
    if request.method == 'POST':
        lat = request.form['lat']
        lon = request.form['lon']
        nowtime = request.form['nowtime']
    occur_plot = [{'lat' : float(lat),
                  'lon' : float(lon),
                  'buzzer_num' : '0'},
                  {'kind' : 0,
                  'lat' : float(lat),
                  'lon' : float(lon),
                  'time' : nowtime}]
    return render_template('map_display.html',
                           data = occur_plot,
                           name = '発生地点')


# 発生事件の編集
@app.route('/add_occur_data', methods=['POST'])
def add_occur_data():
    if request.method == 'POST':
        # checkboxで編集された内容を取得
        gender = request.form.getlist('gender')
        age = request.form.getlist('age')
        casedata = request.form.getlist('case')
        latlon = request.form.getlist('latlon')
        if not casedata or not gender or not age:
            return redirect(url_for('map', is_error=1))
        # 発生した事件の内容を変更
        db = DB()
        sql = ('update occur set '
               'occur_case=%s,occur_gender=%s,occur_age=%s'
               ' where occur_lat=%s and occur_lon=%s;')
        data = (','.join(casedata), gender[0], age[0],
                latlon[0], latlon[1],)
        db.insert_update(sql, data)
        db.end_DB()
    return redirect(url_for('map'))

# 異常検知のメール(使用していない)
@app.route('/abnormal_mail')
def ab_send_mail():
    mail = My_Mail(app)
    mail.ab_send_mail([['a', 'mail_address']],
                      '2019/09/24/ 16:49:37',
                      'address')
    return redirect(url_for('home'))

# ブザーが押された時のメール(使用していない)
@app.route('/buzzer_mail')
def bz_send_mail():
    mail = My_Mail(app)
    mail.pbz_send_mail(['mail_address'])
    mail.sbz_send_mail(['mail_address'])
    return redirect(url_for('home'))

# wioからデータを取得していろいろする
@app.route('/wio', methods=['GET', 'POST'])
def get_wio_data():
    if request.method == 'GET':
        wio_lat = float(request.args.get('lat'))
        wio_lon = float(request.args.get('lon'))
        flag = int(request.args.get('flag'))
        parent_ID = request.args.get('parent_ID')
        buzzer_num = request.args.get('buzzer_num')

    if request.method == 'POST':
        wio_lat = float(request.form['lat'])
        wio_lon = float(request.form['lon'])
        flag = int(request.form['flag'])
        parent_ID = request.form['parent_ID']
        buzzer_num = request.form['buzzer_num']

    if wio_lat == 0:
        wio_lat = 31
    if wio_lon == 0:
        wio_lon = 131

    # latlonを住所変換
    occur_address = cj.iktoaddress(wio_lat, wio_lon)
    if occur_address is None:
        occur_address = 'address'
    # 現在時刻の取得
    jtz = pytz.timezone('Asia/Tokyo')
    nowtime = datetime.now(jtz).strftime('%Y-%m-%d %H-%M-%S')

    mail = My_Mail(app)
    db = DB()

    # ブザーの持ち主(保護者)のデータを取得し送信
    sql = ('select parent_name,parent_mail_address from parent'
           ' where parent_ID=%s')
    pdata = db.select(sql, (parent_ID,))

    # 定期通信用
    if flag == 0:
        # 危険エリア最適化
        area_flag = 0
        # 危険エリアに入っているか
        sql = ('select occur_ID,area_concentration from Hazardous_area'
               ' where area_a_lat>=%s and area_b_lat<=%s and area_a_lon<=%s'
               ' and area_b_lon>=%s and miss_flag!=1')
        data = (wio_lat, wio_lat, wio_lon, wio_lon,)
        area_data = db.select(sql, data)
        # 危険エリアに入っていたら
        if area_data:
            for ac in area_data:
                acon_dict = json.loads(ac[1])
                for i in range(1, 6):
                    for j in range(1, 6):
                        key = 'co' + str(i) + str(j)
                        # メッシュ化したマスのどこかを調べる
                        if acon_dict[key][0][0] <= wio_lon and \
                           acon_dict[key][0][1] >= wio_lon and \
                           acon_dict[key][1][0] >= wio_lat and \
                           acon_dict[key][1][1] <= wio_lat:
                            # 濃度を減らす
                            acon_dict[key][2] = acon_dict[key][2] - 1
                            area_flag = 1
                # DBの濃度情報を更新
                sql = ('update Hazardous_area set area_concentration=%s'
                       ' where occur_ID=%s')
                data = (json.dumps(acon_dict), ac[0],)
                db.insert_update(sql, data)
        
        # 家または学校の情報をとる
        school_house_sql = ('select parent_lat,parent_lon,'
                            'school_lat,school_lon from parent'
                            ' where parent_ID=%s')
        school_house_data = db.select(school_house_sql, (parent_ID,))
        # 学校から現在地の距離を計算
        cd = CalcDistance([[school_house_data[0][0],school_house_data[0][1],'name','address']])
        school_dis = cd.cal_rho(wio_lat, wio_lon)
        # 家から現在地の距離を計算
        cd = CalcDistance([[school_house_data[0][2],school_house_data[0][3],'name','address']])
        home_dis = cd.cal_rho(wio_lat, wio_lon)
        if float(school_dis[0]) >= 100 or float(home_dis[0]) >= 50:
            if area_flag == 1:
                area_flag = 4
            else :
                area_flag = 3

        # 異常検知
        knn = KNN2d(buzzer_num)
        result = knn.main(wio_lat, wio_lon)
        if result:
            # メール送信
            mail.ab_send_mail(pdata, nowtime, occur_address, buzzer_num)

        # 異常検知用のDBに入れる
        sql = "insert into regular_data value (%s,%s,%s,%s)"
        data = (buzzer_num, wio_lat, wio_lon, nowtime,)
        db.insert_update(sql, data)
        db.end_DB()
        return str(area_flag)

    # ボタンが押された用
    elif flag:
        sql = 'select * from occur'
        lendata = len(db.select(sql))
        # 事件をoccurに保存
        sql = ('insert into occur(occur_ID,parent_ID,buzzer_num,occur_lat,'
               'occur_lon,occur_time,occur_address)'
               ' value (%s,%s,%s,%s,%s,%s,%s)')
        data = (lendata+1, parent_ID, buzzer_num,
                wio_lat, wio_lon, nowtime, occur_address,)
        db.insert_update(sql, data)
        # 保存した事件のoccur_IDを取得
        sql = ('select occur_ID from occur'
               ' where parent_ID=%s and occur_lat=%s and occur_lon=%s')
        data = (parent_ID, wio_lat, wio_lon,)
        occur_ID = db.select(sql, data)[-1][0]
        # 保護者にメール送信
        mail.pbz_send_mail(pdata, nowtime,
                           occur_address, occur_ID,
                           parent_ID, buzzer_num,
                           wio_lat, wio_lon)
        # safeguardの情報取得
        sql = ('select'
               ' safeguard_lat,safeguard_lon,'
               'safeguard_name,safeguard_mail_address'
               ' from safeguard')
        sdata = db.select(sql)
        cd = CalcDistance(sdata)
        # 発生地点から500m以内にある家のリストを取得し、送信
        s_namail_list = cd.choice_senduser(cd.cal_rho(wio_lat, wio_lon))
        if s_namail_list:
            mail.sbz_send_mail(s_namail_list, nowtime, occur_address, wio_lat, wio_lon)
        # 対角の座標取得(発生地点を中心)
        edge_ab = great_circle(distance=100*math.sqrt(2),
                               azimuth=[135, -45],
                               latitude=wio_lat,
                               longitude=wio_lon)
        # 濃度を保持するJsonの作成
        create_json = cj.My_Json()
        coo_dict = create_json.concentration_json(edge_ab)
        # JsonをHazardous_areaに保存
        sql = ('insert into Hazardous_area'
               '(occur_ID,area_a_lat,area_a_lon,'
               'area_b_lat,area_b_lon,area_concentration)'
               'value (%s,%s,%s,%s,%s,%s)')
        data = (occur_ID, coo_dict['a'][0],
                coo_dict['a'][1],
                coo_dict['b'][0],
                coo_dict['b'][1],
                json.dumps(coo_dict['latlon']),)
        db.insert_update(sql, data)
        db.end_DB()
        return '2'
    return '0'

# ブザーの誤操作用
@app.route('/mistake', methods=['POST'])
def mistake():
    if request.method == 'POST':
        occur_ID = request.form['occur_ID']
        parent_ID = request.form['parent_ID']
        buzzer_num = request.form['buzzer_num']
    # occurのmiss_flagを1にする
    db = DB()
    sql = ('update occur set miss_flag=1'
           ' where occur_ID=%s and parent_ID=%s and buzzer_num=%s')
    data = (occur_ID, parent_ID, buzzer_num,)
    db.insert_update(sql, data)
    # Hazardous_areaのmiss_flagを1にする
    sql = 'update Hazardous_area set miss_flag=1 where occur_ID=%s'
    db.insert_update(sql, (occur_ID,))
    db.end_DB()
    return redirect(url_for('home'))

# 便利ツール
# wioからデータを送信したようにする仮のフォーム
@app.route('/wio_form')
def wio_form():
    return render_template('wio_form.html')

# db表示関連
@app.route('/db_login')
def db_login():
    return render_template('db_login.html')

@app.route('/show_db', methods=['GET','POST'])
def show_db():
    if request.method == 'GET':
        return redirect(url_for('db_login'))
    if request.method == 'POST':
        name = request.form['id']
        password = request.form['password']
        if name == 'machimori' and password == 'admin':
            db = DB()
            sql = 'select * from occur;'
            occurdata = db.select(sql)
            sql = 'select * from safeguard;'
            safedata = db.select(sql)
            sql = 'select * from parent;'
            parentdata = db.select(sql)
            sql = 'select * from Hazardous_area;'
            areadata = db.select(sql)
            sql = 'select * from regular_data;'
            regulardata = db.select(sql)
            return render_template('db.html',
                                   occurdata = occurdata,
                                   safedata = safedata,
                                   parentdata = parentdata,
                                   areadata = areadata,
                                   regulardata = regulardata)

@app.route('/delete_columns', methods=['POST'])
def delete_columns():
    if request.method == 'POST':
        btnname = request.form['btn']
        clm_data = request.form.getlist(btnname)
        db = DB()
        if len(clm_data) == 11:
            sql = ('delete from parent where'
                   ' parent_ID=%s and buzzer_num=%s'
                   ' and parent_lat=%s and parent_lon=%s'
                   ' and parent_mail_address=%s and parent_password=%s'
                   ' and school_lat=%s and school_lon=%s')
            data = (clm_data[0], clm_data[1], clm_data[3], clm_data[4],
                    clm_data[6], clm_data[7], clm_data[9], clm_data[10],)
        if len(clm_data) == 9:
            sql = ('delete from occur where'
                   ' occur_ID=%s and parent_ID=%s and buzzer_num=%s'
                   ' and occur_lat=%s and occur_lon=%s')
            data = (clm_data[0], clm_data[1], clm_data[2],
                    clm_data[3], clm_data[4],)
        if len(clm_data) == 8:
            sql = ('delete from safeguard where'
                   ' safeguard_ID=%s'
                   ' and safeguard_lat=%s and safeguard_lon=%s'
                   ' and safeguard_mail_address=%s and safeguard_password=%s'
                   ' and safeguard_img_path=%s')
            data = (clm_data[0], clm_data[2], clm_data[3],
                    clm_data[5], clm_data[6],)
        if len(clm_data) == 7:
            sql = ('delete from Hazardous_area where'
                   ' occur_ID=%s and area_a_lat=%s and area_a_lon=%s'
                   ' and area_b_lat=%s and area_b_lon=%s')
            data = (clm_data[0], clm_data[1], clm_data[3], clm_data[4],)
        if len(clm_data) == 4:
            sql = ('delete from regular_data where'
                   ' buzzer_num=%s and regular_lat=%s'
                   ' and regular_lon=%s')
            data = (clm_data[0], clm_data[1], clm_data[2],)
        db.insert_update(sql, data)
        db.end_DB()
        
    return redirect(url_for('show_db'))


if __name__ == "__main__":
    app.run(debug=True)
