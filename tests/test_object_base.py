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

from datetime import datetime

import numpy as np
import numpy.testing as nptest

from pygeobase.object_base import Image


def test_tuple_unpacking():
    lon = np.array([1, 2, 3])
    lat = np.array([1, 2, 3])
    data = {'variable': np.array([1, 2, 3]), 'jd': np.array([5, 6, 7])}
    metadata = {'attribute': 'test'}
    timestamp = datetime(2000, 1, 1, 12)
    img = Image(lon, lat, data, metadata, timestamp, timekey='jd')

    (return_data, return_metadata, return_timestamp, return_lon, return_lat,
     times) = img

    for key in data:
        nptest.assert_allclose(return_data[key], data[key])
    assert return_metadata == metadata
    assert return_timestamp == timestamp
    nptest.assert_allclose(return_lon, lon)
    nptest.assert_allclose(return_lat, lat)
    nptest.assert_allclose(times, data['jd'])


def test_tuple_unpacking_no_timekey():
    lon = np.array([1, 2, 3])
    lat = np.array([1, 2, 3])
    data = {'variable': np.array([1, 2, 3]), 'jd': np.array([5, 6, 7])}
    metadata = {'attribute': 'test'}
    timestamp = datetime(2000, 1, 1, 12)
    img = Image(lon, lat, data, metadata, timestamp)

    (return_data, return_metadata, return_timestamp, return_lon, return_lat,
     times) = img

    for key in data:
        nptest.assert_allclose(return_data[key], data[key])
    assert return_metadata == metadata
    assert return_timestamp == timestamp
    nptest.assert_allclose(return_lon, lon)
    nptest.assert_allclose(return_lat, lat)
    assert times is None


def test_dtype_property():
    lon = np.array([1, 2, 3], dtype=np.float32)
    lat = np.array([1, 2, 3], dtype=np.float32)
    data = {
        'variable': np.array([1, 2, 3], dtype=np.int16),
        'jd': np.array([5, 6, 7], dtype=np.float32)
    }
    metadata = {'attribute': 'test'}
    timestamp = datetime(2000, 1, 1, 12)
    img = Image(lon, lat, data, metadata, timestamp, timekey='jd')
    assert np.dtype([('jd', np.float32), ('variable', np.int16)]) == img.dtype
    assert sorted(list(img.dtype.fields)) == ['jd', 'variable']
    assert img.dtype.names == ('jd', 'variable')


def test_getitem():
    lon = np.array([1, 2, 3], dtype=np.float32)
    lat = np.array([1, 2, 3], dtype=np.float32)
    data = {
        'variable': np.array([1, 2, 3], dtype=np.int16),
        'jd': np.array([5, 6, 7], dtype=np.float32)
    }
    metadata = {'attribute': 'test'}
    timestamp = datetime(2000, 1, 1, 12)
    img = Image(lon, lat, data, metadata, timestamp, timekey='jd')
    nptest.assert_allclose(img['jd'], data['jd'])
    nptest.assert_allclose(img['variable'], data['variable'])
