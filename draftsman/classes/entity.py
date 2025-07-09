# entity.py

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.exportable import (
    Exportable,
)
from draftsman.classes.vector import Vector
from draftsman.constants import (
    Direction,
    InventoryType,
    ValidationMode,
    FOUR_WAY_DIRECTIONS,
    EIGHT_WAY_DIRECTIONS,
    SIXTEEN_WAY_DIRECTIONS,
)
from draftsman.data import entities
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    BlueprintInsertPlan,
    ItemID,
    ItemInventoryPositions,
    InventoryPosition,
    QualityID,
    EntityID,
    get_suggestion,
    uint32,
    uint64,
)
from draftsman.utils import (
    aabb_to_dimensions,
    attrs_reuse,
    get_first,
    passes_surface_conditions,
    reissue_warnings,
)
from draftsman.validators import conditional, instance_of, one_of
from draftsman.warning import (
    GridAlignmentWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
)

from draftsman.data import mods
from draftsman.data.planets import get_surface_properties

import attrs
import math
import pprint
from typing import Any, Optional
import warnings
import weakref


class _PosVector(Vector):
    def __init__(self, x, y, entity):
        super().__init__(x, y)
        self.entity = weakref.ref(entity)

    @Vector.x.setter
    def x(self, value):
        self._data[0] = float(value)
        self.entity().tile_position._data[0] = round(
            value - self.entity().tile_width / 2
        )

    @Vector.y.setter
    def y(self, value):
        self._data[1] = float(value)
        self.entity().tile_position._data[1] = round(
            value - self.entity().tile_height / 2
        )


class _TileVector(Vector):
    def __init__(self, x, y, entity):
        super().__init__(x, y)
        self.entity = weakref.ref(entity)

    @Vector.x.setter
    def x(self, value):
        self._data[0] = int(value)
        self.entity().position._data[0] = value + self.entity().tile_width / 2

    @Vector.y.setter
    def y(self, value):
        self._data[1] = int(value)
        self.entity().position._data[1] = value + self.entity().tile_height / 2


@attrs.define
class Entity(EntityLike, Exportable):
    """
    Entity base-class. Used for all entity types that are specified in Factorio.
    Categorizes entities into "types" based on their class, each of which is
    implemented in :py:mod:`draftsman.prototypes`.

    Instances of this class are created whenever Draftsman cannot determine the
    type of some given entity, usually due to environment or version mismatch.
    In this case, known attributes like :py:attr:`.name` and :py:attr:`.position`
    will be correctly interpreted and validated, while all other keys will be
    stored under :py:attr:`.extra_keys`. This allows the user to manually
    deduce and convert instances of this base type to subtypes manually, if
    there is sufficient context to do so.
    """

    # =========================================================================
    # Init
    # =========================================================================

    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        position: Optional[_PosVector] = None,
        tile_position: _TileVector = attrs.NOTHING,
        mirror: bool = False,
        quality: QualityID = "normal",
        item_requests: list[BlueprintInsertPlan] = attrs.NOTHING,
        tags: Optional[dict[str, Any]] = attrs.NOTHING,
        *,
        entity_number: Optional[uint64] = None,
        extra_keys: Optional[dict[Any, Any]] = None,
        **kwargs
    ):
        self.__attrs_init__(
            name,
            id=id,
            position=position,
            tile_position=tile_position,
            mirror=mirror,
            quality=quality,
            item_requests=item_requests,
            tags=tags,
            entity_number=entity_number,
            extra_keys=extra_keys,
        )

        # Add any extra kwargs to `extra_keys`, which is important in the
        # generic `Entity(...)` case in order to support parameters from
        # subclasses without exploding
        if self.extra_keys:
            self.extra_keys = {**self.extra_keys, **kwargs}
        elif kwargs:
            self.extra_keys = kwargs

    def __attrs_post_init__(self):
        # We gave incorrect defaults for `position` and `tile_position` so that
        # we can deduce which ones were specified in init
        # (For example`position` can be `None` at this point, even though it's
        # type annotated as always being a Vector instance. We wouldn't have to
        # do this if attrs supported kwargs here, but it doesn't, so.)

        # We then do a dummy set of either attribute, which calls the
        # `_set_(tile_)position()` methods, which handles updating both
        # to their proper `_PosVector`/`_TileVector` instances.
        if self.position is not None:
            self.position = self.position
        else:
            # FIXME: technically, this line causes GridAlignment warnings to
            # be issued twice, once during init and once here
            self.tile_position = self.tile_position

        # Cursed, but we make do

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        """
        Returns a list of strings representing the names of entities that share
        the same type as this one.
        """
        return []

    # =========================================================================

    @property
    def prototype(self) -> dict:
        """
        Returns the prototype entry from data.raw for this entity. If the entity
        has a name which is not recognized, an empty dict is returned instead.
        Not exported; read only.
        """
        return entities.raw.get(self.name, {})

    # =========================================================================

    @property
    def type(self) -> Optional[str]:
        """
        The type of the Entity. Equivalent to the key found in Factorio's
        ``data.raw``. Mostly equivalent to the type of the entity instance,
        though there are some differences,
        :ref:`as noted here <handbook.entities.differences>`.
        Can be used as a criteria to search with in
        :py:meth:`.EntityCollection.find_entities_filtered`. Returns ``None`` if
        this entity's name is not recognized when created without validation.
        Not exported; read only.
        """
        return self.prototype.get("type", None)

    # =========================================================================

    @property
    def global_position(self) -> Vector:
        """
        The "global", or root-most position of the Entity. This value is always
        equivalent to :py:meth:`~.Entity.position`, unless the entity exists
        inside an :py:class:`.EntityCollection`. If it does, then it's global
        position is equivalent to the sum of all parent positions plus it's own
        position. For example, if an Entity exists within a :py:class:`.Group`
        at position ``(5, 5)`` and the ``Group`` exists at ``(5, 5)``, the
        ``global_position`` of the Entity will be ``(10, 10)``.

        This is used to get an entity's "actual" position in a blueprint, used
        when adding to a :py:class:`.SpatialHashMap` and when querying the
        entity by region. This attribute is always exported, but renamed to
        "position"; read only.
        """
        if self._parent and hasattr(self._parent, "global_position"):
            return self._parent.global_position + self.position
        else:
            return self.position

    # =========================================================================

    @property
    def valid_directions(self) -> set[Direction]:
        """
        A set containing all directions that this entity can face. Not exported;
        read only.
        """
        if not self.rotatable:  # pragma: no coverage
            return {Direction.NORTH}
        try:
            if "building-direction-8-way" in self.flags:  # pragma: no coverage
                return EIGHT_WAY_DIRECTIONS
            elif "building-direction-16-way" in self.flags:  # pragma: no coverage
                return SIXTEEN_WAY_DIRECTIONS
            else:
                return FOUR_WAY_DIRECTIONS
        except TypeError:
            # In the unknown case, assume that the entity could have any valid
            # direction
            return SIXTEEN_WAY_DIRECTIONS

    # =========================================================================

    @property
    def static_collision_set(self) -> Optional[CollisionSet]:
        """
        The set of all CollisionShapes that this entity inherits. This set is
        always the shape of the entity with it's default orientation (typically
        facing north) and does not change when the entity is rotated/flipped. If
        you want the collision shape of this entity that does change when
        rotated, use :py:attr:`.collision_set` instead.
        """
        return entities.collision_sets.get(self.name, None)

    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        """
        The set of all CollisionShapes that this entity inherits. This set is
        dynamically updated based on the rotation or orientation of the entity,
        if applicable. If you want the collision shape of this entity that does
        not change via rotation or orientation, use :py:attr:`.static_collision_set`
        instead.
        """
        return self.static_collision_set

    # =========================================================================

    @property
    def collision_mask(self) -> set:
        """
        The set of all collision layers that this Entity collides with,
        specified as strings. Equivalent to Factorio's ``data.raw`` equivalent.
        Not exported; read only.
        """
        # We guarantee that the "collision_mask" key will exist during
        # `draftsman-update`, and that it will have it's proper default based
        # on it's type
        return self.prototype.get("collision_mask", None)

    # =========================================================================

    @property
    def static_tile_width(self) -> int:
        """
        The width of the entity irrespective of it's current orientation.
        Equivalent to the :py:attr:`.tile_width` when the entity is facing north.
        """
        if "tile_width" in self.prototype:
            return self.prototype["tile_width"]
        else:
            return aabb_to_dimensions(
                self.static_collision_set.get_bounding_box()
                if self.static_collision_set
                else None
            )[0]

    # =========================================================================

    @property
    def static_tile_height(self) -> int:
        """
        The height of the entity irrespective of it's current orientation.
        Equivalent to the :py:attr:`.tile_width` when the entity is facing north.
        """
        if "tile_height" in self.prototype:
            return self.prototype["tile_height"]
        else:
            return aabb_to_dimensions(
                self.static_collision_set.get_bounding_box()
                if self.static_collision_set
                else None
            )[1]

    # =========================================================================

    @property  # Cache?
    def tile_width(self) -> int:
        # Overwritten by `DirectionMixin` in order to handle `direction`.
        return Entity.static_tile_width.fget(self)

    # =========================================================================

    @property  # Cache?
    def tile_height(self) -> int:
        # Overwritten by `DirectionMixin` in order to handle `direction`.
        return Entity.static_tile_height.fget(self)

    # =========================================================================

    @property
    def square(self) -> bool:
        """
        Whether or not the tile width of this entity matches it's tile height,
        giving it a square footprint. Not exported; read only.
        """
        return self.static_tile_width == self.static_tile_height

    # =========================================================================

    @property
    def flags(self) -> Optional[list[str]]:
        """
        A set of string flags which indicate a number of behaviors of this
        prototype. Not exported; read only.

        .. seealso::

            `<https://wiki.factorio.com/Types/EntityPrototypeFlags>`_
        """
        return self.prototype.get("flags", None)

    # =========================================================================

    @property
    def flippable(self) -> bool:
        """
        Whether or not this entity can be mirrored in game using 'F' or 'G'.
        Not exported; read only.

        .. NOTE::

            Work in progress. May be incorrect, especially for modded entities.
        """
        return entities.flippable[self.name]

    # =========================================================================

    @property
    def surface_conditions(self) -> Optional[dict]:
        """
        Gets the dictionary of surface constraints which apply when placing this
        entity. If this entity has no constraints whatsoever, an empty
        dictionary is returned. If this entity is unrecognized by Draftsman,
        `None` is returned. Not exported; read only.
        """
        return entities.raw.get(self.name, {"surface_conditions": None}).get(
            "surface_conditions", {}
        )

    # =========================================================================
    # Attributes
    # =========================================================================

    # TODO: which of these do I want? Need to investigate what happens when you
    # give the game a blueprint with two entities with the same entity_number...
    _entity_number: Optional[uint64] = attrs.field(
        default=None,
        repr=False,
        eq=False,
        kw_only=True,
        validator=instance_of(Optional[uint64]),
        metadata={"omit": False},
    )

    @property
    def entity_number(self) -> Optional[uint64]:
        # TODO: an entity number is used for associations, dummy
        # Fix this docstring
        # TODO: also, I'm not convinced this should exist in Entity even for
        # posterity/completeness-sake; it's a mechanism for holding relationship
        # information which is entirely superceeded by Associations, and keeping
        # it here will likely confuse more people than help them
        """
        A numeric value associated with this entity, 1-indexed. In practice this is
        the index of the dictionary in the blueprint's 'entities' list, but this is
        not strictly enforced, and its even possible for multiple entities to share
        the same ``entity_number`` in the same blueprint without consequence.

        An :py:class:`.Entity` created outside of a blueprint has no way to
        determine it's own ``entity_number``, so it defaults to ``None``. Entities
        added to blueprints also default to ``None``, as since entity lists
        are frequently modified it makes the most sense to only generate these
        values when exporting. This value is only populated when importing from an
        existing blueprint string, but the value is not kept "accurate" if the
        parent entity list in which it resides changes.

        This attribute is provided for posterity in case this value is somehow
        useful, but since its value is non-authorative, it gets overwritten when
        exporting to follow the above "entity number == index in entities list"
        axiom.
        """
        return self._entity_number

    # =========================================================================

    name: EntityID = attrs.field(
        validator=instance_of(str),
        # on_setattr=read_only, # In a perfect world, but flexibility is better methinks
        metadata={"omit": False},
    )
    """The name of the entity."""

    @name.default
    def get_default_entity(self):
        return get_first(self.similar_entities)

    @name.validator
    @conditional(ValidationMode.STRICT)
    def _ensure_name_recognized(
        self,
        _: attrs.Attribute,
        value: str,
    ):
        """
        Ensures the name of this entity is both recognized by Draftsman and that
        it belongs to this class type.
        """
        if value not in entities.raw:
            msg = "Unknown entity '{}'{}".format(
                value, get_suggestion(value, entities.raw.keys(), n=1)
            )
            warnings.warn(UnknownEntityWarning(msg))
        elif value not in self.similar_entities:
            msg = "'{}' is not a known name for a {}{}".format(
                value,
                type(self).__name__,
                get_suggestion(value, self.similar_entities, n=1),
            )
            warnings.warn(UnknownEntityWarning(msg))

    # =========================================================================

    # TODO: this should be moved into EntityLike since that makes more sense
    def _set_id(self, _attr: attrs.Attribute, value: Optional[str]):
        if self.parent:
            self.parent.entities._remove_key(self.id)
            if value is not None:
                self.parent.entities._set_key(value, self)

        return value

    # TODO: does an ID have to be a string? Is it not being a string ever useful?
    id: Optional[str] = attrs.field(
        default=None, on_setattr=_set_id, metadata={"omit": True}
    )
    """
    A unique string ID associated with this entity. ID's can be anything,
    though there can only be one entity with a particular ID in an
    EntityCollection. Not exported.
    """

    @id.validator
    @conditional(ValidationMode.MINIMUM)  # TODO: should this be a validator?
    def _ensure_id_correct_type(self, _attr: attrs.Attribute, value: Any):
        if value is not None and not isinstance(value, str):
            raise TypeError("'id' must be either a str or None")

    # =========================================================================

    def _set_position(self, attr: attrs.Attribute, value: Any):
        value = Vector.from_other(value)

        # self.position.update_from_other(value, float)
        # self.tile_position.update(
        #     round(self.position.x - self.tile_width / 2),
        #     round(self.position.y - self.tile_height / 2),
        # )

        # res = _PosVector(0, 0, self)
        # res.update_from_other(value)
        res = _PosVector(
            value.x,  # round(value.x - self.tile_width / 2),
            value.y,  # round(value.y - self.tile_height / 2),
            self,
        )

        object.__setattr__(self, "position", res)
        object.__setattr__(
            self,
            "tile_position",
            _TileVector(
                round(value.x - self.tile_width / 2),
                round(value.y - self.tile_height / 2),
                self,
            ),
        )

        # Check of grid-alignment warnings after the positions have been updated
        attr.validator(self, attr, value)

        return res

    position: _PosVector = attrs.field(
        default=None,
        converter=Vector.from_other,
        on_setattr=_set_position,
        metadata={"omit": False},
    )
    """
    The "canonical" position of the Entity, or the one that Factorio uses.
    Positions of most entities are located at their center, which can either
    be in the middle of a tile or on it's transition, depending on the
    Entity's ``tile_width`` and ``tile_height``.

    ``position`` can be specified as a ``dict`` with ``"x"`` and ``"y"``
    keys, or more succinctly as a sequence of floats, usually a ``list`` or
    ``tuple``. ``position`` can also be specified more verbosely as a
    ``Vector`` instance as well.

    This property is updated in tandem with ``tile_position``, so using them
    both interchangeably is both allowed and encouraged.

    :getter: Gets the position of the Entity.
    :setter: Sets the position of the Entity.

    :exception IndexError: If the set value does not match the above
        specification.
    :exception DraftsmanError: If the entities position is modified when
        inside a EntityCollection, :ref:`which is forbidden.
        <handbook.blueprints.forbidden_entity_attributes>`
    """

    @position.validator
    @conditional(ValidationMode.MINIMUM)
    def _position_validator(self, _: attrs.Attribute, value: Vector):
        if self.double_grid_aligned:
            if self.tile_position.x % 2 == 1 or self.tile_position.y % 2 == 1:
                cast_position = Vector(
                    math.floor(self.tile_position.x / 2) * 2,
                    math.floor(self.tile_position.y / 2) * 2,
                )
                msg = (
                    "Double-grid aligned entity is not placed along chunk grid; "
                    "entity's tile position will be cast from {} to {} when "
                    "imported".format(self.tile_position, cast_position)
                )
                warnings.warn(GridAlignmentWarning(msg))

    # =========================================================================

    def _set_tile_position(self, attr: attrs.Attribute, value: Vector):
        # value = attr.converter(value)
        value = Vector.from_other(value, int)

        res = _TileVector(value.x, value.y, self)

        object.__setattr__(self, "tile_position", res)
        self.position = _PosVector(
            value.x + self.tile_width / 2, value.y + self.tile_height / 2, self
        )
        # object.__setattr__(
        #     self,
        #     "position",
        #     _PosVector(
        #         value.x + self.tile_width / 2, value.y + self.tile_height / 2, self
        #     ),
        # )

        # Check of grid-alignment warnings after the positions have been updated
        # attr.validator(self, attr, value)

        return res

    tile_position: _TileVector = attrs.field(
        converter=Vector.from_other, on_setattr=_set_tile_position
    )
    """
    The tile-position of the Entity. The tile position is the position
    according the the LuaSurface tile grid, and is the top left corner of
    the top-leftmost tile of the Entity.

    ``tile_position`` can be specified as a ``dict`` with ``"x"`` and
    ``"y"`` keys, or more succinctly as a sequence of floats, usually a
    ``list`` or ``tuple``.

    This property is updated in tandem with ``position``, so using them both
    interchangeably is both allowed and encouraged.

    :getter: Gets the tile position of the Entity.
    :setter: Sets the tile position of the Entity.

    :exception IndexError: If the set value does not match the above
        specification.
    :exception DraftsmanError: If the entities position is modified when
        inside a EntityCollection, :ref:`which is forbidden.
        <handbook.blueprints.forbidden_entity_attributes>`
    """

    @tile_position.default
    def get_default_tile_position(self):
        """
        Populate the internal _TileVector with a reference to the instantiated
        entity.
        """
        return _TileVector(
            0,
            0,
            self,
        )

    # =========================================================================

    mirror: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this blueprint is mirrored horizontally or vertically, 
    specifically in regards to it's fluid inputs/outputs.
    """

    # =========================================================================

    quality: QualityID = attrs.field(
        default="normal",
        validator=one_of(QualityID),
    )
    """
    The quality of this entity. Can modify certain other attributes of the
    entity in (usually) positive ways.

    Draftsman attributes that are dependent on quality will use this value when
    determining certain attribute values.
    """

    # =========================================================================

    def _items_converter(value):
        if value is None:
            return []
        elif isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                res[i] = BlueprintInsertPlan.converter(elem)
            return res
        else:
            return value

    item_requests: list[BlueprintInsertPlan] = attrs.field(
        factory=list,
        converter=_items_converter,
        validator=instance_of(list[BlueprintInsertPlan]),
    )
    """
    A list of items to deliver to the entity. Not to be confused with logistics
    requests (which are persistent), item requests are only fulfilled once when
    the entity is first constructed. Most notably, modules are requested to
    entities with this field.

    For user-friendly ways to modify this array, see TODO and TODO.
    """

    # =========================================================================

    tags: Optional[dict[str, Any]] = attrs.field(
        factory=dict, validator=instance_of(Optional[dict])
    )
    """
    Tags associated with this Entity. Commonly used by mods to add custom
    data to a particular Entity when exporting and importing Blueprint
    strings.

    :getter: Gets the tags of the Entity, or ``None`` if not set.
    :setter: Sets the Entity's tags.

    :exception TypeError: If tags is set to anything other than a ``dict``
        or ``None``.
    """

    # =========================================================================

    extra_keys = attrs_reuse(attrs.fields(Exportable).extra_keys, validator=None)

    @extra_keys.validator
    @conditional(ValidationMode.STRICT)
    def _extra_keys_validator(
        self,
        _: attrs.Attribute,
        value: Optional[dict],
    ):
        """
        Issue warnings if `extra_keys` is not empty, *except* in the cases where
        self is a generic :py:class:`.Entity`.
        """
        if value and type(self) is not Entity:
            msg = "'{}' object has had the following unrecognized keys:\n{}".format(
                type(self).__name__, pprint.pformat(value)
            )
            warnings.warn(UnknownKeywordWarning(msg))

    # =========================================================================
    # Methods
    # =========================================================================

    def is_placable_on(self, surface_name: str) -> bool:
        """
        Check to see if this entity is placable on a particular planet/surface.
        `surface_name` must be the name of a registered surface in `data.planets`.
        If the `surface_properties` of this entity are unknown, then this
        function always returns `True`.
        """
        surface_properties = get_surface_properties(surface_name)
        return passes_surface_conditions(self.surface_conditions, surface_properties)

    # =========================================================================

    @reissue_warnings
    def set_item_request(
        self,
        item: str,
        count: Optional[uint32] = None,
        quality: QualityID = "normal",
        inventory: InventoryType = 1,
        slot: Optional[uint32] = None,
    ):
        """
        Creates a construction request for an item. Removes the item request if
        ``count`` is set to ``0`` or ``None``.

        :param item: The string name of the requested item.
        :param quality: The quality of the requested item.
        :param count: The desired amount of that item. If omitted a count of
            ``0`` will be assumed.
        :param inventory: The particular inventory to request this item to,
            since entities can have more than one distinct inventories to
            request items to. If omitted, it will default to ``1``, which is
            usally the "primary" inventory.
        :param slot: The particular slot in the inventory to place the item. The
            next open slot will be chosen automatically if omitted.

        :exception TypeError: If ``item`` is anything other than a ``str``, or
            if ``count`` is anything other than an ``int`` or ``None``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception ValueError: If ``count`` is less than zero.
        """
        if count is None:
            count = 0

        if count == 0:
            # TODO: better removal across multiple categories
            # (Might be better to abstract this into `remove_item_request` or similar)
            self.item_requests = [
                i_item for i_item in self.item_requests if i_item.id.name != item
            ]
        else:
            # Try to find an existing entry for `item` with the same quality
            existing_spec = next(
                filter(
                    lambda x: x.id.name == item and x.id.quality == quality,
                    self.item_requests,
                ),
                None,
            )
            if existing_spec is None:
                # If not, add a new item entry
                if slot is None:
                    slot = len(self.item_requests)
                self.item_requests += [
                    BlueprintInsertPlan(
                        id=ItemID(name=item, quality=quality),
                        items=ItemInventoryPositions(
                            in_inventory=[
                                InventoryPosition(
                                    inventory=inventory,
                                    stack=slot,
                                    count=count,
                                )
                            ]
                        ),
                    )
                ]
            else:
                # Try to find an existing entry at the same slot in the same inventory
                # TODO: what if there's an entry, but slot is None? Do we just pick
                # the first valid entry?
                if slot is None:
                    slot = 0
                existing_slot = next(
                    filter(
                        lambda x: x.inventory == inventory and x.stack == slot,
                        existing_spec.items.in_inventory,
                    ),
                    None,
                )
                if existing_slot is None:
                    # If not, make a new one
                    existing_spec.items.in_inventory.append(
                        InventoryPosition(inventory=inventory, stack=slot, count=count)
                    )
                else:
                    # If so, simply modify the count
                    existing_slot.count = count

    # =========================================================================

    def to_dict(
        self,
        version: Optional[tuple[int, ...]] = None,
        exclude_none: bool = True,
        exclude_defaults: bool = True,
        entity_number: Optional[int] = None,
    ):
        if version is None:
            version = mods.versions["base"]
        res = {}
        if entity_number is not None:
            res["entity_number"] = entity_number
        res.update(super().to_dict(version, exclude_none, exclude_defaults))
        return res

    # =========================================================================

    def mergable_with(self, other: "Entity") -> bool:
        return (
            type(self) is type(other)
            and self.name == other.name
            and self.global_position == other.global_position
            and self.id == other.id
        )

    # =========================================================================

    def merge(self, other: "Entity"):
        self.mirror = other.mirror
        self.quality = other.quality
        self.item_requests = other.item_requests
        self.tags = other.tags

    # =========================================================================

    def __hash__(self) -> int:
        return id(self) >> 4  # Apparently this is the default?

    # =========================================================================

    def __str__(self) -> str:  # pragma: no coverage
        # Association debug printing:
        return "<{0}{1} at 0x{2:016X}>{3}".format(
            type(self).__name__,
            " '{}'".format(self.id) if self.id is not None else "",
            id(self),
            str(self.to_dict()),
        )


@attrs.define
class _ExportEntity:
    global_position: Vector = attrs.field(metadata={"omit": False})
    item_requests: dict = attrs.field(factory=dict)


_export_fields = attrs.fields(_ExportEntity)


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Entity,
    lambda fields: {
        "entity_number": fields._entity_number.name,
        "name": fields.name.name,
        "position": fields.position.name,
        # None: fields.mirror.name,
        # None: fields.quality.name,
        "items": (
            _export_fields.item_requests,
            lambda input_dict, _, inst: [
                {
                    "id": {"name": k, "quality": "normal"},
                    "items": {
                        "in_inventory": [
                            # TODO: this is actually very hard to do properly
                            # Modules for example should be split up between
                            # multiple stacks, but fuel requests for locos
                            # shouldn't; how to discern?
                            # Should also check to see how Factorio itself
                            # migrates it, if at all
                            {
                                # "Default" inventory; works for most cases
                                "inventory": 1,
                                "stack": 0,
                                "count": v,
                            }
                        ]
                    },
                }
                for k, v in input_dict.items()
            ],
        ),
        "tags": fields.tags.name,
    },
    lambda fields, converter: {
        "name": fields.name.name,
        "position": _export_fields.global_position,
        "mirror": None,
        "quality": None,
        "items": (
            _export_fields.item_requests,
            lambda inst: {
                item_request.id.name: sum(
                    loc.count for loc in item_request.items.in_inventory
                )
                for item_request in inst.item_requests
                # Skip non-normal item requests since they are unresolvable pre 2.0
                if item_request.id.quality == "normal"
            },
        ),
        "tags": fields.tags.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Entity,
    lambda fields: {
        "entity_number": fields._entity_number.name,
        "name": fields.name.name,
        "position": fields.position.name,
        "mirror": fields.mirror.name,
        "quality": fields.quality.name,
        "items": fields.item_requests.name,
        "tags": fields.tags.name,
    },
    lambda fields, converter: {
        "name": fields.name.name,
        "position": _export_fields.global_position,
        "mirror": fields.mirror.name,
        "quality": fields.quality.name,
        "items": fields.item_requests.name,
        "tags": fields.tags.name,
    },
)
