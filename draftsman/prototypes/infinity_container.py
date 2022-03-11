# infinity_container.py

from draftsman.prototypes.mixins import Entity
from draftsman.error import InvalidItemError
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import infinity_containers
from draftsman.data import items

import warnings


class InfinityContainer(Entity):
    """
    """
    def __init__(self, name = infinity_containers[0], **kwargs):
        # type: (str, **dict) -> None
        super(InfinityContainer, self).__init__(
            name, infinity_containers, **kwargs
        )

        self.infinity_settings = {}
        if "infinity_settings" in kwargs:
            self.set_infinity_settings(kwargs["infinity_settings"])
            self.unused_args.pop("infinity_settings")
        self._add_export("infinity_settings", lambda x: len(x) != 0)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )
    
    def set_infinity_settings(self, settings):
        # type: (dict) -> None
        """
        """
        if settings is None:
            self.infinity_settings = {}
        else:
            self.infinity_settings = signatures.INFINITY_CONTAINER.validate(settings)

    def set_remove_unfiltered_items(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.infinity_settings.pop("remove_unfiltered_items", None)
        else:
            self.infinity_settings["remove_unfiltered_items"] = signatures.BOOLEAN.validate(value)

    def set_infinity_filters(self, filters):
        # type: (list) -> None
        """
        """
        # TODO: error checking
        if filters is None:
            self.infinity_settings.pop("filters", None)
        else:
            self.infinity_settings["filters"] = signatures.INFINITY_FILTERS.validate(filters)

    def set_infinity_filter(self, index, name, mode = "at-least", count = 0):
        # type: (int, str, str, int) -> None
        """
        """
        index = signatures.INTEGER.validate(index)
        name = signatures.STRING.validate(name)
        mode = signatures.STRING.validate(mode)
        count = signatures.INTEGER.validate(count)

        if name is not None and name not in items.raw:
            raise InvalidItemError(name)
        assert mode in {"at-least", "at-most", "exactly"}

        if "filters" not in self.infinity_settings:
            self.infinity_settings["filters"] = []

        # Check to see if filters already contains an entry with the same index
        for i, filter in enumerate(self.infinity_settings["filters"]):
            if index + 1 == filter["index"]: # Index already exists in the list
                if name is None: # Delete the entry
                    del self.infinity_settings["filters"][i]
                else: # Set the new value
                    self.infinity_settings["filters"][i] = {
                        "index": index + 1,
                        "name": name,
                        "count": count,
                        "mode": mode,
                    }
                return

        # If no entry with the same index was found
        self.infinity_settings["filters"].append({
            "name": name,
            "count": count,
            "mode": mode,
            "index": index + 1 
        })

        # Warn the user if the total number of filters exceeds 1000
        # if len(self.infinity_settings["filters"]) > 1000:
        #     warn_user()