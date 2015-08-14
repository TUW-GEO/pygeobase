import pygeogrids.grids as grids
import numpy as np
from pygeobase.io_base import GriddedTsBase


class TestDataset(object):
    """Test dataset that acts as a fake object for the base classes."""

    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.mode = mode

    def read(self, gpi):
        return None

    def write(self, gpi, data):
        return None

    def read_ts(self, gpi):
        return None

    def write_ts(self, gpi, data):
        return None

    def close(self):
        pass

    def flush(self):
        pass


def test_gridded_ts_base_iter_ts():
    """Test iteration over time series in GriddedTsBase."""
    grid = grids.CellGrid(np.array([1, 2, 3, 4]), np.array([1, 2, 3, 4]),
                          np.array([4, 3, 2, 1]), gpis=np.array([1, 2, 3, 4]))

    ds = GriddedTsBase("", grid, TestDataset)
    # during iteration the gpis are traversed based on cells for a cell grid
    gpi_should = [4, 3, 2, 1]
    for ts, gpi in ds.iter_ts():
        assert gpi == gpi_should.pop(0)
