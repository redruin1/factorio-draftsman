# heat_interface.py

from draftsman.classes.entity import Entity
from draftsman.constants import ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.validators import conditional, instance_of, one_of, try_convert
from draftsman.warning import TemperatureRangeWarning

from draftsman.data.entities import heat_interfaces

import attrs
from typing import Literal
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

    temperature: float = attrs.field(
        default=0.0,
        converter=try_convert(float),
        validator=instance_of(float),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The temperature of the interface in degrees.

    Raises :py:class:`.TemperatureRangeWarning` if set to a value not in the
    range ``[0, 1000]``.
    """

    @temperature.validator
    @conditional(ValidationMode.PEDANTIC)
    def _validate_temperature_range(
        self,
        attr: attrs.Attribute,
        value: float,
    ):
        if not 0.0 <= value <= 1000.0:
            msg = "Temperature '{}' exceeds allowed range [0.0, 1000.0]; will be clamped to this range on import".format(
                value
            )
            warnings.warn(TemperatureRangeWarning(msg))

    # =========================================================================

    mode: Literal["at-least", "at-most", "exactly", "add", "remove"] = attrs.field(
        default="at-least",
        validator=one_of("at-least", "at-most", "exactly", "add", "remove"),
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Manner in which to interact with the heat network. Can be one of:

    .. code-block:: python

        "at-least"  # At least this hot
        "at-most"   # At most this hot
        "exactly"   # Exactly this temperature
        "add"       # Add this temperature amount each tick
        "remove"    # Remove this temperature amount each tick
        None        # No mode set
    """

    # =========================================================================

    def merge(self, other: "HeatInterface"):
        super().merge(other)

        self.temperature = other.temperature
        self.mode = other.mode

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    HeatInterface,
    lambda fields: {
        "temperature": fields.temperature.name,
        "mode": fields.mode.name,
    },
)
