import os
import datetime
# import requests
import urllib
import http.cookiejar
import base64

def download_wind(url, save_path):
    # print('url', url)
    handler = urllib.request.HTTPHandler()
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(handler, 
                                         # urllib.request.HTTPSHandler(debuglevel=1), 
                                         urllib.request.HTTPCookieProcessor(cookie_jar)
                                         )
    urllib.request.install_opener(opener)
    
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    print('response', response.status)
    if response.status == 200:
        print('Downloading file ...')
        # Save file to working directory
        body = response.read()
        file = open(save_path, 'wb')
        file.write(body)
        file.close()

if __name__ == '__main__':
    base_url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t{}z.pgrb2.1p00.f000&lev_10_m_above_ground=on&var_UGRD=on&var_VGRD=on&&dir=%2Fgfs.{}%2F{}%2Fatmos'
    save_folder = 'wind'
    start_date = datetime.date.today()
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)
    for i in range(0, 10):
        for hour in ['00', '06', '12']:
            date = start_date - datetime.timedelta(days=i)
            date_str = date.strftime("%Y%m%d")
            print("Date", date_str, 'hour', hour)
            url = base_url.format(hour, date_str, hour)
            try: 
                download_wind(url, os.path.join(save_folder, 'wind_' + date_str + '_' + hour + ".grib"))
            except:
                pass
                
        