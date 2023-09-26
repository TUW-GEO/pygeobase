=========
pygeobase
=========

.. image:: https://github.com/TUW-GEO/pygeobase/workflows/ubuntu/badge.svg
   :target: https://github.com/TUW-GEO/pygeobase/actions/workflows/ubuntu.yml

.. image:: https://github.com/TUW-GEO/pygeobase/workflows/windows/badge.svg
   :target: https://github.com/TUW-GEO/pygeobase/actions/workflows/windows.yml

.. image:: https://coveralls.io/repos/github/TUW-GEO/pygeobase/badge.svg?branch=master
   :target: https://coveralls.io/github/TUW-GEO/pygeobase?branch=master

.. image:: https://badge.fury.io/py/pygeobase.svg
    :target: https://badge.fury.io/py/pygeobase

.. image:: https://readthedocs.org/projects/pygeobase/badge/?version=latest
    :alt: ReadTheDocs
    :target: https://pygeobase.readthedocs.io/en/stable/

The pygeobase package implements base class definitions for the I/O interface used in pytesmo_, pynetCF_, and other packages.

.. _pytesmo: https://github.com/TUW-GEO/pytesmo
.. _pynetCF: https://github.com/TUW-GEO/pynetCF

Citation
========

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.846761.svg
   :target: https://doi.org/10.5281/zenodo.846761

If you use the software in a publication then please cite it using the Zenodo DOI.
Be aware that this badge links to the latest package version.

Please select your specific version at https://doi.org/10.5281/zenodo.846761 to get the DOI of that version.
You should normally always use the DOI for the specific version of your record in citations.
This is to ensure that other researchers can access the exact research artefact you used for reproducibility.

You can find additional information regarding DOI versioning at http://help.zenodo.org/#versioning

Installation
============

This package should be installable through pip:

.. code::

    pip install pygeobase

Its only dependecy is ``numpy``. But to use it effectively you will also probably want to install pygeogrids_.

.. _pygeogrids: https://github.com/TUW-GEO/pygeogrids

Contribute
==========

We are happy if you want to contribute. Please raise an issue explaining what
is missing or if you find a bug. We will also gladly accept pull requests
against our master branch for new features or bug fixes.

Guidelines
----------

If you want to contribute please follow these steps:

- Fork the pygeobase repository to your account
- Clone the repository
- make a new feature branch from the pygeobase master branch
- Add your feature
- Please include tests for your contributions in one of the test directories.
  We use py.test so a simple function called test_my_feature is enough
- submit a pull request to our master branch


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.
