# draftsman_warnings.py

import warnings


class DraftsmanWarning(UserWarning):
    """
    Root warning class for `draftsman`. Useful if you want to easily ignore all
    warnings issued from the module without getting rid of errors entirely;
    simply filter this class. This is a subclass of `UserWarning`, and all other
    warnings are subclasses of this.
    """

    pass


class ValueWarning(DraftsmanWarning):
    """
    Generic warning, similar to ValueError. Raised when a input value is
    incorrect, but wont cause the blueprint to fail import.
    """

    pass


class DirectionWarning(DraftsmanWarning):
    """
    Raised when the direction does not match the rotation type, e.g. setting
    a 4-way rotatable Entity to have `Direction.NORTHWEST`.
    """

    pass


class BarIndexWarning(DraftsmanWarning):
    """
    Raised when the location of the inventory bar is out of range for the
    particular Entity.
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


class RailAlignmentWarning(DraftsmanWarning):
    """
    Raised when an Entity is placed on odd coordinates when it's type restricts
    its placement to the rail grid.
    """

    pass


class ItemLimitationWarning(DraftsmanWarning):
    """
    Raised when an Item request does not match the AssemblingMachine's recipe
    inputs.
    """

    pass


class ModuleLimitationWarning(DraftsmanWarning):
    """
    Raised when the modules inside of an Entity conflict, either with the entity
    type or its recipe.
    """

    pass


class ModuleCapacityWarning(DraftsmanWarning):
    """
    Raised when the number of modules in an Entity with module slots exceeds
    the total module capacity.
    """

    pass


class TemperatureRangeWarning(DraftsmanWarning):
    """
    Raised when the temperature of a heat interface is outside of the range
    [0, 1000].
    """

    pass


class VolumeRangeWarning(DraftsmanWarning):
    """
    Raised when the volume of a programmable speaker is outside of the range
    [0.0, 1.0]
    """

    pass


class HiddenEntityWarning(DraftsmanWarning):
    """
    Raised when an Entity that is marked as hidden is placed within a blueprint.
    """

    pass


class OverlappingEntitiesWarning(DraftsmanWarning):
    """
    Raised when the collision_box for an entity overlaps another inside a
    Blueprint.
    """

    pass


class OverlappingTilesWarning(DraftsmanWarning):
    """
    Raised when two tiles in a blueprint occupy the same coordinate.
    """

    pass


class UselessConnectionWarning(DraftsmanWarning):
    """
    Raised when a circuit connection is functionally useless, such as when a
    wall is connected with a circuit wire without an adjacent gate.
    """

    pass
