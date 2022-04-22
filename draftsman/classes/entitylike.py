# entitylike.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import abc
import six

from typing import TYPE_CHECKING

from draftsman.classes.spatiallike import SpatialLike

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import Collection


@six.add_metaclass(abc.ABCMeta)
class EntityLike(SpatialLike):
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
        # Parent reference (Internal)
        # Overwritten if the EntityLike is placed inside a Blueprint or Group
        self._parent = None

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
    def parent(self):
        # type: () -> Collection
        # TODO: change output type to something generic
        """
        Read only
        TODO
        """
        return self._parent

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

    @property
    def flippable(self):
        # type: () -> bool
        """
        Read only
        TODO
        """
        return self._flippable

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
    def tile_width(self):  # pragma: no coverage
        pass

    @abc.abstractproperty
    def tile_height(self):  # pragma: no coverage
        pass

    # @abc.abstractmethod
    # def get_area(self):  # pragma: no coverage
    #     pass

    def on_insert(self):  # pragma: no coverage
        """
        Default function. Called when an this EntityLike is inserted into an
        EntityList. Allows the user to perform extra checks, validation, or
        operations when the EntityLike is added to the `Collection`. For
        example, if we are placing a rail signal in a blueprint, we might want
        to check the surrounding area to see if we are adjacent to a rail, and
        issue a warning if we are not.

        Note that this is only intended to perform checks in relation to THIS
        specific entity; the `Collection` class has it's own custom functions
        for managing the parent's state.
        """
        pass

    def on_remove(self):  # pragma: no coverage
        """
        Default function. Same functionality as `on_insert`, but for cleanup
        operations when removed instead of when inserted.
        """
        pass

    def get(self):
        # type: () -> EntityLike
        """
        Called during `blueprint.to_dict()`. Returns the entity or list of
        entities that make up this EntityLike. On `Entity`s this is redundant,
        but it allows the user to specify exactly what entities they want to
        return.
        """
        return self
