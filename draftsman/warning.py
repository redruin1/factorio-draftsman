# warning.py

"""
Draftsman warnings. Used to enforce "Factorio-correctness".
"""


class DraftsmanWarning(UserWarning):
    """
    Root warning class for ``draftsman``. Useful if you want to easily ignore
    all warnings issued from the module without getting rid of warnings entirely;
    simply filter this class. This is a subclass of ``UserWarning``, and all
    other Draftsman warnings are subclasses of this.
    """

    pass


class ValueWarning(DraftsmanWarning):
    """
    Generic warning, similar to ``ValueError``. Raised when a input value is
    incorrect, but wont cause the blueprint to fail import.
    """

    pass


class DirectionWarning(DraftsmanWarning):
    """
    Raised when the direction does not match the rotation type, e.g. setting
    a 4-way rotatable Entity's direction to :py:data:`Direction.NORTHWEST`.
    """

    pass


class FlippingWarning(DraftsmanWarning):
    """
    Raised when attempting to flip an entity that may or not be able to be
    flipped. This is only raised when flipping an :py:class:`EntityCollection`
    with modded entities.
    """

    pass


class IndexWarning(DraftsmanWarning):
    """
    Raised when the index of some element is out of expected range, though not
    to the point of failing import.
    """

    pass


class ConnectionDistanceWarning(DraftsmanWarning):
    """
    Raised when an attempted wire connection is too distant to be properly
    resolved in-game.
    """

    pass


class ConnectionSideWarning(DraftsmanWarning):
    """
    Raised when an attempted wire connection is made to an invalid side of the
    Entity.
    """

    pass


class TooManyConnectionsWarning(DraftsmanWarning):
    """
    Raised when a power connection is attempted between an power-pole that
    already has 5 or more connections.
    """

    pass


class RailAlignmentWarning(DraftsmanWarning):
    """
    Raised when an Entity is placed on odd coordinates when it's type restricts
    its placement to the rail grid.
    """

    pass


class ItemLimitationWarning(DraftsmanWarning):
    """
    Raised when an item request does not match the :py:class:`.AssemblingMachine`'s
    recipe inputs.
    """

    pass


class ItemCapacityWarning(DraftsmanWarning):
    """
    Raised when an item request exeeds the number of inventory slots of the
    entity.
    """

    pass


class ModuleLimitationWarning(DraftsmanWarning):
    """
    Raised when the modules inside of an :py:class:`.Entity` conflict, either
    with the Entity's type or it's recipe.
    """

    pass


class ModuleCapacityWarning(DraftsmanWarning):
    """
    Raised when the number of modules in an :py:class:`.Entity` with module slots
    exceeds the total module capacity.
    """

    pass


class TemperatureRangeWarning(DraftsmanWarning):
    """
    Raised when the temperature of a heat interface is outside of the range
    ``[0, 1000]``.
    """

    pass


class VolumeRangeWarning(DraftsmanWarning):
    """
    Raised when the volume of a programmable speaker is outside of the range
    ``[0.0, 1.0]``
    """

    pass


class HiddenEntityWarning(DraftsmanWarning):
    """
    Raised when an Entity that is marked as hidden is placed within a blueprint.
    """

    pass


class OverlappingObjectsWarning(DraftsmanWarning):
    """
    Raised when the area returned by :py:meth:`~.SpatialLike.get_area()` for an
    object overlaps another object or objects already placed inside a
    :py:class:`.SpatialHashMap`. This warning is raised for both entities and
    tiles.
    """

    pass


class UselessConnectionWarning(DraftsmanWarning):
    """
    Raised when a circuit connection is functionally useless, such as when a
    wall is connected with a circuit wire without an adjacent gate (which *is*
    possible).
    """

    pass
