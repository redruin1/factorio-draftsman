# request_items.py

from draftsman import signatures
from draftsman.data import items
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.signatures import DraftsmanBaseModel, SignalID, uint32, ItemName
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
        items: Optional[dict[ItemName, uint32]] = Field(
            {},
            description="""
            List of construction item requests (such as delivering modules for 
            beacons). Distinct from logistics requests, which are a separate 
            system.
            """,
        )

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
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return value

            entity: "RequestItemsMixin" = info.context["object"]
            warning_list: list = info.context["warning_list"]

            if entity.allowed_items is None:  # entity not recognized
                return value

            for item in entity.items:
                if item not in entity.allowed_items:
                    warning_list.append(
                        ItemLimitationWarning(
                            "Cannot request item '{}' to '{}'; this entity cannot recieve it".format(
                                item, entity.name
                            )
                        )
                    )

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
            # In the validator functions for `items`, we use a lot of internal
            # properties that operate on the current items value instead of the
            # items value that we're setting
            # Thus, in order for those to work, we set the items to the new
            # value first, check for errors, and revert it back to the original
            # value if it fails for whatever reason
            try:
                original_items = self._root.items
                self._root.items = value
                value = attempt_and_reissue(
                    self, type(self).Format, self._root, "items", value
                )
            except DataFormatError as e:
                self._root.items = original_items
                raise e

        if value is None:
            self._root.items = {}
        else:
            self._root.items = value

    # =========================================================================

    @reissue_warnings
    def set_item_request(self, item: str, count: Optional[uint32]):
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

        # TODO: inefficient
        new_items = deepcopy(self.items)

        if count == 0:
            new_items.pop(item, None)
        else:
            new_items[item] = count

        try:
            original_items = self._root.items
            self._root.items = new_items
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "items", new_items
            )
        except DataFormatError as e:
            self._root.items = original_items
            raise e
        else:
            self._root.items = result

    # =========================================================================

    def merge(self, other: "RequestItemsMixin"):
        super().merge(other)

        self.items = deepcopy(other.items)

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.items == other.items
