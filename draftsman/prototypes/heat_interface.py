# heat_interface.py

from draftsman.classes.entity import Entity
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.utils import get_first
from draftsman.validators import and_, instance_of, one_of
from draftsman.warning import TemperatureRangeWarning

from draftsman.data.entities import heat_interfaces

import attrs
from pydantic import ConfigDict, Field, ValidationInfo, field_validator
from typing import Any, Literal, Optional, Union
import warnings


@attrs.define
class HeatInterface(Entity):
    """
    An entity that interacts with a heat network.
    """

    @property
    def similar_entities(self) -> list[str]:
        return heat_interfaces

    # =========================================================================

    def _validate_temperature_range(
        self, attr, value, mode: Optional[ValidationMode] = None
    ):
        mode = mode if mode is not None else self.validate_assignment

        if mode >= ValidationMode.PEDANTIC:  # TODO: should this be pedantic?
            if not 0.0 <= value <= 1000.0:
                msg = "Temperature '{}' exceeds allowed range [0.0, 1000.0]; will be clamped to this range on import".format(
                    value
                )
                warnings.warn(TemperatureRangeWarning(msg))

    temperature: float = attrs.field(
        default=0.0,
        validator=and_(instance_of((float, int)), _validate_temperature_range),
    )
    """
    The temperature of the interface in degrees.

    Raises :py:class:`.TemperatureRangeWarning` if set to a value not in the
    range ``[0, 1000]``.

    :getter: Gets the temperature of the interface.
    :setter: Sets the temperature of the interface

    :exception TypeError: If set to anything other than an ``int`` or
        ``None``.
    """

    # =========================================================================

    mode: Literal["at-least", "at-most", "exactly", "add", "remove"] = attrs.field(
        default="at-least",
        validator=one_of("at-least", "at-most", "exactly", "add", "remove"),
    )
    """
    Manner in which to interact with the heat network. Can be one of:

    .. code-block:: python

        "at-least"  # At least this hot
        "at-most"   # At most this hot
        "exactly"   # Exactly this temperature
        "add"       # Add this temperature amount each tick
        "remove"    # Remove this temperature amount each tick
        None        # No mode set

    :exception DataFormatError: If set to anything other than one of the
        valid strings above or ``None``.
    """

    # =========================================================================

    def merge(self, other: "HeatInterface"):
        super().merge(other)

        self.temperature = other.temperature
        self.mode = other.mode

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_schema(
    {"$id": "factorio:heat_interface"},
    HeatInterface,
    lambda fields: {
        "temperature": fields.temperature.name,
        "mode": fields.mode.name,
    },
)
