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
import warnings

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

    """
    Dateset base class for images that implements basic functions and
    also abstract methods that have to be implemented by child classes.

    Parameters
    ----------
    path : string
        Path to dataset.
    filename_templ : string
        template of how datetimes fit into the filename.
        e.g. "ASCAT_%Y%m%d_image.nc" will be translated into the filename
        ASCAT_20070101_image.nc for the date 2007-01-01.
    sub_path : string or list optional
        if given it is used to generate a sub path from the given timestamp.
        This is useful if files are sorted by year or month.
        If a list is one subfolder per item is assumed. This can be used
        if the files for May 2007 are e.g. in folders 2007/05/ then the
        list ['%Y', '%m'] works.
    grid : pygeogrids.grids.BasicGrid of CellGrid instance, optional
        Grid on which all the images of the dataset are stored. This is not
        relevant for datasets that are stored e.g. in orbit geometry
    exact_templ : boolean, optional
        if True then the filename_templ matches the filename exactly.
        If False then the filename_templ will be used in glob to find
        the file.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, filename_templ="",
                 sub_path=None, grid=None,
                 exact_templ=True):
        self.grid = grid
        self.fname_templ = filename_templ
        self.path = path
        if type(sub_path) == str:
            sub_path = [sub_path]
        self.sub_path = sub_path
        self.exact_templ = exact_templ

    @abc.abstractmethod
    def _read_spec_file(self, filename, timestamp=None, **kwargs):
        """
        Read specific image for given filename

        Parameters
        ----------
        filename : string
            filename
        timestamp : datetime, optional
           can be given here if it is already
           known since it has to be returned.

        Returns
        -------
        data : dict
            dictionary of numpy arrays that hold the image data for each
            variable of the dataset
        metadata : dict
            dictionary of numpy arrays that hold the metadata
        timestamp : datetime.datetime
            exact timestamp of the image
        lon : numpy.array or None
            array of longitudes, if None self.grid will be assumed
        lat : numpy.array or None
            array of latitudes, if None self.grid will be assumed
        time : numpy.array or None
            observation times of the data as numpy array of julian dates,
            if None all observations have the same timestamp
        """
        return

    def _search_files(self, timestamp, custom_templ=None,
                      str_param=None):
        """
        searches for filenames for the given timestamp.
        This function is used by _build_filename which then
        checks if a unique filename was found

        Parameters
        ----------
        timestamp: datetime
            datetime for given filename
        custom_tmpl : string, optional
            if given not the fname_templ is used but the custom templ
            This is convienint for some datasets where no all filenames
            follow the same convention and where the read_img function
            can choose between templates based on some condition.
        str_param : dict, optional
            if given then this dict will be applied to the template using
            the fname_template.format(**str_param) notation before the resulting
            string is put into datetime.strftime.

            example from python documentation
            >>> coord = {'latitude': '37.24N', 'longitude': '-115.81W'}
            >>> 'Coordinates: {latitude}, {longitude}'.format(**coord)
            'Coordinates: 37.24N, -115.81W'
        """
        if custom_templ is not None:
            fname_templ = custom_templ
        else:
            fname_templ = self.fname_templ

        if str_param is not None:
            fname_templ = fname_templ.format(**str_param)
        if self.sub_path is None:
            search_file = os.path.join(
                self.path, timestamp.strftime(fname_templ))

        else:
            sub_path = ""
            for s in self.sub_path:
                sub_path = os.path.join(sub_path, timestamp.strftime(s))
            search_file = os.path.join(self.path,
                                       sub_path,
                                       timestamp.strftime(fname_templ))
        if self.exact_templ:
            return [search_file]
        else:
            filename = glob.glob(search_file)

        if not filename:
            raise IOError("File not found {:}".format(search_file))

        return filename

    def _build_filename(self, timestamp, custom_templ=None,
                        str_param=None):
        """
        This function uses _search_files to find the correct
        filename and checks if the search was unambiguous

        Parameters
        ----------
        timestamp: datetime
            datetime for given filename
        custom_tmpl : string, optional
            if given not the fname_templ is used but the custom templ
            This is convienint for some datasets where no all filenames
            follow the same convention and where the read_img function
            can choose between templates based on some condition.
        str_param : dict, optional
            if given then this dict will be applied to the template using
            the fname_template.format(**str_param) notation before the resulting
            string is put into datetime.strftime.

            example from python documentation

            >>> coord = {'latitude': '37.24N', 'longitude': '-115.81W'}
            >>> 'Coordinates: {latitude}, {longitude}'.format(**coord)
            'Coordinates: 37.24N, -115.81W'
        """
        filename = self._search_files(timestamp, custom_templ=custom_templ,
                                      str_param=str_param)

        if len(filename) > 1:
            raise IOError(
                "File search is ambiguous {:}".format(filename))

        return filename[0]

    def _assemble_img(self, timestamp, **kwargs):
        """
        Function between read_img and _build_filename that can
        be used to read a different file for each parameter in a image
        dataset. In the standard impementation it is assumed
        that all necessary information of a image is stored in the
        one file whose filename is built by the _build_filname function.

        Parameters
        ----------
        timestamp : datatime
            timestamp of the image to assemble

        Returns
        -------
        data : dict
            dictionary of numpy arrays that hold the image data for each
            variable of the dataset
        metadata : dict
            dictionary of numpy arrays that hold the metadata
        timestamp : datetime.datetime
            exact timestamp of the image
        lon : numpy.array or None
            array of longitudes, if None self.grid will be assumed
        lat : numpy.array or None
            array of latitudes, if None self.grid will be assumed
        time_var : string or None
            variable name of observation times in the data dict, if None all
            observations have the same timestamp
        """
        return self._read_spec_file(self._build_filename(timestamp),
                                    timestamp=timestamp, **kwargs)

    def read_img(self, timestamp, **kwargs):
        """
        Return an image if a specific datetime is given.

        Parameters
        ----------
        timestamp : datetime.datetime
            Time stamp.

        Returns
        -------
        data : dict
            dictionary of numpy arrays that hold the image data for each
            variable of the dataset
        metadata : dict
            dictionary of numpy arrays that hold the metadata
        timestamp : datetime.datetime
            exact timestamp of the image
        lon : numpy.array or None
            array of longitudes, if None self.grid will be assumed
        lat : numpy.array or None
            array of latitudes, if None self.grid will be assumed
        time_var : string or None
            variable name of observation times in the data dict, if None all
            observations have the same timestamp
        """
        return self._assemble_img(timestamp, **kwargs)

    def tstamps_for_daterange(self, start_date, end_date):
        """
        Return all valid timestamps in a given date range.
        This method must be implemented if iteration over
        images should be possible.

        Parameters
        ----------
        start_date : datetime.date or datetime.datetime
            start date
        end_date : datetime.date or datetime.datetime
            end date

        Returns
        -------
        dates : list
            list of datetimes
        """

        raise NotImplementedError(
            "Please implement to enable iteration over date ranges.")

    def iter_images(self, start_date, end_date, **kwargs):
        """
        Yield all images for a given date range.

        Parameters
        ----------
        start_date : datetime.date or datetime.datetime
            start date
        end_date : datetime.date or datetime.datetime
            end date

        Returns
        -------
        data : dict
            dictionary of numpy arrays that hold the image data for each
            variable of the dataset
        metadata : dict
            dictionary of numpy arrays that hold the metadata
        timestamp : datetime.datetime
            exact timestamp of the image
        lon : numpy.array or None
            array of longitudes, if None self.grid will be assumed
        lat : numpy.array or None
            array of latitudes, if None self.grid will be assumed
        time_var : string or None
            variable name of observation times in the data dict, if None all
            observations have the same timestamp
        """
        timestamps = self.tstamps_for_daterange(start_date, end_date)

        if timestamps:
            for timestamp in timestamps:
                yield_img = self.read_img(
                    timestamp, **kwargs)
                yield yield_img
        else:
            raise IOError("no files found for given date range")

    def daily_images(self, day, **kwargs):
        """
        Yield all images for a day.

        Parameters
        ----------
        day : datetime.date

        Returns
        -------
        data : dict
            dictionary of numpy arrays that hold the image data for each
            variable of the dataset
        metadata : dict
            dictionary of numpy arrays that hold metadata
        timestamp : datetime.datetime
            exact timestamp of the image
        lon : numpy.array or None
            array of longitudes, if None self.grid will be assumed
        lat : numpy.array or None
            array of latitudes, if None self.grid will be assumed
        jd : string or None
            name of the field in the data array representing the observation
            dates
        """
        for img in self.iter_images(day, day, **kwargs):
            yield img


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
                self.fid = self.ioclass(filename, mode=self.mode,
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
        self.fid.write(gp, data, **kwargs)

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

    warnings.warn("GriddedStaticBase is deprecated,"
                  " please use GriddedBase instead.", DeprecationWarning)


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
        warnings.warn("read_ts is deprecated, please use read "
                      "instead.", DeprecationWarning)
        return self.read(*args, **kwargs)

    def write_ts(self, *args, **kwargs):
        """
        Takes either 1, 2 or 3 arguments (the last one always needs to be the
        data to be written) and calls the correct function which is either
        writing the gp directly or finding the nearest gp from given
        lon, lat coordinates and then reading it.
        """
        warnings.warn("write_ts is deprecated, please use write "
                      "instead.", DeprecationWarning)
        return self.write(*args, **kwargs)

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
        warnings.warn("iter_ts is deprecated, please use iter_gp "
                      "instead.", DeprecationWarning)
        return self.iter_gp()
