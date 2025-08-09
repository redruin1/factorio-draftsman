# collection.py

from draftsman.classes.association import Association
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.entity_list import EntityList
from draftsman.classes.train_configuration import TrainConfiguration
from draftsman.classes.schedule import Schedule
from draftsman.classes.schedule_list import ScheduleList
from draftsman.classes.tile import Tile
from draftsman.classes.tile_list import TileList
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, Orientation, WireConnectorID
from draftsman.signatures import StockConnection
from draftsman.error import (
    DuplicateIDError,
    EntityNotPowerConnectableError,
    InvalidWireTypeError,
    InvalidConnectionSideError,
    InvalidAssociationError,
    EntityNotCircuitConnectableError,
)
from draftsman.types import RollingStock
from draftsman.warning import (
    ConnectionSideWarning,
    ConnectionDistanceWarning,
)
from draftsman.utils import (
    AABB,
    PrimitiveAABB,
    distance,
    flatten_entities,
    reissue_warnings,
)
from draftsman.validators import get_mode

import attrs
from abc import ABCMeta

# from collections import UserList
from collections.abc import MutableSequence
from copy import deepcopy
import math
from typing import Any, Iterator, Literal, Optional, Sequence, Union
import warnings

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.entity import Locomotive


class Collection:
    pass


class CollectionList(MutableSequence):
    def __init__(
        self,
        initlist: Optional[list[Collection]] = None,
        parent: Optional[Collection] = None,
    ):
        self.data = []
        self.key_map = {}
        self.key_to_idx = {}
        self.idx_to_key = {}

        self._parent: "Collection" = parent

        if initlist is not None:
            for elem in initlist:
                self.append(elem)

    @reissue_warnings
    def append(self, group, copy=True, merge=False, **kwargs):
        return self.insert(idx=len(self), group=group, copy=copy, merge=merge, **kwargs)

    @reissue_warnings
    def insert(
        self,
        idx: int,
        group: Collection,
        copy: bool = True,
        merge: bool = False,
        **kwargs,
    ) -> Collection:
        # First, make sure that group is actually a Collection
        if not issubclass(type(group), Collection):
            raise TypeError("'groups' can only contain Collections")

        if copy:
            group = deepcopy(group)
            # Overwrite any user keywords if specified in the function signature
            for k, v in kwargs.items():
                setattr(group, k, v)

        # First, check if Group being added is valid
        # if get_mode():
        #     group.validate(mode=get_mode())

        # Add this group's entities/tiles (plus any subgroups as well) to the
        # spatial registry, stripping Group of any merged entities/tiles
        self.add_collection_to_map(group, merge)

        if group.id in self.key_map:
            raise DuplicateIDError("'{}'".format(group.id))

        # Now actually add the group and keep ID indexes up-to-date
        self.data.insert(idx, group)
        self._shift_key_indices(idx, 1)
        if group.id:
            self._set_key(group.id, group)

        # Set the group's parent to the correct value
        group._parent = self._parent

        return group

    def get_pair(self, item: Union[int, str]) -> tuple[int, str]:
        """
        Takes either an index or a key, finds the converse entry associated with
        it, and returns them both as a pair.

        :param item: Either an integer index or a string key.

        :returns: A tuple of the format ``(index, key)``.

        :exception KeyError: If key ``item`` is not found in the key mapping
            dictionaries in the ``EntityList``.
        """
        if isinstance(item, str):
            return (self.key_to_idx[item], item)
        else:
            return (item, self.idx_to_key.get(item, None))

    def add_collection_to_map(self, collection: Collection, merge: bool):
        validation_mode = get_mode()

        merged_entities = []
        for entity in collection.entities:
            # Validate the addition
            if validation_mode:
                self._parent.entities.spatial_map.validate_insert(entity, merge=merge)
            # Perform the add/merge
            result = self._parent.entities.spatial_map.add(entity, merge=merge)
            if result is None:
                merged_entities.append(entity)
        for entity in merged_entities:
            collection.entities.remove(entity)

        merged_tiles = []
        for tile in collection.tiles:
            # Validate the addition
            if validation_mode:
                self._parent.tiles.spatial_map.validate_insert(tile, merge=merge)
            # Perform the add/merge
            result = self._parent.tiles.spatial_map.add(tile, merge=merge)
            if result is None:
                merged_tiles.append(tile)
        for tile in merged_tiles:
            collection.tiles.remove(tile)

        for sub_group in collection.groups:
            self.add_collection_to_map(sub_group, merge=merge)

    def remove_collection_from_map(self, collection: Collection):
        for entity in collection.entities:
            self._parent.entities.spatial_map.remove(entity)
        for tile in collection.tiles:
            self._parent.tiles.spatial_map.remove(tile)
        for sub_group in collection.groups:
            self.remove_collection_from_map(sub_group)

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator["Collection"]:
        return iter(self.data)

    def __eq__(self, other: "CollectionList") -> bool:
        return self.data == other.data

    def __getitem__(
        self, item: Union[int, str, slice, tuple]
    ) -> Union["Collection", list["Collection"]]:
        if isinstance(item, (int, slice)):
            return self.data[item]  # Raises IndexError
        else:
            return self.key_map[item]  # Raises KeyError

    def __setitem__(self, item: Union[int, str], value: "Collection"):
        # TODO: handle slices

        # Get the key and index of the item
        idx, key = self.get_pair(item)

        # TODO: validate that value is a `Collection`

        # Make sure newly added item doesn't have a duplicate ID
        if value.id in self.key_map:
            raise DuplicateIDError("'{}'".format(value.id))

        # Remove all entities/tiles contained within the group from the spatial
        # maps
        self.remove_collection_from_map(self.data[idx])

        # Wipe the parent reference from the item that we're about to replace
        self.data[idx]._parent = None

        # Add all the new entities/tiles contained within the new collection to
        # the spatial maps
        self.add_collection_to_map(value, merge=False)

        # Set the new data association in the list side
        self.data[idx] = value

        # If the element has a new id, set it to that
        if key:
            self._remove_key(key)
        if value.id:
            # key = getattr(value, "id")
            self._set_key(value.id, value)

        # Add a reference to the parent in the object
        value._parent = self._parent

    def __delitem__(self, item: Union[int, str, slice]):
        # TODO: handle slices
        # if isinstance(item, slice):
        #     # Get slice parameters
        #     start, stop, step = item.indices(len(self))
        #     for i in range(start, stop, step):
        #         # Get pair
        #         idx, key = self.get_pair(i)

        #         # Remove the group from maps
        #         self.remove_collection_from_map(self.data[idx])

        #         # Remove key pair
        #         self._remove_key(key)

        #     for i in range(start, stop, step):
        #         # Shift elements above down by 1 for the item immediately removed
        #         self._shift_key_indices(i, -1)

        #     # Delete all entries in the main list
        #     del self.data[item]
        # else:

        # Get pair
        if isinstance(item, int):
            item %= len(self.data)
        idx, key = self.get_pair(item)

        # Remove the entity and its children
        self.remove_collection_from_map(self.data[idx])

        # Delete from list
        del self.data[idx]

        # Remove key pair
        self._remove_key(key)

        # Shift all entries above down by one
        self._shift_key_indices(idx, -1)

    # =========================================================================
    # Internal Functions
    # =========================================================================

    def _remove_key(self, key: str):
        """
        Shorthand to remove ``key`` from the key mapping dictionaries. Does
        nothing if key is ``None``.

        :param key: The string to remove.

        :exception KeyError: If attempting to remove a key that does not exist
            in the ``EntityList``.
        """
        if key is not None:
            idx = self.key_to_idx[key]
            del self.key_map[key]
            del self.key_to_idx[key]
            del self.idx_to_key[idx]

    def _set_key(self, key: str, value: "EntityLike"):
        """
        Shorthand to set ``key`` in the key mapping dictionaries to point to
        ``value``.

        :param key: A ``str`` to associate with ``value``.
        :param value: An ``EntityLike`` instance to associate with ``key``.

        :exception DuplicateIDError: If ``key`` already exists within the
            ``EntityList``.
        :exception IndexError: If ``value`` is not found within the
            ``EntityList``.
        """
        idx = self.data.index(value)
        self.key_map[key] = value
        self.key_to_idx[key] = idx
        self.idx_to_key[idx] = key

    def _shift_key_indices(self, idx: int, amt: int):
        """
        Shifts all of the key mappings above or equal to ``idx`` by ``amt``.
        Used when inserting or removing elements before the end, which moves
        what index each key should point to.
        """

        # Shift the indices for key_to_idx
        self.key_to_idx = {
            key: old_idx + amt if old_idx >= idx else old_idx
            for key, old_idx in self.key_to_idx.items()
        }

        # Reconstruct idx_to_key
        self.idx_to_key = {value: key for key, value in self.key_to_idx.items()}

    def __deepcopy__(self, memo: dict):
        parent = memo.get("new_parent", self._parent)
        new = CollectionList(parent=parent)

        for group in self.data:
            group_copy = memo.get(id(group), deepcopy(group, memo))
            new.append(group_copy, copy=False)
            memo[id(group)] = group_copy

        return new


@attrs.define(slots=False)
class Collection(metaclass=ABCMeta):
    """
    Abstract class used to describe an object that can contain a list of
    :py:class:`.EntityLike` and :py:class:`.Tile` instances.
    """

    # TODO: maybe it would be better to just have one spatial map which stores
    # 2 different maps inside of it? Interactions with it would then have to
    # specifiy which one they wanted to modify
    # Merging both maps together is off the table since it generates far more
    # hash collisions than necessary for 2 types of objects which almost never
    # have actual collisions

    # _entity_map: SpatialDataStructure = attrs.field(
    #     factory=SpatialHashMap, init=False, repr=False, eq=False, kw_only=True
    # )

    # _tile_map: SpatialDataStructure = attrs.field(
    #     factory=SpatialHashMap, init=False, repr=False, eq=False, kw_only=True
    # )

    # @property
    # def spatial_map(self):
    #     """
    #     Accelleration structure for speeding up regional queries. Not intended
    #     for direct manipulation; it is instead modified when adding/removing/
    #     changing entries inside of :py:attr:`.entities`, :py:attr:`.tiles`, and
    #     :py:attr:`.groups`. Read only; not exported.
    #     """
    #     return self._spatial_map

    def __attrs_post_init__(self):
        """
        When initializing from a raw JSON dictionary, convert all numeric IDs
        to use Associations.
        """

        for wire in self.wires:
            entity1 = self.entities[wire[0] - 1]
            wire[0] = Association(entity1)
            entity2 = self.entities[wire[2] - 1]
            wire[2] = Association(entity2)

        for schedule in self.schedules:
            for i, locomotive in enumerate(schedule.locomotives):
                entity = self.entities[locomotive - 1]
                schedule.locomotives[i] = Association(entity)

        for connection in self.stock_connections:
            connection.stock = Association(self.entities[connection.stock - 1])
            if isinstance(connection.front, int):
                connection.front = Association(self.entities[connection.front - 1])
            if isinstance(connection.back, int):
                connection.back = Association(self.entities[connection.back - 1])

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def rotatable(self) -> bool:
        """
        Whether or not this collection can be rotated or not. Included for
        posterity; always returns True, even when containing entities that have
        no direction component. Read only.
        """
        return True

    @property
    def flippable(self) -> bool:
        """
        Whether or not this collection can be flipped or not. This is determined
        by whether or not any of the entities contained can be flipped or not.
        Read only.
        """
        # TODO: no longer accurate
        for entity in self.entities:
            if not entity.flippable:
                return False

        return True

    # =========================================================================
    # Attributes
    # =========================================================================

    def _set_entities(self, _: attrs.Attribute, value: Any):
        if value is None:
            return EntityList(self)
        elif isinstance(value, EntityList):
            return EntityList(self, value.data)
        else:
            return EntityList(self, value)

    entities: EntityList = attrs.field(
        on_setattr=_set_entities,
        kw_only=True,
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The list containing this collection's entities.

    Supports inserting/appending new entities via a string name, as well as any
    keyword arguments to pass to that entity's constructor:

    .. code-block::

        blueprint.entities.append("wooden-chest", bar=10)
        assert type(blueprint.entities[-1]) is Container
        assert blueprint.entities[-1].name == "wooden-chest"
        assert blueprint.entities[-1].bar == 10

    In addition to indexing by integer location, :py:class:`.EntityList` also 
    supports indexing via string, corresponding to the :py:attr:`~.Entity.id` of 
    the entity:

    .. code-block::

        blueprint.entities.insert(0, "wooden-chest", id="example")
        assert blueprint.entities["example"] is blueprint.entities[0]
    """

    @entities.default
    def _(self) -> EntityList:
        return EntityList(self)

    # =========================================================================

    def _set_tiles(self, _: attrs.Attribute, value: Any):
        if value is None:
            return TileList(self)
        elif isinstance(value, TileList):
            return TileList(self, value.data)
        else:
            return TileList(self, value)

    tiles: TileList = attrs.field(
        on_setattr=_set_tiles,
        kw_only=True,
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The list containing this collection's tiles.

    Supports inserting/appending new tiles via a string name, as well as any
    keyword arguments to pass to that entity's constructor:

    .. code-block::

        blueprint.tiles.append("landfill")
        assert type(blueprint.tiles[-1]) is Tile
        assert blueprint.tiles[-1].name == "landfill"
    """

    @tiles.default
    def get_tiles_default(self):
        return TileList(self)

    # =========================================================================

    # `groups` has to live above `schedules`/`wires`/`stock_connections` because
    # group entities/tiles need to be copied before any Associations are
    # resolved

    def _set_groups(self, _: attrs.Attribute, value: Any):
        # Remove all spatial entries from the this instance's entities/tiles
        # spatial maps:
        for group in self.groups:
            self.groups.remove_collection_from_map(group)

        if value is None:
            return CollectionList(parent=self)
        elif isinstance(value, CollectionList):
            return CollectionList(value.data, parent=self)
        else:
            return CollectionList(value, parent=self)

    groups: CollectionList = attrs.field(
        on_setattr=_set_groups,
        kw_only=True,
    )
    """
    A list of child :py:class:`.Group` objects that this collection contains.

    Like :py:class:`.EntityList`, Groups added to this list with populated IDs
    can be accessed via those IDs:
        
    .. doctest::

        >>> blueprint = Blueprint()
        >>> new_group = Group(id="something")
        >>> blueprint.groups.append(new_group)
        >>> assert blueprint.groups["something"] == new_group

    This attribute is not exported. Instead, all entities/tiles that are 
    contained within it are "flattened" to the root-most entity/tile lists, with
    their positions and associations preserved.

    .. versionadded:: 3.0.0
    """

    @groups.default
    def _(self) -> CollectionList:
        return CollectionList(parent=self)

    # =========================================================================

    def _set_schedules(self, _: attrs.Attribute, value: Any):
        # TODO: this needs to be more complex. What about associations already
        # set to one blueprint being copied over to another? Should probably
        # wipe the locomotives of each schedule when doing so
        if value is None:
            return ScheduleList()
        elif isinstance(value, ScheduleList):
            return value
        else:
            return ScheduleList(value)

    schedules: ScheduleList = attrs.field(
        on_setattr=_set_schedules,
        kw_only=True,
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    A list of the Collections's :py:class:`.Schedule` s.
    """

    @schedules.default
    def _(self) -> ScheduleList:
        return ScheduleList()

    # =========================================================================

    wires: list[list[Association, WireConnectorID, Association, WireConnectorID]] = (
        attrs.field(
            factory=list,
            converter=lambda v: list() if v is None else v,
            # TODO: validators
            kw_only=True,
        )
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.
    
    A list of all the wire connections in this blueprint.

    Wires are specified as two pairs of :py:class:`.Association` and 
    :py:class:`.WireType`; the first pair represents the first entity, and the 
    second pair represents the second entity. The association points to the 
    corresponding entity in this collection, and the wire type enum indicates
    what type of connection it is.

    When exported to JSON, the associations and enums in each wire are resolved 
    to integers corresponding to the given ``entity_number`` in the resulting
    ``entities`` list.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================

    stock_connections: list[StockConnection] = attrs.field(
        factory=list,
        # TODO: validators
        kw_only=True,
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    A list of connections between train cars, documenting exactly which ones
    are connected to what. Prior to Factorio 2.0, train car connections were 
    inferred and automatically generated on blueprint import; this field allows
    for manual control over this behavior.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================
    # Entities
    # =========================================================================

    def find_entity(
        self, name: str, position: Union[Vector, PrimitiveVector]
    ) -> EntityLike:
        """
        Finds an entity with ``name`` at a position ``position``. If multiple
        entities exist at the queried position, the one that was first placed is
        returned.

        :param name: The name of the entity to look for.
        :param position: The position to search, either a PrimitiveVector or a
            :py:class:`.Vector`.

        :retuns: The ``EntityLike`` at ``position``, or ``None`` of none were
            found.
        """
        results = self.entities.spatial_map.get_on_point(position)
        try:
            return list(filter(lambda x: x.name == name, results))[0]
        except IndexError:
            return None

    def find_entity_at_position(
        self, position: Union[Vector, PrimitiveVector]
    ) -> EntityLike:
        """
        Finds any entity at the position ``position``. If multiple entities
        exist at the queried position, the one that was first placed is returned.

        :param position: The position to search, either a PrimitiveVector or a
            :py:class:`.Vector`.

        :retuns: The ``EntityLike`` at ``position``, or ``None`` of none were
            found.
        """
        try:
            return self.entities.spatial_map.get_on_point(position)[0]
        except IndexError:
            return None

    def find_entities(
        self, aabb: Union[AABB, PrimitiveAABB, None] = None
    ) -> list[EntityLike]:
        """
        Returns a ``list`` of all entities within the area ``aabb``. Works
        similiarly to
        `LuaSurface.find_entities <https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_entities>`_.
        If no ``aabb`` is provided then the method simply returns all the
        entities in the blueprint.

        :param aabb: An :py:class:`.AABB`, or a ``Sequence`` of 4 floats,
            usually a ``list`` or ``tuple``.

        :returns: A regular ``list`` of ``EntityLikes`` whose ``collision_box``
            overlaps the queried AABB.
        """
        if aabb is None:
            return list(self.entities)

        # Normalize AABB
        aabb = AABB.from_other(aabb)

        return self.entities.spatial_map.get_in_aabb(aabb)

    def find_entities_filtered(
        self,
        position: Optional[Vector] = None,
        radius: Optional[float] = None,
        area: Union[AABB, PrimitiveAABB, None] = None,
        name: Union[str, set[str], None] = None,
        type: Union[str, set[str], None] = None,
        direction: Optional[Direction] = None,
        invert: bool = False,
        limit: Optional[int] = None,
    ) -> list[EntityLike]:
        """
        Returns a filtered list of entities within the ``Collection``. Works
        similarly to `LuaSurface.find_entities_filtered
        <https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_entities_filtered>`_.

        Keywords are organized into two main categrories: **region** and
        **criteria**:

        .. list-table:: Region keywords
            :header-rows: 1

            * - Name
              - Type
              - Description
            * - ``position``
              - ``Vector`` or ``PrimitiveVector``
              - Grid position to search.
            * - ``radius``
              - ``float``
              - Radius of the circle around position to search.
            * - ``area``
              - ``AABB`` or ``PrimitiveAABB``
              - AABB to search in.

        If none of the above are specified, then the search area becomes the
        entire Collection. If ``radius`` is specified but ``position`` is not,
        the search area also becomes the entire Collection.

        .. list-table:: Criteria keywords
            :header-rows: 1

            * - Name
              - Type
              - Description
            * - ``name``
              - ``str`` or ``set{str}``
              - The name(s) of the entities that you want to search for.
            * - ``type``
              - ``str`` or ``set{str}``
              - The type(s) of the entities that you want to search for.
            * - ``direction``
              - ``Direction`` or ``set{Direction}``
              - | The direction(s) of the entities that you want to search for.
                | Excludes entities that have no direction.
            * - ``limit``
              - ``int``
              - | Limit the maximum size of the returned list to this amount.
                | Unlimited by default.
            * - ``invert``
              - ``bool``
              - | Whether or not to return the inverse of the search.
                | False by default.

        :param position: The global position to search the source Collection.
            Can be used in conjunction with ``radius`` to search a circle
            instead of a single point. Takes precedence over ``area``.
        :param radius: The radius of the circle centered around ``position`` to
            search. Must be defined alongside ``position`` in order to search in
            a circular area.
        :param area: The :py:class:`.AABB` or ``PrimitiveAABB`` to search in.
        :param name: Either a ``str``, or a ``set[str]`` where each entry is a
            name of an entity to be returned.
        :param type: Either a ``str``, or a ``set[str]`` where each entry is a
            type of an entity to be returned.
        :param direction: Either a :py:class:`Direction` enum (or corresponding
            ``int``), or a ``set[Direction]`` where each entry is a valid
            direction for each returned entity to match. Excludes entities that
            have no direction attribute.
        :param invert: Whether or not to return the inversion of the search
            criteria.
        :param limit: The total number of matching entities to return. Unlimited
            by default.

        :returns: A list of Entity references inside the searched collection
            that satisfy the search criteria.
        """

        if position is not None:
            if radius is not None:
                # Intersect entities with circle
                search_region = self.entities.spatial_map.get_in_radius(
                    radius, position
                )
            else:
                # Intersect entities with point
                search_region = self.entities.spatial_map.get_on_point(position)
        elif area is not None:
            # Intersect entities with area
            area = AABB.from_other(area)
            search_region = self.entities.spatial_map.get_in_aabb(area)
        else:
            # Search all entities, but make sure it's a 1D list
            search_region = flatten_entities(self)

        # Normalize inputs
        if isinstance(name, str):
            names = {name}
        else:
            names = name
        if isinstance(type, str):
            types = {type}
        else:
            types = type
        if isinstance(direction, int):
            directions = {direction}
        else:
            directions = direction

        # Keep track of how many
        if limit is None:
            limit = len(search_region)

        def test(entity):
            if names is not None and entity.name not in names:
                return False
            if types is not None and entity.type not in types:
                return False
            if (
                directions is not None
                and getattr(entity, "direction", None) not in directions
            ):
                return False
            return True

        if invert:
            return list(filter(lambda entity: not test(entity), search_region))[:limit]
        else:
            return list(filter(lambda entity: test(entity), search_region))[:limit]

    # =========================================================================
    # Tiles
    # =========================================================================

    def find_tile(self, position: Union[Vector, PrimitiveVector]) -> list[Tile]:
        """
        Returns a list containing all the tiles at the tile coordinate
        ``position``. If there are no tiles at that position, an empty list is
        returned.

        :param position: The position to search, either a ``PrimitiveVector`` or
            a :py:class:`.Vector`.

        :returns: A list of all tiles at ``position``.
        """
        return self.tiles.spatial_map.get_on_point(Vector(0.5, 0.5) + position)

    def find_tiles_filtered(
        self,
        position: Union[Vector, PrimitiveVector, None] = None,
        radius: Optional[float] = None,
        area: Union[AABB, PrimitiveAABB, None] = None,
        name: Optional[str] = None,
        invert: bool = False,
        limit: Optional[int] = None,
    ) -> list[Tile]:
        """
        Returns a filtered list of tiles within the blueprint. Works
        similarly to
        `LuaSurface.find_tiles_filtered <https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_tiles_filtered>`_.

        Keywords are organized into two main categrories: **region** and
        **criteria**:

        .. list-table:: Region keywords
            :header-rows: 1

            * - Name
              - Type
              - Description
            * - ``position``
              - ``Vector`` or ``PrimitiveVector``
              - Grid position to search.
            * - ``radius``
              - ``float``
              - Radius of the circle around position to search.
            * - ``area``
              - ``AABB`` or ``PrimitiveAABB``
              - AABB to search in.

        .. list-table:: Criteria keywords
            :header-rows: 1

            * - Name
              - Type
              - Description
            * - ``name``
              - ``str`` or ``set{str}``
              - The name(s) of the entities that you want to search for.
            * - ``limit``
              - ``int``
              - | Limit the maximum size of the returned list to this amount.
                | Unlimited by default.
            * - ``invert``
              - ``bool``
              - | Whether or not to return the inverse of the search. ``False``
                | by default.

        :param position: The global position to search the source Collection.
            Can be used in conjunction with ``radius`` to search a circle
            instead of a single point. Takes precedence over ``area``.
        :param radius: The radius of the circle centered around ``position`` to
            search. Must be defined alongside ``position`` in order to search in
            a circular area.
        :param area: The :py:class:`.AABB` or ``PrimitiveAABB`` to search in.
        :param name: Either a ``str``, or a ``set[str]`` where each entry is a
            name of an entity to be returned.
        :param invert: Whether or not to return the inversion of the search
            criteria.
        :param limit: The total number of matching entities to return. Unlimited
            by default.

        :returns: A list of Tile references inside the searched collection that
            match the specified criteria.
        """

        if position is not None and radius is not None:
            # Intersect entities with circle
            search_region = self.tiles.spatial_map.get_in_radius(radius, position)
        elif area is not None:
            # Intersect entities with area
            area = AABB.from_other(area)
            search_region = self.tiles.spatial_map.get_in_aabb(area)
        else:
            search_region = self.tiles

        if isinstance(name, str):
            names = {name}
        else:
            names = name

        # Keep track of how many
        limit = len(search_region) if limit is None else limit

        def test(tile):
            if names is not None and tile.name not in names:
                return False
            return True

        if invert:
            return list(filter(lambda tile: not test(tile), search_region))[:limit]
        else:
            return list(filter(lambda tile: test(tile), search_region))[:limit]

    # =========================================================================
    # Wires
    # =========================================================================

    def add_power_connection(
        self,
        entity_1: Union[
            EntityLike,
            int,
            str,
            Sequence[Union[int, str]],
        ],
        entity_2: Union[
            EntityLike,
            int,
            str,
            Sequence[Union[int, str]],
        ],
        side_1: Literal["input", "output"] = "input",
        side_2: Literal["input", "output"] = "input",
    ) -> None:
        """
        Adds a copper wire power connection between two entities. Each entity
        can be either a reference to the original entity to connect, the index
        of the entity in the :py:attr:`.entities` list, or it's string ID.
        Tuples of strings and ints mean to recursively search through the
        :py:class:`Collection` 's :py:class:`.groups` for an entity at that tree
        "path". For example:

        .. code-block:: python

            blueprint.entities.append("small-electric-pole")
            group = Group("group") # A type of `Collection`
            group.entities.append("small-electric-pole", tile_position=(5, 0))
            blueprint.groups.append(group)

            # Add a connection between the first power pole and the first entity
            # in the group
            blueprint.add_power_connection(blueprint.entities[0], ("group", 0))

        Side specifies which side to connect to when establishing a
        connection to a dual-power-connectable entity (usually a power-switch).
        Does nothing if the connection already exists.

        Raises :py:class:`~draftsman.warning.ConnectionRangeWarning` if the
        distance between the two entities exceeds the maximum wire distance
        between the two.

        Raises :py:class:`~draftsman.warning.TooManyConnectionsWarning` if
        either of the power poles exceed 5 connections when this connection is
        added.

        :param entity_1: EntityLike, ID, or index of the first entity to join.
        :param entity_2: EntityLike, ID or index of the second entity to join.
        :param side_1: Which side of ``entity_1`` to connect power to. Only 
            necessary to specify for entities that are 
            :py:attr:`.Entity.dual_power_connectable`.
        :param side_2: Which side of ``entity_2`` to connect power to. Only 
            necessary to specify for entities that are 
            :py:attr:`.Entity.dual_power_connectable`.

        :exception KeyError, IndexError: If ``entity_1`` and/or ``entity_2`` are
            invalid ID's or indices to the parent Collection.
        :exception InvalidAssociationError: If ``entity_1`` and/or ``entity_2``
            are not inside the parent Collection.
        :exception EntityNotPowerConnectableError: If either `entity_1` or
            `entity_2` do not have the capability to be copper wire connected.
        :exception DraftsmanError: If both `entity_1` and `entity_2` are
            dual-power-connectable, of which a connection is forbidden.
        """
        if not isinstance(entity_1, EntityLike):
            # entity_1 = self.entities[entity_1]
            entity_1 = self._get_entity_from_path(entity_1)
        if not isinstance(entity_2, EntityLike):
            # entity_2 = self.entities[entity_2]
            entity_2 = self._get_entity_from_path(entity_2)

        if entity_1 not in self:
            raise InvalidAssociationError(
                "entity_1 ({}) not contained within this collection".format(entity_1)
            )
        if entity_2 not in self:
            raise InvalidAssociationError(
                "entity_2 ({}) not contained within this collection".format(entity_2)
            )
        if side_1 not in {"input", "output"}:
            raise InvalidConnectionSideError("'{}'".format(side_1))
        if side_2 not in {"input", "output"}:
            raise InvalidConnectionSideError("'{}'".format(side_2))

        if not entity_1.power_connectable:
            raise EntityNotPowerConnectableError(entity_1.name)
        if not entity_2.power_connectable:
            raise EntityNotPowerConnectableError(entity_2.name)

        # Issue a warning if the entities being connected are too far apart
        min_dist = min(entity_1.maximum_wire_distance, entity_2.maximum_wire_distance)
        real_dist = distance(
            entity_1.global_position._data, entity_2.global_position._data
        )
        if real_dist > min_dist:
            warnings.warn(
                "Distance between entity '{}' and entity '{}' ({}) is greater"
                " than max connection distance ({})".format(
                    entity_1.name, entity_2.name, real_dist, min_dist
                ),
                ConnectionDistanceWarning,
                stacklevel=2,
            )

        # Issue a warning if the either of the connected entities have 5 or more
        # power connections
        # NOTE: only relevant in 1.0
        # if len(entity_1.neighbours) >= 5:
        #     warnings.warn(
        #         "'entity_1' ({}) has more than 5 connections".format(entity_1.name),
        #         TooManyConnectionsWarning,
        #         stacklevel=2,
        #     )
        # if len(entity_2.neighbours) >= 5:
        #     warnings.warn(
        #         "'entity_2' ({}) has more than 5 connections".format(entity_2.name),
        #         TooManyConnectionsWarning,
        #         stacklevel=2,
        #     )

        dir_value = {"input": 5, "output": 6}

        wire_type_1 = dir_value[side_1]
        wire_type_2 = dir_value[side_2]

        # Make sure connection (nor its reverse) already exists in the wires list
        # TODO: just make this a dict, dammit; WE HAVE THE POWER
        if [
            Association(entity_1),
            wire_type_1,
            Association(entity_2),
            wire_type_2,
        ] not in self.wires and [
            Association(entity_2),
            wire_type_2,
            Association(entity_1),
            wire_type_1,
        ] not in self.wires:
            self.wires.append(
                [Association(entity_1), wire_type_1, Association(entity_2), wire_type_2]
            )

    def remove_power_connection(
        self,
        entity_1: Union[
            EntityLike,
            int,
            str,
            Sequence[Union[int, str]],
        ],
        entity_2: Union[
            EntityLike,
            int,
            str,
            Sequence[Union[int, str]],
        ],
        side_1: Literal["input", "output"] = "input",
        side_2: Literal["input", "output"] = "input",
    ) -> None:
        """
        Removes a copper wire power connection between two entities. Each entity
        can be either a reference to the original entity to connect, the index
        of the entity in the ``entities`` list, or it's string ID. ``side``
        specifies which side to remove the connection from when removing a
        connection to a dual-power-connectable entity (usually a power-switch).
        Does nothing if the specified connection does not exist.

        :param entity_1: EntityLike, ID or index of the first entity to remove
            the connection to.
        :param entity_2: EntityLike, ID or index of the second entity to remove
            the connection to.
        :param side_1: Which side of ``entity_1`` to remove a power connection
            from. Only necessary to specify for entities that are 
            :py:attr:`.Entity.dual_power_connectable`.
        :param side_2: Which side of ``entity_2`` to remove a power connection
            from. Only necessary to specify for entities that are 
            :py:attr:`.Entity.dual_power_connectable`.

        :exception KeyError, IndexError: If ``entity_1`` and/or ``entity_2`` are
            invalid ID's or indices to the parent Collection.
        :exception InvalidAssociationError: If ``entity_1`` and/or ``entity_2``
            are not inside the parent Collection.
        """
        if not isinstance(entity_1, EntityLike):
            entity_1 = self.entities[entity_1]
        if not isinstance(entity_2, EntityLike):
            entity_2 = self.entities[entity_2]

        if entity_1 not in self.entities:
            raise InvalidAssociationError(
                "entity_1 ({}) not contained within this collection".format(entity_1)
            )
        if entity_2 not in self.entities:
            raise InvalidAssociationError(
                "entity_2 ({}) not contained within this collection".format(entity_2)
            )

        dir_value = {"input": 5, "output": 6}

        wire_type_1 = dir_value[side_1]
        wire_type_2 = dir_value[side_2]

        try:
            self.wires.remove(
                [Association(entity_1), wire_type_1, Association(entity_2), wire_type_2]
            )
        except ValueError:
            pass
        try:
            self.wires.remove(
                [Association(entity_2), wire_type_2, Association(entity_1), wire_type_1]
            )
        except ValueError:
            pass

    def remove_power_connections(self) -> None:
        """
        Remove all power connections in the Collection, including any power
        connections between power switches. Recurses through any subgroups, and
        removes power connections from them as well. Does nothing if there are
        no power connections in the Collection.
        """
        for group in self.groups:
            group.remove_power_connections()

        self.wires[:] = [wire for wire in self.wires if wire[1] not in {5, 6}]

    def generate_power_connections(
        self, prefer_axis: bool = True, only_axis: bool = False
    ) -> None:
        """
        Automatically create power connections between all electric poles.

        The algorithm used is similar to demi-pixel's `generateElectricalConnections()
        <https://github.com/demipixel/factorio-blueprint/blob/master/src/electrical-connections.ts>`_
        function, but with some slight differences. Power poles are still
        prioritized closest first, but can be selected to prefer to connect
        neighbours on the same axis, as well as *only* connect to neighbours on
        the same axis. This function will only connect power poles that have
        less than 5 power connections already made, preserving power connections
        that were manually specified. This function does not generate
        connections between power-switches.

        :param prefer_axis: Determines whether or not to rank power-poles on the
            same x or y coordinate higher than poles that are closer, but not on
            either axis. Used to prefer creating neat, regular grids when
            possible.
        :param only_axis: Removes any neighbour that does not lie on the same
            x or y axis from the candidate pool, preventing non-grid
            connections.
        """
        # Get all power poles in the Collection (1D list)
        electric_poles = self.find_entities_filtered(type="electric-pole")
        for cur_pole in electric_poles:
            # Get all the power poles candidates
            def power_connectable(other: EntityLike) -> bool:
                # Don't include ourself in the entities we're connecting to
                if other is cur_pole:
                    return False
                # If only_axis is true, only include ones that have the same x
                # or y
                if (
                    cur_pole.global_position.x != other.global_position.x
                    and cur_pole.global_position.y != other.global_position.y
                    and only_axis
                ):
                    return False
                # Only return poles that are less than the max power pole
                # distance
                dist = distance(
                    cur_pole.global_position._data, other.global_position._data
                )
                min_dist = min(
                    cur_pole.maximum_wire_distance, other.maximum_wire_distance
                )
                return dist <= min_dist

            potential_neighbours = list(filter(power_connectable, electric_poles))
            # Sort the power poles by distance
            potential_neighbours.sort(
                key=lambda x: distance(
                    x.global_position._data, cur_pole.global_position._data
                )
            )

            # Sort the power poles by whether or not they are on the axis first
            if prefer_axis:
                potential_neighbours.sort(
                    key=lambda x: not (
                        x.global_position.x == cur_pole.global_position.x
                        or x.global_position.y == cur_pole.global_position.y
                    )
                )

            # Iterate over every potential neighbour
            while len(potential_neighbours) > 0:
                neighbour = potential_neighbours.pop()
                # Make sure this connection would not exceed each entities max
                # connections
                # if len(cur_pole.neighbours) < 5 and len(neighbour.neighbours) < 5: # 1.0
                self.add_power_connection(cur_pole, neighbour)

    # =========================================================================

    def add_circuit_connection(
        self,
        color: Literal["red", "green"],
        entity_1: Union[
            EntityLike,
            int,
            str,
            Sequence[Union[int, str]],
        ],
        entity_2: Union[
            EntityLike,
            int,
            str,
            Sequence[Union[int, str]],
        ],
        side_1: Literal["input", "output"] = "input",
        side_2: Literal["input", "output"] = "input",
    ) -> None:
        """
        Adds a circuit wire connection between two entities. Each entity
        can be either a reference to the original entity to connect, the index
        of the entity in the ``entities`` list, or it's string ID. Color
        specifies the color of the wire to make the connection with, and is
        either ``"red"`` or ``"green"``. ``side1`` specifies which side of the
        first entity to connect to (if applicable), and ``side2`` specifies
        which side of the second entity to connect to (if applicable). Does
        nothing if the connection already exists.

        Raises :py:class:`~draftsman.warning.ConnectionSideWarning` if the side
        of either of the entities is ``2`` when the entity is not
        dual-circuit-connectable.

        Raises :py:class:`~draftsman.warning.ConnectionRangeWarning` if the
        distance between the two entities exceeds the maximum wire distance
        between the two.

        :param color: Color of the wire to make the connection with. Must be
            either ``"red"`` or ``"green"``.
        :param entity_1: ID or index of the first entity to join.
        :param entity_2: ID or index of the second entity to join.
        :param side_1: Which side of ``entity_1`` to connect to. Only necessary 
            to specify for entities that are 
            :py:attr:`.Entity.dual_circuit_connectable`.
        :param side_2: Which side of ``entity_2`` to connect to. Only necessary 
            to specify for entities that are 
            :py:attr:`.Entity.dual_circuit_connectable`.

        :exception KeyError, IndexError: If ``entity_1`` and/or ``entity_2`` are invalid
            ID's or indices to the parent Collection.
        :exception InvalidAssociationError: If ``entity_1`` and/or ``entity_2``
            are not inside the parent Collection.
        :exception InvalidWireTypeError: If ``color`` is neither ``"red"`` nor
            ``"green"``.
        :exception InvalidConnectionSideError: If ``side_1`` or ``side_2`` are
            neither ``"input"`` nor ``"output"``.
        :exception EntityNotCircuitConnectableError: If either `entity_1` or
            `entity_2` do not have the capability to be circuit wire connected.
        """
        # Normalize to tuple form
        # if not isinstance(location_1, tuple):
        #     location_1 = (location_1, "input")
        # if not isinstance(location_2, tuple):
        #     location_2 = (location_2, "input")

        if isinstance(entity_1, EntityLike):
            if entity_1 not in self.entities:
                raise InvalidAssociationError(
                    "entity_1 ({}) not contained within this collection".format(
                        entity_1
                    )
                )
        else:
            # entity_1 = self.entities[entity_1]
            entity_1 = self._get_entity_from_path(entity_1)

        if isinstance(entity_2, EntityLike):
            if entity_2 not in self.entities:
                raise InvalidAssociationError(
                    "entity_2 ({}) not contained within this collection".format(
                        entity_2
                    )
                )
        else:
            # entity_2 = self.entities[entity_2]
            entity_2 = self._get_entity_from_path(entity_2)

        if color not in {"red", "green"}:
            raise InvalidWireTypeError(color)
        if side_1 not in {"input", "output"}:
            raise InvalidConnectionSideError("'{}'".format(side_1))
        if side_2 not in {"input", "output"}:
            raise InvalidConnectionSideError("'{}'".format(side_2))

        if not entity_1.circuit_connectable:
            raise EntityNotCircuitConnectableError(entity_1.name)
        if not entity_2.circuit_connectable:
            raise EntityNotCircuitConnectableError(entity_2.name)

        if side_1 == "output" and not entity_1.dual_circuit_connectable:
            warnings.warn(
                "'side_1' was specified as 'output', but entity '{}' is not"
                " dual circuit connectable".format(type(entity_1).__name__),
                ConnectionSideWarning,
                stacklevel=2,
            )
        if side_2 == "output" and not entity_2.dual_circuit_connectable:
            warnings.warn(
                "'side_2' was specified as 'output', but entity '{}' is not"
                " dual circuit connectable".format(type(entity_2).__name__),
                ConnectionSideWarning,
                stacklevel=2,
            )

        # Issue a warning if the entities being connected are too far apart
        min_dist = min(
            entity_1.circuit_wire_max_distance, entity_2.circuit_wire_max_distance
        )
        real_dist = distance(
            entity_1.global_position._data, entity_2.global_position._data
        )
        if real_dist > min_dist:
            warnings.warn(
                "Distance between entity '{}' and entity '{}' ({}) is greater"
                " than max connection distance ({})".format(
                    entity_1.name, entity_2.name, real_dist, min_dist
                ),
                ConnectionDistanceWarning,
                stacklevel=2,
            )

        color_value = {"red": 1, "green": 2}
        dir_value = {"input": 0, "output": 2}

        wire_type_1 = color_value[color] + dir_value[side_1]
        wire_type_2 = color_value[color] + dir_value[side_2]

        self.wires.append(
            [
                Association(entity_1),
                WireConnectorID(wire_type_1),
                Association(entity_2),
                WireConnectorID(wire_type_2),
            ]
        )

    def remove_circuit_connection(
        self,
        color: Literal["red", "green"],
        entity_1: Union[
            EntityLike,
            int,
            str,
            Sequence[Union[int, str]],
        ],
        entity_2: Union[
            EntityLike,
            int,
            str,
            Sequence[Union[int, str]],
        ],
        side_1: Literal["input", "output"] = "input",
        side_2: Literal["input", "output"] = "input",
    ) -> None:
        """
        Removes a circuit wire connection between two entities. Each entity
        can be either a reference to the original entity to connect, the index
        of the entity in the ``entities`` list, or it's string ID. ``side1``
        specifies which side of the first entity to remove the connection from
        (if applicable), and ``side2`` specifies which side of the second entity
        to remove the connection from (if applicable). Does nothing if the
        specified connection doesn't exist.

        :param color: Color of the wire to remove. Either ``"red"`` or
            ``"green"``.
        :param entity_1: ID or index of the first entity to remove the
            connection to.
        :param entity_2: ID or index of the second entity to remove the
            connection to.
        :param side_1: Which side of ``entity_1`` to remove the connection from. 
            Only necessary to specify for entities that are 
            :py:attr:`.Entity.dual_circuit_connectable`.
        :param side_2: Which side of ``entity_2`` to remove the connection from. 
            Only necessary to specify for entities that are 
            :py:attr:`.Entity.dual_circuit_connectable`.

        :exception KeyError, IndexError: If ``entity_1`` and/or ``entity_2`` are
            invalid ID's or indices to the parent Collection.
        :exception InvalidAssociationError: If ``entity_1`` and/or ``entity_2``
            are not inside the parent Collection.
        """
        # Normalize to tuple form
        # if not isinstance(location_1, tuple):
        #     location_1 = (location_1, "input")
        # if not isinstance(location_2, tuple):
        #     location_2 = (location_2, "input")

        if not isinstance(entity_1, EntityLike):
            entity_1 = self.entities[entity_1]
        if not isinstance(entity_2, EntityLike):
            entity_2 = self.entities[entity_2]

        if entity_1 not in self.entities:
            raise InvalidAssociationError(
                "entity_1 ({}) not contained within this collection".format(entity_1)
            )
        if entity_2 not in self.entities:
            raise InvalidAssociationError(
                "entity_2 ({}) not contained within this collection".format(entity_2)
            )

        if color not in {"red", "green"}:
            raise InvalidWireTypeError(color)
        if side_1 not in {"input", "output"}:
            raise InvalidConnectionSideError("'{}'".format(side_1))
        if side_2 not in {"input", "output"}:
            raise InvalidConnectionSideError("'{}'".format(side_2))

        # 2.0 code
        color_value = {"red": 1, "green": 2}
        dir_value = {"input": 0, "output": 2}

        wire_type_1 = color_value[color] + dir_value[side_1]
        wire_type_2 = color_value[color] + dir_value[side_2]

        try:
            self.wires.remove(
                [
                    Association(entity_1),
                    WireConnectorID(wire_type_1),
                    Association(entity_2),
                    WireConnectorID(wire_type_2),
                ]
            )
        except ValueError:
            pass
        try:
            self.wires.remove(
                [
                    Association(entity_2),
                    WireConnectorID(wire_type_2),
                    Association(entity_1),
                    WireConnectorID(wire_type_1),
                ]
            )
        except ValueError:
            pass

    def remove_circuit_connections(self) -> None:
        """
        Remove all circuit connections in the Collection. Recurses through all
        subgroups and removes circuit connections from them as well. Does
        nothing if there are no circuit connections in the Collection to remove.
        """
        for group in self.groups:
            group.remove_circuit_connections()

        self.wires[:] = [
            wire for wire in self.wires 
            if wire[1] not in { # No need to check the other side
                WireConnectorID.COMBINATOR_INPUT_RED, 
                WireConnectorID.COMBINATOR_INPUT_GREEN, 
                WireConnectorID.COMBINATOR_OUTPUT_RED, 
                WireConnectorID.COMBINATOR_OUTPUT_GREEN
            }]

    # =========================================================================
    # Trains
    # =========================================================================

    def add_train_at_position(
        self,
        config: TrainConfiguration,
        position: Union[Vector, PrimitiveVector],
        direction: Direction,
        schedule: Optional[Schedule] = None,
    ) -> None:
        """
        Adds a train with a specified configuration and schedule at a position
        facing a particular direction. Allows you to place a fully configured
        train in a single function call.

        If schedule is ``specified``, then it's checked if that schedule already
        exists within the collection's :py:attr:`schedules`. If found, all the
        locomotives in the added train are added to that schedule's locomotives;
        if not, a new schedule is appended to the list and the locomotives are
        added to that entry instead.

        .. NOTE:

            Currently can only place trains in a straight line; horizontally,
            vertically, or diagonally. Does not obey curved rails.

        .. see-also:

            :py:meth:`add_train_at_station`

        :param config: The :py:class:`TrainConfiguration` to use as a template
            for the created train, or a `str` that will be converted into one.
        :param position: A :py:class:`Vector` specifying the center of the
            starting wagon.
        :param direction: A :py:class:`Direction` enum or ``int`` specifying
            which direction the train is "facing".
        :param schedule: A :py:class:`Schedule` object specifying the schedule
            that the newly created train should inherit.
        """
        if isinstance(config, str):
            config = TrainConfiguration(config)

        # If we need to add the train to a schedule
        if schedule is not None:
            # Check to see if an equivalent train schedule already exists
            current_schedule = None
            for existing_schedule in self.schedules:
                if schedule.stops == existing_schedule.stops:
                    # If so, use that
                    current_schedule = existing_schedule
                    break
            # Otherwise, add a new schedule and set that as working
            if current_schedule is None:
                self.schedules.append(schedule)
                current_schedule = self.schedules[-1]

        current_pos = Vector.from_other(position)
        for entity in config.cars:
            # Add wagon
            orientation = (direction.to_orientation() + entity.orientation) % 1.0
            self.entities.append(
                entity, copy=True, position=current_pos, orientation=orientation
            )
            # If it's a locomotive, make sure it has the correct schedule
            if schedule is not None and entity.type == "locomotive":
                current_schedule.add_locomotive(self.entities[-1])

            current_pos += direction.to_vector(-7)  # 7 = distance between wagons

    def add_train_at_station(
        self,
        config: TrainConfiguration,
        station: Union[EntityLike, str, int],
        schedule: Optional[Schedule] = None,
    ) -> None:
        """
        Adds a train with a specified configuration and schedule behind a
        specified train stop.

        If schedule is ``specified``, then it's checked if that schedule already
        exists within the collection's :py:attr:`schedules`. If found, all the
        locomotives in the added train are added to that schedule's locomotives;
        if not, a new schedule is appended to the list and the locomotives are
        added to that entry instead.

        .. NOTE:

            Currently can only place trains in a straight line; horizontally or
            vertically. Does not obey curved rails if placed over them.

        .. see-also:

            :py:meth:`add_train_at_position`

        :param config: The :py:class:`TrainConfiguration` to use as a template
            for the created train, or a `str` that will be converted into one.
        :param station: The ID or index of the train entity stop to spawn behind.
            Note that station names cannot be used; if you want to place a train
            behind a stop with a specific station name use
            :py:meth:`find_entities_filtered` to find candidates and then pick
            ones from there.
        :param schedule: A :py:class:`Schedule` object specifying the schedule
            that the newly created train should inherit.
        """
        if isinstance(config, str):
            config = TrainConfiguration(config)

        if not isinstance(station, EntityLike):
            station = self.entities[station]

        if station.type != "train-stop":
            raise ValueError("'station' must be a TrainStop")

        # If we need to add the train to a schedule
        if schedule is not None:
            # Check to see if an equivalent train schedule already exists
            current_schedule = None
            for existing_schedule in self.schedules:
                if schedule == existing_schedule:
                    # If so, use that
                    current_schedule = existing_schedule
                    break
            # Otherwise, add a new schedule and set that as working
            if current_schedule is None:
                self.schedules.append(schedule)
                current_schedule = self.schedules[-1]

        shift_over = station.direction.previous().to_vector(2)
        shift_back = station.direction.to_vector(4)
        current_pos = station.position - shift_back + shift_over
        for entity in config.cars:
            orientation = station.direction.to_orientation() + entity.orientation
            self.entities.append(
                entity, copy=True, position=current_pos, orientation=orientation
            )
            # If it's a locomotive, make to add it to the correct schedule
            if schedule is not None and entity.type == "locomotive":
                current_schedule.add_locomotive(self.entities[-1])

            # 7 = distance between wagons
            current_pos += station.direction.to_vector(-7)

    def set_train_schedule(
        self,
        train_cars: Union["Locomotive", list[RollingStock]],
        schedule: Optional[Schedule],
    ) -> None:
        """
        Sets the schedule of a particular locomotive, or an entire list of
        RollingStock. The list of rolling stock can include non-locomotive cars,
        they will just be skipped when setting schedules. The list of rolling
        stock can also include locomotives across multiple trains; in this case
        all connected train cars from every touched train will be given the new
        schedule. If ``schedule`` is set to ``None``, then any touched
        locomotive will have their schedule cleared instead of set.

        :param train_cars: The single Locomotive, or a list of RollingStock.
        :param schedule: The :py:class:`.Schedule` to give each connected train,
            or ``None`` to remove the schedule from each connected train.
        """
        # Normalize train cars to a list
        if not isinstance(train_cars, Sequence):
            train_cars = [train_cars]

        # We may be given a list of RollingStock that spans multiple trains; so
        # we iterate over each given car and grab the entire train associated
        all_cars: set[RollingStock] = set()
        for train_car in train_cars:
            if train_car in all_cars:
                continue
            connected_stock = self.find_train_from_wagon(train_car)
            all_cars.update(set(connected_stock))

        # Ignore any non-locomotive entities
        locomotives = list(filter(lambda x: x.type == "locomotive", all_cars))

        # Wipe any schedule that the train(s) might already have
        for existing_schedule in self.schedules:
            for locomotive in locomotives:
                locomotive_association = Association(locomotive)
                if locomotive_association in existing_schedule.locomotives:
                    existing_schedule.locomotives.remove(locomotive_association)

        # Add the new schedule, if available
        if schedule is not None:
            # Determine if there already exists an equivalent schedule
            target_schedule = None
            for existing_schedule in self.schedules:
                if schedule.stops == existing_schedule.stops:
                    target_schedule = existing_schedule

            # If not, we append a new one
            if target_schedule is None:
                self.schedules.append(schedule)
                target_schedule = self.schedules[-1]

            # Now iterate over the target_schedule and add all the locomotives
            # to it
            for locomotive in locomotives:
                target_schedule.add_locomotive(locomotive)

    def remove_train(self, cars: list[EntityLike]) -> None:
        """
        Removes all of the rolling stock specified as the list ``cars``, and
        also takes care of removing any locomotive associations in any
        corresponding :py:class:`Schedule` object(s). Does nothing if ``cars``
        is empty.

        :param cars: A ``list`` of references to :py:class:`EntityLike` s within
            the collection.

        :raises KeyError: If the specified entities within the list do not exist
            within the collection being accessed.
        """
        associations_to_remove = set()
        for car in cars:
            if car.type == "locomotive":
                associations_to_remove.add(car)
            self.entities.remove(car)

        for schedule in self.schedules:
            for target in associations_to_remove:
                try:
                    schedule.remove_locomotive(target)
                except ValueError:
                    pass

        # Don't do this; the user can do this later if they want to on their own
        # discretion
        # Remove any empty schedules
        # self.schedules[:] = [
        #     schedule for schedule in self.schedules if len(schedule.locomotives) > 0
        # ]

    # =========================================================================
    # Train Queries
    # =========================================================================

    def find_train_from_wagon(self, wagon: RollingStock) -> list[RollingStock]:
        """
        Returns a list of rolling stock connected together. Allows you to grab
        all connected cars to a particular wagon if you know where one
        is, such as when iterating through the locomotives in a particular
        :py:class:`Schedule` object, cargo wagons with a particular item filter
        returned from :py:meth:`find_entities_filtered`, etc.

        Note that this function may return a working train (rolling stock with
        at least one connected locomotive), but it also may not, since it's
        only criteria is connection.

        .. WARNING::

            This function might also return false positives if rolling stock is
            located right next to each other in a fully-compresssed rail setups.
            PR's to mitigate this are welcome.

        :param wagon: The ID of the wagon or the wagon itself to search for
            neighbours.

        :returns: A ``list`` of references to all connected wagons in the
            :py:class:`Collection`, including ``wagon`` itself. The order of
            wagons is listed from end to end, where the first entry in the list
            is the outermost car in the direction that ``wagon`` points.
        """
        # TODO: remake this function to use "stock" parameter to deduce trains
        train = []
        all_locos_backwards = True  # Flag in case we need to reverse entire train
        used_wagons = set()  # Set of wagons we've already added to the current train

        def traverse_neighbours(
            wagon: RollingStock,
            current_train: list[RollingStock],
            backwards: bool = False,
        ) -> list[RollingStock]:
            """
            Check areas near a specified wagon to see if there are other wagons
            connected to it.
            """
            nonlocal all_locos_backwards

            if wagon.type == "locomotive" and not backwards:
                all_locos_backwards = False

            neighbours: list[RollingStock] = self.find_entities_filtered(
                position=wagon.position,
                radius=7.5,  # Average distance is less than 7 tiles
                type={"locomotive", "cargo-wagon", "fluid-wagon", "artillery-wagon"},
            )
            for neighbour in neighbours:
                # Check to make sure we haven't already added this wagon to a
                # train
                if neighbour in used_wagons:
                    continue

                # If the orientation is +- 45 degrees in either direction from
                # the current wagon's orientation, it may be connected
                wagon_dir = float(wagon.orientation)
                inv_wagon_dir = float(wagon.orientation.opposite())
                if (wagon_dir - 0.125 < neighbour.orientation < wagon_dir + 0.125) or (
                    inv_wagon_dir - 0.125
                    < neighbour.orientation
                    < inv_wagon_dir + 0.125
                ):
                    # Determine the neighbour's closest truck point
                    a = neighbour.position + neighbour.orientation.to_vector(2)
                    b = neighbour.position + neighbour.orientation.to_vector(-2)
                    if distance(wagon.position, a) < distance(wagon.position, b):
                        neighbour_truck = a
                    else:
                        neighbour_truck = b

                    if backwards:
                        forward_orientation = wagon.orientation.opposite()
                    else:
                        forward_orientation = wagon.orientation

                    # Determine the front from `forward_orientation`
                    neighbour_vec = neighbour.orientation.to_vector()
                    forward_vec = forward_orientation.to_vector()
                    dot_prod = sum(
                        [i * j for (i, j) in zip(neighbour_vec, forward_vec)]
                    )
                    if dot_prod < 0:
                        neighbour_is_backwards = True
                    else:
                        neighbour_is_backwards = False

                    # Check "front"
                    wagon_truck = wagon.position + forward_orientation.to_vector(2)
                    if 2.9 < distance(wagon_truck, neighbour_truck) <= 3.1:
                        # Add to beginning of train list
                        used_wagons.add(neighbour)
                        current_train.insert(0, neighbour)
                        traverse_neighbours(
                            neighbour, current_train, neighbour_is_backwards
                        )

                    # Check "back"
                    wagon_truck = wagon.position + forward_orientation.to_vector(-2)
                    if 2.9 < distance(wagon_truck, neighbour_truck) <= 3.1:
                        # Add to end of train list
                        used_wagons.add(neighbour)
                        current_train.append(neighbour)
                        traverse_neighbours(
                            neighbour, current_train, neighbour_is_backwards
                        )

            return current_train

        used_wagons.add(wagon)
        train = traverse_neighbours(wagon, [wagon])

        # Sometimes the starting wagon can be pointing the opposite way, so all
        # locomotives end up pointing back to front
        # If that's the case, we reverse the list so that left is front and
        # right is back
        if all_locos_backwards:
            train.reverse()

        return train

    def find_trains_filtered(
        self,
        train_length: Union[int, tuple, None] = None,
        orientation: Optional[Orientation] = None,
        at_station: Union[bool, set] = False,
        num_type: Optional[dict] = None,
        num_name: Optional[dict] = None,
        config: Optional[TrainConfiguration] = None,
        schedule: Optional[Schedule] = None,
        invert: bool = False,
        limit: Optional[int] = None,
    ) -> list[list[EntityLike]]:
        """
        Finds a set of trains that match the passed in parameters. Formally, a
        "train" in this context is a connected set of wagons which may or may
        not contain a locomotive. This is done so that the user can search a
        blueprint for unconnected rolling stock if any exists, and can filter
        for regular trains more broadly.

        .. NOTE::

            When using the ``config`` parameter, equality is strictly checked;
            which means that if a returned train doesn't _exactly_ match the
            specified argument, the train is filtered from the result. This
            includes things like fuel requests and cargo wagon item filters, so
            check these values in the blueprints you're searching and adjust
            ``config`` accordingly.

        :param train_length: Can either be specified as an ``int`` representing
            the exact length of trains to return, or as a ``Sequence`` of 2
            ``int``s representing the minimum and maximum length of trains to
            return (inclusive). Either the min or the max can also be set to
            ``None`` which indicates no minimum length and no maxiumum length
            respectively.
        :param orientation: A :py:class:`Orientation` (or equivalent ``float``)
            that describes the orientation that every car in the returned train
            list should have. Note that trains placed on curved rails will not
            be returned by this parameter, as _all_ train cars must equal
            ``orientation``.
        :param at_station: Can be specified as a ``bool`` value which will
            return all trains at any station, a ``str`` value where it will
            return all trains at any station with that name, or as a ``set[str]``
            where all of the trains behind any station with one of those names
            is returned.
        :param num_type: A ``dict`` of wagon types where each key is the ``str``
            type of the wagon and the value is an ``int`` representing the
            desired number of those wagons in the returned train. Allows to
            search for trains of a particular composition without regards to
            contents, order, or orientation. Also supports swapping the ``int``
            with a ``Sequence`` of 2 ``int``s representing the minimum and
            maximum tolerable value of a wagon of that type, along with ``None``
            for no particular min or max.
        :param num_name: Identical to ``num_type``, except that instead of
            wagon type it's wagon name, in case there happen to be more than
            one Locomotive, CargoWagon, FluidWagon, or ArtilleryWagon.
            Useful for blueprints with modded trains, where you might want to
            distinguish between them.
        :param config: A :py:class:`TrainConfiguration` object to filter against.
            Performs a equality check between each of the train configuration's
            cars and the cars in the returned trains.
        :param schedule: A :py:class:`Schedule` that the returned trains should
            match. Only trains who's schedules match this one exactly will be
            returned.
        :param invert: Whether or not to return the inversion of the search
            criteria.
        :param limit: A maximum number of unique trains to return.

        :returns: A ``list`` of ``list`` s, where each sub-list represents a
            contiguous train. Trains are ordered such that the first index is
            the "front" of the train, as chosen by the orientation of the first
            found wagon in that group.
        """
        wagons = self.find_entities_filtered(
            type={"locomotive", "cargo-wagon", "fluid-wagon", "artillery-wagon"}
        )
        stops = self.find_entities_filtered(type="train-stop")
        trains = []
        used_wagons = set()  # Create a set of wagons already traversed

        # Get all contiguous trains
        # TODO: this could probably be more performant if we check train
        # validity as we iterate, meaning we could simply early exit if we
        # exceed `limit` for example
        for wagon in wagons:
            if wagon in used_wagons:
                continue

            train = self.find_train_from_wagon(wagon)

            # Record each found wagon as used
            for train_car in train:
                used_wagons.add(train_car)

            trains.append(train)

        def normalize_range(value: int | Sequence) -> tuple[int, int]:
            """
            Converts integers to inclusive ranges like:
                1 -> (1, 1)
            And converts ranges with values of None to no range:
                (None, None) -> (0, math.inf)
            """
            if isinstance(value, int):
                return (value, value)  # min -> max inclusive
            else:  # tuple/list
                min_value = value[0] if value[0] is not None else 0
                max_value = value[1] if value[1] is not None else math.inf
                return (min_value, max_value)

        # Normalize inputs
        if train_length is not None:
            train_length = normalize_range(train_length)
        if isinstance(at_station, str):
            at_station = {at_station}
        if num_type is not None:
            for car_type in num_type:
                num_type[car_type] = normalize_range(num_type[car_type])
        if num_name is not None:
            for car_name in num_name:
                num_name[car_name] = normalize_range(num_name[car_name])
        if limit is None:
            limit = len(trains)

        def equivalent_cars(car1, car2):
            """
            Need this function because checking for equality between cars also
            includes things like orientation and position, which we don't want
            to consider in this case since a train configuration's position and
            orientation are dummy values until they're actually added to a BP.
            """
            # TODO: ensure it includes everything else, like fuel requests, item
            # filters, etc.
            return car1.name == car2.name

        def train_at_station(train):
            """
            Determine whether a train's head is adjacent to a train stop. Returns
            the name of the station the train is (likely) stopped at.
            """
            # Get the position and orientation of where the stop should be if it
            # exists:
            forward = train[0].orientation.to_direction()
            right = forward.next()
            pos = train[0].position + forward.to_vector(3) + right.to_vector(2)
            for stop in stops:
                if stop.position == pos and stop.direction == forward:
                    return stop.station  # station name
            # TODO: check both ends if the we determine that the train is dual
            # headed
            # TODO: check to ensure that this train has a schedule that includes
            # the name of the stop before assuming that this train is at that
            # stop
            return False

        # Filter based on parameters
        def test(train):
            if train_length is not None:
                if not (train_length[0] <= len(train) <= train_length[1]):
                    return False
            if at_station:
                if isinstance(at_station, set):
                    station_name = train_at_station(train)
                    if station_name not in at_station:
                        return False
                else:  # bool
                    # Train can be at a station, but can return an empty name;
                    # thus we have to check that it exactly is False instead of
                    # falsey
                    if train_at_station(train) is False:
                        return False
            if num_type is not None:
                for desired_type, desired_range in num_type.items():
                    num_found = sum(x.type == desired_type for x in train)
                    if not (desired_range[0] <= num_found <= desired_range[1]):
                        return False
            if num_name is not None:
                for desired_name, desired_range in num_name.items():
                    num_found = sum(x.name == desired_name for x in train)
                    if not (desired_range[0] <= num_found <= desired_range[1]):
                        return False
            if orientation is not None:
                for train_car in train:
                    if train_car.orientation != orientation:
                        return False
            if config is not None:
                if len(train) != len(config.cars):
                    return False
                for i, config_car in enumerate(config.cars):
                    if not equivalent_cars(train[i], config_car):
                        return False
            if schedule is not None:
                # Get the first locomotive in the train, since all locomotives
                # on the train should share the same schedule
                for car in train:
                    if car.type == "locomotive":
                        locomotive = car
                # Search for the schedule that that locomotive uses
                for found_schedule in self.schedules:
                    if (
                        Association(locomotive) in found_schedule.locomotives
                        and found_schedule.stops == schedule.stops
                    ):
                        return True  # FIXME: cursed returns
                return False
            return True

        if invert:
            return list(filter(lambda train: not test(train), trains))[:limit]
        else:
            return list(filter(lambda train: test(train), trains))[:limit]

    # =========================================================================
    # Internal methods
    # =========================================================================

    def _get_entity_from_path(self, path: int | str | tuple[Union[int, str], ...]):
        """
        TODO
        """
        if isinstance(path, tuple):
            collection: Collection = self.groups[path[0]]
            path = path[1:]
            return collection._get_entity_from_path(path[0] if len(path) == 1 else path)
        else:
            return self.entities[path]

    def __contains__(self, item: EntityLike) -> bool:
        # Check to see if an entity is within this Collection's entities, or in
        # any subgroup inside of it
        # TODO: could probably be abstracted for any item: tiles, schedules, etc.
        if item in self.entities:
            return True
        else:  # Check every subgroup
            for group in self.groups:
                if item in group:
                    return True
        # Nothing was found
        return False

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        def swap_association(original_association):
            """
            Take an association which points to some entity in `self` and return
            a new association which points to the equivalent entity in `result`.
            """
            original_entity = original_association()
            copied_entity = memo[id(original_entity)]
            return Association(copied_entity)

        memo["new_parent"] = result  # TODO: this should really be fixed
        for attr in attrs.fields(cls):
            if attr.name == "_parent":
                # When copying a Collection, wipe it's parent attribute (if it
                # has one); If this needs to be set, it's set when the newly
                # created collection is assigned to its parent
                object.__setattr__(result, attr.name, None)

            # Handle associations
            elif attr.name == "wires":
                new_wires = deepcopy(getattr(self, attr.name), memo)
                for wire in new_wires:
                    wire[0] = swap_association(wire[0])
                    wire[2] = swap_association(wire[2])
                object.__setattr__(result, attr.name, new_wires)

            elif attr.name == "schedules":
                new_schedules: ScheduleList = deepcopy(getattr(self, attr.name), memo)
                for schedule in new_schedules:
                    schedule.locomotives = [
                        swap_association(loco) for loco in schedule.locomotives
                    ]
                object.__setattr__(result, attr.name, new_schedules)

            elif attr.name == "stock_connections":  # special
                new_connections: list[StockConnection] = deepcopy(
                    getattr(self, attr.name), memo
                )
                for connection in new_connections:
                    connection.stock = swap_association(connection.stock)
                    if connection.front is not None:
                        connection.front = swap_association(connection.front)
                    if connection.back is not None:
                        connection.back = swap_association(connection.back)
                object.__setattr__(result, attr.name, new_connections)

            else:
                object.__setattr__(
                    result, attr.name, deepcopy(getattr(self, attr.name), memo)
                )

        return result
