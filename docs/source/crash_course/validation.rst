Validation
==========

Draftsman is fully annotated and mypy compliant, meaning that you can use any PEP-compliant static analysis tools with Draftsman:

TODO: example

However, while this is helpful and incurs no cost, it has limitaions. 
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