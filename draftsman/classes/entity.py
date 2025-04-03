# entity.py

from draftsman.classes.association import Association
from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.exportable import (
    Exportable,
    ValidationResult,
    attempt_and_reissue,
)
from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.data import entities
from draftsman.error import DraftsmanError, DataFormatError
from draftsman.serialization import MASTER_CONVERTER, draftsman_converters
from draftsman.signatures import (
    DraftsmanBaseModel,
    FloatPosition,
    IntPosition,
    get_suggestion,
    uint64,
)
from draftsman.warning import UnknownEntityWarning
from draftsman import utils, __factorio_version_info__

from draftsman.data.planets import get_surface_properties

from abc import ABCMeta, abstractmethod
import attrs
import cattrs
import copy
import math
from pydantic import (
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
    field_serializer,
    PrivateAttr,
)
from typing import Any, Literal, Optional, Union
import warnings
import weakref


class _PosVector(Vector):
    def __init__(self, x, y, entity):
        super().__init__(x, y)
        self.entity = weakref.ref(entity)

    @Vector.x.setter
    def x(self, value):
        self._data[0] = float(value)
        self.entity()._root._tile_position._data[0] = round(
            value - self.entity().tile_width / 2
        )

    @Vector.y.setter
    def y(self, value):
        self._data[1] = float(value)
        self.entity()._root._tile_position._data[1] = round(
            value - self.entity().tile_height / 2
        )

    # @classmethod
    # def __get_pydantic_core_schema__(
    #     cls, _source_type: Any, handler: GetCoreSchemaHandler
    # ) -> CoreSchema:
    #     return core_schema.no_info_after_validator_function(
    #         cls, handler(FloatPosition)
    #     )  # TODO: correct annotation


class _TileVector(Vector):
    def __init__(self, x, y, entity):
        super().__init__(x, y)
        self.entity = weakref.ref(entity)

    @Vector.x.setter
    def x(self, value):
        self._data[0] = int(value)
        self.entity()._root._position._data[0] = value + self.entity().tile_width / 2

    @Vector.y.setter
    def y(self, value):
        self._data[1] = int(value)
        self.entity()._root._position._data[1] = value + self.entity().tile_height / 2


@attrs.define
class Entity(Exportable, EntityLike, metaclass=ABCMeta):
    """
    Entity base-class. Used for all entity types that are specified in Factorio.
    Categorizes entities into "types" based on their class, each of which is
    implemented in :py:mod:`draftsman.prototypes`.
    """

    @property
    @abstractmethod
    def similar_entities(self) -> list[str]:
        """
        Returns a list of strings representing the names of entities that share
        the same type.
        """
        return []

    class Format(DraftsmanBaseModel):
        """
        The overarching format of this Entity. TODO more

        .. NOTE::
            This is the schema for the Factorio format of the data, not the
            internal format of each entity, which varies in a number of ways.
        """

        # Private attributes, managed internally by Draftsman
        _entity: weakref.ReferenceType["Entity"] = PrivateAttr()
        _position: Vector = PrivateAttr()
        _tile_position: Vector = PrivateAttr()

        # Exported fields
        name: str = Field(
            ...,
            description="""
            The internal ID of the entity.
            """,
        )
        quality: Literal[
            "normal", "uncommon", "rare", "epic", "legendary"
        ] = Field(  # TODO: determine these automatically
            "normal",
            description="""
            The quality of the entity. Defaults to 'normal' when not specified,
            or when quality is not present in the save being imported to /
            exported from.
            """,
        )
        position: FloatPosition = Field(
            ...,
            description="""
            The position of the entity, almost always measured from it's center. 
            Uses Factorio tiles as its unit.
            """,
        )
        entity_number: uint64 = Field(
            ...,
            exclude=True,
            description="""
            The number of the entity in it's parent blueprint, 1-based. In
            practice this is the index of the dictionary in the blueprint's 
            'entities' list, but this is not enforced.
            """,
        )
        tags: Optional[dict[str, Any]] = Field(
            {},
            description="""
            Any other additional metadata associated with this blueprint entity. 
            Frequently used by mods.
            """,
        )

        @field_validator("name")
        @classmethod
        def check_unknown_name(cls, value: str, info: ValidationInfo):
            """
            Warn if the name is not any known Draftsman entity name, either for
            this specific entity class or any entity at all.
            """
            if not info.context:
                return value
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            warning_list: list = info.context["warning_list"]
            entity: Entity = info.context["object"]

            # Similar entities exists on all entities EXCEPT generic `Entity`
            # instances, for which we're trying to ignore validation on
            # if entity.similar_entities is None:
            #     return value

            if (
                entity.similar_entities is not None
                and value not in entity.similar_entities
            ):
                warning_list.append(
                    UnknownEntityWarning(
                        "'{}' is not a known name for a {}{}".format(
                            value,
                            type(entity).__name__,
                            get_suggestion(value, entity.similar_entities, n=1),
                        )
                    )
                )
            elif value not in entities.raw:
                warning_list.append(
                    UnknownEntityWarning(
                        "Unknown entity '{}'{}".format(
                            value, get_suggestion(value, entities.raw.keys(), n=1)
                        )
                    )
                )

            return value

        @field_serializer("position")
        def serialize_position(self, _):
            return self._entity().global_position.to_dict()

        model_config = ConfigDict(title="Entity", revalidate_instances="always")

    # =========================================================================

    # def __init__(
    #     self,
    #     name: Optional[str],
    #     similar_entities: list[str],
    #     quality: Optional[str] = "normal",
    #     tile_position: IntPosition = (0, 0),
    #     id: str = None,
    #     validate: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     Constructs a new Entity. All prototypes have this entity as their most
    #     Parent class.

    #     Raises :py:class:`draftsman.warning.DraftsmanWarning` for every unused
    #     keyword passed into the constructor.

    #     :param name: The name of the entity. Must be one of ``similar_entities``.
    #         Can be ``None`` if and only if the parent entity type has no valid
    #         entities under a particular configuration, in which case the entity
    #         is unable to be created.
    #     :param similar_entities: A list of valid names associated with this
    #         Entity class. Can be though of as a list of all the entities of this
    #         type.
    #     :param tile_position: The tile position to set the entity to. Defaults
    #         to the origin.
    #     :param kwargs: Any other valid parameters to set.

    #     :exception InvalidEntityError: If ``name`` is set to anything other than
    #         an entry in ``similar_entities``.
    #     """
    #     # If name is None, then the user didn't provide a name and a default was
    #     # unobtainable; error
    #     # (This should only occur when the Factorio version is backported to
    #     # the point where certain entity types did not exist (e.g. LinkedBelt))
    #     if name is None:  # pragma: no coverage
    #         raise DataFormatError(
    #             "Unable to create a default entity; the current environment has no entitites of type '{}'".format(
    #                 self.__class__.__name__
    #             )
    #         )

    #     # Init Exportable
    #     Exportable.__init__(self)
    #     # Init EntityLike
    #     EntityLike.__init__(self)

    #     # We don't this to be active when constructing, so we it to NONE now and
    #     # to whatever it should be later in the child-most subclass
    #     self.validate_assignment = ValidationMode.NONE

    #     # If 'None' was passed to position, treat that as the same as omission
    #     # We do this because we want to be able to annotate `position` in each
    #     # entity's __init__ signature and indicate that it's optional
    #     if "position" in kwargs and kwargs["position"] is None:
    #         kwargs.pop("position")

    #     # self._root = self.Format.model_construct(
    #     #     # If these two are omitted, included dummy values so that validation
    #     #     # doesn't complain (since they're required fields)
    #     #     # position={"x": 0, "y": 0},
    #     #     # entity_number=0,
    #     #     # Add all remaining extra keywords; all recognized keywords will be
    #     #     # accessed individually, but this allows us to catch the extra ones
    #     #     # and issue warnings for them
    #     #     **{"position": {"x": 0, "y": 0}, "entity_number": 0, **kwargs}
    #     # )
    #     self._root = type(self).Format.model_validate(
    #         {
    #             "name": name,
    #             "quality": quality,
    #             "position": {"x": 0, "y": 0},
    #             "entity_number": 0,
    #             **kwargs,
    #         },
    #         strict=False,
    #         context={"construction": True, "mode": ValidationMode.NONE},
    #     )

    #     # Private attributes
    #     self._root._entity = weakref.ref(self)
    #     self._root._position = _PosVector(0, 0, self)
    #     self._root._tile_position = _TileVector(0, 0, self)

    #     # TODO: make `parent` private property to discourage manual modification
    #     # TODO: `similar_entities` property(?) to reduce memory
    #     # TODO: `tile_width/height` calculated to reduce memory?

    #     # Entities of the same type
    #     self.similar_entities = similar_entities

    #     # Name
    #     self.name = name

    #     # Quality
    #     self.quality = quality

    #     # ID (used in Blueprints and Groups)
    #     self.id = id

    #     # Tile Width and Height (Internal)
    #     # Usually tile dimensions are implicitly based on the collision box
    #     # When not, they're overwritten later on in a particular subclass
    #     self._tile_width, self._tile_height = utils.aabb_to_dimensions(
    #         self.static_collision_set.get_bounding_box()
    #         if self.static_collision_set
    #         else None
    #     )
    #     # But sometimes it can be overrided in special cases (rails)
    #     if "tile_width" in entities.raw.get(self.name, {}):
    #         self._tile_width = entities.raw[self.name]["tile_width"]
    #     if "tile_height" in entities.raw.get(self.name, {}):
    #         self._tile_height = entities.raw[self.name]["tile_height"]
    #     # And in some other cases are manually overriden later in subclasses

    #     # Position and Tile position
    #     # If "position" was set, use that over "tile_position"
    #     # If not, use the default "tile_position" if necessary
    #     if "position" in kwargs:
    #         self.position = kwargs["position"]
    #     else:
    #         self.tile_position = tile_position

    #     # Entity tags
    #     self.tags = kwargs.get("tags", {})

    def __attrs_post_init__(self):
        self._set_tile_position(None, self.tile_position)

    # =========================================================================

    name: str = attrs.field(
        validator=attrs.validators.instance_of(str), metadata={"omit": False}
    )
    """The name of the entity."""

    @name.default
    def get_default_entity(self):
        return utils.get_first(self.similar_entities)

    @name.validator
    def ensure_name_recognized(self, attribute, value):
        if self.validation:
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

    # @property
    # def name(self) -> str:
    #     """
    #     The name of the entity. Must be a valid Factorio ID string. Read only.
    #     """
    #     return self._root.name

    # @name.setter
    # def name(self, value: str):
    #     if self.parent:
    #         # TODO: eventually remove
    #         raise DraftsmanError(
    #             "Cannot change name of entity while in another collection"
    #         )

    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "name", value
    #         )
    #         self._root.name = result
    #     else:
    #         self._root.name = value

    #     # Unfortunately, we need to recalculate a bunch of stuff when we do this
    #     # More scarily, the amount we have to do might be dynamic
    #     # TODO: clean this up
    #     self._tile_width, self._tile_height = utils.aabb_to_dimensions(
    #         self.collision_set.get_bounding_box() if self.collision_set else None
    #     )
    #     # But sometimes it can be overrided in special cases (rails)
    #     if "tile_width" in entities.raw.get(self.name, {}):
    #         self._tile_width = entities.raw[self.name]["tile_width"]
    #     if "tile_height" in entities.raw.get(self.name, {}):
    #         self._tile_height = entities.raw[self.name]["tile_height"]

    #     # Update position
    #     self.tile_position = self.tile_position

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
        return entities.raw.get(self.name, {"type": None})["type"]

    # =========================================================================

    def _set_id(self, attribute: attrs.Attribute, value: Optional[str]):
        if self.parent:
            if value is None:
                self.parent.entities._remove_key(self.id)
            else:
                old_id = self.id
                self.parent.entities._remove_key(old_id)
                self.parent.entities._set_key(self.id, self)
        self.id = value

    id: Optional[str] = attrs.field(
        default=None, on_setattr=_set_id, metadata={"omit": True, "location": None}
    )
    """
    A unique string ID associated with this entity. ID's can be anything,
    though there can only be one entity with a particular ID in an
    EntityCollection. Not exported.
    """

    @id.validator
    def ensure_id_correct_type(self, attribute: attrs.Attribute, value: Any):
        if value is not None and not isinstance(value, str):
            raise ValueError("TODO")

    # @property
    # def id(self) -> Optional[str]:
    #     """
    #     A unique string ID associated with this entity. ID's can be anything,
    #     though there can only be one entity with a particular ID in an
    #     EntityCollection. Not exported.

    #     :getter: Gets the ID of the entity, or ``None`` if the entity has no ID.
    #     :setter: Sets the ID of the entity.

    #     :exception TypeError: If the set value is anything other than a ``str``
    #         or ``None``.
    #     :exception DuplicateIDError: If the ID is changed while inside an
    #         ``EntityCollection`` to an ID that is already taken by another
    #         entity in said ``EntityCollection``.
    #     """
    #     return self._id

    # @id.setter
    # def id(self, value: str):
    #     # TODO: I think we can use pydantic to validate this...
    #     if value is None:
    #         if self.parent:
    #             self.parent.entities._remove_key(self._id)
    #         self._id = value
    #     elif isinstance(value, str):
    #         if self.parent:
    #             # try:
    #             old_id = self._id
    #             self.parent.entities._remove_key(old_id)
    #             # except AttributeError:
    #             #     pass
    #             self._id = value
    #             self.parent.entities._set_key(self._id, self)
    #         else:
    #             self._id = value
    #     else:
    #         raise TypeError("'id' must be a str or None")

    # =========================================================================

    quality: Literal["normal", "uncommon", "rare", "epic", "legendary"] = attrs.field(
        default="normal", validator=attrs.validators.instance_of(str)
    )  # TODO: literal validator
    """
    The quality of this entity. Can modify certain other attributes of the
    entity in (usually) positive ways.
    """

    # @property
    # def quality(self) -> str:  # TODO: literals
    #     """
    #     The quality of this entity. Can modify certain other attributes of the
    #     entity in (usually) positive ways.
    #     """
    #     return self._root.quality

    # @quality.setter
    # def quality(self, value: str) -> None:  # TODO: literals
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "quality", value
    #         )
    #         self._root.quality = result
    #     else:
    #         self._root.quality = value

    # =========================================================================

    def _set_position(self, _: attrs.Attribute, value: Any):
        self.position.update_from_other(value, float)
        self.tile_position.update(
            round(self.position.x - self.tile_width / 2),
            round(self.position.y - self.tile_height / 2),
        )

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

    # @property
    # def position(self) -> Vector:
    #     """
    #     The "canonical" position of the Entity, or the one that Factorio uses.
    #     Positions of most entities are located at their center, which can either
    #     be in the middle of a tile or on it's transition, depending on the
    #     Entity's ``tile_width`` and ``tile_height``.

    #     ``position`` can be specified as a ``dict`` with ``"x"`` and ``"y"``
    #     keys, or more succinctly as a sequence of floats, usually a ``list`` or
    #     ``tuple``. ``position`` can also be specified more verbosely as a
    #     ``Vector`` instance as well.

    #     This property is updated in tandem with ``tile_position``, so using them
    #     both interchangeably is both allowed and encouraged.

    #     :getter: Gets the position of the Entity.
    #     :setter: Sets the position of the Entity.

    #     :exception IndexError: If the set value does not match the above
    #         specification.
    #     :exception DraftsmanError: If the entities position is modified when
    #         inside a EntityCollection, :ref:`which is forbidden.
    #         <handbook.blueprints.forbidden_entity_attributes>`
    #     """
    #     return self._root._position

    # @position.setter
    # def position(self, value: Vector):
    #     # TODO: relax
    #     if self.parent:
    #         raise DraftsmanError(
    #             "Cannot change position of entity while it's inside another object"
    #         )

    #     # self._position = Vector.from_other(value, float)
    #     self._root._position.update_from_other(value, float)
    #     self._root._tile_position.update(
    #         round(self._root._position.x - self.tile_width / 2),
    #         round(self._root._position.y - self.tile_height / 2),
    #     )

    # =========================================================================

    def _set_tile_position(self, attr, value):
        self.tile_position.update_from_other(value, int)
        self.position.update(
            self.tile_position.x + self.tile_width / 2,
            self.tile_position.y + self.tile_height / 2,
        )
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

    # @property
    # def tile_position(self) -> Vector:
    #     """
    #     The tile-position of the Entity. The tile position is the position
    #     according the the LuaSurface tile grid, and is the top left corner of
    #     the top-leftmost tile of the Entity.

    #     ``tile_position`` can be specified as a ``dict`` with ``"x"`` and
    #     ``"y"`` keys, or more succinctly as a sequence of floats, usually a
    #     ``list`` or ``tuple``.

    #     This property is updated in tandem with ``position``, so using them both
    #     interchangeably is both allowed and encouraged.

    #     :getter: Gets the tile position of the Entity.
    #     :setter: Sets the tile position of the Entity.

    #     :exception IndexError: If the set value does not match the above
    #         specification.
    #     :exception DraftsmanError: If the entities position is modified when
    #         inside a EntityCollection, :ref:`which is forbidden.
    #         <handbook.blueprints.forbidden_entity_attributes>`
    #     """
    #     return self._root._tile_position

    # @tile_position.setter
    # def tile_position(self, value: Vector):
    #     # TODO: re-evaluate
    #     # if self.parent:
    #     #     raise DraftsmanError(
    #     #         "Cannot change position of entity while it's inside another object"
    #     #     )

    #     # self._tile_position.update_from_other(value, int)
    #     self._root._tile_position.update_from_other(value, int)
    #     self._root._position.update(
    #         self._root._tile_position.x + self.tile_width / 2,
    #         self._root._tile_position.y + self.tile_height / 2,
    #     )

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
        if self.parent and hasattr(self.parent, "global_position"):
            return self.parent.global_position + self.position
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
        return entities.raw.get(self.name, {"collision_mask": None})["collision_mask"]

    # =========================================================================

    @property
    def tile_width(self) -> int:
        if "tile_width" in entities.raw.get(self.name, {}):
            return entities.raw[self.name]["tile_width"]
        else:
            return utils.aabb_to_dimensions(
                self.static_collision_set.get_bounding_box()
                if self.static_collision_set
                else None
            )[0]

    # =========================================================================

    @property  # Cache?
    def tile_height(self) -> int:
        if "tile_height" in entities.raw.get(self.name, {}):
            return entities.raw[self.name]["tile_height"]
        else:
            return utils.aabb_to_dimensions(
                self.static_collision_set.get_bounding_box()
                if self.static_collision_set
                else None
            )[1]

    # =========================================================================

    @property
    def flags(self) -> Optional[list[str]]:
        """
        A set of string flags which indicate a number of behaviors of this
        prototype. Not exported; read only.

        .. seealso::

            `<https://wiki.factorio.com/Types/EntityPrototypeFlags>`_
        """
        return entities.raw.get(self.name, {"flags": None}).get("flags", [])

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

    tags: Optional[dict[str, Any]] = attrs.field(factory=dict)
    """
    Tags associated with this Entity. Commonly used by mods to add custom
    data to a particular Entity when exporting and importing Blueprint
    strings.

    :getter: Gets the tags of the Entity, or ``None`` if not set.
    :setter: Sets the Entity's tags.

    :exception TypeError: If tags is set to anything other than a ``dict``
        or ``None``.
    """

    @tags.validator
    def ensure_tags_correct_type(self, attribute: attrs.Attribute, value: Any):
        if value is not None and not isinstance(value, dict):
            raise ValueError("Explode")  # TODO

    # @property
    # def tags(self) -> Optional[dict[str, Any]]:
    #     """
    #     Tags associated with this Entity. Commonly used by mods to add custom
    #     data to a particular Entity when exporting and importing Blueprint
    #     strings.

    #     :getter: Gets the tags of the Entity, or ``None`` if not set.
    #     :setter: Sets the Entity's tags.

    #     :exception TypeError: If tags is set to anything other than a ``dict``
    #         or ``None``.
    #     """
    #     return self._root.tags

    # @tags.setter
    # def tags(self, value: Optional[dict[str, Any]]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "tags", value
    #         )
    #         self._root.tags = result
    #     else:
    #         self._root.tags = value

    # =========================================================================

    def is_placable_on(self, surface_name: str) -> bool:
        """
        Check to see if this entity is placable on a particular planet/surface.
        `surface_name` must be the name of a registered surface in `data.planets`.
        If the `surface_properties` of this entity are unknown, then this
        function always returns `True`.
        """
        surface_properties = get_surface_properties(surface_name)
        return utils.passes_surface_conditions(
            self.surface_conditions, surface_properties
        )

    # def validate(
    #     self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    # ) -> ValidationResult:
    #     mode = ValidationMode(mode)

    #     output = ValidationResult([], [])

    #     if mode is ValidationMode.NONE and not force:  # (self.is_valid and not force):
    #         return output

    #     context = {
    #         "mode": mode,
    #         "object": self,
    #         "warning_list": [],
    #         "assignment": False,
    #         "environment_version": __factorio_version_info__,
    #     }

    #     try:
    #         result = self.Format.model_validate(
    #             self._root,
    #             strict=False,  # TODO: ideally this should be strict
    #             context=context,
    #         )
    #         # Reassign private attributes
    #         result._entity = weakref.ref(self)
    #         result._position = self._root._position
    #         result._tile_position = self._root._tile_position
    #         # Scuffed AF
    #         if hasattr(self._root, "direction"):
    #             result.direction = self._root.direction
    #         if hasattr(self._root, "orientation"):
    #             result.orientation = self._root.orientation
    #         # Acquire the newly converted data
    #         self._root = result
    #     except ValidationError as e:
    #         output.error_list.append(DataFormatError(e))

    #     output.warning_list += context["warning_list"]

    #     return output

    def mergable_with(self, other: "Entity") -> bool:
        return (
            type(self) == type(other)
            and self.name == other.name
            and self.global_position == other.global_position
            and self.id == other.id
        )

    def merge(self, other: "Entity"):
        # Tags (overwrite self with other)
        # (Make sure to make a copy in case the original data gets deleted)
        self.tags = copy.deepcopy(other.tags)

    # def __eq__(self, other: "Entity") -> bool:
    #     return (
    #         type(self) == type(other)
    #         and self.name == other.name
    #         and self.global_position == other.global_position
    #         and self.id == other.id
    #         and self.tags == other.tags
    #     )

    # def __hash__(self) -> int:
    #     return id(self) >> 4  # Apparently this is the default?

    def __repr__(self) -> str:  # pragma: no coverage
        # return "<{0}{1}>{2}".format(
        #     type(self).__name__,
        #     " '{}'".format(self.id) if self.id is not None else "",
        #     str(self.to_dict()),
        # )
        # Association debug printing:
        return "<{0}{1} at 0x{2:016X}>{3}".format(
            type(self).__name__,
            " '{}'".format(self.id) if self.id is not None else "",
            id(self),
            str(self.to_dict()),
        )

    # def __deepcopy__(self, memo) -> "Entity":
    #     # Perform the normal deepcopy
    #     result = super().__deepcopy__(memo=memo)
    #     # This is very cursed
    #     # We need a reference to the parent entity stored in `_root` so that we
    #     # can properly serialize it's position
    #     # If we use a regular reference, it copies properly, but then it creates
    #     # a circular reference which makes garbage collection worse
    #     # We use a weakref to mitigate this memory issue (and ensure that
    #     # deleting an entity immediately destroys it), but means that we have to
    #     # manually update it's reference here
    #     result._root._entity = weakref.ref(result)
    #     # Get me out of here
    #     return result


# draftsman_converters[(1, 0)].register_unstructure_hook(
#     Entity,
#     cattrs.gen.make_dict_unstructure_fn(
#         Entity,
#         draftsman_converters[(1, 0)],
#         _cattrs_omit_if_default=True,
#         name=cattrs.gen.override(omit_if_default=False),
#         position=cattrs.gen.override(omit_if_default=False),
#         id=cattrs.gen.override(omit=True)
#     )
# )
# draftsman_converters[(2, 0)].register_unstructure_hook(
#     Entity,
#     cattrs.gen.make_dict_unstructure_fn(
#         Entity,
#         draftsman_converters[(2, 0)],
#         _cattrs_omit_if_default=True,
#         name=cattrs.gen.override(omit_if_default=False),
#         position=cattrs.gen.override(omit_if_default=False),
#         id=cattrs.gen.override(omit=True)
#     )
# )
