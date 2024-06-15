# entitylike.py

from abc import ABCMeta, abstractmethod
import copy

from typing import Optional, Union

from draftsman.classes.spatial_like import SpatialLike

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import EntityCollection
    from draftsman.classes.entity import Entity


class EntityLike(SpatialLike, metaclass=ABCMeta):
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

    def __init__(self) -> None:
        # Parent reference (Internal)
        # Overwritten if the EntityLike is placed inside a Blueprint or Group
        self._parent = None

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def parent(self) -> "EntityCollection":
        """
        The parent :py:class:`.EntityCollection` object that contains the entity,
        or ``None`` if the entity does not currently exist within an
        :py:class:`.EntityCollection`. Not exported; read only.
        """
        return self._parent

    # =========================================================================

    @property
    def power_connectable(self) -> bool:
        """
        Whether or not this EntityLike can be connected using power wires. Not
        exported; read only.
        """
        return False

    # =========================================================================

    @property
    def dual_power_connectable(self) -> bool:
        """
        Whether or not this EntityLike has two power connection points. Not
        exported; read only.
        """
        return False

    # =========================================================================

    @property
    def circuit_connectable(self) -> bool:
        """
        Whether or not this EntityLike can be connected using circuit wires. Not
        exported; read only.
        """
        return False

    # =========================================================================

    @property
    def dual_circuit_connectable(self) -> bool:
        """
        Whether or not this EntityLike has two circuit connection points. Not
        exported; read only.
        """
        return False

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        """
        Whether or not this EntityLike is "double-grid-aligned", which applies
        to a number of rail entities. Not exported; read only.
        """
        return False

    # =========================================================================

    @property
    def rotatable(self) -> bool:
        """
        Whether or not this EntityLike can be rotated. Note that this does not
        mean that the entity will prevent a blueprint from rotating; more, that
        this EntityLike does not have a concept of different rotation angles.
        For example, any :py:class:`.Reactor` entity will always return
        ``rotatable`` as ``False`` when queried. Not exported; read only.
        """
        return False

    # =========================================================================

    @property
    def flags(self) -> set[str]:
        """
        The set of flags associated with this EntityLike. Returns ``None`` if
        the entitylike is not recognized by Draftsman. Not exported; read only.
        """
        return set()

    # =========================================================================
    # Abstract Properties
    # =========================================================================

    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no coverage
        pass

    @property
    @abstractmethod
    def type(self) -> str:  # pragma: no coverage
        pass

    @property
    @abstractmethod
    def id(self) -> Optional[str]:  # pragma: no coverage
        pass

    # =========================================================================
    # Abstract Methods
    # =========================================================================

    @abstractmethod
    def mergable_with(self, other: "EntityLike") -> bool:  # pragma: no coverage
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
            to see if such a merge is considered valid. To actually merge the
            two entities use :py:meth:`merge`.

        :param other: The other :py:class:`EntityLike` to check against.

        :returns: ``True`` if they can be merged, ``False`` otherwise.
        """
        pass

    @abstractmethod
    def merge(self, other: "EntityLike") -> None:  # pragma: no coverage
        """
        Changes the attributes of the calling entity with the attributes of the
        passed in entity. The attributes of ``other`` take precedence over the
        attributes of the calling entity. They can be either copied or merged
        together, depending on the specific attribute being merged.

        For the full list of all merging rules, see (TODO).

        :param other: The other :py:class:`EntityLike` to merge with.
        """
        pass

    def get(self) -> Union["Entity", list["Entity"]]:
        """
        Gets this :py:class:`.Entity`. Redundant for regular instances of 
        :py:class:`.Entity`, but is needed for :py:class:`.EntityCollections`
        like :py:class:`.Group`.

        This function represents the resolution from some abstract EntityLike
        object (which can have no relation to Factorio whatsoever) to one or 
        more valid Factorio-importable Entity instances.

        :returns: This :py:class:`.EntityLike` minimum :py:class:`.Entity`
            representation.
        """
        return self

    def __deepcopy__(self, memo: dict) -> "EntityLike":
        """
        We override the default deepcopy method so that we don't get infinite
        recursion when attempting to copy it's 'parent' attribute. We instead
        set it to ``None`` because we don't want entities to have a parent if
        they are not in an :py:class:`.EntityCollection`.

        This means that if you attempt to deepcopy an Entity that exists within
        an EntityCollection, that copied entity will *not* be inside of that
        EntityCollection, and will have to be added manually. If instead the
        *entire* EntityCollection is deepcopied, then the parent will be the
        copied EntityCollection and everything *should* remain correct.

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
