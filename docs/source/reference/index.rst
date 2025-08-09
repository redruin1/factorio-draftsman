Reference
=========

.. automodule:: draftsman
    :members:

Draftsman includes most of it's methods organized within a number of submodules:

* :doc:`blueprintable <./blueprintable>`
    Includes all Blueprintable objects, such as :py:class:`.Blueprint`, :py:class:`.BlueprintBook`, :py:class:`.UpgradePlanner`, :py:class:`.DeconstructionPlanner`, as well as Draftsman's :py:class:`.Group`.
* :doc:`constants <./constants>`
    Commonly (re)used enumerations required when defining blueprints or their entities.
* :doc:`entity <./entity>`
    All :py:class:`.Entity` implementations, as well as their abstract base classes.
* :doc:`error <./error>`
    All exception types that Draftsman can issue.
* :doc:`extras <./extras>`
    Extra features, such as a function to reverse all belts in a blueprint.
* :doc:`signatures <./signatures>`
    Abstract data format "signatures", for data types that are used across multiple class implementations.
* :doc:`tile <./tile>`
    The :py:class:`.Tile` class and related methods.
* :doc:`utils <./utils>`
    Additional generic utility functions.
* :doc:`warning <./warning>`
    All warning types that Draftsman can issue.
* :doc:`classes <./classes/index>`
    A directory containing all primary (sub)class implementations.
* :doc:`environment <./environment/index>`
    A directory containing modules for extracting data from Factorio and storing it as Draftsman's environment.
* :doc:`data <./data/index>`
    A directory containing modules reading and modifying Draftsman's environment.
* :doc:`prototypes <./prototypes/index>`
    A directory containing each individual :py:class:`.Entity` prototype definition.

.. toctree::
    :hidden:
    :maxdepth: 2

    blueprintable.rst
    constants.rst
    entity.rst
    error.rst
    extras.rst
    signatures.rst
    tile.rst
    utils.rst
    warning.rst
    classes/index.rst
    environment/index.rst
    data/index.rst
    prototypes/index.rst