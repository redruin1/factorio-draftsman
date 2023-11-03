# request_items.py

from draftsman import signatures
from draftsman.data import items
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import ValidationMode
from draftsman.signatures import DraftsmanBaseModel, SignalID, uint32, get_suggestion
from draftsman.utils import reissue_warnings
from draftsman.warning import ItemLimitationWarning, UnknownItemWarning

from pydantic import Field, ValidationInfo, field_validator
from copy import deepcopy

from typing import Optional, Union


class RequestItemsMixin:
    """
    Enables an entity to request items during its construction. Note that this
    is *not* for Logistics requests such as requester and buffer chests (that's
    what :py:class:`~.mixins.request_filters.RequestFiltersMixin` is for).
    Instead this is for specifying additional construction components, things
    like speed modules for beacons or productivity modules for assembling
    machines.
    """

    class Format(DraftsmanBaseModel):
        items: Optional[dict[str, uint32]] = Field(
            {},
            description="""
            List of construction item requests (such as delivering modules for 
            beacons). Distinct from logistics requests, which are a separate 
            system.
            """,
        )

        @field_validator("items")
        @classmethod
        def validate_items_exist(
            cls, value: Optional[dict[str, int]], info: ValidationInfo
        ):
            """
            Issue warnings if Draftsman cannot recognize the set item.
            """
            if not info.context or value is None:
                return value
            if info.context["mode"] is ValidationMode.MINIMUM:
                return value

            warning_list: list = info.context["warning_list"]
            for k, _ in value.items():
                if k not in items.raw:
                    issue = UnknownItemWarning(
                        "Unknown item '{}'{}".format(
                            k, get_suggestion(k, items.raw.keys())
                        )
                    )
                    if info.context["mode"] == "pedantic":
                        raise issue
                    else:
                        warning_list.append(issue)

            return value

        @field_validator("items")
        @classmethod
        def ensure_in_allowed_items(
            cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        ):
            """
            Warn the user if they set a fuel item that is disallowed for this
            particular entity.
            """
            if not info.context or value is None:
                return value
            if info.context["mode"] is ValidationMode.MINIMUM:
                return value

            entity: "RequestItemsMixin" = info.context["object"]
            warning_list: list = info.context["warning_list"]

            print(entity.allowed_items)

            if entity.allowed_items is None:  # entity not recognized
                return value

            for item in entity.items:
                if item not in entity.allowed_items:
                    issue = ItemLimitationWarning(
                        "Cannot request item '{}' to '{}'; this entity cannot recieve it".format(
                            item, entity.name
                        )
                    )

                    warning_list.append(issue)

            return value

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.items = kwargs.get("items", {})

    # =========================================================================

    @property  # TODO abstractproperty
    def allowed_items(self) -> Optional[set[str]]:
        pass  # return set()

    # =========================================================================

    @property
    def items(self) -> Optional[dict[str, uint32]]:
        """
        TODO
        """
        return self._root.items

    @items.setter
    def items(self, value: dict[str, uint32]):
        if self.validate_assignment:
            # Set the value beforehand, so the new value is available to the
            # validation step
            self._root.items = value  # TODO: FIXME, this is bad
            value = attempt_and_reissue(
                self, type(self).Format, self._root, "items", value
            )

        if value is None:
            self._root.items = {}
        else:
            self._root.items = value

    # =========================================================================

    @reissue_warnings
    def set_item_request(self, item: str, count: Optional[uint32]):  # TODO: ItemID
        """
        Requests an amount of an item. Removes the item request if ``count`` is
        set to ``0`` or ``None``. Manages ``module_slots_occupied``.

        Raises a number of warnings if the requested item is mismatched for the
        type of entity you're requesting items for. For example,
        :py:class:`.ModuleLimitationWarning` will be raised when requesting an
        item that is not a module to a Beacon entity.

        :param item: The string name of the requested item.
        :param count: The desired amount of that item.

        :exception TypeError: If ``item`` is anything other than a ``str``, or
            if ``count`` is anything other than an ``int`` or ``None``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception ValueError: If ``count`` is less than zero.
        """
        if count is None:
            count = 0

        if not isinstance(item, str):  # TODO: better
            raise TypeError("Expected 'item' to be a str, found '{}'".format(item))
        if not isinstance(count, int):  # TODO: better
            raise TypeError("Expected 'count' to be an int, found '{}'".format(count))

        if count == 0:
            self.items.pop(item, None)
        else:
            self.items[item] = count

        self._root.items = attempt_and_reissue(
            self, type(self).Format, self._root, "items", self.items
        )

    # =========================================================================

    def merge(self, other: "RequestItemsMixin"):
        super().merge(other)

        self.items = deepcopy(other.items)

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.items == other.items
