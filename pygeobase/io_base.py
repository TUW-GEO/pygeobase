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
import glob
from datetime import datetime
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


class ImageBase(object):

    """
    ImageBase class serves as a template for i/o objects used for reading
    and writing image data.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, mode='r', **kwargs):
        """
        Initialization of i/o object.

        Parameters
        ----------
        mode : str, optional
            Opening mode. Default: r
        """
        self.mode = mode
        self.kwargs = kwargs

    @abc.abstractmethod
    def read(self, filename, **kwargs):
        """
        Read data of an image file.

        Parameters
        ----------
        filename : str
            File name.

        Returns
        -------
        image : object
            pygeobase.object_base.Image object
        """
        return

    def read_masked_data(self, filename, **kwargs):
        """
        Read data of an image file and mask the data according to
        specifications.

        Parameters
        ----------
        filename : str
            File name.

        Returns
        -------
        image : object
            pygeobase.object_base.Image object
        """
        raise NotImplementedError('Please implement to enable.')

    @abc.abstractmethod
    def write(self, filename, image, **kwargs):
        """
        Write data to an image file.

        Parameters
        ----------
        filename : str
            File name.
        image : object
            pygeobase.object_base.Image object
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

        if self.previous_cell != cell:
            self.close()
            self.fid = self.ioclass(filename, mode=self.mode,
                                    **self.ioclass_kws)
            self.previous_cell = cell

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
        self._open(gpi)

        if self.mode in ['r']:
            raise IOError("File is not open in write/append mode")

        lon, lat = self.grid.gpi2lonlat(gpi)

        self.fid.write_ts(gpi, data, lon=lon, lat=lat, **kwargs)

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
        self._open(gpi)

        if self.mode in ['w', 'a']:
            raise IOError("File is not open in read mode")

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


class MultiTemporalImageBase(object):

    """
    The MultiTemporalImageBase class make use of an ImageBase object to
    read/write a sequence of multi temporal images under a given path.

    Parameters
    ----------
    path : string
        Path to dataset.
    ioclass : class
        IO class.
    mode : str, optional
        File mode and can be read 'r', write 'w' or append 'a'. Default: 'r'
    fname_templ : str
        Filename template of the data to read. Default placeholder for
        parsing datetime information into the fname_templ is "{datetime}".
        e.g. "ASCAT_{datetime}_image.nc" will be translated into the filename
        ASCAT_20070101_image.nc for the date 2007-01-01.
    datetime_format : str
        String specifying the format of the datetime object to be parsed
        into the fname_template.
        e.g. "%Y/%m" will result in 2007/01 for datetime 2007-01-01 12:15:00
    subpath_templ : list, optional
        If given it is used to generate a sub-paths from the given timestamp.
        Each item in the list represents one folder level. This can be used
        if the files for May 2007 are e.g. in folders 2007/05/ then the
        files can be accessed via the list ['%Y', '%m'].
    ioclass_kws : dict
        Additional keyword arguments for the ioclass.
    exact_templ : boolean, optional
        If True then the fname_templ matches the filename exactly.
        If False then the fname_templ will be used in glob to find the file.
    dtime_placeholder : str
        String used in fname_templ as placeholder for datetime.
        Default value is "datetime".
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, path, ioclass, mode='r', fname_templ="",
                 datetime_format="", subpath_templ=None, ioclass_kws=None,
                 exact_templ=True, dtime_placeholder="datetime"):

        self.path = path
        self.ioclass = ioclass
        self.mode = mode
        self.fname_templ = fname_templ
        self.datetime_format = datetime_format
        self.subpath_templ = subpath_templ
        self.exact_templ = exact_templ
        self.dtime_placeholder = dtime_placeholder
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

    def _open(self):
        """
        Open file.

        Parameters
        ----------
        filepath : str
            Path to file.
        """
        if self.fid is None:
            self.fid = self.ioclass(mode=self.mode, **self.ioclass_kws)


    def _search_files(self, timestamp, custom_templ=None, str_param=None,
                      custom_datetime_format=None):
        """
        searches for filenames with the given timestamp. This function is
        used by _build_filename which then checks if a unique filename was
        found.

        Parameters
        ----------
        timestamp: datetime
            Datetime for given filename
        custom_tmpl : string, optional
            If given the custom_templ is used instead of the fname_templ. This
            is convenient for some datasets where not all file names follow
            the same convention and where the read_image function can choose
            between templates based on some condition.
        custom_datetime_format: string, optional
            If given the custom_datetime_format will be used instead of the
            datetime_format. This adds support to search for multiple files
            for example for a given day, a given month or a specific year.
        str_param : dict, optional
            If given then this dict will be applied to the fname_templ using
            the fname_templ.format(**str_param) notation before the resulting
            string is put into datetime.strftime.

            - example from python documentation:
                coord = {'latitude': '37.24N', 'longitude': '-115.81W'}
                'Coordinates: {latitude}, {longitude}'.format(**coord)
                'Coordinates: 37.24N, -115.81W'
        """
        if custom_templ is not None:
            fname_templ = custom_templ
        else:
            fname_templ = self.fname_templ

        if custom_datetime_format is not None:
            dFormat = {self.dtime_placeholder: custom_datetime_format}

        else:
            dFormat = {self.dtime_placeholder: self.datetime_format}

        fname_templ = fname_templ.format(**dFormat)

        if str_param is not None:
            fname_templ = fname_templ.format(**str_param)

        sub_path = ''
        if self.subpath_templ is not None:
            for s in self.subpath_templ:
                 sub_path = os.path.join(sub_path, timestamp.strftime(s))

        search_file = os.path.join(self.path, sub_path,
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
            If given the fname_templ is not used but the custom_templ. This
            is convenient for some datasets where not all file names follow
            the same convention and where the read_image function can choose
            between templates based on some condition.
        str_param : dict, optional
            If given then this dict will be applied to the fname_templ using
            the fname_templ.format(**str_param) notation before the resulting
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

    def _assemble_img(self, timestamp, mask=False, **kwargs):
        """
        Function between read_img and _build_filename that can
        be used to read a different file for each parameter in a image
        dataset. In the standard implementation it is assumed
        that all necessary information of an image is stored in the
        one file whose filename is built by the _build_filname function.

        Parameters
        ----------
        timestamp : datetime
            timestamp of the image to assemble
        mask : optional, boolean
            Switch to read already masked data which requires the
            implementation of an read_mask_data() in the ioclass

        Returns
        -------
        img: object
            pygeobase.object_base.Image object
        """
        filepath = self._build_filename(timestamp, **kwargs)
        self._open(**kwargs)
        kwargs['timestamp'] = timestamp
        if mask is False:
            img = self.fid.read(filepath, **kwargs)
        else:
            img = self.fid.read_masked_data(filepath, **kwargs)
        return img

    def read(self, timestamp, **kwargs):
        """
        Return an image for a specific timestamp.

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

    def write(self, timestamp, data, **kwargs):
        """
        Write image data for a given timestamp.

        Parameters
        ----------
        timestamp : datetime.datetime
            exact timestamp of the image
        data : numpy.ndarray
            Data records.
        """
        if self.mode in ['r']:
            raise IOError("File is not open in write/append mode")
        filename = self._build_filename(timestamp)

        self.fid.write(filename, data, **kwargs)

    def get_tstamp_from_filename(self, filename):
        """
        Return the timestamp contained in a given file name in accordance to
        the defined fname_templ.

        Parameters
        ----------
        filename : string
            File name.

        Returns
        -------
        tstamp : datetime.dateime
            Time stamp according to fname_templ as datetime object.
        """
        StartPos = self.fname_templ.find(self.dtime_placeholder) - 1
        EndPos = StartPos + len(datetime.now().strftime(self.datetime_format))
        StringDate = filename[StartPos:EndPos]
        return datetime.strptime(StringDate, self.datetime_format)


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
                yield_img = self.read(timestamp, **kwargs)
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