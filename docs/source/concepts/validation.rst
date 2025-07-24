Validation
==========

Draftsman is fully annotated and mypy compliant, meaning that you can use any PEP-compliant static analysis tools with Draftsman:

TODO: example

However, while this is helpful and incurs no cost, it has limitations. 
For example, one of this simplest Draftsman utilities (entity name suggestion) is entirely impossible to do statically, since it depends on the data of the environment which must be loaded beforehand:

.. doctest::

    >>> from draftsman.entity import Container
    >>> Container("woden-chest")
    UnknownEntityWarning: Unknown entity 'woden-chest'; did you mean 'wooden-chest'?

Instead of fully relying on static analysis, Draftsman also has a suite of runtime validators that it runs to ensure *Factorio-safety* and *Factorio-correctness*.
This allows you to use Draftsman as not only a way to manipulate blueprint strings, but also a way to lint them:

.. code-block:: python

    # TODO

However, runtime validation of course incurs a runtime cost, which may not be desirable. 
Hence, Draftsman allows you to disable runtime validation in cases where it is deemed unnecessary:

TODO

You may also want

Entity Attributes
-----------------

Most attributes on entities are implemented as properties with custom getters and setters.
This allows for a clean API, inline type checking, as well as ensuring that certain values are read only and not (easily) deletable.
It also allows for the ability to specify values in more concise "shorthand" formats, which are then automatically expanded into their true internal representation:

.. code-block:: python

    # TODO

TODO

.. code-block:: python

    container = Container()    
    # Incorrect values are correctly caught by validators at runtime
    container.bar = "incorrect"

By default, entity attributes run a set of validator functions at runtime. However, these functions can be disabled to reduce (almost) all of the overhead associated with them.