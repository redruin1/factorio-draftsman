# entity.py

from draftsman import __factorio_version_info__
from draftsman.classes.association import Association
from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.exportable import (
    Exportable,
)
from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.data import entities
from draftsman.error import DataFormatError
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    QualityID,
    EntityID,
    get_suggestion,
    uint64,
)
from draftsman.utils import aabb_to_dimensions, get_first, passes_surface_conditions
from draftsman.validators import and_, conditional, instance_of, one_of
from draftsman.warning import GridAlignmentWarning, UnknownEntityWarning

from draftsman.data.planets import get_surface_properties

import attrs
import copy
import math
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
    deduce and convert instances of this base type to subtypes, if there is
    sufficient context to do so.
    """

    def __attrs_pre_init__(self):
        super(EntityLike).__init__()

    def __init__(
        self,
        name: str,
        id: str | None = None,
        quality: QualityID = "normal",
        position: _PosVector = attrs.NOTHING,
        tile_position: _TileVector = attrs.NOTHING,
        tags: dict[str, Any] | None = attrs.NOTHING,
        entity_number: uint64 | None = None,
        *,
        validate_assignment: Any = ValidationMode.STRICT,
        extra_keys: dict[Any, Any] | None = None,
        **kwargs
    ):
        self.__attrs_init__(
            name,
            id=id,
            quality=quality,
            position=position,
            tile_position=tile_position,
            tags=tags,
            entity_number=entity_number,
            validate_assignment=validate_assignment,
            extra_keys=extra_keys,
        )
        if self.extra_keys:
            self.extra_keys.update(kwargs)
        elif kwargs:
            self.extra_keys = kwargs

    def __attrs_post_init__(self):
        self._set_tile_position(None, self.tile_position)

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

    # TODO: maybe it should be impossible to change the name of the entity after
    # it is created. This would prevent the complications that would arise from
    # such flexibility
    name: EntityID = attrs.field(
        validator=instance_of(str),
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

    # TODO: this should be moved into EntityLike since that makes more sense
    def _set_id(self, _: attrs.Attribute, value: Optional[str]):
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
    def _ensure_id_correct_type(self, _: attrs.Attribute, value: Any, **kwargs):
        if value is not None and not isinstance(value, str):
            raise TypeError("'id' must be either a str or None")

    # =========================================================================

    quality: QualityID = attrs.field(
        default="normal",
        validator=one_of(QualityID),
    )
    """
    The quality of this entity. Can modify certain other attributes of the
    entity in (usually) positive ways.
    """

    # =========================================================================

    def _set_position(self, _: attrs.Attribute, value: Any):
        self.position.update_from_other(value, float)
        self.tile_position.update(
            round(self.position.x - self.tile_width / 2),
            round(self.position.y - self.tile_height / 2),
        )

        if self.validate_assignment and self.double_grid_aligned:
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

        return self.position

    position: _PosVector = attrs.field(
        converter=Vector.from_other, on_setattr=_set_position, metadata={"omit": False}
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

    @position.default
    def get_default_position(self):
        """
        Populate the internal _PosVector with a reference to the instantiated
        entity.
        """
        return _PosVector(self.tile_width / 2, self.tile_height / 2, self)

    # =========================================================================

    def _set_tile_position(self, attr, value):
        self.tile_position.update_from_other(value, int)
        self.position.update(
            self.tile_position.x + self.tile_width / 2,
            self.tile_position.y + self.tile_height / 2,
        )

        if self.validate_assignment and self.double_grid_aligned:
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

        return self.tile_position

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
            self.position.x - self.tile_width / 2,
            self.position.y - self.tile_height / 2,
            self,
        )

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
        return entities.collision_sets.get(self.name, None)

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

    @property  # Cache?
    def tile_width(self) -> int:
        if "tile_width" in self.prototype:
            return self.prototype["tile_width"]
        else:
            return aabb_to_dimensions(
                self.static_collision_set.get_bounding_box()
                if self.static_collision_set
                else None
            )[0]

    # =========================================================================

    @property  # Cache?
    def tile_height(self) -> int:
        if "tile_height" in self.prototype:
            return self.prototype["tile_height"]
        else:
            return aabb_to_dimensions(
                self.static_collision_set.get_bounding_box()
                if self.static_collision_set
                else None
            )[1]

    # =========================================================================

    @property
    def static_tile_width(self) -> int:
        """
        The width of the entity irrespective of it's current orientation.
        Equivalent to the :py:attr:`.tile_width` when the entity is facing north.
        """
        return Entity.tile_width.fget(self)

    # =========================================================================

    @property
    def static_tile_height(self) -> int:
        """
        The height of the entity irrespective of it's current orientation.
        Equivalent to the :py:attr:`.tile_width` when the entity is facing north.
        """
        return Entity.tile_height.fget(self)

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

    mirror: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this blueprint is mirrored horizontally or vertically, 
    specifically in regards to it's fluid inputs/outputs.
    """

    # =========================================================================

    # TODO: which of these do I want? Need to investigate what happens when you
    # give the game a blueprint with two entities with the same entity_number...
    _entity_number: Optional[uint64] = attrs.field(
        default=None,
        repr=False,
        eq=False,
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

    def is_placable_on(self, surface_name: str) -> bool:
        """
        Check to see if this entity is placable on a particular planet/surface.
        `surface_name` must be the name of a registered surface in `data.planets`.
        If the `surface_properties` of this entity are unknown, then this
        function always returns `True`.
        """
        surface_properties = get_surface_properties(surface_name)
        return passes_surface_conditions(self.surface_conditions, surface_properties)

    def to_dict(
        self,
        version=__factorio_version_info__,
        exclude_none=True,
        exclude_defaults=True,
        entity_number: Optional[int] = None,
    ):
        res = {}
        if entity_number is not None:
            res["entity_number"] = entity_number
        res.update(super().to_dict(version, exclude_none, exclude_defaults))
        return res

    def mergable_with(self, other: "Entity") -> bool:
        return (
            type(self) == type(other)
            and self.name == other.name
            and self.global_position == other.global_position
            and self.id == other.id
        )

    def merge(self, other: "Entity"):
        # Tags (overwrite self with other)
        self.tags = other.tags

    def __hash__(self) -> int:
        return id(self) >> 4  # Apparently this is the default?

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


_export_fields = attrs.fields(_ExportEntity)


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Entity,
    lambda fields: {
        "name": fields.name.name,
        "position": fields.position.name,
        None: fields.quality.name,
        "tags": fields.tags.name,
        "entity_number": fields._entity_number.name,
    },
    lambda fields, converter: {
        "name": fields.name.name,
        "position": _export_fields.global_position,
        "quality": None,
        "tags": fields.tags.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Entity,
    lambda fields: {
        "name": fields.name.name,
        "position": fields.position.name,
        "quality": fields.quality.name,
        "mirror": fields.mirror.name,
        "tags": fields.tags.name,
        "entity_number": fields._entity_number.name,
    },
    lambda fields, converter: {
        "name": fields.name.name,
        "position": _export_fields.global_position,
        "quality": fields.quality.name,
        "mirror": fields.mirror.name,
        "tags": fields.tags.name,
    },
)
