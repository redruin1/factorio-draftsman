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
from draftsman.signatures import (
    DraftsmanBaseModel,
    FloatPosition,
    IntPosition,
    get_suggestion,
    uint64,
)
from draftsman.warning import UnknownEntityWarning
from draftsman import utils

import copy
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


class Entity(Exportable, EntityLike):
    """
    Entity base-class. Used for all entity types that are specified in Factorio.
    Categorizes entities into "types" based on their class, each of which is
    implemented in :py:mod:`draftsman.prototypes`.
    """

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
        position: FloatPosition = Field(
            ...,
            description="""
            The position of the entity, almost always measured from it's center. 
            Measured in Factorio tiles.
            """,
        )
        entity_number: uint64 = Field(
            ...,
            exclude=True,
            description="""
            The number of the entity in it's parent blueprint, 1-based. In
            practice this is the index of the dictionary in the blueprint's 
            'entities' list, but this is not enforced.

            NOTE: The range of this number is described as a 64-bit unsigned int,
            but due to limitations with Factorio's PropertyTree implementation,
            values above 2^53 will suffer from floating-point precision error.
            See here: https://forums.factorio.com/viewtopic.php?p=592165#p592165
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
            Warn if the name is not any known Draftsman entity name. Only called
            when the entity is an instance of the base class :py:cls:`Entity`.
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

    def __init__(
        self,
        name: Optional[str],
        similar_entities: list[str],
        tile_position: IntPosition = (0, 0),
        id: str = None,
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        Constructs a new Entity. All prototypes have this entity as their most
        Parent class.

        Raises :py:class:`draftsman.warning.DraftsmanWarning` for every unused
        keyword passed into the constructor.

        :param name: The name of the entity. Must be one of ``similar_entities``.
            Can be ``None`` if and only if the parent entity type has no valid
            entities under a particular configuration, in which case the entity
            is unable to be created.
        :param similar_entities: A list of valid names associated with this
            Entity class. Can be though of as a list of all the entities of this
            type.
        :param tile_position: The tile position to set the entity to. Defaults
            to the origin.
        :param kwargs: Any other valid parameters to set.

        :exception InvalidEntityError: If ``name`` is set to anything other than
            an entry in ``similar_entities``.
        """
        # If name is None, then the user didn't provide a name and a default was
        # unobtainable; error
        # (This should only occur when the Factorio version is backported to 
        # the point where certain entity types did not exist (e.g. LinkedBelt))
        if name is None:  # pragma: no coverage
            raise DataFormatError(
                "Unable to create a default entity; 'similar_entities' is an empty list"
            )

        # Init Exportable
        Exportable.__init__(self)
        # Init EntityLike
        EntityLike.__init__(self)

        # We don't this to be active when constructing, so we it to NONE now and
        # to whatever it should be later in the child-most subclass
        self.validate_assignment = ValidationMode.NONE

        # If 'None' was passed to position, treat that as the same as omission
        # We do this because we want to be able to annotate `position` in each
        # entity's __init__ signature and indicate that it's optional
        if "position" in kwargs and kwargs["position"] is None:
            kwargs.pop("position")

        # self._root = self.Format.model_construct(
        #     # If these two are omitted, included dummy values so that validation
        #     # doesn't complain (since they're required fields)
        #     # position={"x": 0, "y": 0},
        #     # entity_number=0,
        #     # Add all remaining extra keywords; all recognized keywords will be
        #     # accessed individually, but this allows us to catch the extra ones
        #     # and issue warnings for them
        #     **{"position": {"x": 0, "y": 0}, "entity_number": 0, **kwargs}
        # )
        self._root = type(self).Format.model_validate(
            {"name": name, "position": {"x": 0, "y": 0}, "entity_number": 0, **kwargs},
            strict=False,
            context={"construction": True, "mode": ValidationMode.NONE},
        )

        # Private attributes
        self._root._entity = weakref.ref(self)
        self._root._position = _PosVector(0, 0, self)
        self._root._tile_position = _TileVector(0, 0, self)

        # TODO: make `parent` private property to discourage manual modification
        # TODO: `similar_entities` property(?) to reduce memory
        # TODO: `tile_width/height` calculated to reduce memory?

        # Entities of the same type
        self.similar_entities = similar_entities

        # Name
        self.name = name

        # ID (used in Blueprints and Groups)
        self.id = id

        # Tile Width and Height (Internal)
        # Usually tile dimensions are implicitly based on the collision box
        # When not, they're overwritten later on in a particular subclass
        self._tile_width, self._tile_height = utils.aabb_to_dimensions(
            self.static_collision_set.get_bounding_box()
            if self.static_collision_set
            else None
        )
        # But sometimes it can be overrided in special cases (rails)
        if "tile_width" in entities.raw.get(self.name, {}):
            self._tile_width = entities.raw[self.name]["tile_width"]
        if "tile_height" in entities.raw.get(self.name, {}):
            self._tile_height = entities.raw[self.name]["tile_height"]
        # And in some other cases are manually overriden later in subclasses

        # Position and Tile position
        # If "position" was set, use that over "tile_position"
        # If not, use the default "tile_position" if necessary
        if "position" in kwargs:
            self.position = kwargs["position"]
        else:
            self.tile_position = tile_position

        # Entity tags
        self.tags = kwargs.get("tags", {})

    # =========================================================================

    @property
    def name(self) -> str:
        """
        The name of the entity. Must be a valid Factorio ID string. Read only.

        TODO: How to make this changable, or alert the user of it's danger?

        :type: ``str``
        """
        return self._root.name

    @name.setter
    def name(self, value: str):
        if self.parent:
            # TODO: eventually remove
            raise DraftsmanError(
                "Cannot change name of entity while in another collection"
            )

        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "name", value
            )
            self._root.name = result
        else:
            self._root.name = value

        # Unfortunately, we need to recalculate a bunch of stuff when we do this
        # More scarily, the amount we have to do might be dynamic
        # TODO: clean this up
        self._tile_width, self._tile_height = utils.aabb_to_dimensions(
            self.collision_set.get_bounding_box() if self.collision_set else None
        )
        # But sometimes it can be overrided in special cases (rails)
        if "tile_width" in entities.raw.get(self.name, {}):
            self._tile_width = entities.raw[self.name]["tile_width"]
        if "tile_height" in entities.raw.get(self.name, {}):
            self._tile_height = entities.raw[self.name]["tile_height"]

        # Update position
        self.tile_position = self.tile_position

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

        :type: ``str``
        """
        return entities.raw.get(self.name, {"type": None})["type"]

    # =========================================================================

    @property
    def id(self) -> Optional[str]:
        """
        A unique string ID associated with this entity. ID's can be anything,
        though there can only be one entity with a particular ID in an
        EntityCollection. Not exported.

        :getter: Gets the ID of the entity, or ``None`` if the entity has no ID.
        :setter: Sets the ID of the entity.
        :type: ``str``

        :exception TypeError: If the set value is anything other than a ``str``
            or ``None``.
        :exception DuplicateIDError: If the ID is changed while inside an
            ``EntityCollection`` to an ID that is already taken by another
            entity in said ``EntityCollection``.
        """
        return self._id

    @id.setter
    def id(self, value: str):
        # TODO: I think we can use pydantic to validate this...
        if value is None:
            if self.parent:
                self.parent.entities._remove_key(self._id)
            self._id = value
        elif isinstance(value, str):
            if self.parent:
                # try:
                old_id = self._id
                self.parent.entities._remove_key(old_id)
                # except AttributeError:
                #     pass
                self._id = value
                self.parent.entities._set_key(self._id, self)
            else:
                self._id = value
        else:
            raise TypeError("'id' must be a str or None")

    # =========================================================================

    @property
    def position(self) -> Vector:
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
        :type: :py:class:`.Vector`

        :exception IndexError: If the set value does not match the above
            specification.
        :exception DraftsmanError: If the entities position is modified when
            inside a EntityCollection, :ref:`which is forbidden.
            <handbook.blueprints.forbidden_entity_attributes>`
        """
        return self._root._position

    @position.setter
    def position(self, value: Vector):
        # TODO: relax
        if self.parent:
            raise DraftsmanError(
                "Cannot change position of entity while it's inside another object"
            )

        # self._position = Vector.from_other(value, float)
        self._root._position.update_from_other(value, float)
        self._root._tile_position.update(
            round(self._root._position.x - self.tile_width / 2),
            round(self._root._position.y - self.tile_height / 2),
        )

    # =========================================================================

    @property
    def tile_position(self) -> Vector:
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
        :type: :py:class:`.Vector`

        :exception IndexError: If the set value does not match the above
            specification.
        :exception DraftsmanError: If the entities position is modified when
            inside a EntityCollection, :ref:`which is forbidden.
            <handbook.blueprints.forbidden_entity_attributes>`
        """
        return self._root._tile_position

    @tile_position.setter
    def tile_position(self, value: Vector):
        # TODO: re-evaluate
        # if self.parent:
        #     raise DraftsmanError(
        #         "Cannot change position of entity while it's inside another object"
        #     )

        # self._tile_position.update_from_other(value, int)
        self._root._tile_position.update_from_other(value, int)
        self._root._position.update(
            self._root._tile_position.x + self.tile_width / 2,
            self._root._tile_position.y + self.tile_height / 2,
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

        :type: ``Vector``
        """
        if self.parent and hasattr(self.parent, "global_position"):
            return self.parent.global_position + self.position
        else:
            return self.position

    # =========================================================================

    @property
    def static_collision_set(self) -> Optional[CollisionSet]:
        """
        TODO
        """
        return entities.collision_sets.get(self.name, None)

    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        """
        TODO
        """
        return entities.collision_sets.get(self.name, None)

    # =========================================================================

    @property
    def collision_mask(self) -> set:
        """
        The set of all collision layers that this Entity collides with,
        specified as strings. Equivalent to Factorio's ``data.raw`` equivalent.
        Not exported; read only.

        :type: ``set{str}``
        """
        # We guarantee that the "collision_mask" key will exist during
        # `draftsman-update`, and that it will have it's proper default based
        # on it's type
        return entities.raw.get(self.name, {"collision_mask": None})["collision_mask"]

    # =========================================================================

    @property
    def tile_width(self) -> Optional[int]:
        """
        The width of the entity in tiles, rounded up to the nearest integer.
        Not exported; read only.

        :type: ``int``
        """
        return self._tile_width

    # =========================================================================

    @property
    def tile_height(self) -> Optional[int]:
        """
        The height of the entity in tiles, rounded up to the nearest integer.
        Not exported; read only.

        :type: ``int``
        """
        return self._tile_height

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
    def tags(self) -> Optional[dict[str, Any]]:
        """
        Tags associated with this Entity. Commonly used by mods to add custom
        data to a particular Entity when exporting and importing Blueprint
        strings.

        :getter: Gets the tags of the Entity, or ``None`` if not set.
        :setter: Sets the Entity's tags.
        :type: ``dict{Any: Any}``

        :exception TypeError: If tags is set to anything other than a ``dict``
            or ``None``.
        """
        return self._root.tags

    @tags.setter
    def tags(self, value: Optional[dict[str, Any]]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "tags", value
            )
            self._root.tags = result
        else:
            self._root.tags = value

    # =========================================================================

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:
        """
        TODO
        If ``mode`` is NONE, then this function will return an empty validation
        Result.

        :param mode: The validation mode to evaluate the object against.
            Determines the contents of the returned ValidationResult.
        :param force: Whether or not to force revalidation, even if ``is_valid``
            on this entity is ``True``. Useful if you know that an object is
            dirty when Draftsman doesn't, which can happen in [select
            circumstances.](TODO)
        """
        mode = ValidationMode(mode)

        output = ValidationResult([], [])

        if mode is ValidationMode.NONE or (self.is_valid and not force):
            return output

        context = {
            "mode": mode,
            "object": self,
            "warning_list": [],
            "assignment": False,
        }

        try:
            result = self.Format.model_validate(
                self._root,
                strict=False,  # TODO: ideally this should be strict
                context=context,
            )
            # Reassign private attributes
            result._entity = weakref.ref(self)
            result._position = self._root._position
            result._tile_position = self._root._tile_position
            # Scuffed AF
            if hasattr(self._root, "direction"):
                result.direction = self._root.direction
            if hasattr(self._root, "orientation"):
                result.orientation = self._root.orientation
            # Acquire the newly converted data
            self._root = result
        except ValidationError as e:
            output.error_list.append(DataFormatError(e))

        output.warning_list += context["warning_list"]

        return output

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

    def __eq__(self, other: "Entity") -> bool:
        return (
            type(self) == type(other)
            and self.name == other.name
            and self.global_position == other.global_position
            and self.id == other.id
            and self.tags == other.tags
        )

    def __hash__(self) -> int:
        return id(self) >> 4  # Apparently this is the default?

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

    def __deepcopy__(self, memo) -> "Entity":
        # Perform the normal deepcopy
        result = super().__deepcopy__(memo=memo)
        # This is very cursed
        # We need a reference to the parent entity stored in `_root` so that we
        # can properly serialize it's position
        # If we use a regular reference, it copies properly, but then it creates
        # a circular reference which makes garbage collection worse
        # We use a weakref to mitigate this memory issue (and ensure that
        # deleting an entity immediately destroys it), but means that we have to
        # manually update it's reference here
        result._root._entity = weakref.ref(result)
        # Get me out of here
        return result
