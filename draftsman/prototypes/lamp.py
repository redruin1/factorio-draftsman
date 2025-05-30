# lamp.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ColorMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
)
from draftsman.constants import LampColorMode
from draftsman.serialization import (
    draftsman_converters,
)
from draftsman.signatures import AttrsColor, AttrsSignalID
from draftsman.validators import instance_of, try_convert

from draftsman.data import mods
from draftsman.data.entities import lamps

import attrs
from typing import Optional


@attrs.define
class Lamp(
    ColorMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that illuminates an area.
    """

    @property
    def similar_entities(self) -> list:
        return lamps

    # =========================================================================

    use_colors: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this entity should use color signals to determine it's
    color.

    :exception TypeError: If set to anything other than a ``bool`` or ``None``.
    """

    # =========================================================================

    color_mode: Optional[LampColorMode] = attrs.field(
        default=LampColorMode.COLOR_MAPPING,
        converter=try_convert(LampColorMode),
        validator=instance_of(LampColorMode),
    )
    """
    In what way to interpret signals given to the lamp if ``use_colors`` is 
    ``True``.
    """

    # =========================================================================

    red_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-red", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID])
    )
    """
    The signal to pull the red color component from, if :py:attr:`color_mode` is
    ``1``.
    """

    # =========================================================================

    green_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-green", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID])
    )
    """
    The signal to pull the green color component from, if :py:attr:`color_mode` 
    is ``1``.
    """

    # =========================================================================

    blue_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-blue", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID])
    )
    """
    The signal to pull the blue color component from, if :py:attr:`color_mode` 
    is ``1``.
    """

    # =========================================================================

    rgb_signal: Optional[AttrsSignalID] = attrs.field(
        factory=lambda: AttrsSignalID(name="signal-white", type="virtual"),
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID])
    )
    """
    The signal to pull the entire encoded color from, if :py:attr:`color_mode` 
    is ``2``.
    """

    # =========================================================================

    always_on: Optional[bool] = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not this entity should always be active, regardless of the
    current day-night cycle. This option is superceeded by any condition
    simultaneously specified.
    """

    # =========================================================================

    color: AttrsColor = attrs.field(
        converter=AttrsColor.converter,
        validator=instance_of(AttrsColor),
    )
    """
    What (static) color should this lamp have. Setting the lamp's color via
    ``use_colors`` and ``color_mode`` overrides this value if either are present.
    """
    # TODO: different defaults for different Factorio versions
    # < 2.0: white
    # >= 2.0: off-white

    @color.default
    def _(self):
        if mods.versions.get("base", (2, 0)) >= (2, 0):
            return AttrsColor(r=1.0, g=1.0, b=191 / 255, a=1.0)
        else:
            return AttrsColor(r=1.0, g=1.0, b=1.0, a=1.0)

    # =========================================================================

    def merge(self, other: "Lamp"):
        super().merge(other)

        self.use_colors = other.use_colors
        self.color_mode = other.color_mode
        self.always_on = other.always_on
        self.color = other.color

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.get_version((1, 0)).add_hook_fns(
    Lamp,
    lambda fields: {
        ("control_behavior", "use_colors"): fields.use_colors.name,
        None: fields.color_mode.name,
        None: fields.red_signal.name,
        None: fields.green_signal.name,
        None: fields.blue_signal.name,
        None: fields.rgb_signal.name,
        None: fields.always_on.name,
        "color": fields.color.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    Lamp,
    lambda fields: {
        ("control_behavior", "use_colors"): fields.use_colors.name,
        ("control_behavior", "color_mode"): fields.color_mode.name,
        ("control_behavior", "red_signal"): fields.red_signal.name,
        ("control_behavior", "green_signal"): fields.green_signal.name,
        ("control_behavior", "blue_signal"): fields.blue_signal.name,
        ("control_behavior", "rgb_signal"): fields.rgb_signal.name,
        "always_on": fields.always_on.name,
        "color": fields.color.name,
    },
)
