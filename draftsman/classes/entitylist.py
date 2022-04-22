# entitylist.py

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
    TODO
    """

    @utils.reissue_warnings
    def __init__(self, parent, initlist=None):
        # type: (EntityCollection, Any) -> None
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
    def append(self, entity, **kwargs):
        # type: (EntityLike, **dict) -> None
        """
        Appends the EntityLike to the end of the sequence.
        """
        self.insert(len(self.data), entity, **kwargs)

    @utils.reissue_warnings
    def insert(self, idx, entity, copy=True, **kwargs):
        # type: (int, EntityLike, bool, **dict) -> None
        """
        Inserts an element into the EntityList. If the added entity has an "id"
        attribute, the key_map is automatically set to point to the same entity.
        """
        # Determine the id of the input entity
        entity_id = None
        if "id" in kwargs:
            entity_id = kwargs["id"]
        elif hasattr(entity, "id"):
            entity_id = entity.id

        # Convert to Entity if constructed via keyword
        if isinstance(entity, six.string_types):
            entity = new_entity(six.text_type(entity), **kwargs)
        else:
            # Create a DEEPCopy of the entity if desired
            if copy:
                entity = deepcopy(entity)

        # Make sure were not causing any problems by putting this entity in
        self.check_entity(entity)

        # If the entity has any custom logic, perform that now
        entity.on_insert()

        # If the parent has any custom logic, perform that now
        self._parent.on_entity_insert(entity)

        # Manage the EntityList
        self.data.insert(idx, entity)
        self._shift_key_indices(idx, 1)
        if entity_id:
            self.set_key(entity_id, entity)

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
        # TODO: maybe make it possible for this function to take string keys?

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
            key = getattr(value, "id")
            self.set_key(key, value)

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

    def check_entity(self, entity):
        # type: (EntityLike) -> None
        """
        Check to see if adding the entity to the EntityList would cause any
        problems. Raises errors and warnings.
        """
        if not isinstance(entity, EntityLike):
            raise TypeError("Entry in EntityList must be an EntityLike")

        if entity.id is not None and entity.id in self.key_map:
            raise DuplicateIDError(entity.id)

        # Warn if the placed entity is hidden
        if getattr(entity, "hidden", False):
            warnings.warn("{}".format(type(entity)), HiddenEntityWarning, stacklevel=2)

    def remove_key(self, key):
        # type: (str) -> None
        """
        Removes the key from the key mapping dicts.
        """
        if key is not None:
            idx = self.key_to_idx[key]
            del self.key_map[key]
            del self.key_to_idx[key]
            del self.idx_to_key[idx]

    def set_key(self, key, value):
        # type: (str, Any) -> None
        """
        Sets a key in the key mapping structures such that they point to
        `value`.
        """
        idx = self.data.index(value)
        self.key_map[key] = value
        self.key_to_idx[key] = idx
        self.idx_to_key[idx] = key

    def get_pair(self, item):
        # type: (Union[int, str]) -> tuple[int, str]
        """
        Gets the converse key or index and returns them both as a pair.
        """
        if isinstance(item, six.string_types):
            return (self.key_to_idx[six.text_type(item)], item)
        else:
            return (item, self.idx_to_key.get(item, None))

    def _shift_key_indices(self, idx, amt):
        # type: (int, int) -> None
        """
        Shifts all of the key mappings above `idx` by `amt`. Used when
        inserting or removing elements before the end, which moves what index
        each key should point to.
        """
        for key in self.key_map:
            old_idx = self.key_to_idx[key]
            if old_idx >= idx:
                new_idx = old_idx + amt
                self.key_to_idx[key] = new_idx
                del self.idx_to_key[old_idx]
                self.idx_to_key[new_idx] = key
