# entitylike.py

import abc

from typing import Union


# name
# type
# id
# position
# collision_box
# width, height
# get_area()
# to_dict()
# set_absolute_position()
# set_tile_position()

# similar_entities?

class EntityLike(metaclass=abc.ABCMeta):
    """
    Abstract base class for a blueprintable entity. Allows the user to specify
    custom entity analogues that can be passed into Blueprint instances. `Group`
    and `RailPlanner` are examples of custom EntityLike classes.

    All `EntityLike` subclasses must have the following properties:
        * `name`
        * `type`
        * `id`
        * `collision_box`
        * `tile_width`
        * `tile_height`

    All `EntityLike` subclasses must have the following methods:
        * `get_area()` for placing them in spatial hashmap(?)
        * `to_dict()` for converting it to a blueprint string when exported
    """

    def __init__(self):
        # Power connectable? (Internal) (Overwritten if applicable)
        self._power_connectable = False
        # Dual power connectable? (Internal) (Overwritten if applicable)
        self._dual_power_connectable = False

        # Circuit connectable? (Interal) (Overwritten if applicable)
        self._circuit_connectable = False
        # Dual circuit connectable? (Internal) (Overwritten if applicable)
        self._dual_circuit_connectable = False

        # Double grid aligned? (Internal) (Overwritten if applicable)
        self._double_grid_aligned = False

    # =========================================================================

    @property
    def power_connectable(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._power_connectable

    # =========================================================================

    @property
    def dual_power_connectable(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._dual_power_connectable

    # =========================================================================

    @property
    def circuit_connectable(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._circuit_connectable

    # =========================================================================

    @property
    def dual_circuit_connectable(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._dual_circuit_connectable

    # =========================================================================

    @property
    def double_grid_aligned(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._double_grid_aligned

    # =========================================================================
    # Abstract Properties
    # =========================================================================

    @abc.abstractproperty
    def name(self): # pragma: no cover
        pass

    @abc.abstractproperty
    def type(self): # pragma: no cover
        pass

    @abc.abstractproperty
    def id(self): # pragma: no cover
        pass

    @abc.abstractproperty
    def position(self): # pragma: no cover
        pass

    @abc.abstractproperty
    def collision_box(self): # pragma: no cover
        pass

    @abc.abstractproperty
    def tile_width(self): # pragma: no cover
        pass

    @abc.abstractproperty
    def tile_height(self): # pragma: no cover
        pass

    @abc.abstractmethod
    def get_area(self): # pragma: no cover
        pass

    @abc.abstractmethod
    def to_dict(self): # pragma: no cover
        pass