import os
import datetime
# import requests
import urllib
import http.cookiejar
import base64

def download_ocean_currents(url, save_path, username = 'TomHeaven', password = 'TomSimple123'):
    # print('url', url)
    password_mgr = urllib.request.HTTPPasswordMgr()
    top_level_url = "https://urs.earthdata.nasa.gov"
    password_mgr.add_password(None, top_level_url, username, password)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(handler, 
                                        #  urllib.request.HTTPSHandler(debuglevel=1), 
                                         urllib.request.HTTPCookieProcessor(cookie_jar)
                                         )
    urllib.request.install_opener(opener)
    
    request = urllib.request.Request(url)
    credentials = ('%s:%s' % (username, password))
    encoded_credentials = base64.b64encode(credentials.encode('ascii'))
    request.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))
    #request.add_header('cookie', cookie_jar)

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
    base_url = 'https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/OSCAR_L4_OC_INTERIM_V2.0/oscar_currents_interim_'
    save_folder = 'ocean_currents'
    start_date = datetime.datetime.strptime("2021-01-01", "%Y-%m-%d")
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)
    for i in range(366+365):
        date = start_date + datetime.timedelta(days=i)
        data_str = date.strftime("%Y%m%d")
        print("Date", i, data_str)
        url = base_url + data_str + '.nc'
        download_ocean_currents(url, os.path.join(save_folder, 'oscar_currents_interim_' + data_str + ".nc"))
        