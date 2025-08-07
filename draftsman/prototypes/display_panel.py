# display_panel.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import Exportable
from draftsman.classes.mixins import (
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import SignalID, Condition
from draftsman.validators import instance_of

from draftsman.data.entities import display_panels

import attrs
from typing import Optional


@attrs.define
class DisplayPanel(
    PlayerDescriptionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    An entity which can display text and an icon to a surface or map view.
    """

    @attrs.define
    class Message(Exportable):
        """
        One of (possibly) many messages that a display panel can show. Only used
        if said display panel is connected to a circuit network to evaluate
        their :py:attr:`.condition` against.
        """

        icon: Optional[SignalID] = attrs.field(
            default=None,
            converter=SignalID.converter,
            validator=instance_of(Optional[SignalID]),
        )
        """
        .. serialized::

            This attribute is imported/exported from blueprint strings.

        The message's display icon.
        """

        text: str = attrs.field(default="", validator=instance_of(str))
        """
        .. serialized::

            This attribute is imported/exported from blueprint strings.

        The message's text label.
        """

        condition: Condition = attrs.field(
            factory=Condition,
            converter=Condition.converter,
            validator=instance_of(Condition),
        )
        """
        .. serialized::

            This attribute is imported/exported from blueprint strings.

        The condition that must be satisfied in order for this message to be
        displayed.
        """

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return display_panels

    # =========================================================================

    text: str = attrs.field(default="", validator=instance_of(str))
    """
    The (static) text that this display panel is configured to show. This value
    is wiped and overridden by the list of :py:attr:`.messages` if the display 
    panel is connected to a circuit network.
    """

    # =========================================================================

    icon: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
    )
    """
    The (static) visual icon to display on the surface of the display panel. 
    This value is wiped and overridden by the list of :py:attr:`.messages` if 
    the display panel is connected to a circuit network.
    """

    # =========================================================================

    always_show_in_alt_mode: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not to always display the panels :py:attr:`.text` when alt-mode 
    is enabled.
    """

    # =========================================================================

    show_in_chart: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to render the display panel's configured :py:attr:`.icon` on
    the map like a map tag.
    """

    # =========================================================================

    messages: list[Message] = attrs.field(
        factory=list,
        validator=instance_of(list[Message]),
    )
    """
    A list of :py:class:`.DisplayPanel.Message` objects, where each one has 
    unique icon, text, and a simple condition describing when the message should 
    be displayed on the panel. These messages take precedence over the 
    :py:attr:`.text` and :py:attr:`.icon` base fields.

    If multiple messages are configured to display at the same time, then the 
    message with the lowest index in this list is the one which is displayed.
    """

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    DisplayPanel.Message,
    lambda fields: {
        "text": fields.text.name,
        "icon": fields.icon.name,
        "condition": fields.condition.name,
    },
)

draftsman_converters.add_hook_fns(
    DisplayPanel,
    lambda fields: {
        "text": fields.text.name,
        "icon": fields.icon.name,
        "always_show": fields.always_show_in_alt_mode.name,
        "show_in_chart": fields.show_in_chart.name,
        ("control_behavior", "parameters"): fields.messages.name,
    },
)
