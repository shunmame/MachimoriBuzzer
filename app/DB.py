import mysql.connector
import os
import pandas as pd

class DB:
    def __init__(self):
        self.conn = mysql.connector.connect(user=os.environ['DB_USER'],
                                            password=os.environ['DB_PASS'],
                                            host=os.environ['DB_HOST'],
                                            database=os.environ['DB_DB'],
                                            port=os.environ['DB_PORT'])

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
    df = pd.read_csv('/home/sysken/mapdata.csv')
    for bn,lat,lon,time in zip(df['bn'], df['lat'], df['lon'], df['time']):
        insertsql = 'insert into regular_data values (%s,%s,%s,%s)'
        db.insert_update(insertsql, (bn, lat, lon, time,))
    db.end_DB()
    print('done')
