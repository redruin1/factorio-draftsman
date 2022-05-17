# error.py

"""
Draftsman errors. Used to enforce "Factorio-safety".
"""

# =============================================================================
# Base
# =============================================================================


class DraftsmanError(Exception):
    """
    Default error for ``draftsman``. Issued when some behavior directly
    conflicts with the module's function.
    """

    pass


class DataFormatError(DraftsmanError):
    """
    Issued when a value passed in to a method or attribute violates the required
    structure for that data, such that it violates "Factorio-correctness".
    """

    pass


# =============================================================================
# Blueprintables
# =============================================================================


class IncorrectBlueprintTypeError(DraftsmanError):
    """
    Raised when attempting to construct a :py:class:`.Blueprint` object without
    the ``"blueprint"`` key or a :py:class:`.BlueprintBook` without the
    ``"blueprint_book"`` key in their root trees. Most commonly issued when
    trying to create a ``Blueprint`` with a ``BlueprintBook`` string, and
    vice-versa.
    """

    pass


class DuplicateIDError(DraftsmanError):
    """
    Raised when two EntityLike's are added to a :py:class:`.EntityCollection`
    with the same ID, which is disallowed.
    """

    pass


class UnreasonablySizedBlueprintError(DraftsmanError):
    """
    Raised when a :py:class:`.Blueprint` exceeds 10,000 x 10,000 tiles in
    relative size. Note that this is not about distance from the origin; rather
    the distance from the furthest entities on either axis across the Blueprint.
    """

    pass


class RotationError(DraftsmanError):
    """
    Raised when a rotation angle has been chosen that does not align with the
    possible rotations that the :py:class:`.EntityCollection` can have, such as
    rotations by 45 degrees.
    """

    pass


class FlippingError(DraftsmanError):
    """
    Raised when attempting to flip a :py:class:`.EntityCollection` that contains
    entities that cannot be flipped.
    """

    pass


# =============================================================================
# Entities
# =============================================================================


class InvalidEntityError(DraftsmanError):
    """
    Raised when an Entity's name is not one of the ``similar_entities`` for it's
    child type, or when it is not any valid entry in
    :py:data:`draftsman.data.entities.raw`.
    """

    pass


class InvalidOperationError(DraftsmanError):
    """
    Raised whan a condition is set to have an unrecognized operation for that
    particular case.
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
    Raised when either a circuit wire is not either ``"red"`` or ``"green"`` or
    when a power wire connection type is not either ``"Cu0"`` or ``"Cu1"``.
    """

    pass


class InvalidConnectionError(DraftsmanError):
    """
    Raised when an Association to an Entity still persists even when the Entity
    that it refers to has been deleted.
    """


class InvalidConnectionSideError(DraftsmanError):
    """
    Raised when a circuit connection is connected to a side other than ``1``
    or ``2``.
    """

    pass


class InvalidRecipeError(DraftsmanError):
    """
    Raised when an input recipe name is not an entry in
    :py:data:`draftsman.data.recipes.raw`.
    """

    pass


class InvalidModuleError(DraftsmanError):
    """
    Raised when an input module name is not an entry in
    :py:data:`draftsman.data.modules.raw`
    """

    pass


class InvalidInstrumentID(DraftsmanError):
    """
    Raised when setting a :py:class:`ProgrammableSpeaker`'s instrument to a
    number that exceeds it's instrument count, or a string that is not the name
    of any of it's instruments.
    """

    pass


class InvalidNoteID(DraftsmanError):
    """
    Raised when setting a :py:class:`ProgrammableSpeaker`'s note to a number
    that exceeds the number of notes in it's selected instrument, or a string
    that is not the name of any of the notes created by the current instrument.
    """


class InvalidSideError(DraftsmanError):
    """
    Raised when a Splitter's input or output priority is set to something other
    than ``"left"`` or ``"right"``.
    """

    pass


class InvalidFluidError(DraftsmanError):
    """
    Raised when a :py:class:`InfinityPipe`'s fluid is set to anything other than
    a valid entry in :py:data:`draftsman.data.signals.fluid`.
    """

    pass


class EntityNotPowerConnectableError(DraftsmanError):
    """
    Raised when a power connection is attempted between an entity or entities
    that cannot be connected with power wires.
    """

    pass


class EntityNotCircuitConnectableError(DraftsmanError):
    """
    Raised when a circuit connection is attempted between an entity or entities
    that cannot be connected with circuit wires.
    """

    pass


# =============================================================================
# Environment
# =============================================================================


class IncompatableModError(DraftsmanError):
    """
    Raised when two mods in the ``factorio-mods`` folder specify the other as
    incompatible.
    """

    pass


class MissingModError(DraftsmanError):
    """
    Raised when a mod depends on another to function, but the desired mod is not
    in the ``factorio-mods`` folder.
    """

    pass


class IncorrectModVersionError(DraftsmanError):
    """
    Raised when a loaded mod's version is incompatible with the version of
    Factorio or the versions of other mods.
    """

    pass


class IncorrectModFormatError(DraftsmanError):
    """
    Raised when the format of a loaded mod conflicts with expectations.
    """

    pass


# =============================================================================
# Data
# =============================================================================


class InvalidTileError(DraftsmanError):
    """
    Raised when creating a :py:class:`.Tile` with, or changing it's name to,
    anything other than a valid tile name.
    """

    pass


class InvalidSignalError(DraftsmanError):
    """
    Raised when a signal name does not match any valid entry in
    :py:data:`draftsman.data.signals.raw`.
    """

    pass


class InvalidItemError(DraftsmanError):
    """
    Raised when an item name does not match any valid entry in
    :py:data:`draftsman.data.items.raw`.
    """

    pass


# =============================================================================
# Utilities
# =============================================================================


class MalformedBlueprintStringError(DraftsmanError):
    """
    Raised when a blueprint string cannot be resolved due to an error with the
    zlib or base64 decompression. This usually means that the string is either
    missing characters or has been encoded improperly.
    """

    pass
