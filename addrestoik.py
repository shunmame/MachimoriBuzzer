import requests
from bs4 import BeautifulSoup


def address_to_latlon(address):
    url = 'http://www.geocoding.jp/api/'
    payload = {"v": 1.1, 'q': address}
    r = requests.get(url, params=payload)
    ret = BeautifulSoup(r.text, 'html.parser')
    if ret.find('error'):
        raise ValueError("Invalid address submitted. {address}")
    else:
        lat = ret.find('lat').string
        lon = ret.find('lng').string
    return lat, lon


if __name__ == "__main__":
    address = "熊本県八代市平山新町2627"
    lat, lon = address_to_latlon(address)
    print(lat, lon)
