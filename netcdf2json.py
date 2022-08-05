"""
Read in a netCDF file and output the u and v data to json. Write one file per
time step for compatibility with the earth package:
    https://github.com/cambecc/earth
"""

import os
import glob
import json
import multiprocessing
import traceback

import numpy as np

from netCDF4 import Dataset, num2date
from datetime import datetime
from scipy.interpolate import griddata
import tqdm

DEBUG = False


def main(f):
    """
    Function to run the main logic. This is mapped with the multiprocessing
    tools to run in parallel.
    """
    
    def fix_data(var, config, extranan=np.inf):
        var.x[var.x < 0] = var.x[var.x < 0] + 360
        var.data[np.isnan(var.data)] = config.nanvalue
        # Fix unrealistic values from the interpolation to the nanvalue.
        var.data[var.data > extranan] = config.nanvalue
        var.data[var.data < -extranan] = config.nanvalue
        return var
        

    def interpolate(var, r, config, extranan=np.inf):
        """
        Interpolate the data in u.data and v.data onto a grid from 0 to 360 and
        -80 to 80.
        Parameters
        ----------
        var : Process
            Process class objects with the relevant data to interpolate.
        r : float
            Grid resolution for the interpolation.
        config : Config
            Config class with the various configuration parameters for the data
            in var.
        extranan : float
            An extra check for nonsense data. Set to np.inf by default (i.e.
            ignored).
        Returns
        -------
        vari : Process
            Updated class with the interpolated data.
        """

        # Move longitudes to 0-360 instead of -180 to 180.
        var.x[var.x < 0] = var.x[var.x < 0] + 360
        lon, lat = np.arange(0, 360, r), np.arange(-80, 80 + r, r)
        LON, LAT = np.meshgrid(lon, lat)
        X, Y = np.meshgrid(var.x, var.y)
        X, Y, VAR = X.flatten(), Y.flatten(), var.data.flatten()
        if DEBUG:
            print('var', var.x.shape, var.y.shape)
            print('X', len(X))
        var.data = griddata((X, Y), VAR, (LON.flatten(), LAT.flatten()))
        var.data = np.reshape(var.data, (len(lat), len(lon)))
        var.data[np.isnan(var.data)] = config.nanvalue
        # Fix unrealistic values from the interpolation to the nanvalue.
        var.data[var.data > extranan] = config.nanvalue
        var.data[var.data < -extranan] = config.nanvalue
        # Update the metadata
        var.x, var.y = LON, LAT
        var.dx, var.dy = r, r
        var.nx, var.ny = len(lon), len(lat)
        del(lon, lat, LON, LAT, X, Y, VAR, r)

        return var


    print('File {} of {}'.format(f + 1, len(files)))

    uconfig = Config(file=files[f],
            calendar='noleap',
            clip={'depthu':(0, 1), 'time':(0, 1)})
    try:
        if DEBUG:
            print('file', files[f], 'uname', uconfig.uname)
        u = Process(files[f], uconfig.uname, config=uconfig)
        v = Process(files[f], uconfig.vname, config=uconfig)
    except Exception:
        print(traceback.format_exc()) 
        print('Warning: interpolation for {} failed.'.format(files[f]))
        return

    r = 1 # native resolution, but on a sensible grid.
    #u = interpolate(u, r, uconfig, extranan=100)
    #u = fix_data(u, uconfig, extranan=100)
    
    if DEBUG:
        print('uvstem', os.path.splitext(uconfig.file)[0].split('_')[-1])

    uvstem = os.path.join(out, '%s-surface-currents-oscar-0.25' %
             os.path.splitext(uconfig.file)[0].split('_')[-1]
            )

    # Write out the JSON of the UV data and the chlorophyll data.
    W = WriteJSON(u, v, uconf=uconfig, vconf=uconfig, fstem=uvstem)


class Config():
    """
    Class for storing netCDF configuration options.
    Parameters
    ----------
    file : str, optional
        Full paths to the netCDF file.
    uname, vname, xname, yname, tname : str
        Names of the u and v velocity component variable names, and the x,
        y and time variable names.
    basedate : str, optional
        The time to which the time variable refers (assumes time is stored as
        units since some date). Format is "%Y-%m-%d %H:%M:%S".
    calendar : str, optional
        netCDF calendar to use. One of `standard', `gregorian',
        `proleptic_gregorian' `noleap', `365_day', `360_day', `julian',
        `all_leap' or `366_day'. Defaults to `standard'.
    xdim, ydim, tdim : str, optional
        Names of the x, y and time dimensions in the netCDF files.
    clip : dict, optional
        Dictionary of the index and dimension name to extract from the
        netCDF variable. Can be multiple dimensions (e.g. {'time_counter':(0,
        100), 'depthu':0}).
    nanvalue : float, optional
        Specify a value to replace with null values when exporting to JSON.
    Author
    ------
    Pierre Cazenave (Plymouth Marine Laboratory)
    """

    def __init__(self, file=None, uname=None, vname=None, xname=None, yname=None, tname=None, basedate=None, calendar=None, xdim=None, ydim=None, tdim=None, clip=None, nanvalue=None):
        self.__dict = {}
        self.__set(file, 'file', str)
        self.__set(uname, 'uname', str)
        self.__set(vname, 'vname', str)
        self.__set(xname, 'xname', str)
        self.__set(yname, 'yname', str)
        self.__set(tname, 'tname', str)
        self.__set(basedate, 'basedate', str)
        self.__set(calendar, 'calendar', str)
        self.__set(xdim, 'xdim', str)
        self.__set(ydim, 'ydim', str)
        self.__set(tdim, 'tdim', str)
        self.__set(clip, 'clip', dict)
        self.__set(nanvalue, 'nanvalue', float)

    def __set(self, value, target_name, value_type):
        if value:
            actual = value
        else:
            actual = self.__default[target_name]
        self.__dict[target_name] = value_type(actual)

    def __file(self):
        return self.__dict['file']

    def __uname(self):
        return self.__dict['uname']

    def __vname(self):
        return self.__dict['vname']

    def __xname(self):
        return self.__dict['xname']

    def __yname(self):
        return self.__dict['yname']

    def __tname(self):
        return self.__dict['tname']

    def __basedate(self):
        return self.__dict['basedate']

    def __calendar(self):
        return self.__dict['calendar']

    def __xdim(self):
        return self.__dict['xdim']

    def __ydim(self):
        return self.__dict['ydim']

    def __tdim(self):
        return self.__dict['tdim']

    def __clip(self):
        return self.__dict['clip']

    def __nanvalue(self):
        return self.__dict['nanvalue']

    file = property(__file)
    uname = property(__uname)
    vname = property(__vname)
    xname = property(__xname)
    yname = property(__yname)
    tname = property(__tname)
    basedate = property(__basedate)
    calendar = property(__calendar)
    xdim = property(__xdim)
    ydim = property(__ydim)
    tdim = property(__tdim)
    clip = property(__clip)
    nanvalue = property(__nanvalue)
    
    if DEBUG:
        print('file', file)
        print('uname', uname)

    # Set some sensible defaults. These are based on my concatenated netCDFs of
    # Lee's global model run (so NEMO, I guess).
    __default = {}
    __default['file'] = 'test_u.nc'
    __default['uname'] = 'u'
    __default['vname'] = 'v'
    __default['xname'] = 'lon'
    __default['yname'] = 'lat'
    __default['tname'] = 'time'
    __default['basedate'] = '1990-01-01 00:00:00' # units: days since 1990-1-1
    __default['calendar'] = 'standard'
    __default['xdim'] = 'x'
    __default['ydim'] = 'y'
    __default['tdim'] = 'time'
    __default['clip'] = {'depth':(0, 1)}
    __default['nanvalue'] = 9.969209968386869e+36


class Process():
    """
    Class for loading data from the netCDFs and preprocessing ready for writing
    out to JSON.
    """

    def __init__(self, file, var, config=None):
        if config:
            self.config = config
        else:
            self.config = Config()

        self.__read_var(file, var)

    def __read_var(self, file, var):
        ds = Dataset(file, 'r')
        if DEBUG:
            print('ds', ds.__dict__)
            print('self.config.xdim', self.config.xdim) # == x
            print('ds.dimensions', ds.dimensions, ds.dimensions['time'])
            #print('ds.variables', ds.variables['lat']) # lat, lon, time, u, v, ug, vg # current shape = (1, 1440, 719)
            print('ds.variables',  ds.variables['lon'][:].shape, ds.variables['u'][:][0].shape, ds.variables['ug'][:][0].shape)  # dict_keys(['lat', 'lon', 'time', 'u', 'v', 'ug', 'vg'])
            print('var', var)
        self.nx = ds.dimensions['longitude'].size
        self.ny = ds.dimensions['latitude'].size

        self.dx = 0.25
        self.dy = 0.25

        self.x = ds.variables['lon'][:]
        self.y = ds.variables['lat'][:]

        # Sort out the dimensions.
        if self.config.clip:
            alldims = {}
            for key, val in list(ds.variables.items()):
                if DEBUG:
                    print('key', key, 'val', len(val))
                alldims[key] = (0, len(val))
            vardims = ds.variables[var].dimensions
            
            if DEBUG:
                print('alldims', alldims)
                print('vardims', vardims)
        
        self.data = np.flipud(np.squeeze(ds.variables[var][:]).T).flatten()
        self.data = np.around(self.data, 2)

        if DEBUG:
            print('ds var', ds.variables[var][:].shape)
            print('self.data', self.data.shape)

        self.time = ds.variables['time'][:]
        self.Times = []
        for t in self.time:
            date = num2date(
                t - 8,
                'days since {}'.format(self.config.basedate),
                calendar=self.config.calendar
                )
            self.Times.append(date)
            
            if DEBUG:
                print('self.time', self.time)
                print('date', date)

        ds.close()


class WriteJSON():
    """
    Write the Process object data to JSON in the earth format.
    Parameters
    ----------
    u, v : Process
        Process classes of data to export. Each time step will be exported to
        a new file. If v is None, only write u.
    uconf, vconf : Config
        Config classes containing the relevant information. If omitted, assumes
        default options (see `Config.__doc__' for more information).
    """

    def __init__(self, u, v=None, uconf=None, vconf=None, fstem=None):
        self.data = {}

        if uconf:
            self.uconf = uconf
        else:
            self.uconf = Config()

        if vconf:
            self.vconf = vconf
        else:
            self.vconf = Config()

        if fstem:
            self.fstem = fstem
        else:
            self.fstem = '{}-{}'.format(
                    os.path.split(os.path.splitext(self.uconf.file)[0])[-1],
                    os.path.split(os.path.splitext(self.vconf.file)[0])[-1]
                    )

        self.header = {}
        # The y data is complicated because NEMO has twin poles.
        self.header['template'] = {
                'discipline':10,
                'disciplineName':'Oceanographic_products',
                'center':-3,
                'centerName':'Plymouth Marine Laboratory',
                'significanceOfRT':0,
                'significanceOfRTName':'Analysis',
                'parameterCategory':1,
                'parameterCategoryName':'Currents',
                'parameterNumber':2,
                'parameterNumberName':'U_component_of_current',
                'parameterUnit':'m.s-1',
                'forecastTime':0,
                'surface1Type':160,
                'surface1TypeName':'Depth below sea level',
                'surface1Value':15,
                'numberPoints':u.nx * u.ny,
                'shape':0,
                'shapeName':'Earth spherical with radius = 6,367,470 m',
                'scanMode':0,
                'nx':u.nx,
                'ny':u.ny,
                'lo1':u.x.min().astype(float),
                'la1':u.y.max().astype(float),
                'lo2':u.x.max().astype(float),
                'la2':u.y.min().astype(float),
                'dx':u.dx,
                'dy':u.dy
                }

        if v:
            self.write_json(u, uconf, v=v, vconf=vconf)
        else:
            self.write_json(u, uconf)


    def write_json(self, u, uconf, v=None, vconf=None, fstem=None):

        self.data['u'], self.data['v'] = {}, {}
        # Template is based on u data.
        self.data['u']['header'] = self.header['template'].copy()
        # Can't use datetime.strftime because the model starts before 1900.
        date = datetime.strptime(str(u.Times[uconf.clip[uconf.tname][0]]), '%Y-%m-%d %H:%M:%S')
        if DEBUG:
            print('date', date)
        self.data['u']['header']['refTime'] = '{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:06.3f}Z'.format(
                date.year, date.month, date.day, date.hour, date.minute, date.second
                )
        # Add the flattened data.
        self.data['u']['data'] = u.data.flatten().tolist()
        self.data['u']['data'] = [None if i == uconf.nanvalue else i for i in self.data['u']['data']]

        # Do the same for v if we have it.
        if v:
            self.data['v']['header'] = self.header['template'].copy()
            self.data['v']['header']['parameterNumber'] = 3
            self.data['v']['header']['parameterNumberName'] = 'V_component_of_current'
            date = datetime.strptime(str(v.Times[vconf.clip[vconf.tname][0]]), '%Y-%m-%d %H:%M:%S')
            self.data['v']['header']['refTime'] = '{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:06.3f}Z'.format(
                    date.year, date.month, date.day, date.hour, date.minute, date.second
                    )
            self.data['v']['data'] = v.data.flatten().tolist()
            self.data['v']['data'] = [None if i == vconf.nanvalue else i for i in self.data['v']['data']]
            
        if DEBUG:
            print('self.data', self.data['u'].keys(), self.data.keys())

        with open('{}.json'.format(self.fstem), 'w') as f:
            f.write('[')
            for count, var in enumerate(self.data.keys()):
                s = json.dumps(self.data[var])
                f.write(s)
                if count < len(self.data.keys()) - 1: f.write(',')
            f.write(']')

if __name__ == '__main__':
    serial = True
    base = '.'
    out = 'ocean_currents_json'
    out_dir = os.path.join(base, out)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
        
    files = glob.glob(os.path.join(base, 'ocean_currents', 'oscar_currents_interim_*.nc'))

    idx = range(len(files))

    if serial:
        for f in tqdm.tqdm(idx):
            main(f)
    else:
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        pool.map(main, idx)
        pool.close()

    files = glob.glob(os.path.join(base, out, '*.json'))
    files = [os.path.split(i)[-1] for i in files]
    with open(os.path.join(base, 'catalog.json'), 'w') as f:
         json.dump(np.sort(files).tolist(), f)