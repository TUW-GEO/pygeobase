import pygeogrids.grids as grids
import numpy as np
from datetime import datetime
from pygeobase.io_base import GriddedTsBase
from pygeobase.io_base import ImageBase
from pygeobase.io_base import MultiTemporalImageBase
from pygeobase.object_base import Image


class TestDataset(object):
    """Test dataset that acts as a fake object for the base classes."""

    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.mode = mode

    def read(self, gpi, factor=1):
        return gpi * factor

    def write(self, gpi, data):
        return None

    def read_ts(self, gpi, factor=1):
        return gpi * factor

    def write_ts(self, gpi, data):
        return None

    def close(self):
        pass

    def flush(self):
        pass


def test_gridded_ts_base_iter_ts():
    """Test iteration over time series in GriddedTsBase."""
    grid = grids.CellGrid(np.array([1, 2, 3, 4]), np.array([1, 2, 3, 4]),
                          np.array([4, 4, 2, 1]), gpis=np.array([1, 2, 3, 4]))

    ds = GriddedTsBase("", grid, TestDataset)
    # during iteration the gpis are traversed based on cells for a cell grid
    gpi_should = [4, 3, 1, 2]
    for ts, gpi in ds.iter_ts():
        assert gpi == gpi_should.pop(0)


def test_gridded_ts_base_iter_ts_kwargs():
    """Test iteration over time series in GriddedTsBase."""
    grid = grids.CellGrid(np.array([1, 2, 3, 4]), np.array([1, 2, 3, 4]),
                          np.array([4, 4, 2, 1]), gpis=np.array([1, 2, 3, 4]))

    ds = GriddedTsBase("", grid, TestDataset)
    # during iteration the gpis are traversed based on cells for a cell grid
    gpi_should = [4, 3, 1, 2]
    ts_should = [4, 3, 1, 2]
    for ts, gpi in ds.iter_ts(factor=2):
        assert gpi == gpi_should.pop(0)
        assert ts == ts_should.pop(0) * 2


class TestImageDataset(ImageBase):

    def read(self, timestamp=None, additional_kw=None):

        return Image(None, None, None, {'kw': additional_kw}, timestamp)

    def write(self, data):
        raise NotImplementedError()

    def flush(self):
        pass

    def close(self):
        pass


class TestMultiTemporalImageDataset(MultiTemporalImageBase):

    def __init__(self):
        super(TestMultiTemporalImageDataset,
              self).__init__("", TestImageDataset)


def test_multi_temp_dataset():
    ds = TestMultiTemporalImageDataset()

    data = ds.read(datetime(2000, 1, 1))

    assert type(data) == Image
    assert data.timestamp == datetime(2000, 1, 1)
    assert data.metadata == {'kw': None}


def test_multi_temp_dataset_kw_passing():
    ds = TestMultiTemporalImageDataset()

    data = ds.read(datetime(2000, 1, 1), additional_kw="test")

    assert type(data) == Image
    assert data.timestamp == datetime(2000, 1, 1)
    assert data.metadata == {'kw': "test"}
