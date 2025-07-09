# group.py

from draftsman.classes.association import Association
from draftsman.classes.blueprint import (
    structure_blueprint_1_0_factory,
)
from draftsman.classes.collection import Collection
from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.exportable import Exportable, ValidationMode, ValidationResult
from draftsman.classes.schedule import Schedule
from draftsman.classes.spatial_hashmap import SpatialHashMap
from draftsman.classes.transformable import Transformable
from draftsman.classes.vector import Vector
from draftsman.error import (
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
    string_to_JSON,
)
from draftsman.validators import instance_of, try_convert

from draftsman.data import mods

import attrs
from typing import Any, Optional


@attrs.define
class Group(
    Transformable, Collection, EntityLike, Exportable
):  # TODO: remove EntityLike and only include what we need
    """
    Group entities together, so you can manipulate them all as one unit.

    Allows for the creation of "blocks" that can be added multiple times very
    easily to a blueprint. This allows you to create a complex portion of your
    desired blueprint only once, and then add that ``Group`` multiple times to
    the final blueprint.

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

    # TODO: ideally we would only define this method once
    @classmethod
    def from_string(
        cls,
        string: str,
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

        version_info = draftsman_converters.get_version(version)
        converter = version_info.get_converter()
        return converter.structure(json_dict, cls)

    # def __attrs_post_init__(self):
    #     # 1.0 code
    #     # Convert circuit and power connections to Associations
    #     # for entity in self.entities:
    #     #     if hasattr(entity, "connections"):  # Wire connections
    #     #         connections: Connections = entity.connections
    #     #         for side in connections.true_model_fields():
    #     #             if connections[side] is None:
    #     #                 continue

    #     #             if side in {"1", "2"}:
    #     #                 for color, _ in connections[side]:  # TODO fix
    #     #                     connection_points = connections[side][color]
    #     #                     if connection_points is None:
    #     #                         continue
    #     #                     for point in connection_points:
    #     #                         old = point["entity_id"] - 1
    #     #                         point["entity_id"] = Association(self.entities[old])

    #     #             elif side in {"Cu0", "Cu1"}:  # pragma: no branch
    #     #                 connection_points = connections[side]
    #     #                 if connection_points is None:
    #     #                     continue  # pragma: no coverage
    #     #                 for point in connection_points:
    #     #                     old = point["entity_id"] - 1
    #     #                     point["entity_id"] = Association(self.entities[old])

    #     #     if hasattr(entity, "neighbours"):  # Power pole connections
    #     #         neighbours = entity.neighbours
    #     #         for i, neighbour in enumerate(neighbours):
    #     #             neighbours[i] = Association(self.entities[neighbour - 1])

    #     _convert_wires_to_associations(self.wires, self.entities)
    #     _convert_schedules_to_associations(self.schedules, self.entities)
    #     _convert_stock_connections_to_associations(
    #         self.stock_connections, self.entities
    #     )

    #     # if self.validation:
    #     #     self.validate(mode=self.validation).reissue_all()

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

    # =========================================================================

    # TODO: delete this or fix this
    collision_mask: dict = attrs.field(
        factory=lambda: {"layers": set()},
        converter=lambda v: {"layers": set()} if v is None else v,
        validator=instance_of(dict),
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

    # =========================================================================

    @property
    def double_grid_aligned(self) -> bool:
        for entity in self.entities:
            if entity.double_grid_aligned:
                return True
        return False

    # =========================================================================

    # children: list["Group"] = attrs.field(
    #     factory=[],
    #     validator=instance_of(list)
    # )
    # """
    # Children of this entity-like.
    # """

    # =========================================================================

    def get(self) -> list[EntityLike]:
        """
        Gets all the child-most ``Entity`` instances in this ``Group`` and
        returns them as a "flattened" 1-dimensional list. Offsets all of their
        positions by the position of the parent ``Group``.

        :returns: A ``list`` of ``Entity`` instances associated with this
            ``Group``.
        """
        return flatten_entities(self)

    def get_world_bounding_box(self) -> Optional[AABB]:
        area = None
        for entity in self.entities:
            area = extend_aabb(area, entity.get_world_bounding_box())

        return area

    def get_dimensions(self) -> tuple[int, int]:
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
        self, mode: ValidationMode = ValidationMode.STRICT
    ) -> ValidationResult:
        # Validate regular attributes
        output = super().validate(mode=mode)

        # Validate recursive attributes
        output += self.entities.validate(mode=mode)
        output += self.tiles.validate(mode=mode)

        # if len(output.error_list) == 0:
        #     # Set the `is_valid` attribute
        #     # This means that if mode="pedantic", an entity that issues only
        #     # warnings will still not be considered valid
        #     super().validate()

        return output

    # def __str__(self) -> str:  # pragma: no coverage
    #     # TODO: better formatting
    #     return "<Group>" + str(self)


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Group,
    lambda fields: {
        ("blueprint", "item"): None,
        ("blueprint", "label"): None,
        ("blueprint", "label_color"): None,
        ("blueprint", "description"): None,
        ("blueprint", "icons"): None,
        ("blueprint", "version"): None,
        ("blueprint", "snap-to-grid"): None,
        ("blueprint", "absolute-snapping"): None,
        ("blueprint", "position-relative-to-grid"): None,
        ("blueprint", "entities"): fields.entities.name,
        ("blueprint", "tiles"): fields.tiles.name,
        ("blueprint", "wires"): fields.wires.name,
        ("blueprint", "schedules"): fields.schedules.name,
        ("blueprint", "stock_connections"): fields.stock_connections.name,
    },
)

draftsman_converters.get_version((1, 0)).register_structure_hook(
    Group, structure_blueprint_1_0_factory(Group)
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Group,
    lambda fields: {
        ("blueprint", "item"): None,
        ("blueprint", "label"): None,
        ("blueprint", "label_color"): None,
        ("blueprint", "description"): None,
        ("blueprint", "icons"): None,
        ("blueprint", "version"): None,
        ("blueprint", "snap-to-grid"): None,
        ("blueprint", "absolute-snapping"): None,
        ("blueprint", "position-relative-to-grid"): None,
        ("blueprint", "entities"): fields.entities.name,
        ("blueprint", "tiles"): fields.tiles.name,
        ("blueprint", "wires"): fields.wires.name,
        ("blueprint", "schedules"): fields.schedules.name,
        ("blueprint", "stock_connections"): fields.stock_connections.name,
    },
)
