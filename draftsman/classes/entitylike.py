# entitylike.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import abc
import copy
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
    * `tile_width`
    * `tile_height`
    * `position`
    * `collision_set`
    * `collision_mask`
    """

    def __init__(self):
        # type: () -> None
        # Parent reference (Internal)
        # Overwritten if the EntityLike is placed inside a Blueprint or Group
        self._parent = None

        # Default attributes (Overwritten on a per-Entity basis)
        self._power_connectable = False
        self._dual_power_connectable = False
        self._circuit_connectable = False
        self._dual_circuit_connectable = False
        self._double_grid_aligned = False
        self._rotatable = False
        self._flippable = True

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def parent(self):
        # type: () -> EntityCollection
        """
        The parent :py:class:`.EntityCollection` object that contains the entity,
        or ``None`` if the entity does not currently exist within an
        :py:class:`.EntityCollection`. Not exported; read only.

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
        this EntityLike does not have a concept of different rotation angles.
        For example, any :py:class:`.Reactor` entity will always return
        ``rotatable`` as ``False`` when queried. Not exported; read only.

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
        pass  # TODO: do we need this?

    @abc.abstractproperty
    def tile_height(self):  # pragma: no coverage
        pass  # TODO: do we need this?

    # =========================================================================
    # Abstract Methods
    # =========================================================================

    def on_insert(self, parent):  # pragma: no coverage
        # type: (EntityCollection) -> None
        """
        TODO
        """
        pass

    def on_remove(self, parent):  # pragma: no coverage
        # type: (EntityCollection) -> None
        """
        TODO
        """
        pass

    @abc.abstractmethod
    def mergable_with(self, other):  # pragma: no coverage
        # type: (EntityLike) -> bool
        """
        Checks to see if an entity is "mergable" with another entity. This means
        that if a certain set of criteria is met, the attributes of ``other``
        will be combined to the attributes of this entity. This is useful for
        mimicking cases where entities of the same name and type are placed on
        top of each other, merging them together into a single entity with
        shared attributes.

        For the full list of all merging rules, see (TODO).

        .. NOTE::
            This function does *not* actually merge the two, it simply checks
            to see if such a merge is considered valid. To actually merge two
            entities use :py:meth:`merge`.

        :param other: The other :py:class:`EntityLike` to check against.

        :returns: ``True`` if they can be merged, ``False`` otherwise.
        """
        pass

    @abc.abstractmethod
    def merge(self, other):  # pragma: no coverage
        # type: (EntityLike) -> None
        """
        Changes the attributes of the calling entity with the attributes of the
        passed in entity. The attributes of ``other`` take precedence over the
        attributes of the calling entity. They can be either copied or merged
        together, depending on the specific attribute being merged.

        For the full list of all merging rules, see (TODO).

        :param other: The other :py:class:`EntityLike` to merge with.
        """
        pass

    def get(self):
        # type: () -> Union[Entity, list[Entity]]
        """
        TODO
        """
        return self

    def __deepcopy__(self, memo):
        # type: (dict) -> EntityLike
        """
        We override the default deepcopy method so that we don't get infinite
        recursion when attempting to copy it's 'parent' attribute. We instead
        set it to ``None`` because we don't want entities to have a parent if
        they are not in an :py:class:`.EntityCollection`.

        This means that if you attempt to deepcopy an Entity that exists within
        an EntityCollection, that copied entity will *not* be inside of that
        EntityCollection, and will have to be added manually. If instead the
        *entire* EntityCollection is deepcopied, then the parent will be the
        copied EntityCollection and everything *should* work.

        See `here <https://github.com/redruin1/factorio-draftsman/issues/22>`
        for more information.

        :returns: A copy of the EntityLike.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "_parent":
                setattr(result, k, None)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result
