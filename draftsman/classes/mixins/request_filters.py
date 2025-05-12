# request_filters.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    ManualSection,
)
from draftsman.validators import instance_of

import attrs
from typing import Optional, Union


@attrs.define(slots=False)
class RequestFiltersMixin(Exportable):
    """
    Used to allow entities to request items from the Logistic network.
    """

    trash_not_requested: bool = attrs.field(
        default=False,
        validator=instance_of(bool),
    )
    """
    Whether or not to mark items in the inventory not currently requested for 
    removal.
    """

    # =========================================================================

    request_from_buffers: bool = attrs.field(
        default=True,
        validator=instance_of(bool),
    )
    """
    Whether or not this chest should request items from buffer chests in its 
    logistic network.
    """

    # =========================================================================

    requests_enabled: bool = attrs.field(
        default=True,
        validator=instance_of(bool),
    )
    """
    Master toggle for all logistics requests on this entity. Superceeds any 
    logistic request toggles on any contained logistic sections.
    """

    # =========================================================================

    def _sections_converter(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                res[i] = ManualSection.converter(elem)
            return res
        return value

    sections: list[ManualSection] = attrs.field(
        factory=list,
        converter=_sections_converter,
        validator=instance_of(list[ManualSection]),
    )  # TODO: validator: can only have 100 of these
    """
    The list of logistics sections that this entity is configured to request.
    """

    # =========================================================================

    def add_section(
        self,
        group: Union[str, None] = None,
        index: Optional[int] = None,  # TODO: integer size
        active: bool = True,
    ) -> ManualSection:
        """
        Adds a new section of request/signal entries to the entity.

        .. NOTE::

            Beware of giving sections the same names; if a named group already
            exists within the save you are importing into, then that group will
            take precedence over the group inside of the blueprint.

        :param group: The name to give this group. The group will have no name
            if omitted.
        :param index: The index at which to insert the filter group. Defaults to
            the end if omitted.
        :param active: Whether or not this particular group is contributing its
            contents to the output in this specific combinator.

        :returns: A reference to the :class:`.ManualSection` just added.
        """
        self.sections += [
            ManualSection(
                group=group,
                index=index + 1 if index is not None else len(self.sections) + 1,
                active=active,
            )
        ]
        return self.sections[-1]

    # =========================================================================

    def merge(self, other: "RequestFiltersMixin"):
        super().merge(other)

        self.sections = other.sections


# TODO: versioning

RequestFiltersMixin.add_schema(
    {
        "properties": {
            "request_filters": {
                "type": "object",
                "properties": {
                    "trash_not_requested": {"type": "boolean", "default": "false"},
                    "request_from_buffers": {"type": "boolean", "default": "true"},
                    "enabled": {"type": "boolean", "default": "true"},
                    "sections": {
                        "type": "array",
                        "items": {"$ref": "urn:factorio:manual-section"},
                        "maxItems": 100,
                    },
                },
            }
        }
    },
    version=(2, 0),
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    RequestFiltersMixin,
    lambda fields: {
        ("request_filters", "trash_not_requested"): fields.trash_not_requested.name,
        ("request_filters", "request_from_buffers"): fields.request_from_buffers.name,
        ("request_filters", "enabled"): fields.requests_enabled.name,
        ("request_filters", "sections"): fields.sections.name,
    },
)
