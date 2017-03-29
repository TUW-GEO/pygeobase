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


def test_dtype_property():
    lon = np.array([1, 2, 3], dtype=np.float32)
    lat = np.array([1, 2, 3], dtype=np.float32)
    data = {'variable': np.array([1, 2, 3], dtype=np.int16),
            'jd': np.array([5, 6, 7], dtype=np.float32)}
    metadata = {'attribute': 'test'}
    timestamp = datetime(2000, 1, 1, 12)
    img = Image(lon, lat, data, metadata, timestamp, timekey='jd')
    assert np.dtype([('jd', np.float32), ('variable', np.int16)]) == img.dtype
    assert sorted(list(img.dtype.fields)) == ['jd', 'variable']
    assert img.dtype.names == ('jd', 'variable')


def test_getitem():
    lon = np.array([1, 2, 3], dtype=np.float32)
    lat = np.array([1, 2, 3], dtype=np.float32)
    data = {'variable': np.array([1, 2, 3], dtype=np.int16),
            'jd': np.array([5, 6, 7], dtype=np.float32)}
    metadata = {'attribute': 'test'}
    timestamp = datetime(2000, 1, 1, 12)
    img = Image(lon, lat, data, metadata, timestamp, timekey='jd')
    nptest.assert_allclose(img['jd'], data['jd'])
    nptest.assert_allclose(img['variable'], data['variable'])
