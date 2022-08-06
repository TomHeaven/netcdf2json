import os
import datetime
# import requests
import urllib
import http.cookiejar
import base64

def download_wind(url, save_path, over_write=False):
    # print('url', url)
    if not over_write and os.path.isfile(save_path):
        print("Save path exists and will not overwrite.")
        return
    
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
    grid = "0p25" # '0p25', '1p00'
    base_url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_{}.pl?file=gfs.t{}z.pgrb2.{}.f0{}&lev_10_m_above_ground=on&var_UGRD=on&var_VGRD=on&&dir=%2Fgfs.{}%2F{}%2Fatmos'
    save_folder = 'wind'
    start_date = datetime.date.today()
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)
    for i in range(0, 10): # 过去天数
        date = start_date - datetime.timedelta(days=i)
        date_str = date.strftime("%Y%m%d")
        for hour in [0, 6, 12, 18]: # 基准小时
            hour_str = "%02d" % hour
            for forecast in range(6): # 预报小时
                real_hour = "%02d" % (hour + forecast)
                print("Date", date_str, 'hour', real_hour)
                url = base_url.format(grid, hour_str, grid, "%02d" % forecast, date_str, hour_str)
                try: 
                    download_wind(url, os.path.join(save_folder, 'wind_' + date_str + '_' + real_hour + ".grib"))
                except:
                    pass
                
        