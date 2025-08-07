# entitylike.py

from abc import ABCMeta, abstractmethod

from typing import Optional, Union

from draftsman.classes.spatial_like import SpatialLike

import attrs
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import Collection
    from draftsman.classes.entity import Entity


@attrs.define(slots=False)
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

    # def __init__(self) -> None:
    #     # Parent reference (Internal)
    #     # Overwritten if the EntityLike is placed inside a Blueprint or Group
    #     self._parent = None

    # =========================================================================
    # Properties
    # =========================================================================

    _parent = attrs.field(
        default=None,
        init=False,
        repr=False,
        eq=False,
        metadata={"omit": True, "deepcopy_func": lambda value, memo: None},
    )

    @property
    def parent(self) -> Optional["Collection"]:
        """
        The parent :py:class:`.Collection` object that contains the entity,
        or ``None`` if the entity does not currently exist within an
        :py:class:`.Collection`.
        """
        return self._parent

    # =========================================================================

    @property
    def power_connectable(self) -> bool:
        """
        Whether or not this EntityLike can be connected using power wires.

        :example:

        .. doctest::

            >>> from draftsman.entity import *
            >>> Beacon().power_connectable
            False
            >>> ElectricPole().power_connectable
            True
            >>> PowerSwitch().power_connectable
            True
        """
        return False

    # =========================================================================

    @property
    def dual_power_connectable(self) -> bool:
        """
        Whether or not this EntityLike has two power connection points.

        :example:

        .. doctest::

            >>> from draftsman.entity import *
            >>> Beacon().dual_power_connectable
            False
            >>> ElectricPole().dual_power_connectable
            False
            >>> PowerSwitch().dual_power_connectable
            True
        """
        return False

    # =========================================================================

    @property
    def circuit_connectable(self) -> bool:
        """
        Whether or not this EntityLike can be connected using circuit wires.

        :example:

        .. doctest::

            >>> from draftsman.entity import *
            >>> Beacon().circuit_connectable
            False
            >>> Inserter().circuit_connectable
            True
            >>> DeciderCombinator().circuit_connectable
            True
        """
        return False

    # =========================================================================

    @property
    def dual_circuit_connectable(self) -> bool:
        """
        Whether or not this EntityLike has two circuit connection points.

        :example:

        .. doctest::

            >>> from draftsman.entity import *
            >>> Beacon().dual_circuit_connectable
            False
            >>> Inserter().dual_circuit_connectable
            False
            >>> DeciderCombinator().dual_circuit_connectable
            True
        """
        return False

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        """
        Whether or not this EntityLike is "double-grid-aligned", which applies
        to entities which need to align with the rail grid.
        """
        return False

    # =========================================================================

    @property
    def rotatable(self) -> bool:
        """
        Whether or not this :py:class:`.EntityLike` has the capability of
        being rotated. This does not mean that blueprints containing these
        entities cannot be rotated; rather, it just means they will only ever
        have one orientation.

        For example, it's impossible for a Factorio :py:class:`.Reactor` to be
        oriented, so :py:attr:`.Reactor.rotatable` always returns ``False``.
        """
        return False

    # =========================================================================

    @property
    def flags(self) -> set[str]:
        """
        The set of flags associated with this EntityLike. Returns ``None`` if
        the entitylike is not recognized by Draftsman.
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
        :py:class:`.Entity`, but is needed for :py:class:`.Collections`
        like :py:class:`.Group`.

        This function resolves some abstract :py:class:`.EntityLike`
        object (which can have no direct relation to Factorio whatsoever) to one
        or more valid Factorio-importable :py:class:`.Entity` instances.

        :returns: One or more :py:class:`.Entity` instances that represents this
            entire :py:class:`.EntityLike`.
        """
        return self

    # @abstractmethod # TODO
    # def validate():
    #     pass
