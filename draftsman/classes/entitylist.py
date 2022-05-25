# entitylist.py
# -*- encoding: utf-8 -*-

from draftsman.classes.entitylike import EntityLike
from draftsman.entity import new_entity
from draftsman.error import DuplicateIDError
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
    Custom object for storing sequences of
    :py:class:`~draftsman.classes.entitylike.EntityLike`.

    Contains all the functionality of a normal ``list``. Adds the ability
    to index with id strings, as well as extra framework for interfacing with
    :py:class:`~draftsman.classes.collection.EntityCollection` classes.
    """

    @utils.reissue_warnings
    def __init__(self, parent, initlist=None):
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
    def append(self, entity, copy=True, **kwargs):
        # type: (EntityLike, bool, **dict) -> None
        """
        Appends the ``EntityLike`` to the end of the sequence.

        Supports an optional shorthand where you can specify the string name of
        an Entity as ``entity`` and any keyword arguments, which are appended to
        the constructor of that entity.

        :param entity: Either an instance of ``EntityLike``, or a string
            reprenting the name of an Entity.
        :param copy: Whether or not to create a copy of the passed in
            ``EntityLike``. If ``entity`` is in string shorthand, this option
            is ignored and a new instance is always created.
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
        self.insert(len(self.data), entity, copy=copy, **kwargs)

    @utils.reissue_warnings
    def insert(self, idx, entity, copy=True, **kwargs):
        # type: (int, EntityLike, bool, **dict) -> None
        """
        Inserts an ``EntityLike`` into the sequence.

        Supports an optional shorthand where you can specify the string name of
        an Entity as ``entity`` and any keyword arguments, which are appended to
        the constructor of that entity.

        :param idx: The integer index to put the ``EntityLike``.
        :param entity: Either an instance of ``EntityLike``, or a string
            reprenting the name of an Entity.
        :param copy: Whether or not to create a copy of the passed in
            ``EntityLike``. If ``entity`` is in string shorthand, this option
            is ignored and a new instance is always created.
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

        # Convert to Entity if constructed via keyword
        if isinstance(entity, six.string_types):
            entity = new_entity(six.text_type(entity), **kwargs)
        else:
            # Create a DEEPCopy of the entity if desired
            if copy:
                entity = deepcopy(entity)

        # Determine the id of the input entity
        # entity_id = None
        # if "id" in kwargs:
        #     entity_id = kwargs["id"]
        # elif entity.id: #hasattr(entity, "id")
        #     entity_id = entity.id

        # Make sure were not causing any problems by putting this entity in
        self.check_entity(entity)

        # If the entity has any custom logic, perform that now
        entity.on_insert()

        # If the parent has any custom logic, perform that now
        self._parent.on_entity_insert(entity)

        # Manage the EntityList
        self.data.insert(idx, entity)
        self._shift_key_indices(idx, 1)
        if entity.id:
            self.set_key(entity.id, entity)

        # Add a reference to the parent in the object
        entity._parent = self._parent

    def __getitem__(self, item):
        # type: (Union[int, str, slice]) -> Union[EntityLike, list[EntityLike]]
        if isinstance(item, (list, tuple)):
            new_base = self.key_map[item[0]]
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
        self.check_entity(value)

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

        self._parent.recalculate_area()

    def __delitem__(self, item):
        # type: (Union[int, str]) -> None
        if isinstance(item, slice):
            # Get slice parameters
            start, stop, step = item.indices(len(self))
            for i in range(start, stop, step):
                # Get pair
                idx, key = self.get_pair(i)

                # Handle EntityLike
                self.data[idx].on_remove()

                # Handle parent
                self._parent.on_entity_remove(self.data[idx])

                # Remove key pair
                self.remove_key(key)

            for i in range(start, stop, step):
                # Shift elements above down by slice.step
                self._shift_key_indices(i, -step)

            # Delete all entries in the main list
            del self.data[item]

            self._parent.recalculate_area()
        else:
            # Get pair
            if isinstance(item, int):
                item %= len(self.data)
            idx, key = self.get_pair(item)

            # Handle EntityLike
            self.data[idx].on_remove()

            # Handle parent
            self._parent.on_entity_remove(self.data[idx])

            # Delete from list
            del self.data[idx]

            # Remove key pair
            self.remove_key(key)

            # Shift all entries above down by one
            self._shift_key_indices(idx, -1)

            self._parent.recalculate_area()

    def __len__(self):
        # type: () -> int
        return len(self.data)

    def check_entity(self, entitylike):
        # type: (EntityLike) -> None
        """
        Check to see if adding the entity to the EntityList would cause any
        problems.

        Raises :py:class:`~draftsman.warning.HiddenEntityWarning` if the
        ``Entity`` is marked as hidden.

        :param entitylike: ``EntityLike`` instance to check.

        :exception TypeError: If ``entitylike`` is not an ``EntityLike``
            instance.
        :exception DuplicateIDError: If ``entitylike.id`` already exists in the
            ``EntityList``
        """
        if not isinstance(entitylike, EntityLike):
            raise TypeError("Entry in EntityList must be an EntityLike")

        if entitylike.id is not None and entitylike.id in self.key_map:
            raise DuplicateIDError(entitylike.id)

        # Warn if the placed entity is hidden
        if getattr(entitylike, "hidden", False):
            warnings.warn(
                "{}".format(type(entitylike)), HiddenEntityWarning, stacklevel=2
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
        for key in self.key_map:
            old_idx = self.key_to_idx[key]
            if old_idx >= idx:
                new_idx = old_idx + amt
                self.key_to_idx[key] = new_idx
                # del self.idx_to_key[old_idx]
                # # self.idx_to_key.pop(old_idx)
                # self.idx_to_key[new_idx] = key

        # Reconstruct idx_to_key
        self.idx_to_key = {}
        for key in self.key_to_idx:
            self.idx_to_key[self.key_to_idx[key]] = key
