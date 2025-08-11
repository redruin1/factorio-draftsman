Validation
==========

Factorio-safety and Factorio-correctness
----------------------------------------

Draftsman is designed to be as easy to pick up and use as possible, particularly for the layman Factorio players who do not posess intricate knowledge of Factorio's blueprint string format.
To help ensure this, Draftsman (by default) has a suite of mechanisms for ensuring proper usage, reducing the hysterisis of creating a disformed blueprint string, attempting to import it into Factorio, it failing with a difficult to read error message, deducing the mistake, and then finally fixing your script.
This is particularly handy for the majority of "layman" Factorio players who do not posess intricate knowledge of Factorio's blueprint string format.

Draftsman is fully annotated and mypy compliant, meaning that you can use any PEP-compliant static analysis tools with Draftsman:

TODO: example

However, while this is helpful and incurs no cost, it has limitations. 
For example, one of this simplest Draftsman utilities (entity name suggestion) is entirely impossible to do statically, since it depends on the data of the environment which must be loaded beforehand:

.. doctest::

    >>> from draftsman.entity import Container
    >>> Container("woden-chest")
    %%%: UnknownEntityWarning: Unknown entity 'woden-chest'; did you mean 'wooden-chest'?
        ...

Instead of fully relying on static analysis, Draftsman also has a suite of runtime validators that it runs to ensure *Factorio-safety* and *Factorio-correctness*.
This allows you to use Draftsman as not only a way to manipulate blueprint strings, but also a way to lint them:

.. code-block:: python

    # TODO


These warnings and exceptions can then be caught or ignored, at the user's discretion.

However, while runtime validation is useful when prototyping your scripts; it incurs a serious performance overhead, especially when working with large blueprints with very many components.
In addition, a user might want to control the types of errors/warnings that are issued; sometimes you might want only to be notified of catastrophic errors and to ignore minor issues, and perhaps at other times you want even more linting-like behavior than the default setting provides.
Thus, validation can be configured to meet individual scripts needs:

.. code-block:: python

    import draftsman
    from draftsman.constants import ValidationMode

    draftsman.validation.set_mode(ValidationMode.DISABLED)
    # No Draftsman errors will be issued beyond this point.

Here ``ValidationMode`` corresponds to different preconfigured severities, in order of least to most strict:

* ``DISABLED``: Disables all validation entirely, reducing runtime cost to almost nothing.
* ``MINIMUM``: Only issues exceptions when Draftsman is absolutely certain that the structure of data it owns is malformed in some way, and will be unable to import into Factorio - aligning with *Factorio-safety*.
* ``STRICT``: The default Draftsman behavior. Issues all the same exceptions of ``MINIMUM``, in addition to warnings about items that Draftsman *believes* will cause an error on import, but cannot guarantee. An example includes things like trying to create a modded entity that Draftsman does not know anything about - it *might* have the correct attributes and data and import into the game just fine, but Draftsman cannot know for sure - so it issues a warning. Matching Draftsman's environment will resolve errors like these.
* ``PEDANTIC``: This includes all of the above errors and warnings, in addition to "ineffectual" issues where no functionality is different, albeit conceptually out-of-spec.

This flag is global for the entire module, but it can be used as a context manager if you only want to change the validation mode for a specific section of code:

.. code-block:: python

    draftsman.validation.set_mode(ValidationMode.DISABLED):
    assert draftsman.validation.get_mode() is ValidationMode.DISABLED

    with draftsman.validation.set_mode(ValidationMode.PEDANTIC):
        assert draftsman.validation.get_mode() is ValidationMode.PEDANTIC

    # Now that we're out of the context manager block, we return to `DISABLED`
    assert draftsman.validation.get_mode() is ValidationMode.DISABLED