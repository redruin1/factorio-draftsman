# errors.py

# TODO: documentation!
"""
TODO
"""


class DraftsmanError(Exception):
    """
    Default error for `draftsman`.
    """

    pass


# Utils
class MalformedBlueprintStringError(DraftsmanError):
    """
    Raised when a blueprint string cannot be resolved due to an error with the
    zlib or JSON decompression. This usually means that the string is either
    missing characters or has been constructed improperly.
    """

    pass


class DataFormatError(DraftsmanError):
    """
    Usually a thin wrapper around SchemaError; issued when a value passed in
    to a method or attributes violates the required structure for that data.
    """

    pass


# Blueprints
class IncorrectBlueprintTypeError(DraftsmanError):
    """
    Raised when a ``Blueprint`` doesn't have the key "blueprint" in it's root
    tree, and when ``BlueprintBook`` doesn't have the key "blueprint-book" in
    it's tree. Most commonly issued when trying to create a ``Blueprint`` with
    a ``BlueprintBook`` string, and vice-versa.
    """

    pass


class DuplicateIDError(DraftsmanError):
    """
    Raised when two EntityLike's are added to a ``Blueprint`` with the same id
    in the same Collection, which is disallowed.
    """

    pass


class UnreasonablySizedBlueprintError(DraftsmanError):
    """
    Raised when a Blueprint exceeds 10,000 x 10,000 tiles in relative size.
    Note that this is not about distance from the origin; rather the distance
    from the furthest entities on either axis within the blueprint itself.
    """

    pass


class RotationError(DraftsmanError):
    """
    Raised when a rotation angle has been chosen that does not align with the
    possible rotations that the Collection can have, such as rotations by 45
    degrees.
    """

    pass


class FlippingError(DraftsmanError):
    """
    Raised when attempting to flip a Collection that contains entities that
    cannot be flipped.
    """

    pass


# Tiles
class InvalidTileError(DraftsmanError):
    """
    Raised when creating a Tile or changing it's name to anything other than a
    valid Factorio tile ID.
    """

    pass


# Signals
class InvalidSignalError(DraftsmanError):
    """
    Raised when a signal name does not match any valid entry in
    ``draftsman.data.signals.raw``.
    """

    pass


# Items
class InvalidItemError(DraftsmanError):
    """
    Raised when an item name does not match any valid entry in
    ``draftsman.data.items.raw``.
    """

    pass


# Entities
class InvalidEntityError(DraftsmanError):
    """
    Raised when an Entity's name is not one of the similar_entities for it's
    child type, or when it is not any valid entity name.
    """

    pass


class InvalidOperationError(DraftsmanError):
    """
    Raised when a circuit condition of some type (Logisitic, EnableDisable,
    Arithmetic/Decider, etc.) operation does not match any valid operation for
    that particular case.

    ```
        arithmetic_combinator.set_conditions(10, "wrong", 10, "signal-red")
    ```
    """

    pass


class InvalidModeError(DraftsmanError):
    """
    Raised when a string mode doesn't match any valid value for that particular
    method.
    """

    pass


class InvalidWireTypeError(DraftsmanError):
    """
    Raised when either a circuit wire is not either "red" or "green" or
    when a power wire connection type is not either "Cu0" or "Cu1".
    """

    pass


class InvalidConnectionSideError(DraftsmanError):
    """
    Raised when a circuit connection is connected to a side other than "1" or
    "2".
    """

    pass


class InvalidRecipeError(DraftsmanError):
    """
    Raised when an input recipe name is not an entry in
    ``draftsman.data.recipes.raw``.
    """

    pass


class InvalidModuleError(DraftsmanError):
    """
    Raised when an input module name is not an entry in
    ``draftsman.data.modules.raw``
    """

    pass


class InvalidInstrumentID(DraftsmanError):
    """
    Raised when setting a ProgrammableSpeaker's instrument to a number that
    exceeds it's instrument count, or a string that is not the name of any of
    it's instruments.
    """

    pass


class InvalidNoteID(DraftsmanError):
    """
    Raised when setting a ProgrammableSpeaker's note to a number that exceeds
    the number of notes in it's selected instrument, or a string that is not
    the name of any of the notes created by the current instrument.
    """


class InvalidSideError(DraftsmanError):
    """
    Raised when a Splitter's input or output priority is set to something other
    than 'left' or 'right'.
    """

    pass


class InvalidFluidError(DraftsmanError):
    """
    Raised when a InfinityPipe's fluid is set to anything other than a valid
    entry in ``draftsman.data.signals.fluid``.
    """

    pass


class BarIndexError(DraftsmanError):
    """
    Raised when the set value for a `Container`'s bar is not an unsigned short
    (in the range `[0, 65535]`).
    """

    pass


class FilterIndexError(DraftsmanError):
    """
    Raised when the filter index for an Entity with item-request filters is
    outside of the valid range for the Entity.
    """

    pass


class EntityNotPowerConnectableError(DraftsmanError):
    """
    Raised when a power connection is attempted between an Entity or Entities
    that cannot be connected with power wires.
    """

    pass


class EntityNotCircuitConnectableError(DraftsmanError):
    """
    Raised when a circuit connection is attempted between an Entity or Entities
    that cannot be connected with circuit wires.
    """

    pass


# Update
class IncompatableModError(DraftsmanError):
    """
    Raised when two mods in the `factorio-mods` folder specify the other as
    incompatible.
    """

    pass


class MissingModError(DraftsmanError):
    """
    Raised when a mod depends on another to function, but the desired mod is not
    in the `factorio-mods` folder.
    """

    pass


class IncorrectModVersionError(DraftsmanError):
    """
    Raised when a loaded mod version is incompatible with the version of
    Factorio or other mods.
    """

    pass
