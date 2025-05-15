# infinity_pipe.py

from draftsman.classes.entity import Entity
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.serialization import draftsman_converters
from draftsman.signatures import int64, FluidName
from draftsman.validators import and_, conditional, instance_of, ge, one_of

from draftsman.data.entities import infinity_pipes
from draftsman.data import fluids

import attrs
from typing import Literal, Optional


@attrs.define
class InfinityPipe(Entity):
    """
    An entity used to create an infinite amount of any fluid at any temperature.
    """

    @property
    def similar_entities(self) -> list[str]:
        return infinity_pipes

    # =========================================================================

    fluid_name: Optional[FluidName] = attrs.field(
        default=None,
        validator=instance_of(Optional[FluidName]),
    )
    """
    Sets the name of the infinite fluid.

    :getter: Gets the infinite fluid name, or ``None`` if not set.
    :setter: Sets the infinite fluid name. Removes the key if set to ``None``.

    :exception TypeError: If set to anything other than a ``str`` or ``None``.
    :exception InvalidFluidError: If set to an invalid fluid name.
    """

    # =========================================================================

    percentage: float = attrs.field(
        default=0.0, validator=and_(instance_of((float, int)), ge(0.0))
    )
    """
    The percentage of the infinite fluid in the pipe, where ``1.0`` is 100%.

    :exception TypeError: If set to anything other than an number or ``None``.
    :exception ValueError: If set to a negative percentage, which is forbidden.
    """

    # =========================================================================

    mode: Literal["at-least", "at-most", "exactly", "add", "remove"] = attrs.field(
        default="at-least",
        validator=one_of("at-least", "at-most", "exactly", "add", "remove"),
    )
    """
    The mode in which to manage the infinite fluid. Can be one of:

    .. code-block:: python

        "at-least"  # At least this much fluid
        "at-most"   # At most this much fluid
        "exactly"   # Exactly this much fluid
        "add"       # Add this much fluid each tick
        "remove"    # Remove this much fluid each tick

    :getter: Gets the fluid mode, or ``None`` if not set.
    :setter: Sets the fluid mode. Removes the key if set to ``None``.

    :exception TypeError: If set to anything other than a ``str`` or ``None``.
    :exception InvalidModeError: If set to anything other than one of the
        values described above.
    """

    # =========================================================================

    temperature: int64 = attrs.field(default=0, validator=instance_of(int64))
    """
    The temperature of the infinite fluid, in degrees.

    Raises :py:class:`TemperatureRangeWarning` if ``temperature`` is set to
    anything not in the range ``[0, 1000]``.

    :getter: Gets the fluid temperature, or ``None`` if not set.
    :setter: Sets the fluid temperature. Removes the key if set to ``None``.

    :exception DataFormatError: If set to anything other than a number in range.
    """

    @temperature.validator
    @conditional(ValidationMode.MINIMUM)
    def _validate_temperature(
        self,
        _: attrs.Attribute,
        value: int64,
    ):
        """
        Factorio errors if a fluid temperature is set when no fluid name is set
        while the temperature is set, or if the fluid temperature exceeds the
        allowed range for the given fluid name.
        """
        # if self.fluid_name is None:
        #     msg = "Infinite fluid temperature cannot be set without infinite fluid name"
        #     raise DataFormatError(msg)
        if self.fluid_name in fluids.raw:
            min_temp, max_temp = fluids.get_temperature_range(self.fluid_name)
            if not (min_temp <= value <= max_temp):
                msg = "Temperature '{}' exceeds acceptable temperature range [{}, {}] for fluid '{}'".format(
                    value, min_temp, max_temp, self.fluid_name
                )
                raise DataFormatError(msg)

    # =========================================================================

    def set_infinite_fluid(
        self,
        name: str = None,
        percentage: float = 0.0,
        mode: Literal[
            "at-least", "at-most", "exactly", "add", "remove", None
        ] = "at-least",
        temperature: int64 = None,
    ):
        """
        Sets all of the parameters of the infinite fluid at once.

        :param name: The name of the fluid to set.
        :param percentage: The percentage full the pipe is. Specified as a float
            where 0 is 0% and 1.0 is 100%.
        :param mode: The mode in which to interact with the fluid.
        :param temperature: The temperature of the fluid to create.

        :exception DataFormatError: If any of the argument's types mismatch their
            intended values.
        :exception InvalidFluidError: If ``name`` is not a valid name for a
            fluid.
        :exception InvalidModeError: If ``mode`` is not one of the values
            specified above.
        :exception ValueError: If percentage was set to a negative value.
        """
        self.fluid_name = name
        self.percentage = percentage
        self.mode = mode
        self.temperature = temperature

    def merge(self, other: "InfinityPipe"):
        super().merge(other)

        self.fluid_name = other.fluid_name
        self.percentage = other.percentage
        self.mode = other.mode
        self.temperature = other.temperature

    # =========================================================================

    __hash__ = Entity.__hash__


InfinityPipe.add_schema(
    {
        "$id": "urn:factorio:entity:infinity_pipe",
        "properties": {
            "infinity_settings": {
                "type": "object",
                "properties": {
                    "name": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "percentage": {"type": "number"},
                    "mode": {
                        "enum": ["at-least", "at-most", "exactly", "add", "remove"],
                        "default": "at-least",
                    },
                    "temperature": {"$ref": "urn:int64"},
                },
            }
        },
    }
)

draftsman_converters.add_hook_fns(
    # {"$id": "factorio:infinity_pipe"},
    InfinityPipe,
    lambda fields: {
        ("infinity_settings", "name"): fields.fluid_name.name,
        ("infinity_settings", "percentage"): fields.percentage.name,
        ("infinity_settings", "mode"): fields.mode.name,
        ("infinity_settings", "temperature"): fields.temperature.name,
    },
)
