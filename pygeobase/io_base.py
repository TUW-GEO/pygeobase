# Copyright (c) 2015, Vienna University of Technology, Department of Geodesy
# and Geoinformation. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Vienna University of Technology, Department of
#     Geodesy and Geoinformation nor the names of its contributors may be
#     used to endorse or promote products derived from this software without
#     specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import abc

import numpy as np


class StaticBase(object):

    """
    The StaticBase class serves as a template for i/o objects used in
    GriddedStaticBase.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, filename, mode='r', **kwargs):
        """
        Initialization of i/o object.

        Parameters
        ----------
        filename : str
            File name.
        mode : str, optional
            Opening mode. Default: r           
        """
        self.filename = filename
        self.mode = mode
        self.kwargs = kwargs

    @abc.abstractmethod
    def read(self, gpi):
        """
        Read data for given grid point.

        Parameters
        ----------
        gpi : int
            Grid point index.

        Returns
        -------
        data : numpy.ndarray
            Data set.
        """
        return

    @abc.abstractmethod
    def write(self, data):
        """
        Write data.

        Parameters
        ----------
        data : numpy.ndarray
            Data records.
        """
        return

    @abc.abstractmethod
    def flush(self):
        """
        Flush data.
        """
        return

    @abc.abstractmethod
    def close(self):
        """
        Close file.
        """
        return


class TsBase(object):
    pass


class ImageBase(object):
    pass


class GriddedStaticBase(object):

    """
    The GriddedStaticBase class uses another IO class together with a grid
    object to read/write a dataset under the given path.

    Parameters
    ----------
    path : string
        Path to dataset.
    grid : pytesmo.grid.grids.BasicGrid of CellGrid instance
        Grid on which the time series data is stored.
    ioclass : class
        IO class.
    mode : str, optional
        File mode and can be read 'r', write 'w' or append 'a'. Default: 'r'
    fn_format : str, optional
        The string format of the cell files. Default: '{:04d}'
    ioclass_kws : dict
        Additional keyword arguments for the ioclass.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, grid, ioclass, mode='r', fn_format='{:04d}',
                 ioclass_kws=None):

        self.path = path
        self.grid = grid
        self.ioclass = ioclass
        self.mode = mode
        self.fn_format = fn_format
        self.previous_cell = None
        self.fid = None

        if ioclass_kws is None:
            self.ioclass_kws = {}
        else:
            self.ioclass_kws = ioclass_kws

    def __enter__(self):
        """
        Context manager initialization.

        Returns
        -------
        self : GriddedStaticBase object
            self
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object. The file will be
        closed. The parameters describe the exception that caused the
        context to be exited.

        exc_type :

        exc_value :

        traceback :

        """
        self.close()

    def _open(self, gpi):
        """
        Open file.

        Parameters
        ----------
        gpi : int
            Grid point index.
        """
        cell = self.grid.gpi2cell(gpi)
        filename = os.path.join(self.path, self.fn_format.format(cell))

        if self.previous_cell != cell:
            if self.fid is not None:
                self.close()

            self.fid = self.ioclass(filename, mode=self.mode,
                                    **self.ioclass_kws)
            self.previous_cell = cell

    def read(self, *args, **kwargs):
        """
        Takes either 1 or 2 arguments and calls the correct function
        which is either reading the gpi directly or finding
        the nearest gpi from given lat,lon coordinates and then reading it
        """
        if len(args) == 1:
            data = self.read_gp(args[0], **kwargs)
        if len(args) == 2:
            data = self._read_lonlat(args[0], args[1], **kwargs)

        return data

    def _read_lonlat(self, lon, lat, **kwargs):
        """
        Reading data for given longitude and latitude coordinate.

        Parameters
        ----------
        lon : float
            Longitude coordinate.
        lat : float
            Latitude coordinate.

        Returns
        -------
        data : dict of values
            data record.
        """
        gp, _ = self.grid.find_nearest_gpi(lon, lat)

        return self.read_gp(gp, **kwargs)

    def read_gp(self, gpi):
        """
        Read data for given grid point.

        Parameters
        ----------
        gpi : int
            Grid point index.

        Returns
        -------
        data : numpy.ndarray
            Data set.
        """
        self._open(gpi)

        return self.fid.read(gpi)

    def iter_gp(self):
        """
        Yield all values for all grid points.

        Yields
        ------
        data : pandas.DataFrame
            pandas.DateFrame with DateTimeIndex
        """
        gpi_info = list(self.grid.grid_points())
        gps = np.array(gpi_info, dtype=np.int)[:, 0]

        for gp in gps:
            yield self.read_gp(gp), gp

    def write(self, data):
        """
        Write data.

        Parameters
        ----------
        data : numpy.ndarray
            Data records. A field 'gpi', indicating the grid point index
            has to be included.
        """
        self.write_gp(data['gpi'], data)

    def write_gp(self, gpi, data):
        """
        Write data for given grid point.

        Parameters
        ----------
        gpi : int
            Grid point index.
        data : numpy.ndarray
            Data
        """
        self._open(gpi)
        self.fid.write(data)

    def flush(self):
        """
        Flush data.
        """
        if self.fid is not None:
            self.fid.flush()

    def close(self):
        """
        Close file.
        """
        if self.fid is not None:
            self.fid.close()


class GriddedTsBase(object):

    """
    The GriddedTsBase class uses another IO class together with a grid object
    to read/write a time series dataset under the given path.

    Parameters
    ----------
    path : string
        Path to dataset.
    grid : pytesmo.grid.grids.BasicGrid of CellGrid instance
        Grid on which the time series data is stored.
    ioclass : class
        IO class.
    mode : str, optional
        File mode and can be read 'r', write 'w' or append 'a'. Default: 'r'
    fn_format : str, optional
        The string format of the cell files. Default: '{:04d}'
    ioclass_kws : dict
        Additional keyword arguments for the ioclass.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, grid, ioclass, mode='r', fn_format='{:04d}',
                 read_bulk=False, write_bulk=False, ioclass_kws=None):

        self.path = path
        self.grid = grid
        self.ioclass = ioclass
        self.mode = mode
        self.fn_format = fn_format
        self.previous_cell = None
        self.fid = None
        self.first_write = True
        self._read_bulk = read_bulk
        self._write_bulk = write_bulk

        if ioclass_kws is None:
            self.ioclass_kws = {}
        else:
            self.ioclass_kws = ioclass_kws

    def __enter__(self):
        """
        Context manager initialization.

        Returns
        -------
        self : GriddedBaseTs object
            self
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object. The file will be
        closed. The parameters describe the exception that caused the
        context to be exited.

        exc_type :

        exc_value :

        traceback :

        """
        self.close()

    def _open(self, gpi):
        """
        Open file.

        Parameters
        ----------
        gpi : int
            Grid point index.
        """
        cell = self.grid.gpi2cell(gpi)
        filename = os.path.join(self.path, self.fn_format.format(cell))

        if self.mode == 'r':
            if self._read_bulk:
                if self.previous_cell != cell:
                    self.close()
                    self.previous_cell = cell
                    self.fid = self.ioclass(filename, mode=self.mode,
                                            **self.ioclass_kws)
            else:
                self.close()
                self.fid = self.ioclass(filename, mode=self.mode,
                                        **self.ioclass_kws)

        if self.mode in ['w', 'a']:
            if self._write_bulk:
                if self.previous_cell != cell:
                    self.flush()
                    self.close()
                    self.previous_cell = cell
                    self.__open_write(filename, cell)
            else:
                self.flush()
                self.close()
                self.__open_write(filename, cell)

    def __open_write(self, filename, cell):
        """
        The function checks if the file already exists, in order to
        open the file in append mode for further write calls.

        Parameters
        ----------
        filename : str
            File name.
        cell : int
            Cell number.
        """
        if os.path.exists(filename):
            if self.first_write and self.mode == 'w':
                self.fid = self.ioclass(filename, mode=self.mode,
                                        **self.ioclass_kws)
                self.first_write = False
            else:
                # open in append mode after first write
                self.fid = self.ioclass(filename, mode='a',
                                        **self.ioclass_kws)
        else:
            self.fid = self.ioclass(filename, mode=self.mode,
                                    **self.ioclass_kws)
            self.first_write = False

    def _read_lonlat(self, lon, lat, **kwargs):
        """
        Reading time series for given longitude and latitude coordinate.

        Parameters
        ----------
        lon : float
            Longitude coordinate.
        lat : float
            Latitude coordinate.

        Returns
        -------
        data : pandas.DataFrame
            pandas.DateFrame with DateTimeIndex.
        """
        gp, _ = self.grid.find_nearest_gpi(lon, lat)

        return self.read_gp(gp, **kwargs)

    def _write_lonlat(self, lon, lat, data, **kwargs):
        """
        Write time series for given longitude and latitude coordinate.

        Parameters
        ----------
        lon : float
            Longitude coordinate.
        lat : float
            Latitude coordinate.
        data : numpy.ndarray
            Data records.
        """
        gp, _ = self.grid.find_nearest_gpi(lon, lat)

        return self.write_gp(gp, **kwargs)

    def get_nearest_gp_info(self, lon, lat):
        """
        get info for nearest grid point

        Parameters
        ----------
        lon : float
            Longitude coordinate.
        lat : float
            Latitude coordinate.

        Returns
        -------
        gpi : int
            Grid point index of nearest grid point.
        gp_lon : float
            Lontitude coordinate of nearest grid point.
        gp_lat : float
            Latitude coordinate of nearest grid point.
        gp_dist : float
            Geodetic distance to nearest grid point.
        """
        gpi, gp_dist = self.grid.find_nearest_gpi(lon, lat)
        gp_lon, gp_lat = self.grid.gpi2lonlat(gpi)

        return gpi, gp_lon, gp_lat, gp_dist

    def write_gp(self, gpi, data, **kwargs):
        """
        Write data for given grid point.

        Parameters
        ----------
        gpi : int
            Grid point index.
        data : numpy.ndarray
            Data records.
        """
        if self.mode in ['r']:
            raise IOError("File is not open in write/append mode")

        self._open(gpi)

        lon, lat = self.grid.gpi2lonlat(gpi)

        self.fid.write_ts(gpi, data, lon=lon, lat=lat, **kwargs)

        if self._write_bulk:
            self.flush()
            self.close()

    def write_ts(self, *args, **kwargs):
        """
        Takes either 2 or 3 arguments (the last one always needs to be the
        data to be written) and calls the correct function which is either
        writing the gpi directly or finding the nearest gpi from given
        lon, lat coordinates and then reading it.
        """
        if len(args) == 2:
            self.write_gp(args[0], args[1], **kwargs)
        if len(args) == 3:
            self._write_lonlat(args[0], args[1], args[2], **kwargs)
        if len(args) < 2 or len(args) > 3:
            raise ValueError("Wrong number of arguments")

    def read_gp(self, gpi, **kwargs):
        """
        Reads time series for a given grid point index.

        Parameters
        ----------
        gpi : int
            grid point index

        Returns
        -------
        data : pandas.DataFrame
            pandas.DateFrame with DateTimeIndex
        """
        if self.mode in ['w', 'a']:
            raise IOError("File is not open in read mode")

        self._open(gpi)

        return self.fid.read_ts(gpi, **kwargs)

    def read_ts(self, *args, **kwargs):
        """
        Takes either 1 or 2 arguments and calls the correct function
        which is either reading the gpi directly or finding
        the nearest gpi from given lat,lon coordinates and then reading it
        """
        if len(args) == 1:
            data = self.read_gp(args[0], **kwargs)
        if len(args) == 2:
            data = self._read_lonlat(args[0], args[1], **kwargs)
        if len(args) < 1 or len(args) > 2:
            raise ValueError("Wrong number of arguments")

        return data

    def iter_ts(self):
        """
        Yield time series for all grid points.

        Yields
        ------
        data : pandas.DataFrame
            pandas.DateFrame with DateTimeIndex
        gpi : int
            Grid point index
        """
        gpi_info = list(self.grid.grid_points())
        gps = np.array(gpi_info, dtype=np.int)[:, 0]

        for gp in gps:
            yield self.read_gp(gp), gp

    def flush(self):
        """
        Flush data.
        """
        if self.fid is not None:
            self.fid.flush()

    def close(self):
        """
        Close file.
        """
        if self.fid is not None:
            self.fid.close()
            self.fid = None
