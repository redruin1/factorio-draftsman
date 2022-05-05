.. factorio-draftsman documentation master file

factorio-draftsman
==============================================

**factorio-draftsman** is a python module for creating Blueprint strings for the game `Factorio <https://factorio.com/>`_.

.. image:: ../img/logo.png
   :alt: The Draftsman logo created by an example script.

.. image:: https://readthedocs.org/projects/factorio-draftsman/badge/?version=latest
   :target: https://factorio-draftsman.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://codecov.io/gh/redruin1/factorio-draftsman/branch/main/graph/badge.svg?token=UERAOXVTO1
   :target: https://codecov.io/gh/redruin1/factorio-draftsman
   :alt: Code Coverage    

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code Style: Black

Overview:
---------

Draftsman aims to provide a 'one-stop shop' solution to the problem of manipulating blueprint strings. 
It allows the user to import, modify, create, add, remove, and export blueprints and their contents in dynamic and flexible ways. 
It's API is designed to be clear and self-documenting, from its imports to its errors. 

In addition to the standard features you would expect, Draftsman also has a number of quality-of-life features, including:

* Unique entity IDs, as well as dynamic association between entities.
* Querying blueprint contents by area, name, type, as well as other criteria.
* The grouping of entities to reuse for aid in structure and design.
* Verbose warnings for modifications on import normally ignored by Factorio.

Draftsman is also unique in that it emulates the `Factorio data lifecycle <https://lua-api.factorio.com/latest/Data-Lifecycle.html>`_ directly, extracting all data that the module uses directly from `Wube's public repository <https://github.com/wube/factorio-data>`_. 
This ensures a direct continuity between Factorio's data and Draftsman, which makes the module much easier to maintain over specific Factorio versions, as well as over time.
By emulating the data-lifecycle in this manner, Draftsman is also the first package of this type to allow mod support *built-in*.

Draftsman is cross-platform, and guaranteed to work on the latest versions of Python 2 and 3.
Draftsman is also guaranteed to work with versions of Factorio 1.0 and up. 
Prior to that most functionality *should* still work, but your mileage may vary.

Contents
--------
.. toctree::
   :maxdepth: 1

   quickstart.rst
   handbook/index.rst
   reference/index.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
