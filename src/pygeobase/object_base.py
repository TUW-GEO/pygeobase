# Copyright (c) 2023, TU Wien, Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of TU Wien, Department of Geodesy and Geoinformation
#      nor the names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior written
#      permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL TU WIEN, DEPARTMENT OF GEODESY AND
# GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np


class TS:

    """
    The TS class represents the base object of a time series.

    Parameters
    ----------
    lon : float
        Longitude of the time series
    lat : float
        Latitude of the time series
    data : pandas.DataFrame
        Pandas DataFrame that holds data for each variable of the time
        series
    metadata : dict
        dictionary that holds metadata
    """

    def __init__(self, gpi, lon, lat, data, metadata):
        """
        Initialization of the time series object.

        """
        self.gpi = gpi
        self.lon = lon
        self.lat = lat
        self.data = data
        self.metadata = metadata

    def __repr__(self):
        return f"Time series gpi:{self.gpi} lat:{self.lat} lon:{self.lon}"

    def plot(self, *args, **kwargs):
        """
        wrapper for pandas.DataFrame.plot which adds title to plot
        and drops NaN values for plotting

        Returns
        -------
        ax : axes
            matplotlib axes of the plot
        """
        tempdata = self.data.dropna(how='all')
        ax = tempdata.plot(*args, figsize=(15, 5), **kwargs)
        ax.set_title(self.__repr__())
        return ax


class Image:

    """
    The Image class represents the base object of an image.

    Parameters
    ----------
    lon : numpy.array
        array of longitudes
    lat : numpy.array
        array of latitudes
    data : dict
        dictionary of numpy arrays that holds the image data for each
        variable of the dataset
    metadata : dict
        dictionary that holds metadata
    timestamp : datetime.datetime
        exact timestamp of the image
    timekey : str, optional
        Key of the time variable, if available, stored in data dictionary.
    """

    def __init__(self, lon, lat, data, metadata, timestamp, timekey=None):
        """
        Initialization of the image object.
        """

        self.lon = lon
        self.lat = lat
        self.data = data
        self.metadata = metadata
        self.timestamp = timestamp
        self.timekey = timekey

    def __iter__(self):
        l = [self.data, self.metadata,
             self.timestamp, self.lon,
             self.lat]

        if self.timekey is not None:
            l.append(self.data[self.timekey])
        else:
            l.append(None)

        for attr in l:
            yield attr

    @property
    def dtype(self):
        """
        Fake numpy recarray dtype field based
        on the dictionary keys and the dtype of the
        numpy array.
        """
        dtype_list = []
        for key in sorted(list(self.data)):
            dtype_list.append((key, self.data[key].dtype.type))

        return np.dtype(dtype_list)

    def __getitem__(self, key):
        return self.data[key]
