# display_panel.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import Exportable
from draftsman.classes.mixins import (
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID, AttrsSimpleCondition
from draftsman.utils import get_first
from draftsman.validators import instance_of

from draftsman.data.entities import display_panels

import attrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


@attrs.define
class DisplayPanel(
    ControlBehaviorMixin, CircuitConnectableMixin, DirectionalMixin, Entity
):
    """
    An entity which can display text and an icon to a surface or map view.
    """

    @attrs.define
    class Message(Exportable):
        icon: Optional[AttrsSignalID] = attrs.field(
            default=None,
            converter=AttrsSignalID.converter,
            validator=instance_of(Optional[AttrsSignalID]),
        )
        """
        The message's display icon.
        """
        text: str = attrs.field(default="", validator=instance_of(str))
        """
        The message's text label.
        """
        condition: AttrsSimpleCondition = attrs.field(
            factory=AttrsSimpleCondition,
            converter=AttrsSimpleCondition.converter,
            validator=instance_of(AttrsSimpleCondition),
        )
        """
        The condition that must be satisfied in order for this messsage to be
        able to be displayed.
        """

    # class Format(
    #     ControlBehaviorMixin.Format,
    #     CircuitConnectableMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     class ControlBehavior(DraftsmanBaseModel):
    #         class PanelMessage(DraftsmanBaseModel):
    #             condition: Optional[Condition] = Field(
    #                 Condition(),
    #                 description="""The condition upon which to display the associated text and icon.""",
    #             )
    #             icon: Optional[SignalID] = Field(
    #                 None, description="""The icon to display alongside the message."""
    #             )
    #             text: Optional[str] = Field("", description="""The text to display.""")

    #         parameters: list[PanelMessage] = Field(
    #             [],
    #             description="""List of messages to issue when connected to a circuit network.""",
    #         )

    #     control_behavior: Optional[ControlBehavior] = ControlBehavior()

    #     text: Optional[str] = Field("", description="""The text to display.""")
    #     icon: Optional[SignalID] = Field(
    #         None, description="""The icon to display alongside the message."""
    #     )
    #     always_show: Optional[bool] = Field(
    #         False, description="""Will always show the message in alt-mode if true."""
    #     )
    #     show_in_chart: Optional[bool] = Field(
    #         False,
    #         description="""Whether or not to show the icon on the corresponding position in the map view.""",
    #     )

    #     model_config = ConfigDict(title="DisplayPanel")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(display_panels),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Optional[Direction] = Direction.NORTH,
    #     text: Optional[str] = "",
    #     icon: Optional[SignalID] = None,
    #     always_show: Optional[bool] = False,
    #     show_in_chart: Optional[bool] = False,
    #     control_behavior: Optional[Format.ControlBehavior] = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     super().__init__(
    #         name=name,
    #         similar_entities=display_panels,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         control_behavior=control_behavior,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.text = text
    #     self.icon = icon
    #     self.always_show = always_show
    #     self.show_in_chart = show_in_chart

    #     self.validate_assignment = validate_assignment

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

    # @property
    # def text(self) -> Optional[str]:
    #     return self._root.text

    # @text.setter
    # def text(self, value: Optional[str]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "text", value
    #         )
    #         self._root.text = result
    #     else:
    #         self._root.text = value

    # =========================================================================

    icon: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    The (static) visual icon to display on the surface of the display panel. 
    This value is wiped and overridden by the list of :py:attr:`.messages` if 
    the display panel is connected to a circuit network.
    """

    # @property
    # def icon(self) -> Optional[SignalID]:
    #     return self._root.icon

    # @icon.setter
    # def icon(self, value: Optional[SignalID]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "icon", value
    #         )
    #         self._root.icon = result
    #     else:
    #         self._root.icon = value

    # =========================================================================

    always_show_in_alt_mode: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not to always display the panels :py:attr:`.text` when alt-mode 
    is enabled.
    """

    # @property
    # def always_show(self) -> Optional[bool]:
    #     return self._root.always_show

    # @always_show.setter
    # def always_show(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "always_show", value
    #         )
    #         self._root.always_show = result
    #     else:
    #         self._root.always_show = value

    # =========================================================================

    show_in_chart: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to render the display panel's configured :py:attr:`.icon` on
    the map like a map tag.
    """

    # @property
    # def show_in_chart(self) -> Optional[bool]:
    #     return self._root.show_in_chart

    # @show_in_chart.setter
    # def show_in_chart(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "show_in_chart", value
    #         )
    #         self._root.show_in_chart = result
    #     else:
    #         self._root.show_in_chart = value

    # =========================================================================

    messages: list[Message] = attrs.field(
        factory=list,
        # TODO: converter
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
    # {"$id": "factorio:display_panel:message"},
    DisplayPanel.Message,
    lambda fields: {
        "text": fields.text.name,
        "icon": fields.icon.name,
        "condition": fields.condition.name,
    },
)

draftsman_converters.add_hook_fns(
    # {"$id": "factorio:display_panel"},
    DisplayPanel,
    lambda fields: {
        "text": fields.text.name,
        "icon": fields.icon.name,
        "always_show": fields.always_show_in_alt_mode.name,
        "show_in_chart": fields.show_in_chart.name,
        ("control_behavior", "parameters"): fields.messages.name,
    },
)
