# infinity_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.error import InvalidItemError, InvalidModeError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import infinity_containers
from draftsman.data import items

from schema import SchemaError
import six
import warnings


class InfinityContainer(Entity):
    """ """

    def __init__(self, name=infinity_containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(InfinityContainer, self).__init__(name, infinity_containers, **kwargs)

        self.infinity_settings = {}
        if "infinity_settings" in kwargs:
            self.infinity_settings = kwargs["infinity_settings"]
            self.unused_args.pop("infinity_settings")
        self._add_export("infinity_settings", lambda x: len(x) != 0)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def infinity_settings(self):
        # type: () -> dict
        """
        TODO
        """
        return self._infinity_settings

    @infinity_settings.setter
    def infinity_settings(self, value):
        # type: (dict) -> None
        if value is None:
            self._infinity_settings = {}
        else:
            try:
                value = signatures.INFINITY_CONTAINER.validate(value)
                self._infinity_settings = value
            except SchemaError:
                # TODO: more verbose
                raise TypeError("Invalid infinity_settings format")

    # =========================================================================

    @property
    def remove_unfiltered_items(self):
        # type: () -> bool
        """
        TODO
        """
        return self.infinity_settings.get("remove_unfiltered_items", None)

    @remove_unfiltered_items.setter
    def remove_unfiltered_items(self, value):
        # type: (bool) -> None
        if value is None:
            self.infinity_settings.pop("remove_unfiltered_items", None)
        elif isinstance(value, bool):
            self.infinity_settings["remove_unfiltered_items"] = value
        else:
            raise TypeError("'remove_unfiltered_items' must be a bool or None")

    # =========================================================================

    def set_infinity_filter(self, index, name, mode="at-least", count=0):
        # type: (int, str, str, int) -> None
        """ """

        try:
            index = signatures.INTEGER.validate(index)
            name = signatures.STRING_OR_NONE.validate(name)
            mode = signatures.STRING.validate(mode)
            count = signatures.INTEGER.validate(count)
        except SchemaError as e:
            six.raise_from(TypeError(e), None)

        if not 0 <= index < 1000:
            raise IndexError("Filter index {} not in range [0, 1000)")
        if name is not None and name not in items.raw:
            raise InvalidItemError(name)
        if mode not in {"at-least", "at-most", "exactly"}:
            raise InvalidModeError(mode)

        if "filters" not in self.infinity_settings:
            self.infinity_settings["filters"] = []

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.infinity_settings["filters"]):
            if index + 1 == filter["index"]:  # Index already exists in the list
                if name is None:  # Delete the entry
                    del self.infinity_settings["filters"][i]
                else:  # Set the new value
                    self.infinity_settings["filters"][i] = {
                        "index": index + 1,
                        "name": name,
                        "count": count,
                        "mode": mode,
                    }
                return

        # If no entry with the same index was found
        self.infinity_settings["filters"].append(
            {"name": name, "count": count, "mode": mode, "index": index + 1}
        )

    def set_infinity_filters(self, filters):
        # type: (list) -> None
        """ """
        # TODO: error checking
        if filters is None:
            self.infinity_settings.pop("filters", None)
        else:
            self.infinity_settings["filters"] = signatures.INFINITY_FILTERS.validate(
                filters
            )
