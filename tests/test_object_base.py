from pygeobase.object_base import Image
from datetime import datetime
import numpy as np
import numpy.testing as nptest


def test_tuple_unpacking():
    lon = np.array([1, 2, 3])
    lat = np.array([1, 2, 3])
    data = {'variable': np.array([1, 2, 3]),
            'jd': np.array([5, 6, 7])}
    metadata = {'attribute': 'test'}
    timestamp = datetime(2000, 1, 1, 12)
    img = Image(lon, lat, data, metadata, timestamp, timekey='jd')

    (return_data,
     return_metadata,
     return_timestamp,
     return_lon,
     return_lat,
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
    data = {'variable': np.array([1, 2, 3]),
            'jd': np.array([5, 6, 7])}
    metadata = {'attribute': 'test'}
    timestamp = datetime(2000, 1, 1, 12)
    img = Image(lon, lat, data, metadata, timestamp)

    (return_data,
     return_metadata,
     return_timestamp,
     return_lon,
     return_lat,
     times) = img

    for key in data:
        nptest.assert_allclose(return_data[key], data[key])
    assert return_metadata == metadata
    assert return_timestamp == timestamp
    nptest.assert_allclose(return_lon, lon)
    nptest.assert_allclose(return_lat, lat)
    assert times is None
