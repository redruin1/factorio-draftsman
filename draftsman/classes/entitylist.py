# entitylist.py
# -*- encoding: utf-8 -*-

from draftsman.classes.association import Association
from draftsman.classes.entitylike import EntityLike
from draftsman.entity import new_entity
from draftsman.error import DuplicateIDError, InvalidAssociationError
from draftsman import utils
from draftsman.warning import HiddenEntityWarning

try:  # pragma: no coverage
    from collections.abc import MutableSequence
except ImportError:  # pragma: no coverage
    from collections import MutableSequence
from copy import deepcopy
import six
from typing import Union, Any, TYPE_CHECKING
import warnings

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import EntityCollection


class EntityList(MutableSequence):
    """
    Custom object for storing sequences of :py:class:`.EntityLike`.

    Contains all the functionality of a normal ``list``. Adds the ability
    to index with id strings, as well as extra framework for interfacing with
    :py:class:`.EntityCollection` classes.
    """

    @utils.reissue_warnings
    def __init__(self, parent=None, initlist=None):
        # type: (EntityCollection, Any) -> None
        """
        Instantiates a new ``EntityList``.

        :param parent: The parent object that contains the EntityList; used when
            assigning the ``parent`` to entities when inserted.
        :param initlist: A list containing data to initialize with.

        :exception TypeError: If any of the entries in ``initlist`` are neither
            a ``dict`` nor an ``EntityLike``.
        """
        self.data = []
        self.key_map = {}
        self.key_to_idx = {}
        self.idx_to_key = {}

        self._parent = parent

        if initlist is not None:
            for elem in initlist:
                if isinstance(elem, EntityLike):
                    self.append(elem)
                elif isinstance(elem, dict):
                    name = elem.pop("name")
                    self.append(name, **elem)
                else:
                    raise TypeError(
                        "Constructor either takes EntityLike or dict entries"
                    )

    @utils.reissue_warnings
    def append(self, name, copy=True, merge=False, **kwargs):
        # type: (Union[str, EntityLike], bool, bool, **dict) -> None
        """
        Appends the ``EntityLike`` to the end of the sequence.

        Supports an optional shorthand where you can specify the string name of
        an Entity as ``entity`` and any keyword arguments, which are appended to
        the constructor of that entity.

        :param name: Either a string reprenting the name of an ``Entity``, or an
            :py:class:`.EntityLike` instance.
        :param copy: Whether or not to create a copy of the passed in
            ``EntityLike``. If ``entitylike`` is in string shorthand, this
            option is ignored and a new instance is always created.
        :param merge: Whether or not to merge entities of the same type at the
            same position. Merged entities share non-overlapping attributes and
            prefer the attributes of the last entity added. Useful for merging
            things like rails or power-poles on the edges of tiled blueprints.
        :param kwargs: Any other keyword arguments to pass to the constructor
            in string shorthand.

        .. NOTE::

            Keyword arguments are only considered if ``entity`` is a string:

            .. code-block:: python

                test_inserter = Inserter("fast-inserter")
                blueprint.entities.append(test_inserter, id="test")
                # Prints "None" because id was never set in test_inserter
                print(blueprint.entities[-1].id)

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
        self.insert(len(self.data), name, copy=copy, merge=merge, **kwargs)

    @utils.reissue_warnings
    def insert(self, idx, name, copy=True, merge=False, **kwargs):
        # type: (int, Union[str, EntityLike], bool, bool, **dict) -> None
        """
        Inserts an ``EntityLike`` into the sequence.

        Supports an optional shorthand where you can specify the string name of
        an Entity as ``entity`` and any keyword arguments, which are appended to
        the constructor of that entity.

        :param idx: The integer index to put the ``EntityLike``.
        :param name: Either a string reprenting the name of an ``Entity``, or an
            :py:class:`.EntityLike` instance.
        :param copy: Whether or not to create a copy of the passed in
            ``EntityLike``. If ``entitylike`` is in string shorthand, this
            option is ignored and a new instance is always created.
        :param merge: Whether or not to merge entities of the same type at the
            same position. Merged entities share non-overlapping attributes and
            prefer the attributes of the last entity added. Useful for merging
            things like rails or power-poles on the edges of tiled blueprints.
        :param kwargs: Any other keyword arguments to pass to the constructor
            in string shorthand.

        .. NOTE::

            Keyword arguments are only considered if ``entity`` is a string:

            .. code-block:: python

                test_inserter = Inserter("fast-inserter")
                blueprint.entities.insert(0, test_inserter, id="test")
                # Prints "None" because id was never set in test_inserter
                print(blueprint.entities[-1].id)

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
        if isinstance(name, six.string_types):
            entitylike = new_entity(name, **kwargs)
            new = True
        else:
            entitylike = name

        if copy and not new:
            # Create a DEEPCopy of the entity if desired
            entitylike = deepcopy(entitylike)

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

        # In general, the parent entity is in charge of issuing Collection-
        # specific warnings and errors, such as OverlappingObjectsWarnings and
        # handling it's spatial map, if desired. The parent is also in charge of
        # handling per-entity warnings, as that information is more closely tied
        # to the parent than the `EntityList`.
        # To keep data consistency, any changes made to the passed in entitylike
        # during the course of the function are persistent afterwards.
        entitylike = self._parent.on_entity_insert(entitylike, merge)

        if entitylike is None:  # input entity was entirely merged
            return  # exit without adding to list

        # Once the parent has itself in order, we can update our data
        self.data.insert(idx, entitylike)
        self._shift_key_indices(idx, 1)
        if entitylike.id:
            self.set_key(entitylike.id, entitylike)

        # We make sure the entity we just added points to the correct parent now
        # that it's inserted
        entitylike._parent = self._parent

    def recursive_remove(self, item):
        # type: (EntityLike) -> None
        """
        Removes an EntityLike from the EntityList. Recurses through any
        subgroups to see if ``item`` is there, removing the root-most entity
        first.
        """
        # First, try to delete the item from this list
        try:
            del self[self.index(item)]
            return
        except ValueError:
            pass

        # Then, try to delete the item from any sublists
        for existing_item in self.data:
            # if isinstance(existing_item, EntityCollection): # better, but impossible
            if hasattr(existing_item, "entities"):  # FIXME: somewhat unsafe
                try:
                    existing_item.entities.remove(item)
                    return
                except ValueError:
                    pass

        # If we've made it this far, it's not anywhere in the list
        raise ValueError

    def __getitem__(self, item):
        # type: (Union[int, str, slice]) -> Union[EntityLike, list[EntityLike]]
        if isinstance(item, (list, tuple)):
            new_base = self[item[0]]
            item = item[1:]
            if len(item) == 1:
                item = item[0]
            return new_base.entities[item]  # Raises AttributeError or KeyError
        elif isinstance(item, (int, slice)):
            return self.data[item]  # Raises IndexError
        else:
            return self.key_map[item]  # Raises KeyError

    def clear(self):
        del self.data[:]
        self.key_map.clear()
        self.key_to_idx.clear()
        self.idx_to_key.clear()

    @utils.reissue_warnings
    def __setitem__(self, item, value):
        # type: (Union[int, str], EntityLike) -> None

        # Get the key and index of the item
        idx, key = self.get_pair(item)

        # Make sure were not causing any problems by putting this entity in
        self.check_entitylike(value)

        # Perform any logic that the parent has to do
        self._parent.on_entity_set(self.data[idx], value)

        # Set the new data association in the list side
        self.data[idx] = value

        # If the element has a new id, set it to that
        if key:
            self.remove_key(key)
        if value.id:
            # key = getattr(value, "id")
            self.set_key(value.id, value)

        # Add a reference to the parent in the object
        value._parent = self._parent

        # TODO: this sucks man
        self._parent.recalculate_area()

    def __delitem__(self, item):
        # type: (Union[int, str]) -> None
        if isinstance(item, slice):
            # Get slice parameters
            start, stop, step = item.indices(len(self))
            for i in range(start, stop, step):
                # Get pair
                idx, key = self.get_pair(i)

                # Handle parent
                self._parent.on_entity_remove(self.data[idx])

                # Remove key pair
                self.remove_key(key)

            for i in range(start, stop, step):
                # Shift elements above down by slice.step
                self._shift_key_indices(i, -step)

            # Delete all entries in the main list
            del self.data[item]

            # TODO: this sucks man
            self._parent.recalculate_area()
        else:
            # Get pair
            if isinstance(item, int):
                item %= len(self.data)
            idx, key = self.get_pair(item)

            # Handle parent
            self._parent.on_entity_remove(self.data[idx])

            # Delete from list
            del self.data[idx]

            # Remove key pair
            self.remove_key(key)

            # Shift all entries above down by one
            self._shift_key_indices(idx, -1)

            # TODO: this sucks man
            self._parent.recalculate_area()

    def __len__(self):
        # type: () -> int
        return len(self.data)

    def __contains__(self, item):
        # type: (EntityLike) -> bool
        if item in self.data:
            return True
        else:  # Check every entity for sublists
            for entity in self.data:
                if hasattr(entity, "entities"):
                    if item in entity.entities:  # recurse
                        return True
        # Nothing was found
        return False

    def __deepcopy__(self, memo):
        # type: (dict) -> EntityList
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

        # We create a new entity with no parent; this is important because we
        # don't want two EntityLists pointing at the same parent, as this often
        # leads to overlapping entity warnings
        # Anything to do with EntityCollection specific things has to be
        # performed AFTER the deepcopy manually by the caller
        parent = memo.get("new_parent", self._parent)
        new = EntityList(parent)

        # First, we make a copy of all entities in self.data and assign them to
        # a new entity list while keeping track of which new entity corresponds
        # to which old entity
        for entity in self.data:
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
            if hasattr(entity, "connections"):
                connections = entity.connections
                for side in connections:
                    if side in {"1", "2"}:
                        for color in connections[side]:
                            connection_points = connections[side][color]
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

    def check_entitylike(self, entitylike):
        # type: (EntityLike) -> None
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
        if getattr(entitylike, "hidden", False):
            warnings.warn(
                "Attempting to add hidden entity '{}'".format(type(entitylike)),
                HiddenEntityWarning,
                stacklevel=2,
            )

    def remove_key(self, key):
        # type: (str) -> None
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

    def set_key(self, key, value):
        # type: (str, EntityLike) -> None
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
        idx = self.data.index(value)
        self.key_map[key] = value
        self.key_to_idx[key] = idx
        self.idx_to_key[idx] = key

    def get_pair(self, item):
        # type: (Union[int, str]) -> tuple[int, str]
        """
        Takes either an index or a key, finds the converse entry associated with
        it, and returns them both as a pair.

        :param item: Either an integer index or a string key.

        :returns: A tuple of the format ``(index, key)``.

        :exception KeyError: If key ``item`` is not found in the key mapping
            dictionaries in the ``EntityList``.
        """
        if isinstance(item, six.string_types):
            return (self.key_to_idx[six.text_type(item)], item)
        else:
            return (item, self.idx_to_key.get(item, None))

    def _shift_key_indices(self, idx, amt):
        # type: (int, int) -> None
        """
        Shifts all of the key mappings above or equal to``idx`` by ``amt``. Used
        when inserting or removing elements before the end, which moves what
        index each key should point to.
        """

        # Shift the indices for key_to_idx
        self.key_to_idx = {
            key: old_idx + amt if old_idx >= idx else old_idx
            for key, old_idx in self.key_to_idx.items()
        }

        # Reconstruct idx_to_key
        self.idx_to_key = {value: key for key, value in self.key_to_idx.items()}
