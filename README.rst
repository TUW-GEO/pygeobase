=========
pygeobase
=========

The pygeobase package implements base class definitions for the I/O interface used in pytesmo_, pynetCF_, and other packages.

.. _pytesmo: https://github.com/TUW-GEO/pytesmo
.. _pynetCF: https://github.com/TUW-GEO/pynetCF

Documentation
=============

.. image:: https://readthedocs.org/projects/pygeobase/badge/?version=latest
   :target: http://pygeobase.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status

Installation
============

This package should be installable through pip::

    pip install pygeobase

Its only dependecy is ``numpy``. But to use it effectively you will also probably want to install pygeogrids_.

.. _pygeogrids: https://github.com/TUW-GEO/pygeogrids

Setup Development environment
-----------------------------

1. Install Miniconda_. This will give you the ``conda`` command in your shell.
2. Run ``conda env create -f conda_environment.yml`` this will install all the
   dependencies listed in the ``conda_environment.yml`` file in this repository.
   By default this will create a new conda enviroment with the name ``pygeobase_env``.
   This can be changed by editing the ``conda_environment.yml`` file.

.. _Miniconda: http://conda.pydata.org/miniconda.html

Example installation script
---------------------------

The following script will install miniconda and setup the environment on a UNIX
like system. Miniconda will be installed into ``$HOME/miniconda``.

::

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

After that you should be able to run::

    python setup.py test

to run the test suite.
