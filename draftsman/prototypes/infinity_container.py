# infinity_container.py

from draftsman.prototypes.mixins import Entity
from draftsman.errors import InvalidEntityID, InvalidItemID
from draftsman.utils import warn_user
import draftsman.signatures as signatures

from draftsman.data.entities import infinity_containers
from draftsman.data import items


class InfinityContainer(Entity):
    """
    """
    def __init__(self, name: str = infinity_containers[0], **kwargs):
        if name not in infinity_containers:
            raise InvalidEntityID("'{}' is not a valid name for this type".format(name))
        super(InfinityContainer, self).__init__(name, **kwargs)

        self.infinity_settings = {}
        if "infinity_settings" in kwargs:
            self.set_infinity_settings(kwargs["infinity_settings"])
            self.unused_args.pop("infinity_settings")
        self._add_export("infinity_settings", lambda x: len(x) != 0)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))
    
    def set_infinity_settings(self, settings: dict) -> None:
        """
        """
        if settings is None:
            self.infinity_settings = {}
        else:
            self.infinity_settings = signatures.INFINITY_CONTAINER.validate(settings)

    def set_remove_unfiltered_items(self, value: bool) -> None:
        """
        """
        if value is None:
            self.infinity_settings.pop("remove_unfiltered_items", None)
        else:
            self.infinity_settings["remove_unfiltered_items"] = signatures.BOOLEAN.validate(value)

    def set_infinity_filters(self, filters: list) -> None:
        """
        """
        # TODO: error checking
        if filters is None:
            self.infinity_settings.pop("filters", None)
        else:
            self.infinity_settings["filters"] = signatures.INFINITY_FILTERS.validate(filters)

    def set_infinity_filter(self, index: int, name: str, mode: str = "at-least", count: int = 0) -> None:
        """
        """
        index = signatures.INTEGER.validate(index)
        name = signatures.STRING.validate(name)
        mode = signatures.STRING.validate(mode)
        count = signatures.INTEGER.validate(count)

        if name is not None and name not in items.all:
            raise InvalidItemID(name)
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