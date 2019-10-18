# coding: UTF-8
import json
import requests


def iktoaddress(lat, lon):
    url = ('https://www.finds.jp/ws/rgeocode.php?'
           'json&lat={0}&lon={1}').format(lat, lon)
    response = requests.get(url)
    js = json.loads(response.text)
    try:
        pm = js['result']['prefecture']['pname'] + \
             js['result']['municipality']['mname']
        try:
            sh = js['result']['local'][0]['section'] + \
                 js['result']['local'][0]['homenumber']
            return pm+sh
        except KeyError:
            return pm
    except KeyError:
        return None


class My_Json():
    def data_molding(self, okind, odata, skind, sdata, inuserdata, user_flag):
        plot_list = []
        for ulis in inuserdata:
            plot_dict = {}
            if user_flag == 0:
                plot_dict['buzzer_num'] = ulis[0]
            elif user_flag == 1:
                plot_dict['buzzer_num'] = 'sample01'
            plot_dict['lat'] = ulis[1]
            plot_dict['lon'] = ulis[2]
            plot_list.append(plot_dict)

        for olis in odata:
            if olis[7] == 1:
                continue
            plot_dict = {}
            plot_dict['kind'] = okind
            plot_dict['lat'] = olis[3]
            plot_dict['lon'] = olis[4]
            plot_dict['time'] = olis[5].strftime('%Y/%m/%d %H:%M:%S')
            plot_dict['case'] = olis[8]
            plot_dict['buzzer_num'] = olis[2]
            plot_dict['address'] = olis[6]
            plot_dict['gender'] = olis[9]
            plot_dict['age'] = olis[10]
            plot_list.append(plot_dict)

        for slis in sdata:
            plot_dict = {}
            plot_dict['kind'] = skind
            plot_dict['lat'] = slis[2]
            plot_dict['lon'] = slis[3]
            plot_dict['name'] = slis[4]
            plot_dict['address'] = slis[1]
            plot_dict['img'] = slis[7].lstrip('/var/www/app')
            plot_list.append(plot_dict)
        return plot_list

    def concentration_json(self, edge_ab):
        coordinate_dict = {}
        coordinate_dict['a'] = (edge_ab['latitude'][1],
                                edge_ab['longitude'][1])
        coordinate_dict['b'] = (edge_ab['latitude'][0],
                                edge_ab['longitude'][0])
        diff_lat = abs(edge_ab['latitude'][0] - edge_ab['latitude'][1])
        diff_lon = abs(edge_ab['longitude'][0] - edge_ab['longitude'][1])
        split_lat = diff_lat / 5
        split_lon = diff_lon / 5
        latlon_dict = {}
        for i in range(1, 6):
            for j in range(1, 6):
                latlon_dict['co'+str(i)+str(j)] = ((edge_ab['longitude'][1]+split_lon*(j-1),
                                                   edge_ab['longitude'][0]+split_lon*j),
                                                   (edge_ab['latitude'][1]+split_lat*(i-1),
                                                   edge_ab['latitude'][0]+split_lon*i),
                                                   50)
        coordinate_dict['latlon'] = latlon_dict
        return coordinate_dict

    def abnormal_json(self, regular_latlon):
        regular_latlon_list = []
        regular_latlon_list.append({'lat' : 32,
                                    'lon' : 130,
                                    'buzzer_num' : '0'})
        for latlon in regular_latlon:
            regular_latlon_dict = {}
            regular_latlon_dict["kind"] = 0
            regular_latlon_dict["lat"] = latlon[1]
            regular_latlon_dict["lon"] = latlon[2]
            regular_latlon_dict["time"] = latlon[3].strftime('%Y/%m/%d %H:%M:%S')
            regular_latlon_list.append(regular_latlon_dict)
        return regular_latlon_list


if __name__ == '__main__':
    i_json = My_Json()
    # i_json.data_molding()
