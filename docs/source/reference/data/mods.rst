.. py:currentmodule:: draftsman.data.mods

:py:mod:`~draftsman.data.mods`
==============================

.. py:data:: mod_list

    A ``dict`` of all the mods currently loaded, and their version as a tuple.
    Allows for checking the loaded mods at runtime, such as to ensure that a specific mod is enabled and loaded before trying to make modded entities.
    Exists as the format:

    .. code-block:: python

        {
            "mod_name_1": mod_version_tuple_1,
            "mod_name_2": mod_version_tuple_2,
            # ...
        }

    :example:

    .. code-block:: python

        from draftsman.data import mods

        print(mods.mod_list["base"]) # "base" is Factorio itself, and is always considered a mod

    .. code-block:: text

        (1, 1, 57, 0)