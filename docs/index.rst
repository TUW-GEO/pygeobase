=========
pygeobase
=========

This is the documentation of **pygeobase**.


The pygeobase package implements base class definitions for the I/O interface
used in pytesmo_, pynetCF_, and other packages.

Usage
=====

The Abstract base classes in this package are used to provide a consistent
interface for reading various kinds of data.

Image datasets
--------------

When we talk about a image dataset we are generally talking about a dataset that
can be represented through one or several two dimensional arrays. Such a dataset
might consist of multiple layers or bands. It can have implicit or explicit
geolocation information attached. In the simplest case all the datapoints of a
image are referenced to the the same time. But we can also envision a reference
timestamp for a image with a layer of exact time stamps for each observation.

The :class:`pygeobase.io_base.ImageBase` implements the reading and writing of a
single file whereas :class:`pygeobase.io_base.MultiTemporalImageBase` is
responsible for building the filename for a reference timestamp and using the
ImageBase class for the io. In this way any number of underlying file formats
can be supported.

:ref:`overview-img` shows :class:`pygeobase.io_base.ImageBase` which is the
abstract base class for implementing a reader for a single image linked to one
file on disk. The ``read``, ``write``, ``flush`` and ``close`` methods have to
be implemented. For reading from a dataset it is generally enough to implement
the ``read`` and ``close`` methods and use dummy methods for ``write`` and
``flush``. The ``read`` method must return a
:class:`pygeobase.object_base.Image` instance.

.. _overview-img:

.. figure:: /graphs/overview_img.svg
   :width: 50 %
   :align: center

   Figure 1

A implemented class for the ImageBase can then be used in
:class:`pygeobase.io_base.MultiTemporalImageBase`. This class models a dataset
consisting of several files on disk. Each file is linked to a reference
timestamp from which the filename can be built.
:class:`pygeobase.io_base.MultiTemporalImageBase` can be used directly when
configured correctly. Configuration means setting the ``fname_templ`` and the
``datetime_format`` so that it fits to the dataset. If the single files are
stored in subfolders by e.g. month or day then the keyword ``subpath_templ`` can
be used to specify that. Please see
:class:`pygeobase.io_base.MultiTemporalImageBase` for detailed information about
each keyword.


Example for implementing a new image dataset
____________________________________________

Let's imagine we have a regular daily dataset stored on a global regular grid of
0.1 degrees. The folder structure and filenames of the dataset are e.g.

- /2015/01/dataset_2015-01-01.dat
- /2015/01/dataset_2015-01-02.dat
- ...
- /2015/02/dataset_2015-02-01.dat

For simplicities sake lets assume that the dat files are just pickled python
dictionaries.

We could now write a new class based on :class:`pygeobase.io_base.ImageBase`
that reads one of these files:

.. code:: python

    from pygeobase.object_base import Image
    from pygeobase.io_base import ImageBase
    import pygeogrids.grids as grids
    import pickle


    class PickleImg(ImageBase):

        def __init__(self, filename, mode='r'):
            super(PickleImg, self).__init__(filename, mode=mode)
            self.grid = grids.genreg_grid(1, 1)

        def read(self, timestamp=None):

            data = pickle.load(self.filename)
            metadata = {'Type': 'pickle'}

            return Image(self.grid.arrlon,
                         self.grid.arrlat,
                         data,
                         metadata,
                         timestamp)

        def write(self, data):
            raise NotImplementedError()

        def flush(self):
            pass

        def close(self):
            pass


This new class ``PickleImg`` will read a pickled dictionary of data from the
given filename. For the representation of the longitude and latitude of each
datapoint the attributes of a :class:`pygeogrids.grids.BasicGrid` object can be
used but a regular numpy array would also do.

The next code snippet shows how this newly written class can be used in an
implementation of :class:`pygeobase.io_base.MultiTemporalImageBase`:

.. code:: python

    class PickleDs(MultiTemporalImageBase):

        def __init__(self, root_path):
            sub_path = ['%Y', '%m']
            fname_templ = "dataset_{datetime}.dat"
            datetime_format = "%Y-%m-%d"

            super(PickleDs, self).__init__(root_path, PickleImg,
                                          fname_templ=fname_templ,
                                          datetime_format=datetime_format,
                                          subpath_templ=sub_path)

The ``sub_path`` variable is a list of strings that build the path to the file
from the python datetime object. The strftime_ syntax is used. ``fname_templ``
specifies the filename template in which ``{datetime}`` will be substituted
by the string built by ``datetime_format`` according to the strftime_ syntax.
There are more options to customize how the filename is build from a given
python datetime. Please see the
:class:`pygeobase.io_base.MultiTemporalImageBase` documentation.

Please see the :ref:`modindex` for more details.


.. _strftime: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
.. _pytesmo: https://github.com/TUW-GEO/pytesmo
.. _pynetCF: https://github.com/TUW-GEO/pynetCF


Working with a lot of small files
---------------------------------

Some datasets are distributed in very small files like e.g. 3 minute parts of an
orbit. Numerous applications can be sped up if a number of these files are read
together and concatenated before furhter processing. For this use case the
:class:`pygeobase.io_base.IntervalReadingMixing` was developed.

The class does only work if the ``tstamps_for_daterange`` method is implemented.
If this is the case it can be used to generate a new class based on an existing
reader class like this:

.. code:: python

    class IntervalReadingPickeDs(IntervalReadingMixin, PickleDs):
        pass

Please consult the working test example ``IntervalReadingTestDataset`` in
``tests/test_io_base.py``.

Contents
========

.. toctree::
   :maxdepth: 2

   License <license>
   Authors <authors>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
