# entitylike.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import abc
import six

from typing import TYPE_CHECKING, Union

from draftsman.classes.spatiallike import SpatialLike

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import EntityCollection
    from draftsman.classes.entity import Entity


@six.add_metaclass(abc.ABCMeta)
class EntityLike(SpatialLike):
    """
    Abstract base class for a blueprintable entity. Allows the user to specify
    custom entity analogues that can be passed into Blueprint instances. `Group`
    and `RailPlanner` are examples of custom EntityLike classes.

    All `EntityLike` subclasses must implement the following properties:

    * `name`
    * `type`
    * `id`
    * `position`
    * `collision_box`
    * `collision_mask`
    * `tile_width`
    * `tile_height`
    """

    def __init__(self):
        # type: () -> None
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
        # type: () -> EntityCollection
        """
        The parent EntityCollection object that contains the entity, or
        ``None`` if the entity does not currently exist within an
        EntityCollection. Not exported; read only.

        :type: ``EntityCollection``
        """
        return self._parent

    # =========================================================================

    @property
    def power_connectable(self):
        # type: () -> bool
        """
        Whether or not this EntityLike can be connected using power wires. Not
        exported; read only.

        :type: ``bool``
        """
        return self._power_connectable

    # =========================================================================

    @property
    def dual_power_connectable(self):
        # type: () -> bool
        """
        Whether or not this EntityLike has two power connection points. Not
        exported; read only.

        :type: ``bool``
        """
        return self._dual_power_connectable

    # =========================================================================

    @property
    def circuit_connectable(self):
        # type: () -> bool
        """
        Whether or not this EntityLike can be connected using circuit wires. Not
        exported; read only.

        :type: ``bool``
        """
        return self._circuit_connectable

    # =========================================================================

    @property
    def dual_circuit_connectable(self):
        # type: () -> bool
        """
        Whether or not this EntityLike has two circuit connection points. Not
        exported; read only.

        :type: ``bool``
        """
        return self._dual_circuit_connectable

    # =========================================================================

    @property
    def double_grid_aligned(self):
        # type: () -> bool
        """
        Whether or not this EntityLike is "double-grid-aligned", which applies
        to a number of rail entities. Not exported; read only.

        :type: ``bool``
        """
        return self._double_grid_aligned

    # =========================================================================

    @property
    def rotatable(self):
        # type: () -> bool
        """
        Whether or not this EntityLike can be rotated. Note that this does not
        mean that the entity will prevent a blueprint from rotating; more, that
        this blueprint does not have a concept of different rotation angles. For
        example, any :py:class:`.Reactor` entity will always return ``rotatable``
        as ``False`` when queried. Not exported; read only.

        :type: ``bool``
        """
        return self._rotatable

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

    def on_insert(self):  # pragma: no coverage
        # type: () -> None
        pass

    def on_remove(self):  # pragma: no coverage
        # type: () -> None
        pass

    def get(self):
        # type: () -> Union[Entity, list[Entity]]
        return self
