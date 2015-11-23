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

    def flush(self):
        """
        Flush data.
        """
        return

    def close(self):
        """
        Close file.
        """
        return


class TsBase(object):

    """
    The TsBase class serves as a template for i/o objects used in
    GriddedTsBase.
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
    def read_ts(self, gpi, **kwargs):
        """
        Read time series data for given grid point.

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
    def write_ts(self, gpi, data, **kwargs):
        """
        Write data.

        Parameters
        ----------
        gpi : int
            Grid point index.
        data : numpy.ndarray
            Data records.
        """
        return

    def flush(self):
        """
        Flush data.
        """
        return

    def close(self):
        """
        Close file.
        """
        return


class ImageBase(object):
    pass


class GriddedBase(object):

    """
    The GriddedBase class uses another IO class together with a grid
    object to read/write a dataset under the given path.

    Parameters
    ----------
    path : string
        Path to dataset.
    grid : pygeogrids.BasicGrid of CellGrid instance
        Grid on which the time series data is stored.
    ioclass : class
        IO class.
    mode : str, optional
        File mode and can be read 'r', write 'w' or append 'a'. Default: 'r'
    fn_format : str, optional
        The string format of the cell files. Default: '{:04d}'
    ioclass_kws : dict, optional
        Additional keyword arguments for the ioclass. Default: None
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
        self._first_write = True

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

    def _open(self, gp):
        """
        Open file.

        Parameters
        ----------
        gp : int
            Grid point.
        """
        cell = self.grid.gpi2cell(gp)
        filename = os.path.join(self.path, self.fn_format.format(cell))

        if self.mode == 'r':
            if self.previous_cell != cell:
                self.close()
                self.previous_cell = cell
                self.fid = self.ioclass(filename, mode=self.mode,
                                        **self.ioclass_kws)

        if self.mode in ['w', 'a']:
            if self.previous_cell != cell:
                self.flush()
                self.close()
                self.previous_cell = cell
                if self._first_write and self.mode == 'w':
                    self.fid = self.ioclass(filename, mode=self.mode,
                                            **self.ioclass_kws)
                    self._first_write = False
                else:
                    # open in append mode after first write
                    self.fid = self.ioclass(filename, mode='a',
                                            **self.ioclass_kws)

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

        return self._read_gp(gp, **kwargs)

    @abc.abstractmethod
    def _read_gp(self, gp, **kwargs):
        return

    def read(self, *args, **kwargs):
        """
        Takes either 1 or 2 arguments and calls the correct function
        which is either reading the gpi directly or finding
        the nearest gpi from given lat,lon coordinates and then reading it
        """
        if len(args) == 1:
            data = self._read_gp(args[0], **kwargs)
        if len(args) == 2:
            data = self._read_lonlat(args[0], args[1], **kwargs)
        if len(args) < 1 or len(args) > 2:
            raise ValueError("Wrong number of arguments")

        return data

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

        return self._write_gp(gp, data, **kwargs)

    def write(self, *args, **kwargs):
        """
        Takes either 1 or 2 arguments and calls the correct function
        which is either reading the gpi directly or finding
        the nearest gpi from given lat,lon coordinates and then reading it
        """
        if len(args) == 1:
            # args: data
            self._write_gp(args[0]['gpi'], args[0], **kwargs)
        if len(args) == 2:
            # args: gp, data
            self._write_gp(args[0], args[1], **kwargs)
        if len(args) == 3:
            # args: lon, lat, data
            self._write_lonlat(args[0], args[1], args[2], **kwargs)
        if len(args) < 1 or len(args) > 3:
            raise ValueError("Wrong number of arguments")

    @abc.abstractmethod
    def _write_gp(self, gp, data, **kwargs):
        return

    def iter_gp(self):
        """
        Yield all values for all grid points.

        Yields
        ------
        data : pandas.DataFrame
            Data set.
        gp : int
            Grid point.
        """
        gp_info = list(self.grid.grid_points())
        gps = np.array(gp_info, dtype=np.int)[:, 0]

        for gp in gps:
            yield self._read_gp(gp), gp

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


class GriddedStaticBase(GriddedBase):

    """
    The GriddedStaticBase class uses another IO class together with a grid
    object to read/write a dataset under the given path.
    """

    def _read_gp(self, gp, **kwargs):
        """
        Read data for given grid point.

        Parameters
        ----------
        gp : int
            Grid point.

        Returns
        -------
        data : numpy.ndarray
            Data set.
        """
        if self.mode in ['w', 'a']:
            raise IOError("File is not open in read mode")

        self._open(gp)

        return self.fid.read(gp, **kwargs)

    def _write_gp(self, gp, data, **kwargs):
        """
        Write data for given grid point.

        Parameters
        ----------
        gp : int
            Grid point.
        data : numpy.ndarray
            Data
        """
        if self.mode in ['r']:
            raise IOError("File is not open in write/append mode")

        self._open(gp)
        self.fid.write(data, **kwargs)


class GriddedTsBase(GriddedBase):

    """
    The GriddedTsBase class uses another IO class together with a grid object
    to read/write a time series dataset under the given path.
    """

    def _read_gp(self, gp, **kwargs):
        """
        Reads time series for a given grid point index.

        Parameters
        ----------
        gp : int
            Grid point.

        Returns
        -------
        data : pandas.DataFrame
            pandas.DateFrame with DateTimeIndex
        """
        if self.mode in ['w', 'a']:
            raise IOError("File is not open in read mode")

        self._open(gp)

        return self.fid.read_ts(gp, **kwargs)

    def _write_gp(self, gp, data, **kwargs):
        """
        Write data for given grid point.

        Parameters
        ----------
        gp : int
            Grid point.
        data : numpy.ndarray
            Data records.
        """
        if self.mode in ['r']:
            raise IOError("File is not open in write/append mode")

        self._open(gp)
        lon, lat = self.grid.gpi2lonlat(gp)
        self.fid.write_ts(gp, data, lon=lon, lat=lat, **kwargs)

    def read_ts(self, *args, **kwargs):
        """
        Takes either 1 or 2 arguments and calls the correct function
        which is either reading the gpi directly or finding
        the nearest gpi from given lat,lon coordinates and then reading it
        """
        if len(args) == 1:
            data = self._read_gp(args[0], **kwargs)
        if len(args) == 2:
            data = self._read_lonlat(args[0], args[1], **kwargs)
        if len(args) < 1 or len(args) > 2:
            raise ValueError("Wrong number of arguments")

        return data

    def write_ts(self, *args, **kwargs):
        """
        Takes either 2 or 3 arguments (the last one always needs to be the
        data to be written) and calls the correct function which is either
        writing the gp directly or finding the nearest gp from given
        lon, lat coordinates and then reading it.
        """
        if len(args) == 2:
            self._write_gp(args[0], args[1], **kwargs)
        if len(args) == 3:
            self._write_lonlat(args[0], args[1], args[2], **kwargs)
        if len(args) < 2 or len(args) > 3:
            raise ValueError("Wrong number of arguments")

    def iter_ts(self):
        """
        Yield time series for all grid points.

        Yields
        ------
        data : pandas.DataFrame
            pandas.DateFrame with DateTimeIndex
        gp : int
            Grid point.
        """
        yield self.iter_gp()
