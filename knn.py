import numpy as np
from DB import DB

# x : lon
# y : lat


class KNN2d:
    def __init__(self, buzzer_num):
        # DBからデータ読み込み
        db = DB()
        sql = ('select regular_lat, regular_lon'
               ' from regular_data where buzzer_num=%s')
        regular_data = db.select(sql, (buzzer_num,))

        # データをself.リストに格納
        self.lon_list = [i[1] for i in regular_data]
        self.lat_list = [i[0] for i in regular_data]

    # wioのデータを受け取り異常検知
    def main(self, lat, lon):
        if self.lon_list != []:
            result = self.__abnormal_decision(self.__knn2d(lon, lat, 5),
                                              0.0008)
            if result == 1:
                return 1
        return 0

    def __knn2d(self, test_x, test_y, k):
        num = self.lon_list.shape[0]
        l_list = []
        for i in range(num):
            xl = self.lon_list[i] - test_x
            yl = self.lat_list[i] - test_y
            l2 = xl ** 2 + yl ** 2
            lr = l2 ** 0.5
            l_list.append(lr)
        l_li = np.array(l_list)
        l_li = np.sort(l_li)
        return l_li[k]

    def __abnormal_decision(self, abnormal, treshold):
        if abnormal > treshold:
            return 1  # 異常
        return 0      # 正常
