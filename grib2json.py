"""
The script requires grib2json to be installed correctly.
Please refer to: https://github.com/TomHeaven/necdf2json

Author: TomHeaven.
"""

import os
import glob
import json
import multiprocessing
import numpy as np
import tqdm

DEBUG = False

def main(file_path, out_path, over_write=False):
    if not over_write and os.path.isfile(out_path):
        print("Save path exists and will not overwrite.")
        return
    cmd = "grib2json -d -n -o {} {}".format(out_path, file_path)
    os.system(cmd)
    # save to 
    with open(out_path, 'r') as f:
        data_json = json.load(f)
        for i in range(2):
            data = np.around(data_json[i]['data'], 2)
            data_json[i]['data'] = data.tolist()
    
    with open(out_path, 'w') as f:
        json.dump(data_json, f)
            

if __name__ == '__main__':
    serial = True
    base = '.'
    out = 'wind_json'
    out_dir = os.path.join(base, out)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
        
    files = glob.glob(os.path.join(base, 'wind', '*.grib'))

    idx = range(len(files))

    if serial:
        for f in tqdm.tqdm(idx):
            out_path = files[f].replace("wind/",  out + "/")
            out_path =  out_path.replace(".grib", '.json')
            main(files[f], out_path)
            #break
    else:
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        out_path = files[idx].replace("wind/", out + "/")
        out_path =  out_path.replace(".grib", '.json')
        pool.map(main, files[idx])
        pool.close()

    files = glob.glob(os.path.join(base, out, '*.json'))
    files = [os.path.split(i)[-1] for i in files]
    with open(os.path.join(base, 'catalog_wind.json'), 'w') as f:
         json.dump(np.sort(files).tolist(), f)