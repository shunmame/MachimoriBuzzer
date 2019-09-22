from flask_mail import Mail, Message

class My_Mail:
    def __init__(self, app):
        self.mail = Mail(app)

    def ab_send_mail(self, senddata, nowtime, address):
        msg = Message("[まちもりブザー]異常を検知しました",  #title
                      sender="sysken.machimori@gmail.com",  # 送信元
                      recipients=[senddata[0][1]],  # 送信先
                      charset="shift_jis")  # 日本語表示するため
        msg.html = """
        <!DOCTYPE html>
        <head>
        </head>
        <body style="background-color:rgb(255,183,36);color:black;padding: 1em 2em;">
        <header>
        <div class="header-logo">
            <h2>まちもりブザーからのお知らせ</h2>
        </div>
        </header>
        <p>こんにちは、松永さま。まちもりブザーのからのお知らせです。</p>
        <p>松永さまのまちもりブザーで異常を検知しました。<br>お子様が普段の通学路から外れた場所を歩いている可能性がありますのでご注意ください。</p>
        <p>時間 : {0}</p>
        <p>住所 : {1}</p>
        <br>
        <p>以下のサイトで、街の危険エリアやこどもをまもるいえを示した「まちもりマップ」がご確認できます。</p>
        <p>machimori.japanwest.cloudapp.azure.com</p>
        </body>
        </html>
        """.format(nowtime, address)
        self.mail.send(msg)  # メール送信

    # parent buzzer
    def pbz_send_mail(self, senddata, nowtime, address, occur_ID, parent_ID, buzzer_num):
        msg = Message("[まちもりブザー]ブザーが鳴らされました",
                      sender="sysken.machimori@gmail.com",
                      bcc=[senddata[0][1]],
                      charset="shift_jis")
        msg.html = """
        <!DOCTYPE html>
        <head>
        </head>
        <body style="background-color:rgb(255,183,36);color:black;padding: 1em 2em;">
        <header>
        <div class="header-logo">
            <h2>[保護者]まちもりブザーからのお知らせ</h2>
        </div>
        </header>
        <p>こんにちは、{0}さま。まちもりブザーのからのお知らせです。</p>
        <p>{0}さまのまちもりブザーが鳴らされました。<br>お子様に何らかの危険が迫っている可能性があります。</p>
        <p>発生時刻：{1}<br>発生地点：{2}</p>
        <br> 
        <p>もし誤操作だった場合は、こちらのサイトにアクセスしていただき、お取消しいただきますようお願いします。</p>
        <p>machimori.japanwest.cloudapp.azure.com/mistake?occur_ID={3}&parent_ID={4}&buzzer_num={5}</p>
        <br>
        <p>以下のサイトで、街の危険エリアやこどもをまもるいえを示した「まちもりマップ」がご確認できます。</p>
        <p>machimori.japanwest.cloudapp.azure.com</p>
        </body>
        </html>
        """.format(senddata[0][0], nowtime, address, occur_ID, parent_ID, buzzer_num)
        self.mail.send(msg)

    # safeguard buzzer
    def sbz_send_mail(self, sdata, nowtime, address):
        for sd in sdata:
            msg = Message("[まちもりブザー]ブザーが鳴らされました",
                          sender="sysken.machimori@gmail.com",
                          bcc=[sd['mail_address']],
                          charset="shift_jis")
            msg.html = """
            <!DOCTYPE html>
            <head>
            </head>
            <body style="background-color:rgb(255,183,36);color:black;padding: 1em 2em;">
            <header>
            <div class="header-logo">
                <h2>[こどもをまもるいえ]まちもりブザーからのお知らせ</h2>
            </div>
            </header>
            <p>こんにちは、{0}さま。まちもりブザーのからのお知らせです。</p>
            <p>{0}さまのお近くでまちもりブザーが鳴らされました。<br>お近くを通行中の子どもに何らかの危険が迫っている可能性がありますのでご確認とご対応をお願いします。</p>
            <p>もし、子どもが被害にあっている様子を確認された場合には、警察などへの連絡や子どもの保護をお願いします。</p>
            <p>発生時刻：{1}<br>発生地点：{2}</p>
            <br>
            <p>以下のサイトで、街の危険エリアやこどもをまもるいえを示した「まちもりマップ」がご確認できます。</p>
            <p>machimori.japanwest.cloudapp.azure.com</p>
            </body>
            </html>
            """.format(sd['name'], nowtime, address)
            self.mail.send(msg)

    def wio_get_mail(self, mail_addresses, flag_text, lat, lon):
        msg = Message("[連絡用]Wioからデータがきました",
                      sender="sysken.machimori@gmail.com",
                      bcc=mail_addresses,
                      charset="shift_jis")
        msg.body = "Wioからデータがきました。\n" + flag_text + "\nlat : " + str(lat) + "\nlon : " + str(lon)
        self.mail.send(msg)

    def p_registration_mail(self, mail_addresses, parent_name, parent_ID):
        msg = Message("[まちもりブザー]ブザー新規登録",
                      sender="sysken.machimori@gmail.com",
                      recipients=mail_addresses,
                      charset="shift_jis")
        msg.html = """
        %sさんのIDは%sです
        """ % (parent_name, parent_ID)
        self.mail.send(msg)

    def s_registration_mail(self, mail_addresses, parent_name, parent_ID):
        msg = Message("[まちもりブザー]こどもをまもるいえ新規登録",
                      sender="sysken.machimori@gmail.com",
                      recipients=mail_addresses,
                      charset="shift_jis")
        msg.html = """
        %sさんのIDは%sです
        """ % (parent_name, parent_ID)
        self.mail.send(msg)


if __name__ == "__main__":
    print('done')
