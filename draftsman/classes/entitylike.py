# entitylike.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import abc
import six

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.blueprint import Blueprint


@six.add_metaclass(abc.ABCMeta)
class EntityLike(object):
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
        # Blueprint reference (Internal)
        # Overwritten if the EntityLike is placed inside a Blueprint
        self._blueprint = None

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
        # Rotatable? (Internal) (Overwritten if applicable)
        self._rotatable = False
        # Flippable? (Internal) (Overwritten if applicable)
        self._flippable = True

    # =========================================================================

    @property
    def blueprint(self):
        # type: () -> Blueprint
        """
        Read only
        TODO
        """
        return self._blueprint

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

    @property
    def rotatable(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._rotatable

    # =========================================================================

    # @property
    # def flippable(self):
    #     # type: () -> bool
    #     """
    #     Read only
    #     TODO
    #     """
    #     return self._flippable

    # =========================================================================
    # Abstract Properties
    # =========================================================================

    @abc.abstractproperty
    def name(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def type(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def id(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def position(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def collision_box(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def collision_mask(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def tile_width(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def tile_height(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def get_area(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def to_dict(self):  # pragma: no cover
        pass
