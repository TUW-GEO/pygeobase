=========
pygeobase
=========

.. image:: https://travis-ci.org/TUW-GEO/pygeobase.svg?branch=master
    :target: https://travis-ci.org/TUW-GEO/pygeobase

.. image:: https://coveralls.io/repos/github/TUW-GEO/pygeobase/badge.svg?branch=master
   :target: https://coveralls.io/github/TUW-GEO/pygeobase?branch=master

.. image:: https://badge.fury.io/py/pygeobase.svg
    :target: https://badge.fury.io/py/pygeobase

.. image:: https://readthedocs.org/projects/pygeobase/badge/?version=latest
   :target: http://pygeobase.readthedocs.org/en/latest/?badge=latest

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

Development setup
-----------------

For Development we recommend a ``conda`` environment. You can create one
including test dependencies and debugger by running
``conda env create -f conda_requirements.yml``. This will create a new
``pygeobase_env`` environment which you can activate by using
``source activate pygeobase_env``.

Example installation script
---------------------------

The following script will install miniconda and setup the environment on a UNIX
like system. Miniconda will be installed into ``$HOME/miniconda``.

.. code::

   wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
   bash miniconda.sh -b -p $HOME/miniconda
   export PATH="$HOME/miniconda/bin:$PATH"
   git clone git@github.com:TUW-GEO/pygeobase.git pygeobase
   cd pygeobase
   conda env create -f conda_environment.yml
   source activate pygeobase_env

This script adds ``$HOME/miniconda/bin`` temporarily to the ``PATH`` to do this
permanently add ``export PATH="$HOME/miniconda/bin:$PATH"`` to your ``.bashrc``
or ``.zshrc``

The last line in the example activates the ``pygeobase_env`` environment.

After that you should be able to run:

.. code::

    python setup.py test

to run the test suite.

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
