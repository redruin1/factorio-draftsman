# request_filters.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import ManualSection, SignalFilter, LuaDouble
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
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not to mark items in the inventory not currently requested for 
    removal.

    Only has an effect on versions of Factorio >= 2.0.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================

    request_from_buffers: bool = attrs.field(
        default=True,
        validator=instance_of(bool),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this entity should request items from buffer chests in its 
    logistic network.
    """

    # =========================================================================

    requests_enabled: bool = attrs.field(
        default=True,
        validator=instance_of(bool),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Master toggle for all logistics requests on this entity. Superceeds any 
    logistic request toggles on any contained logistic :py:attr:`.sections`.

    Only has an effect on versions of Factorio >= 2.0.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # =========================================================================

    sections: list[ManualSection] = attrs.field(
        factory=list,
        validator=instance_of(list[ManualSection]),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The list of logistics sections that this entity is configured to request.
    """

    # =========================================================================

    def add_section(
        self,
        group: Union[str, None] = None,
        index: Optional[LuaDouble] = None,
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

        :returns: A reference to the :class:`.ManualSection` just added, from
            which you can add entries to.
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


@attrs.define
class _ExportedRequestFiltersMixin:
    sections: list = attrs.field(factory=list)


_export_fields = attrs.fields(_ExportedRequestFiltersMixin)

draftsman_converters.get_version((1, 0)).add_hook_fns(
    RequestFiltersMixin,
    lambda fields, converter: {
        # None: fields.trash_not_requested.name,
        "request_from_buffers": fields.request_from_buffers.name,
        # None: fields.requests_enabled.name,
        "request_filters": (
            _export_fields.sections,
            lambda input_dict, _, inst: [
                ManualSection(
                    index=0, filters=converter.structure(input_dict, list[SignalFilter])
                )
            ],
        ),
    },
    lambda fields, converter: {
        # None: fields.trash_not_requested.name,
        "request_from_buffers": fields.request_from_buffers.name,
        # None: fields.requests_enabled.name,
        "request_filters": (
            _export_fields.sections,
            lambda inst: (
                converter.unstructure(inst.sections[0].filters)
                if len(inst.sections) > 0
                else []
            ),
        ),
    },
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
