# group.py
# TODO: needs quite a bit of a rework due to the changed functionality of JSON
# obejects
# TODO: add tiles to this bad boy (somehow)

from draftsman.classes.association import Association
from draftsman.classes.blueprint import (
    Blueprint,
    structure_blueprint_1_0_factory,
    _convert_wires_to_associations,
    _convert_schedules_to_associations,
    _convert_stock_connections_to_associations,
)
from draftsman.classes.collection import EntityCollection, TileCollection
from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.entity_list import EntityList
from draftsman.classes.exportable import Exportable, ValidationMode, ValidationResult
from draftsman.classes.schedule import Schedule
from draftsman.classes.schedule_list import ScheduleList
from draftsman.classes.transformable import Transformable
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.error import (
    DraftsmanError,
    IncorrectBlueprintTypeError,
)
from draftsman.signatures import StockConnection
from draftsman.serialization import draftsman_converters
from draftsman.utils import (
    AABB,
    aabb_to_dimensions,
    decode_version,
    extend_aabb,
    flatten_entities,
    reissue_warnings,
    string_to_JSON,
)
from draftsman.validators import instance_of, try_convert

from draftsman.data import mods

import attrs
import copy
from typing import Any, Optional


@attrs.define
class Group(Transformable, TileCollection, EntityCollection, EntityLike, Exportable):
    """
    Group entities together, so you can manipulate them all as one unit.

    Allows for the creation of "blocks" that can be added multiple times very
    easily to a blueprint. This allows you to create a section with complex
    circuit connections, and then add that ``Group`` multiple times and the
    circuit connections will be the same for every block with no extra work.

    Groups can also be used to organize Blueprints at the structure level. You
    can give entities the same name in a Blueprint as long as they exist in
    different groups. For example, the following is a perfectly valid structure
    for a Blueprint to have:

    .. code-block::

        <Blueprint>.entities => [
            <Group "1">.entities => [<Entity "A">, <Entity "B">, <Entity "C">],
            <Group "2">.entities => [<Entity "A">, <Entity "B">, <Entity "C">],
        ]

    This is particularly useful if each group has a similar function, but just
    exists as a different "part" of the overall blueprint.

    To aid in quickly accessing nested entities in such structures,
    ``EntityLists`` support indexing with a sequence, usually a tuple. For
    example, assuming the Blueprint structure above, all of the following
    assertions are true:

    .. code-block:: python

        assert blueprint.entities[("1", "A")].id == "A"
        assert isinstance(blueprint.entities[("2", "A")], Entity)
        assert blueprint.entities[("1", "C")] is blueprint.entities["1"].entities["C"]

    ``EntityLike`` instances in a Group are considered to be in "group-space";
    meaning their positions are offset by the position of the Group they reside
    in. If a Group is located at position ``(5, 5)``, and an entity inside of it
    is located at ``(5, 5)``, when added to a Blueprint the entity will be
    located at ``(10, 10)``. This effect continues if Groups nest inside of
    other Groups, which is also perfectly legal.

    Groups have their own ``SpatialHashMap`` instances, so they will issue
    :py:class:`~draftsman.warning.OverlappingObjectsWarning` when entities
    overlap, both when adding entities to the Group and when adding the Group to
    another ``EntityCollection``.
    """

    # @reissue_warnings
    # def __init__(
    #     self,
    #     id: str = None,
    #     name: str = "group",
    #     type: str = "group",
    #     position: Union[Vector, PrimitiveVector] = (0, 0),
    #     entities: Union[list[EntityLike], EntityList] = [],
    #     schedules: Union[list[Schedule], ScheduleList] = [],
    #     wires: Optional[list[list[int]]] = None,
    #     string: str = None,
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    # ):
    #     """
    #     :param string: A blueprint string to use as the basis for this Group;
    #         inherits all entities and schedules and populates the Group with
    #         them.
    #     :param id: A unique string ID to give the group, for indexing in an
    #         :py:class:`.EntityList`.
    #     :param name: A string name to give this Group, to allow easier searching.
    #     :param type: Similar to ``name``, except this one describes the type or
    #         category of the group. Also used to aid in searching/identification.
    #     :param position: The position to place this Group at. When resolved,
    #         offsets all child entities contained within it by this amount. No
    #         translation is performed until resolving into a dict or blueprint
    #         string, and all child entities retain their specified positions as
    #         set.
    #     :param entities: A list of entities to contain within this Group.
    #     :param schedules: A list of schedules to associate with this Group.
    #     """
    #     super().__init__()  # EntityLike

    #     # TODO: better mixin inheritance
    #     self.validate_assignment = validate_assignment

    #     self.id = id

    #     self.name = name
    #     self.type = type

    #     # Collision box
    #     self._collision_set = CollisionSet([])

    #     # Tile dimensions
    #     # self.tile_width, self.tile_height = 0, 0

    #     # Collision mask
    #     self.collision_mask = None  # empty set()

    #     # List of entities
    #     if string is not None:
    #         self.load_from_string(string)
    #     else:
    #         self.setup(
    #             entities=entities,
    #             schedules=schedules,
    #             wires=[] if wires is None else wires,
    #         )

    #     # TODO: the position of this shouldn't matter, but in practice it does,
    #     # investigate
    #     self.position = position

    # TODO: ideally we would only define this method once
    @classmethod
    def from_string(
        cls,
        string: str,
        # validate: Union[
        #     ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        # ] = ValidationMode.NONE,
    ):
        """
        Creates a :py:class:`.Group` with the contents of a
        :py:class:`.Blueprint` ``string``.

        Raises :py:class:`.UnknownKeywordWarning` if there are any unrecognized
        keywords in the blueprint string for this particular blueprintable.

        :param string: Factorio-encoded blueprint string.

        :exception MalformedBlueprintStringError: If the input string is not
            decodable to a JSON object.
        :exception IncorrectBlueprintTypeError: If the input string is of a
            different type than the base class, such as trying to load the
            string of an upgrade planner into a ``Blueprint`` object.
        """
        json_dict = string_to_JSON(string)
        # Groups can only import from blueprint strings (for now at least)
        if "blueprint" not in json_dict:
            raise IncorrectBlueprintTypeError(
                "Groups can only be constructed from blueprint strings"
            )
        # Try and get the version from the dictionary, falling back to current
        # environment configuration if not found
        if "version" in json_dict["blueprint"]:
            version = decode_version(json_dict["blueprint"]["version"])
        else:
            version = mods.versions["base"]

        # print(version)
        version_info = draftsman_converters.get_version(version)
        converter = version_info.get_converter()
        # import inspect
        # print(inspect.getsource(converter.get_structure_hook(cls)))
        return converter.structure(json_dict, cls)

        # self.setup(
        #     **root[self._root_item],
        #     index=root.get("index", None),
        #     validate=validate,
        # )

        # Convert circuit and power connections to Associations
        # TODO: write a single function to do this and reuse
        # for entity in self.entities:
        #     if hasattr(entity, "connections"):  # Wire connections
        #         connections: Connections = entity.connections
        #         for side in connections.true_model_fields():
        #             if connections[side] is None:
        #                 continue

        #             if side in {"1", "2"}:
        #                 for color, _ in connections[side]:
        #                     connection_points = connections[side][color]
        #                     if connection_points is None:
        #                         continue
        #                     for point in connection_points:
        #                         old = point["entity_id"] - 1
        #                         point["entity_id"] = Association(self.entities[old])

        #             elif side in {"Cu0", "Cu1"}:  # pragma: no branch
        #                 connection_points = connections[side]
        #                 if connection_points is None:
        #                     continue  # pragma: no coverage
        #                 for point in connection_points:
        #                     old = point["entity_id"] - 1
        #                     point["entity_id"] = Association(self.entities[old])

        #     if hasattr(entity, "neighbours"):  # Power pole connections
        #         neighbours = entity.neighbours
        #         for i, neighbour in enumerate(neighbours):
        #             neighbours[i] = Association(self.entities[neighbour - 1])

        # # Change all locomotive numbers to use Associations
        # for schedule in self._schedules:
        #     for i, locomotive in enumerate(schedule.locomotives):
        #         schedule.locomotives[i] = Association(self.entities[locomotive - 1])

        # TODO: wires

    # @reissue_warnings
    # def setup(self, **kwargs) -> None:  # TODO: kwargs
    #     """
    #     Sets up a Group using a blueprint JSON dict. Currently only reads the
    #     ``"entities"`` and ``"schedules"`` keys and loads them into
    #     :py:attr:`Group.entities` and :py:attr:`Group.schedules`.

    #     TODO: update
    #     """
    #     if "entities" in kwargs:
    #         self._entities = EntityList(self, kwargs.pop("entities"))
    #     else:
    #         self._entities = EntityList(self)

    #     if "schedules" in kwargs:
    #         self._schedules = ScheduleList(kwargs.pop("schedules"))
    #     else:
    #         self._schedules = ScheduleList()

    #     if "wires" in kwargs:
    #         self._wires = kwargs.pop("wires")

    def __attrs_post_init__(self):
        # 1.0 code
        # Convert circuit and power connections to Associations
        # for entity in self.entities:
        #     if hasattr(entity, "connections"):  # Wire connections
        #         connections: Connections = entity.connections
        #         for side in connections.true_model_fields():
        #             if connections[side] is None:
        #                 continue

        #             if side in {"1", "2"}:
        #                 for color, _ in connections[side]:  # TODO fix
        #                     connection_points = connections[side][color]
        #                     if connection_points is None:
        #                         continue
        #                     for point in connection_points:
        #                         old = point["entity_id"] - 1
        #                         point["entity_id"] = Association(self.entities[old])

        #             elif side in {"Cu0", "Cu1"}:  # pragma: no branch
        #                 connection_points = connections[side]
        #                 if connection_points is None:
        #                     continue  # pragma: no coverage
        #                 for point in connection_points:
        #                     old = point["entity_id"] - 1
        #                     point["entity_id"] = Association(self.entities[old])

        #     if hasattr(entity, "neighbours"):  # Power pole connections
        #         neighbours = entity.neighbours
        #         for i, neighbour in enumerate(neighbours):
        #             neighbours[i] = Association(self.entities[neighbour - 1])

        _convert_wires_to_associations(self.wires, self.entities)
        _convert_schedules_to_associations(self.schedules, self.entities)
        _convert_stock_connections_to_associations(
            self.stock_connections, self.entities
        )

        # if self.validation:
        #     self.validate(mode=self.validation).reissue_all()

    # =========================================================================

    # TODO: this should be moved into EntityLike since that makes more sense
    def _set_id(self, attr: attrs.Attribute, value: Optional[str]):
        attr.validator(self, attr, value)
        if self.parent:
            self.parent.entities._remove_key(self.id)
            if value is not None:
                self.parent.entities._set_key(value, self)

        return value

    # TODO: does an ID have to be a string? Is it not being a string ever useful?
    id: Optional[str] = attrs.field(default=None, on_setattr=_set_id)
    """
    The ID of the Group. The most local form of identification between
    Groups.

    :getter: Gets the ID of the Group.
    :setter: Sets the ID of the Group.

    :exception TypeError: If set to anything other than a ``str`` or ``None``.
    """

    @id.validator
    def _ensure_id_correct_type(self, _: attrs.Attribute, value: Any, **kwargs):
        if value is not None and not isinstance(value, str):
            raise TypeError("'id' must be either a str or None")

    # =========================================================================

    # # TODO: should only be defined once
    # validate_assignment: ValidationMode = attrs.field(
    #     default=ValidationMode.STRICT,
    #     converter=ValidationMode,
    #     validator=instance_of(ValidationMode),
    #     repr=False,
    #     eq=False,
    #     kw_only=True,
    #     metadata={"omit": True},
    # )
    # """
    # Toggleable flag that indicates whether assignments to this object should
    # be validated, and how. Can be set in the constructor of the entity or
    # changed at any point during runtime. Note that this is on a per-entity
    # basis, so multiple instances of otherwise identical entities can have
    # different validation configurations.
    # """

    # =========================================================================

    name: str = attrs.field(default="group", validator=instance_of(str), kw_only=True)
    """
    The name of the Group. Defaults to ``"group"``. Can be specified to any
    string to aid in organization. For example:

    .. code-block:: python

        blueprint.entities.append(Group("A"))
        blueprint.entities.append(Group("B", name="different_name"))

        diff = blueprint.find_entities_filtered(name="different_name")
        assert diff[0] is blueprint.entities["B"]

    :getter: Gets the name of the Group.
    :setter: Sets the name of the Group.

    :exception TypeError: If set to anything other than a ``str``.
    """

    # @property
    # def name(self) -> str:
    #     """
    #     The name of the Group. Defaults to ``"group"``. Can be specified to any
    #     string to aid in organization. For example:

    #     .. code-block:: python

    #         blueprint.entities.append(Group("A"))
    #         blueprint.entities.append(Group("B", name="different_name"))

    #         diff = blueprint.find_entities_filtered(name="different_name")
    #         assert diff[0] is blueprint.entities["B"]

    #     :getter: Gets the name of the Group.
    #     :setter: Sets the name of the Group.

    #     :exception TypeError: If set to anything other than a ``str``.
    #     """
    #     return self._name

    # @name.setter
    # def name(self, value: str):
    #     if isinstance(value, str):
    #         self._name = value
    #     else:
    #         raise TypeError("'name' must be a str")

    # =========================================================================

    type: str = attrs.field(
        default="group",
        validator=instance_of(str),
        kw_only=True,
    )
    """
    The type of the Group. Defaults to ``"group"``. Can be specified to any
    string to aid in organization. For example:

    .. code-block:: python

        blueprint.entities.append(Group("A"))
        blueprint.entities.append(Group("B", type="different_type"))

        diff = blueprint.find_entities_filtered(type="different_type")
        assert diff[0] is blueprint.entities["B"]

    :getter: Gets the type of the Group.
    :setter: Sets the type of the Group.

    :exception TypeError: If set to anything other than a ``str``.
    """

    # @property
    # def type(self) -> str:
    #     """
    #     The type of the Group. Defaults to ``"group"``. Can be specified to any
    #     string to aid in organization. For example:

    #     .. code-block:: python

    #         blueprint.entities.append(Group("A"))
    #         blueprint.entities.append(Group("B", type="different_type"))

    #         diff = blueprint.find_entities_filtered(type="different_type")
    #         assert diff[0] is blueprint.entities["B"]

    #     :getter: Gets the type of the Group.
    #     :setter: Sets the type of the Group.

    #     :exception TypeError: If set to anything other than a ``str``.
    #     """
    #     return self._type

    # @type.setter
    # def type(self, value: str):
    #     if isinstance(value, str):
    #         self._type = value
    #     else:
    #         raise TypeError("'type' must be a str")

    # =========================================================================

    position: Vector = attrs.field(
        factory=lambda: Vector(0.0, 0.0),
        converter=try_convert(Vector.from_other),
        validator=instance_of(Vector),
        kw_only=True,
        # metadata={"omit": True}
    )
    """
    The position of the Group. Acts as the origin of all the entities
    contained within, and offsets them on export.

    ``position`` can be specified as a ``dict`` with ``"x"`` and ``"y"``
    keys, or more succinctly as a sequence of floats, usually a ``list`` or
    ``tuple``.

    :getter: Gets the position of the Group.
    :setter: Sets the position of the Group.

    :exception IndexError: If the set value does not match the above
        specification.
    :exception DraftsmanError: If the Group's position is modified when
        inside a EntityCollection, :ref:`which is forbidden
        <handbook.blueprints.forbidden_entity_attributes>`.
    """

    # @property
    # def position(self) -> Vector:
    #     """
    #     The position of the Group. Acts as the origin of all the entities
    #     contained within, and offsets them on export.

    #     ``position`` can be specified as a ``dict`` with ``"x"`` and ``"y"``
    #     keys, or more succinctly as a sequence of floats, usually a ``list`` or
    #     ``tuple``.

    #     :getter: Gets the position of the Group.
    #     :setter: Sets the position of the Group.

    #     :exception IndexError: If the set value does not match the above
    #         specification.
    #     :exception DraftsmanError: If the Group's position is modified when
    #         inside a EntityCollection, :ref:`which is forbidden
    #         <handbook.blueprints.forbidden_entity_attributes>`.
    #     """
    #     return self._position

    # @position.setter
    # def position(self, value: Union[Vector, PrimitiveVector]):
    #     if self.parent:
    #         raise DraftsmanError(
    #             "Cannot change position of Group while it's inside a Collection"
    #         )

    #     self._position = Vector.from_other(value, float)

    #     # if "x" in value and "y" in value:
    #     #     self._position = {"x": float(value["x"]), "y": float(value["y"])}
    #     # elif isinstance(value, (list, tuple)):
    #     #     self._position = {"x": float(value[0]), "y": float(value[1])}
    #     # else:
    #     #     raise TypeError("Incorrectly formatted position ({})".format(value))

    # =========================================================================

    @property
    def global_position(self) -> Vector:
        """
        The "global", or root-most position of the Group. This value is always
        equivalent to :py:attr:`~.Group.position`, unless the group exists
        inside another :py:class:`.EntityCollection`. If it does, then it's
        global position is equivalent to the sum of all parent positions plus
        it's own position. Used when recursing the position of any sub-entity
        contained within the ``Group``. Read only.
        """
        if self.parent and hasattr(self.parent, "global_position"):
            return self.parent.global_position + self.position
        else:
            return self.position

    # =========================================================================

    @property
    def collision_set(self) -> Optional[CollisionSet]:
        """
        TODO: is this even a good idea to have in the first place? It seems like
        having this set be the union of all entities it contains would make the
        most sense, but that would be slow to compute instead of using a spatial
        map for that. The user could specify a custom collision set, but how
        is that supposed to interact with the hashmap? no idea
        """
        # For now just return an empty collision set, it's probably better to
        # have each sub-entity handle their own collisions
        return CollisionSet([])

    # @collision_set.setter
    # def collision_set(self, value: CollisionSet) -> None:
    #     # TODO: error checking
    #     if value is None:
    #         self._collision_set = CollisionSet([])
    #     else:
    #         self._collision_set = value
    # self._collision_set = value

    # =========================================================================

    # TODO: delete this
    collision_mask: set[str] = attrs.field(
        factory=set,
        converter=lambda v: set() if v is None else v,
        validator=instance_of(set),
        kw_only=True,
    )
    """
    The set of all collision layers that this Entity collides with,
    specified as strings. Defaults to an empty ``set``. Not exported.

    :getter: Gets the collision mask of the Group.
    :setter: Sets the collision mask of the Group, or sets it to an empty
        set if ``None`` was input.

    :exception TypeError: If set to anything other than a `set` or None.
    """

    # @property
    # def collision_mask(self) -> set[str]:
    #     """
    #     The set of all collision layers that this Entity collides with,
    #     specified as strings. Defaults to an empty ``set``. Not exported.

    #     :getter: Gets the collision mask of the Group.
    #     :setter: Sets the collision mask of the Group, or sets it to an empty
    #         set if ``None`` was input.

    #     :exception TypeError: If set to anything other than a `set` or None.
    #     """
    #     return self._collision_mask

    # @collision_mask.setter
    # def collision_mask(self, value: Optional[set[str]]):
    #     if value is None:
    #         self._collision_mask = set()
    #     elif isinstance(value, set):
    #         self._collision_mask = value
    #     else:
    #         raise TypeError("'collision_mask' must be a set or None")

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        for entity in self.entities:
            if entity.double_grid_aligned:
                return True
        return False

    # =========================================================================

    # def _set_entities(self, _: attrs.Attribute, value: Any):
    #     if value is None:
    #         self.entities.clear()
    #     elif isinstance(value, EntityList):
    #         self.entities = EntityList(self, value._root)
    #     else:
    #         self.entities = EntityList(self, value)

    #     return self.entities

    # # TODO: move into EntityCollection
    # entities: EntityList = attrs.field(
    #     on_setattr=_set_entities,
    # )

    # @entities.default
    # def _(self):
    #     return EntityList(self)

    # @property
    # def entities(self) -> EntityList:
    #     """
    #     The list of the Group's entities. Internally the list is a custom
    #     class named :py:class:`draftsman.classes.EntityList`, which has all the
    #     normal properties of a regular list, as well as some extra features.
    #     For more information on ``EntityList``, check out this writeup
    #     :ref:`here <handbook.blueprints.blueprint_differences>`.
    #     """
    #     return self._entities

    # @entities.setter
    # @reissue_warnings
    # def entities(self, value: Union[list[EntityLike], EntityList]):
    #     if value is None:
    #         self._entities.clear()
    #     elif isinstance(value, list):
    #         self._entities = EntityList(self, value)
    #     elif isinstance(value, EntityList):
    #         # Just don't ask
    #         self._entities = copy.deepcopy(value, memo={"new_parent": self})
    #     else:
    #         raise TypeError("'entities' must be an EntityList, list, or None")

    # =========================================================================

    # # TODO: move into EntityCollection
    # @property
    # def schedules(self) -> ScheduleList:
    #     """
    #     A list of the Group's train schedules.

    #     .. seealso::

    #         `<https://wiki.factorio.com/Blueprint_string_format#Schedule_object>`_

    #     :getter: Gets the schedules of the Blueprint.
    #     :setter: Sets the schedules of the Blueprint. Defaults to ``[]`` if set
    #         to ``None``.

    #     :exception DataFormatError: If set to anything other than a ``list`` of
    #         :py:data:`.SCHEDULE`.
    #     """
    #     return self._schedules

    # @schedules.setter
    # def schedules(self, value: Union[list, ScheduleList]):
    #     if value is None:
    #         self._schedules = ScheduleList()
    #     elif isinstance(value, ScheduleList):
    #         self._schedules = value  # TODO: what about reference copying?
    #     else:
    #         self._schedules = ScheduleList(value)

    # =========================================================================

    # # TODO: move into EntityCollection
    # wires: list[list[Association, int, Association, int]] = attrs.field(
    #     factory=list,
    #     converter=lambda v: [] if v is None else v,
    #     validator=instance_of(list) # TODO: validators
    # )
    # """
    # A list of the wire connections in this collection.

    # Wires are specified as a list of 4 integers; the first pair of numbers
    # represents the first entity, and the second pair represents the second
    # entity. The first number of each pair represents the ``entity_number``
    # of the corresponding entity in the list, and the second number indicates
    # what type of connection it is.

    # TODO: more detail

    # :getter: Gets the wires of the Blueprint.
    # :setter: Sets the wires of the Blueprint. Defaults to an empty list if
    #     set to ``None``.
    # """

    # # @property
    # # def wires(self) -> list[list[int]]:
    # #     """
    # #     TODO
    # #     """
    # #     return self._wires

    # # @wires.setter
    # # def wires(self, value: list[list[int]]) -> None:
    # #     if value is None:
    # #         self._wires = []
    # #     else:
    # #         self._wires = value

    # =========================================================================

    def get(self) -> list[EntityLike]:
        """
        Gets all the child-most ``Entity`` instances in this ``Group`` and
        returns them as a "flattened" 1-dimensional list. Offsets all of their
        positions by the position of the parent ``Group``.

        :returns: A ``list`` of ``Entity`` instances associated with this
            ``Group``.
        """
        return flatten_entities(self.entities)

    def get_world_bounding_box(self) -> Optional[AABB]:
        """
        TODO
        """
        area = None
        for entity in self.entities:
            area = extend_aabb(area, entity.get_world_bounding_box())

        return area

    def get_dimensions(self) -> tuple[int, int]:
        """
        TODO
        """
        return aabb_to_dimensions(self.get_world_bounding_box())

    def mergable_with(self, other: "Group") -> bool:
        # For now, we assume that Groups themselves are not mergable
        # Note that the entities *inside* groups are perfectly mergable; the
        # only case where this is important is when two identical groups are
        # merged on top of one another: currently, both instances of the group
        # will exist, one of which will be empty
        return False

    def merge(self, other: "Group"):
        # For now, we assume that Groups themselves are not mergable
        return  # Do nothing

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:
        # Validate regular attributes
        output = ValidationResult([], [])

        # Validate recursive attributes
        output += self.entities.validate(mode=mode, force=force)
        output += self.tiles.validate(mode=mode, force=force)

        # if len(output.error_list) == 0:
        #     # Set the `is_valid` attribute
        #     # This means that if mode="pedantic", an entity that issues only
        #     # warnings will still not be considered valid
        #     super().validate()

        return output

    def __str__(self) -> str:  # pragma: no coverage
        # TODO: better formatting
        return "<Group>" + str(self.entities._root)

    def __repr__(self) -> str:  # pragma: no coverage
        return "<Group>{}".format(self.entities._root)

    def __deepcopy__(self, memo: Optional[dict[int, Any]] = None):
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
            if attr.name == "_parent":  # special
                object.__setattr__(result, attr.name, None)
            elif attr.name == "wires":  # special
                new_wires = copy.deepcopy(getattr(self, attr.name), memo)
                for wire in new_wires:
                    wire[0] = swap_association(wire[0])
                    wire[2] = swap_association(wire[2])

                object.__setattr__(result, attr.name, new_wires)
            elif attr.name == "schedules":
                new_schedules = copy.deepcopy(getattr(self, attr.name), memo)
                for schedule in new_schedules:
                    schedule: Schedule
                    schedule.locomotives = [
                        swap_association(loco) for loco in schedule.locomotives
                    ]

                object.__setattr__(result, attr.name, new_schedules)
            elif attr.name == "stock_connections":  # special
                new_connections: list[StockConnection] = copy.deepcopy(
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
                    result, attr.name, copy.deepcopy(getattr(self, attr.name), memo)
                )

        return result

    #     # Making the copy of an entity directly "removes" its parent, as there
    #     # is no guarantee that that cloned entity will actually lie in some
    #     # EntityCollection
    #     if attr.name == "_parent":
    #         object.__setattr__(result, "_parent", None)
    #     __deepcopy__ = Blueprint.__deepcopy__

    # def __deepcopy__(self, memo: dict) -> "Group":
    #     """
    #     Creates a deepcopy of a :py:class:`.Group` and it's contents. Preserves
    #     all Entities and Associations within the copied group, *except* for
    #     assocations that point to entities outside the copied group.

    #     :returns: A deepcopy of a :py:class:`.Group`.
    #     """
    #     cls = self.__class__
    #     result = cls.__new__(cls)
    #     memo[id(self)] = result

    #     # Make sure we copy "_entity_map" first so we don't get
    #     # OverlappingEntitiesWarnings
    #     # v = getattr(self, "_entity_map")
    #     # setattr(result, "_entity_map", copy.deepcopy(v, memo))
    #     # result.entity_map.clear()
    #     # Also make sure "_collision_set" is intialized before setting up
    #     # "_entities"
    #     v = getattr(self, "_collision_set")
    #     setattr(result, "_collision_set", copy.deepcopy(v, memo))

    #     for k, v in self.__dict__.items():
    #         if k == "_parent":
    #             # Reset parent to None
    #             setattr(result, k, None)
    #         # elif k == "_entity_map":
    #         #     continue
    #         elif k == "_entities":
    #             # Create a copy of EntityList with copied self as new parent so
    #             # that `result.entities[0].parent` will be `result`
    #             memo["new_parent"] = result
    #             setattr(result, k, copy.deepcopy(v, memo))
    #         else:
    #             setattr(result, k, copy.deepcopy(v, memo))

    #     # Iterate over each locomotive in each schedule
    #     # (which still point to the old locomotives in each list)
    #     for i, schedule in enumerate(self.schedules):
    #         for j, locomotive in enumerate(schedule.locomotives):
    #             # Replace the old one with the copied one
    #             result.schedules[i].locomotives[j] = Association(memo[id(locomotive())])

    #     # Wires
    #     for i, old_wire in enumerate(self.wires):
    #         # Replace the old one with the copied one
    #         old_entity_1: Association = old_wire[0]
    #         old_entity_2: Association = old_wire[2]
    #         result.wires[i][0] = Association(memo[id(old_entity_1())])
    #         result.wires[i][2] = Association(memo[id(old_entity_2())])

    #     return result


draftsman_converters.add_hook_fns(
    # {"$id": "draftsman:group"},
    Group,
    lambda fields: {
        ("blueprint", "entities"): fields.entities.name,
        ("blueprint", "tiles"): fields.tiles.name,
        ("blueprint", "schedules"): fields.schedules.name,
        ("blueprint", "wires"): fields.wires.name,
        ("blueprint", "stock_connections"): fields.stock_connections.name,
    },
)


draftsman_converters.get_version((1, 0)).register_structure_hook(
    Group, structure_blueprint_1_0_factory(Group)
)
