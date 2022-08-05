# netcdf2json

Convert netcdf4 ocean current data to json for Null School Earth project.

## How to Use netcdf2json
+ Setup NullSchool Earth project from: https://github.com/cambecc/earth
+ Download ocean current data from: https://cmr.earthdata.nasa.gov/virtual-directory/collections/C2102959417-POCLOUD/temporal and put .nc files in `in` folder.
+ run
```
python3 netcdf2json.py
```
and json files should be generated in the `out` folder.
+ copy catalog.json and .json files in the `out` folder to `public\data\oscar` folder of the Earth project.

## Addtional Tools and Tutorials
### Data Download Tools
+ download ocean current data of every day from 2021 to 2022.
```
 python3 oscar_download.py
 # if you need to use proxy, add your own proxy url ahead.
 # proxy=127.0.0.1:1081 python3 oscar_download.py
```
and save data in `ocean_currents` folder.
+ download wind data for the last 10 days:
```
python3 wind_download.py
```
and save data in `wind` folder.

### Convert data Format
+ Convert wind data (grib format) to json
```
# The java grib2json tool neeeds to be installed first.
# Please refer to: https://github.com/cambecc/grib2json
python3 grib2json.py
```
+ Convert ocean crrent data (netcdf4 format) to json
```
python3 netcdf2json.py
```