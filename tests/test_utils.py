
from pygeobase.utils import split_daterange_in_intervals
import datetime


def test_split_daterange_in_intervals():

    intervals = split_daterange_in_intervals(datetime.datetime(2000, 1, 1),
                                             datetime.datetime(2000, 1, 1, 23, 59, 59, 999), 50)
    assert len(intervals) == 29
    assert intervals[-2] == (datetime.datetime(2000, 1, 1, 22, 30),
                             datetime.datetime(2000, 1, 1, 23, 19, 59, 999999))
    assert intervals[-1] == (datetime.datetime(2000, 1, 1, 23, 20),
                             datetime.datetime(2000, 1, 1, 23, 59, 59, 999))
