# netcdf2json

Convert netcdf4 ocean current data to json for Null School Earth project.

## How to use
+ Setup NullSchool Earth project from: https://github.com/cambecc/earth
+ Download ocean current data from: https://cmr.earthdata.nasa.gov/virtual-directory/collections/C2102959417-POCLOUD/temporal and put .nc files in `in` folder.
+ Make `out` folder.
+ run
```
python3 netcdf2json.py
```
and json files should be generated in the `out` folder.
+ copy catalog.json and .json files in the `out` folder to `public\data\oscar` folder of the Earth project.

## Tools
+ download ocean current data
```
 python3 oscar_download.py
 # proxy=127.0.0.1:1080 python3 oscar_download.py
```