=========
Changelog
=========

Version 0.3.16
==============

- Fix cell switch bug
- Update copyright year

Version 0.3.15
==============

- Allow reading of data in append mode.

Version 0.3.14
==============

- iter_gp does not longer stop if an IOError occurs in the subclass. It catches
  the error warns the user and returns None as the dataset object.

Version 0.3.13
==============

- Add ``IntervalReadingMixin`` for reading files in bigger chunks based on intervals.

Version 0.3.12
==============

- change ``resample_data`` interface to get weights directly instead of windowRadius.
- Add ``dtype`` and ``__getitem__`` to ``Image`` class.

Version 0.3.11
==============

- Fix issue 10 and add new spatial subset method

Version 0.3.10
==============

- allow iteration over time series to take keyword arguments.

Version 0.3.9
=============

- Fix bug in passing of keyword arguments to Image readers.

Version 0.3.8
=============

- Make the Image object backward compatible.
- Improve documentation.

Version 0.3.7
=============

- Fix issue #28, reading from non-existing cell

Version 0.3.6
=============

- Add exception handling for opening a files
- Add lon, lat information in writing operation of GriddedBase

Version 0.3.5
=============

- Remove unnecessary dependencies and improve documentation.

Version 0.3.4
=============

- Add conda requirements file
- Add object base classes for time series and image
- Add image base and multitemporal-image base classes

Version 0.3.3
=============

- Update requirements

Version 0.3.2
=============

- Add ImageBase class (moved from pytesmo)
- Fixing documentation

Version 0.3.1
=============

- Updating pyscaffold version to 

Version 0.3.0
=============

- New GriddedBase class
- Slight changes in the method names

Version 0.2.0
=============

- Support of ioclass keyword arguments
- Fix iteration inconsistency

Version 0.1
===========

- First developer release
