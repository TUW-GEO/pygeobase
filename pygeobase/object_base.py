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


class TS(object):
    """
    The TS class represents the base object of a time series.
    """
    def __init__(self, gpi, data, metadata):
        """
        Initialization of the image object.

        Parameters
        ----------
        gpi : int
            Grid point index associated with the time series
        data : pandas.DataFrame
            Pandas DataFrame that holds data for each variable of the time
            series
        metadata : dict
            dictionary of numpy arrays that hold the metadata
        """
        self.gpi = gpi
        self.data = data
        self.metadata = metadata


class Image(object):
    """
    The Image class represents the base object of an image.
    """
    def __init__(self, data, metadata, lon, lat, timestamp, timekey='jd'):
        """
        Initialization of the image object.

        Parameters
        ----------
        data : dict
            dictionary of numpy arrays that holds the image data for each
            variable of the dataset
        metadata : dict
            dictionary of numpy arrays that hold the metadata
        lon : numpy.array or None
            array of longitudes, if None self.grid will be assumed
        lat : numpy.array or None
            array of latitudes, if None self.grid will be assumed
        timestamp : datetime.datetime
            exact timestamp of the image
        timekey : str
            Key of the time variable stored in data dictionary.
        """

        self.data = data
        self.metadata = metadata
        self.lon = lon
        self.lat = lat
        self.timestamp = timestamp
        self.timekey = timekey
