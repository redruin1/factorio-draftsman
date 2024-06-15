# entitylist.py

from draftsman.classes.association import Association
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.exportable import Exportable, ValidationResult
from draftsman.classes.spatial_hashmap import SpatialDataStructure, SpatialHashMap
from draftsman.constants import ValidationMode
from draftsman.entity import new_entity
from draftsman.error import (
    DataFormatError,
    DuplicateIDError,
    InvalidAssociationError,
    InvalidEntityError,
)
from draftsman.utils import reissue_warnings
from draftsman.signatures import Connections, DraftsmanBaseModel
from draftsman.warning import HiddenEntityWarning

from collections.abc import MutableSequence
from copy import deepcopy
from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationError,
    model_validator,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from typing import Any, Callable, Iterator, Literal, Union

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import EntityCollection


class EntityList(Exportable, MutableSequence):
    """
    Custom object for storing sequences of :py:class:`.EntityLike`.

    Contains all the functionality of a normal ``list``. Adds the ability
    to index with id strings, as well as extra framework for interfacing with
    :py:class:`.EntityCollection` classes.
    """

    class Format(DraftsmanBaseModel):
        _root: List[EntityLike]

        root: List[Any]  # should be a better way to validate this

        @model_validator(mode="after")
        def ensure_no_duplicate_ids(self, info):  # TODO
            known_ids = set()
            for entitylike in self.root:
                if entitylike.id in known_ids:  # pragma: no coverage
                    raise AssertionError(
                        "Cannot have two entities with the same id"
                    )  # TODO better
                if entitylike.id is not None:
                    known_ids.add(entitylike.id)
            return self

        # TODO: issue OverlappingObjectsWarnings

        # TODO: determine a way to check if entities can be placed in a blueprint
        # ("hidden" flag, "not-blueprintable" flag, etc.)

    @reissue_warnings
    def __init__(
        self,
        parent: "EntityCollection" = None,
        initlist: list[EntityLike] = [],
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        if_unknown: str = "error",  # TODO: enum
    ):
        """
        Instantiates a new ``EntityList``.

        :param parent: The parent object that contains the EntityList; used when
            assigning the ``parent`` to entities when inserted.
        :param initlist: A list containing data to initialize with.

        :exception TypeError: If any of the entries in ``initlist`` are neither
            a ``dict`` nor an ``EntityLike``.
        """
        # Init Exportable
        super().__init__()

        self._root: list[EntityLike] = []
        self.key_map = {}
        self.key_to_idx = {}
        self.idx_to_key = {}

        self.spatial_map: SpatialDataStructure = SpatialHashMap()

        self._parent = parent

        for elem in initlist:
            if isinstance(elem, EntityLike):
                self.append(elem, if_unknown=if_unknown)
            elif isinstance(elem, dict):
                name = elem.pop("name")
                self.append(name, **elem, if_unknown=if_unknown)
            else:
                raise TypeError("Constructor either takes EntityLike or dict entries")

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    @reissue_warnings
    def append(
        self,
        name: Union[str, "EntityLike"],
        copy: bool = True,
        merge: bool = False,
        if_unknown: str = "error",  # TODO: enum
        **kwargs
    ):
        """
        Appends the ``EntityLike`` to the end of the sequence.

        Supports an optional shorthand where you can specify the string name of
        an Entity as ``entity`` and any keyword arguments, which are appended to
        the constructor of that entity.

        If ``copy`` is specified, a deepcopy of the passed in entity is created.
        If any additional keyword arguments are specified alongside, the
        attributes of that newly copied entity are overwritten with them.

        :param name: Either a string reprenting the name of an ``Entity``, or an
            :py:class:`.EntityLike` instance.
        :param copy: Whether or not to create a copy of the passed in
            ``EntityLike``. If ``name`` is in string shorthand, this option is
            ignored and a new instance is always created.
        :param merge: Whether or not to merge entities of the same type at the
            same position. Merged entities share non-overlapping attributes and
            prefer the attributes of the last entity added. Useful for merging
            things like rails or power-poles on the edges of tiled blueprints.
        :param if_unknown: The behavior this method should perform if ``name``
            is not recognized as any known valid entity. See TODO for a more
            complete explanation.
        :param kwargs: Any other keyword arguments to pass to the entity
            instance. This is used primarily when constructing a new entity from
            a string name, but can also be used to overwrite certain attributes
            of a passed in ``EntityLike`` before adding it to the ``EntityList``.

        :example:

        .. code-block:: python

            blueprint = Blueprint()
            assert isinstance(blueprint.entities, EntityList)

            # Append Entity instance
            blueprint.entities.append(Container("steel-chest"))
            assert blueprint.entities[-1].name == "steel-chest"

            # Append shorthand
            blueprint.entities.append("wooden-chest", tile_position=(1, 1))
            assert blueprint.entities[-1].name == "wooden-chest"
            assert blueprint.entities[-1].tile_position == {"x": 1, "y": 1}

            # Key indexing
            blueprint.entities.append(
                TransportBelt(id = "some_id", tile_position=(1, 0))
            )
            assert isinstance(blueprint.entities["some_id"], TransportBelt)

            # No copy
            inserter = Inserter("fast-inserter", tile_position=(0, 1))
            blueprint.entities.append(inserter, copy=False)
            inserter.stack_size_override = 1
            assert inserter is blueprint.entities[-1]
            assert blueprint.entities[-1].stack_size_override == 1
        """
        self.insert(
            idx=len(self),
            name=name,
            copy=copy,
            merge=merge,
            if_unknown=if_unknown,
            **kwargs
        )

    @reissue_warnings
    def insert(
        self,
        idx: int,
        name: Union[str, "EntityLike"],
        copy: bool = True,
        merge: bool = False,
        if_unknown: str = "error",
        **kwargs
    ):
        """
        Inserts an ``EntityLike`` into the sequence.

        Supports an optional shorthand where you can specify the string name of
        an Entity as ``entity`` and any keyword arguments, which are appended to
        the constructor of that entity.

        If ``copy`` is specified, a deepcopy of the passed in entity is created.
        If any additional keyword arguments are specified alongside, the
        attributes of that newly copied entity are overwritten with them.

        :param idx: The integer index to put the ``EntityLike``.
        :param name: Either a string reprenting the name of an ``Entity``, or an
            :py:class:`.EntityLike` instance.
        :param copy: Whether or not to create a copy of the passed in
            ``EntityLike``. If ``name`` is a string name of an entity, this
            option is ignored and a new instance is always created.
        :param merge: Whether or not to merge entities of the same type at the
            same position. Merged entities share non-overlapping attributes and
            prefer the attributes of the last entity added. Useful for merging
            things like rails or power-poles on the edges of tiled blueprints.
        :param if_unknown: The behavior this method should perform if ``name``
            is not recognized as any known valid entity. See TODO for a more
            complete explanation.
        :param kwargs: Any other keyword arguments to pass to the entity
            instance. This is used primarily when constructing a new entity from
            a string name, but can also be used to overwrite certain attributes
            of a passed in ``EntityLike`` before adding it to the ``EntityList``.

        :example:

        .. code-block:: python

            blueprint = Blueprint()
            assert isinstance(blueprint.entities, EntityList)

            # Insert Entity instance
            blueprint.entities.insert(0, Container("steel-chest"))
            assert blueprint.entities[0].name == "steel-chest"

            # Insert shorthand
            blueprint.entities.insert(1, "wooden-chest", tile_position=(1, 1))
            assert blueprint.entities[1].name == "wooden-chest"
            assert blueprint.entities[1].tile_position == {"x": 1, "y": 1}

            # Key indexing
            blueprint.entities.insert(
                0, TransportBelt(id = "some_id", tile_position=(1, 0))
            )
            assert isinstance(blueprint.entities["some_id"], TransportBelt)

            # No copy
            inserter = Inserter("fast-inserter", tile_position=(0, 1))
            blueprint.entities.insert(0, inserter, copy=False)
            inserter.stack_size_override = 1
            assert inserter is blueprint.entities[0]
            assert blueprint.entities[0].stack_size_override == 1
        """
        # Convert to new Entity if constructed via string keyword
        new = False
        if isinstance(name, str):
            entitylike = new_entity(name, **kwargs, if_unknown=if_unknown)
            if entitylike is None:
                return
            new = True
        else:
            entitylike = name

        if copy and not new:
            # Create a DEEPcopy of the entity if desired
            entitylike = deepcopy(entitylike)
            # Overwrite any user keywords if specified in the function signature
            for k, v in kwargs.items():
                setattr(entitylike, k, v)

        # If we attempt to merge an entitylike that isn't a copy, bad things
        # will probably happen
        # Not really sure what *should* happen in that case, so lets just nip
        # that in the bud for now
        if not copy and merge:
            raise ValueError(
                "Attempting to merge a non-copy, which is disallowed (for now at least)"
            )

        # Do a set of idiot checks on the entity to make sure everything's okay
        self.check_entitylike(entitylike)

        # Here we issue warnings for overlapping entities, modify existing
        # entities if merging is enabled and delete excess entities in entitylike
        if self.validate_assignment:
            self.spatial_map.validate_insert(entitylike, merge)

        # If no errors, add this to hashmap (as well as any of it's children),
        # merging as necessary
        entitylike = self.spatial_map.recursive_add(entitylike, merge)

        if entitylike is None:  # input entitylike was entirely merged
            return  # exit without adding to list

        # Once the parent has itself in order, we can update our data
        self._root.insert(idx, entitylike)
        self._shift_key_indices(idx, 1)
        if entitylike.id:
            self._set_key(entitylike.id, entitylike)

        # We make sure the entity we just added points to the correct parent now
        # that it's inserted
        entitylike._parent = self._parent

    def recursive_remove(self, item: "EntityLike") -> None:
        """
        Removes an EntityLike from the EntityList. Recurses through any
        subgroups to see if ``item`` is there, removing the root-most entity
        first.

        :raises ValueError: If unable to locate the passed in entity anywhere
            in the ``EntityList``.
        """
        # First, try to delete the item from this list
        try:
            del self[self.index(item)]
            return
        except ValueError:
            pass

        # Then, try to delete the item from any sublists
        for existing_item in self._root:
            # if isinstance(existing_item, EntityCollection): # better, but impossible
            if hasattr(existing_item, "entities"):  # FIXME: somewhat unsafe
                try:
                    existing_item.entities.remove(item)
                    return
                except ValueError:
                    pass

        # If we've made it this far, it's not anywhere in the list, nested or otherwise
        raise ValueError

    def check_entitylike(self, entitylike: "EntityLike"):
        """
        A set of universal checks that all :py:class:`.EntityLike`s have to
        follow if they are to be added to this ``EntityList``.

        Raises :py:class:`.HiddenEntityWarning` if the ``EntityLike`` being
        checked is marked as hidden.

        :param entitylike: ``EntityLike`` instance to check.

        :exception TypeError: If ``entitylike`` is not an ``EntityLike``
            instance.
        :exception DuplicateIDError: If ``entitylike.id`` is already taken in
            the ``EntityList``.
        """
        if not isinstance(entitylike, EntityLike):
            raise TypeError("Entry in EntityList must be an EntityLike")

        if entitylike.id is not None and entitylike.id in self.key_map:
            raise DuplicateIDError(entitylike.id)

        # Warn if the placed entity is hidden
        # TODO: move this elsewhere, perhaps to entity itself in case the user
        # accidentally creates an instance of a hidden entity
        # If not in the entity itself it would likely live in the `Format` of
        # this class
        # if getattr(entitylike, "hidden", False):
        #     warnings.warn(
        #         "Attempting to add hidden entity '{}'".format(entitylike.name),
        #         HiddenEntityWarning,
        #         stacklevel=2,
        #     )

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

    def union(self, other: "EntityList") -> "EntityList":
        """
        TODO
        """
        new_entity_list = EntityList()

        for entity in self:
            new_entity_list.append(entity)
            new_entity_list[-1]._parent = None

        for other_entity in other:
            already_in = False
            for entity in self:
                if entity == other_entity:
                    already_in = True
                    break
            if not already_in:
                new_entity_list.append(other_entity)

        return new_entity_list

    def intersection(self, other: "EntityList") -> "EntityList":
        """
        TODO
        """
        new_entity_list = EntityList()

        for entity in self:
            in_both = False
            for other_entity in other:
                if other_entity == entity:
                    in_both = True
                    break
            if in_both:
                new_entity_list.append(entity)

        return new_entity_list

    def difference(self, other: "EntityList") -> "EntityList":
        """
        TODO
        """
        new_entity_list = EntityList()

        for entity in self:
            different = True
            for other_entity in other:
                if other_entity == entity:
                    different = False
                    break
            if different:
                new_entity_list.append(entity)

        return new_entity_list

    def clear(self):
        del self._root[:]
        self.key_map.clear()
        self.key_to_idx.clear()
        self.idx_to_key.clear()
        self.spatial_map.clear()

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:
        mode = ValidationMode(mode)

        output = ValidationResult([], [])

        if mode is ValidationMode.NONE or (self.is_valid and not force):
            return output

        context: dict[str, Any] = {
            "mode": mode,
            "object": self,
            "warning_list": [],
            "assignment": False,
        }

        try:
            result = self.Format.model_validate(
                {"root": self._root},
                strict=False,  # TODO: ideally this should be strict
                context=context,
            )
            # Reassign private attributes
            # Acquire the newly converted data
            self._root = result["root"]
        except ValidationError as e:  # pragma: no coverage
            output.error_list.append(DataFormatError(e))

        output.warning_list += context["warning_list"]

        return output

    # =========================================================================
    # Metamethods
    # =========================================================================

    def __getitem__(
        self, item: Union[int, str, slice, tuple]
    ) -> Union[EntityLike, list[EntityLike]]:
        if isinstance(item, (list, tuple)):
            new_base = self[item[0]]
            item = item[1:]
            if len(item) == 1:
                item = item[0]
            return new_base.entities[item]  # Raises AttributeError or KeyError
        elif isinstance(item, (int, slice)):
            return self._root[item]  # Raises IndexError
        else:
            return self.key_map[item]  # Raises KeyError

    @reissue_warnings
    def __setitem__(self, item: Union[int, str], value: "EntityLike"):
        # TODO: handle slices

        # Get the key and index of the item
        idx, key = self.get_pair(item)

        # Make sure were not causing any problems by putting this entity in
        self.check_entitylike(value)

        # Remove the entity and its children
        self.spatial_map.recursive_remove(self._root[idx])

        # Check for overlapping entities
        if self.validate_assignment:
            self.spatial_map.validate_insert(value, False)

        # Add the new entity and its children
        self.spatial_map.recursive_add(value, False)

        # Set the new data association in the list side
        self._root[idx] = value

        # If the element has a new id, set it to that
        if key:
            self._remove_key(key)
        if value.id:
            # key = getattr(value, "id")
            self._set_key(value.id, value)

        # Add a reference to the parent in the object
        value._parent = self._parent

    def __delitem__(self, item: Union[int, str]):
        if isinstance(item, slice):
            # Get slice parameters
            start, stop, step = item.indices(len(self))
            for i in range(start, stop, step):
                # Get pair
                idx, key = self.get_pair(i)

                # Remove the entity and its children
                self.spatial_map.recursive_remove(self._root[idx])

                # Remove key pair
                self._remove_key(key)

            for i in range(start, stop, step):
                # Shift elements above down by slice.step
                self._shift_key_indices(i, -step)

            # Delete all entries in the main list
            del self._root[item]
        else:
            # Get pair
            if isinstance(item, int):
                item %= len(self._root)
            idx, key = self.get_pair(item)

            # Remove the entity and its children
            self.spatial_map.recursive_remove(self._root[idx])

            # Delete from list
            del self._root[idx]

            # Remove key pair
            self._remove_key(key)

            # Shift all entries above down by one
            self._shift_key_indices(idx, -1)

    def __len__(self) -> int:
        return len(self._root)
    
    __iter__: Callable[..., Iterator[EntityLike]]

    def __contains__(self, item: EntityLike) -> bool:
        if item in self._root:
            return True
        else:  # Check every entity for sublists
            for entity in self._root:
                if hasattr(entity, "entities"):
                    if item in entity.entities:  # recurse
                        return True
        # Nothing was found
        return False

    def __or__(self, other: "EntityList") -> "EntityList":
        return self.union(other)

    # def __ior__(self, other: "EntityList") -> None:
    #     self.union(other)

    def __and__(self, other: "EntityList") -> "EntityList":
        return self.intersection(other)

    # def __iand__(self, other: "EntityList") -> None:
    #     self.intersection(other)

    def __sub__(self, other: "EntityList") -> "EntityList":
        return self.difference(other)

    # def __isub__(self, other: "EntityList") -> None:
    #     self.difference(other)

    def __eq__(self, other: "EntityList") -> bool:
        if not isinstance(other, EntityList):
            return False

        if len(self._root) != len(other._root):
            return False

        for i in range(len(self._root)):
            if self._root[i] != other._root[i]:
                return False

        return True

    def __deepcopy__(self, memo: dict) -> "EntityList":
        """
        Creates a deepcopy of the EntityList. Also copies Associations such that
        they are preserved.

        Deepcopying a raw EntityList will usually lead to complications, as
        EntityLists were not designed to point to the same parent at the same
        time; thus, if you specify the key ``"new_parent"`` in the ``memo`` dict,
        the new EntityList will automatically be created with that object as
        it's parent. This is bootleg as *fuck*, but it works for now.
        """
        # If we've already deepcopied this list, no sense doing it twice
        # if id(self) in memo:
        #     return memo[id(self)]

        # We create a new list with no parent; this is important because we
        # don't want two EntityLists pointing at the same parent, as this often
        # leads to overlapping entity warnings
        # Anything to do with EntityCollection specific things has to be
        # performed AFTER the deepcopy manually by the caller
        parent = memo.get("new_parent", self._parent)
        new = EntityList(parent)

        # First, we make a copy of all entities in self.data and assign them to
        # a new entity list while keeping track of which new entity corresponds
        # to which old entity
        for entity in self._root:
            entity_copy = memo.get(id(entity), deepcopy(entity, memo))
            new.append(entity_copy, copy=False)
            memo[id(entity)] = entity_copy

        def try_to_replace_association(old):
            try:
                return Association(memo[id(old())])
            except KeyError:
                # The association must belong outside of the copied region
                raise InvalidAssociationError(
                    "Attempting to connect to {} which lies outside this "
                    "EntityCollection; are all Associations between entities "
                    "contained within this EntityCollection being copied?".format(
                        repr(old())
                    )
                )

        # Then, we iterate over all the associations in every Entity in the new
        # EntityList and replace them with associations to the new Entities
        for entity in new:
            # swap linked position lmao
            # entity._position.linked = entity._tile_position
            # entity._tile_position.linked = entity._position
            if hasattr(entity, "connections"):
                connections: Connections = entity.connections
                for side in connections.true_model_fields():
                    if connections[side] is None:
                        continue
                    if side in {"1", "2"}:
                        for color, _ in connections[side]:
                            connection_points = connections[side][color]
                            if connection_points is None:
                                continue
                            for point in connection_points:
                                old = point["entity_id"]
                                point["entity_id"] = try_to_replace_association(old)
                    elif side in {"Cu0", "Cu1"}:  # pragma: no branch
                        connection_points = connections[side]
                        for point in connection_points:
                            old = point["entity_id"]
                            point["entity_id"] = try_to_replace_association(old)
            if hasattr(entity, "neighbours"):
                neighbours = entity.neighbours
                for i, neighbour in enumerate(neighbours):
                    neighbours[i] = try_to_replace_association(neighbour)

        return new

    def __repr__(self) -> str:  # pragma: no coverage
        return "<EntityList>{}".format(self._root)

    @classmethod
    def __get_pydantic_core_schema__(  # pragma: no coverage
        cls, _source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, handler(list[dict])  # TODO: correct annotation
        )  # pragma: no coverage

    # =========================================================================
    # Internal functions
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
        if key in self.key_map:
            raise DuplicateIDError("'{}'".format(key))
        idx = self._root.index(value)
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
