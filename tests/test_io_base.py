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

import warnings

import numpy as np
from datetime import datetime, date

import pygeogrids.grids as grids

from pygeobase.io_base import GriddedBase
from pygeobase.io_base import GriddedTsBase
from pygeobase.io_base import ImageBase
from pygeobase.io_base import MultiTemporalImageBase
from pygeobase.io_base import IntervalReadingMixin
from pygeobase.object_base import Image
from pygeobase.utils import split_daterange_in_intervals


class Dataset:
    """
    Test dataset that acts as a fake object for the base classes.
    """

    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.mode = mode
        self.read = self.read_ts

    def read_ts(self, gpi, factor=1):
        if gpi == 1234:
            raise IOError("GPI does not exist")
        return gpi * factor

    def write(self, gpi, data, **kwargs):
        return None

    def write_ts(self, gpi, data, **kwargs):
        return None

    def close(self):
        pass

    def flush(self):
        pass


def test_gridded_ts_base_iter_ts():
    """
    Test iteration over time series in GriddedTsBase.
    """
    grid = grids.CellGrid(np.array([1, 2, 3, 4]),
                          np.array([1, 2, 3, 4]),
                          np.array([4, 4, 2, 1]),
                          gpis=np.array([1, 2, 3, 4]))

    ds = GriddedTsBase("", grid, Dataset)
    # during iteration the gpis are traversed based on cells for a cell grid
    gpi_should = [4, 3, 1, 2]
    for ts, gpi in ds.iter_gp():
        assert gpi == gpi_should.pop(0)


def test_gridded_ts_base_read_append():
    """
    Test reading in append mode in GriddedTs. Should be allowed.
    """
    grid = grids.CellGrid(np.array([1, 2, 3, 4]),
                          np.array([1, 2, 3, 4]),
                          np.array([4, 4, 2, 1]),
                          gpis=np.array([1, 2, 3, 4]))

    ds = GriddedTsBase("", grid, Dataset, mode='a')
    # during iteration the gpis are traversed based on cells for a cell grid
    assert ds.read(1) == 1


def test_gridded_ts_base_iter_gp_IOError_None_yield():
    """
    Test iteration over time series in GriddedTsBase.
    Should yield None if IOError is raised.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        grid = grids.CellGrid(np.array([1, 2, 3, 4]),
                            np.array([1, 2, 3, 4]),
                            np.array([4, 4, 2, 1]),
                            gpis=np.array([1, 2, 3, 1234]))

        ds = GriddedTsBase("", grid, Dataset)
        # during iteration the gpis are traversed based on cells for a cell grid
        gpi_should = [1234, 3, 1, 2]
        for ts, gpi in ds.iter_gp():
            assert gpi == gpi_should.pop(0)
            if gpi == 1234:
                assert ts is None


def test_gridded_ts_base_iter_ts_kwargs():
    """
    Test iteration over time series in GriddedTsBase.
    """
    grid = grids.CellGrid(np.array([1, 2, 3, 4]),
                          np.array([1, 2, 3, 4]),
                          np.array([4, 4, 2, 1]),
                          gpis=np.array([1, 2, 3, 4]))

    ds = GriddedTsBase("", grid, Dataset)
    # during iteration the gpis are traversed based on cells for a cell grid
    gpi_should = [4, 3, 1, 2]
    ts_should = [4, 3, 1, 2]
    for ts, gpi in ds.iter_gp(factor=2):
        assert gpi == gpi_should.pop(0)
        assert ts == ts_should.pop(0) * 2


def test_gridded_base_spatial_subset():
    """
    Test selection of spatial subset.
    """
    lons = np.arange(4)
    lats = np.arange(4)
    cells = np.array([4, 4, 2, 1])
    gpis = np.arange(4)

    grid = grids.CellGrid(lons, lats, cells, gpis=gpis)
    ds = GriddedBase("", grid, Dataset)

    # gpi subset
    new_ds = ds.get_spatial_subset(gpis=[1, 2, 3])
    np.testing.assert_array_equal(new_ds.grid.gpis, gpis[1:])

    # cell subset
    new_ds = ds.get_spatial_subset(cells=[4])
    np.testing.assert_array_equal(new_ds.grid.gpis, gpis[:2])

    # ll_bbox subset
    # takes cell order into account
    ll_bbox = (0, 2, 0, 2)
    new_ds = ds.get_spatial_subset(ll_bbox=ll_bbox)
    np.testing.assert_array_equal(new_ds.grid.gpis, np.array([2, 0, 1]))

    # grid subset
    new_grid = grids.CellGrid(lons[2:], lats[2:], cells[2:], gpis=gpis[2:])
    new_ds = ds.get_spatial_subset(grid=new_grid)
    np.testing.assert_array_equal(new_ds.grid.gpis, new_grid.gpis)


class ImageDataset(ImageBase):

    def read(self, timestamp=None, additional_kw=None):

        return Image(np.array([1]), np.array([1]),
                     {'variable1': np.array([1])}, {'kw': additional_kw},
                     timestamp)

    def write(self, data):
        raise NotImplementedError()

    def flush(self):
        pass

    def close(self):
        pass


class MultiTemporalImageDataset(MultiTemporalImageBase):

    def __init__(self):
        super(MultiTemporalImageDataset, self).__init__("", ImageDataset)

    def tstamps_for_daterange(self, startdate, enddate):
        """
        Simulate a dataset every 5 minutes
        """
        intervals = split_daterange_in_intervals(startdate, enddate, 5)
        startdates = [interval[0] for interval in intervals]
        return startdates


def test_multi_temp_dataset():
    """
    Test multi-temporal data sets.
    """
    ds = MultiTemporalImageDataset()

    data = ds.read(datetime(2000, 1, 1))

    assert type(data) == Image
    assert data.timestamp == datetime(2000, 1, 1)
    assert data.metadata == {'kw': None}


def test_multi_temp_dataset_kw_passing():
    """
    Test keyword pass of multi-temporal data sets.
    """
    ds = MultiTemporalImageDataset()

    data = ds.read(datetime(2000, 1, 1), additional_kw="test")

    assert type(data) == Image
    assert data.timestamp == datetime(2000, 1, 1)
    assert data.metadata == {'kw': "test"}


def test_daily_images():
    ds = MultiTemporalImageDataset()
    count = 0
    for data in ds.daily_images(date(2000, 1, 1)):
        count = count + 1
    assert count == (24 * 60) / 5


class IntervalReadingTestDataset(IntervalReadingMixin,
                                 MultiTemporalImageDataset):
    pass


def test_interval_reading():
    ds = IntervalReadingTestDataset()
    count = 0
    interval = ds.tstamps_for_daterange(datetime(2000, 1, 1),
                                        datetime(2000, 1, 1, 0, 50))
    data = ds.read(interval[0])
    count = count + 1
    assert data.lon.shape == (10, )
