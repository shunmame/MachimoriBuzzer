import mysql.connector
import os


class DB:
    def __init__(self):
        self.conn = mysql.connector.connect(user=os.environ["DB_USER"],
                                            password=os.environ["DB_PASS"],
                                            host=os.environ["DB_HOST"],
                                            database=os.environ["DB_DB"],
                                            port=os.environ["DB_PORT"])

    def select(self, sql, data=()):
        cur = self.conn.cursor()
        cur.execute(sql, data)
        data = cur.fetchall()
        cur.close
        return data

    def insert_update(self, sql, data=()):
        cur = self.conn.cursor()
        cur.execute(sql, data)
        cur.close
        self.conn.commit()

    def end_DB(self):
        self.conn.close


if __name__ == "__main__":
    db = DB()
    data = db.select('select area_concentration from Hazardous_area;')
    db.end_DB()
    print(data)
