import numpy as np


class CalcDistance:
    def __init__(self, sdata):
        self.lat_b = np.array([sd[0] for sd in sdata])
        self.lon_b = np.array([sd[1] for sd in sdata])
        self.sname = np.array([sd[2] for sd in sdata])
        self.smail_address = np.array([sd[3] for sd in sdata])

    def cal_rho(self, lat, lon):
        ra = 6378.140   # equatorial radius (km)
        rb = 6356.755   # polar radius (km)
        F = (ra-rb)/ra  # flattening of the earth
        lat_a = np.array([lat])
        lon_a = np.array([lon])
        rad_lat_a = np.radians(lat_a)
        rad_lon_a = np.radians(lon_a)
        rad_lat_b = np.radians(self.lat_b)
        rad_lon_b = np.radians(self.lon_b)
        pa = np.arctan(rb/ra*np.tan(rad_lat_a))
        pb = np.arctan(rb/ra*np.tan(rad_lat_b))
        xx = np.arccos(np.sin(pa) * np.sin(pb) +
                       np.cos(pa) * np.cos(pb) *
                       np.cos(rad_lon_a-rad_lon_b))
        c1 = (np.sin(xx)-xx)*(np.sin(pa)+np.sin(pb))**2/np.cos(xx/2)**2
        c2 = (np.sin(xx)+xx)*(np.sin(pa)-np.sin(pb))**2/np.sin(xx/2)**2
        dr = F/8*(c1-c2)
        rho = ra*(xx+dr)
        rho = rho * 1000
        result_list = []
        for dis, name, md in zip(rho, self.sname, self.smail_address):
            if dis > 500:
                continue
            safeguard_dict = {}
            safeguard_dict['name'] = name
            safeguard_dict['mail_address'] = md
            result_list.append(safeguard_dict)
        return result_list
