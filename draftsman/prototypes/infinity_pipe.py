# infinity_pipe.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue, test_replace_me
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.serialization import draftsman_converters
from draftsman.signatures import DraftsmanBaseModel, int64, FluidName
from draftsman.validators import and_, instance_of, ge, one_of

from draftsman.data.entities import infinity_pipes
from draftsman.data import fluids

import attrs
from pydantic import ConfigDict, Field, ValidationInfo, model_validator
from typing import Any, Literal, Optional, Union


@attrs.define
class InfinityPipe(Entity):
    """
    An entity used to create an infinite amount of any fluid at any temperature.
    """

    # class Format(Entity.Format):
    #     class InfinitySettings(DraftsmanBaseModel):
    #         name: Optional[FluidName] = Field(
    #             None,
    #             description="""
    #             The fluid to infinitely generate or consume.
    #             """,
    #         )
    #         percentage: Optional[float] = Field(
    #             0.0,
    #             ge=0.0,
    #             description="""
    #             Desired fill-level to keep the pipe at of the selected fluid.
    #             Described as a float in the range [0.0, 1.0], where 1.0 is 100%.
    #             Cannot be negative.
    #             """,
    #         )
    #         mode: Optional[
    #             Literal["at-least", "at-most", "exactly", "add", "remove"]
    #         ] = Field(
    #             "at-least",
    #             description="""
    #             What action to perform when connected to a fluid network.
    #             """,
    #         )
    #         temperature: Optional[int64] = Field(
    #             None,
    #             description="""
    #             The temperature with which to keep the fluid at, in degrees
    #             Celsius. Factorio will error if this value exceeds the minimum
    #             or maximum temperature for a specified fluid, or if temperature
    #             is specified but no fluid name is specified.

    #             Note: he datatype defined for both 'default_temperature' and
    #             'maximum_temperature' is defined as a double, but the format
    #             that the blueprint string uses seems to be a integer of some
    #             kind. For now, the range is defined as a int64, but this might
    #             not be quite correct.""",
    #         )

    #         @model_validator(mode="after")
    #         def validate_temperature(self, info: ValidationInfo):
    #             """
    #             Factorio errors if a fluid temperature is set when no fluid name
    #             is set, or if the fluid temperature exceeds the allowed range
    #             for the set fluid name.
    #             """
    #             if not info.context:
    #                 return self
    #             if info.context["mode"] <= ValidationMode.MINIMUM:
    #                 return self

    #             if self.temperature is not None:
    #                 if self.name is None:
    #                     raise ValueError(
    #                         "Infinite fluid temperature cannot be set without infinite fluid name"
    #                     )
    #                 elif self.name is not None and self.name in fluids.raw:
    #                     min_temp, max_temp = fluids.get_temperature_range(self.name)
    #                     if not min_temp <= self.temperature <= max_temp:
    #                         raise ValueError(
    #                             "Temperature '{}' exceeds acceptable temperature range [{}, {}] for fluid '{}'".format(
    #                                 self.temperature, min_temp, max_temp, self.name
    #                             )
    #                         )

    #             return self

    #     infinity_settings: Optional[InfinitySettings] = InfinitySettings()

    #     model_config = ConfigDict(title="InfinityPipe")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(infinity_pipes),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     infinity_settings: Format.InfinitySettings = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     self._root: __class__.Format

    #     super().__init__(
    #         name,
    #         infinity_pipes,
    #         position=position,
    #         tile_position=tile_position,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.infinity_settings = infinity_settings

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return infinity_pipes

    # =========================================================================

    # @property
    # def infinity_settings(self) -> Optional[Format.InfinitySettings]:
    #     """
    #     The settings that control the manner in which what fluid is spawned or
    #     removed.

    #     :getter: Gets the ``infinity_settings`` of the ``InfinityPipe``.
    #     :setter: Sets the ``infinity_settings`` of the ``InfinityPipe``.
    #         Defaults to an empty ``dict`` if set to ``None``.

    #     :exception DataFormatError: If set to anything that does not match the
    #         :py:data:`.INFINITY_PIPE` format.
    #     """
    #     return self._root.infinity_settings

    # @infinity_settings.setter
    # def infinity_settings(self, value: Optional[Format.InfinitySettings]):
    #     test_replace_me(
    #         self,
    #         type(self).Format,
    #         self._root,
    #         "infinity_settings",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self, type(self).Format, self._root, "infinity_settings", value
    #     #     )
    #     #     self._root.infinity_settings = result
    #     # else:
    #     #     self._root.infinity_settings = value

    # =========================================================================

    # def _reset_temperature(self, attr, value, mode=None):
    #     # In order for this to work, the validator would have to be after
    #     # `fluid_name` was set
    #     """
    #     If we set the fluid name, we want to make sure that the temperature is
    #     still valid; so we set the temperature to itself to trigger a
    #     revalidation.
    #     """
    #     print("test_validator")
    #     self.temperature = self.temperature

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

    # @property
    # def infinite_fluid_name(self) -> Optional[str]:
    #     """
    #     Sets the name of the infinite fluid.

    #     :getter: Gets the infinite fluid name, or ``None`` if not set.
    #     :setter: Sets the infinite fluid name. Removes the key if set to ``None``.

    #     :exception TypeError: If set to anything other than a ``str`` or ``None``.
    #     :exception InvalidFluidError: If set to an invalid fluid name.
    #     """
    #     return self.infinity_settings.get("name", None)

    # @infinite_fluid_name.setter
    # def infinite_fluid_name(self, value: Optional[str]):
    #     test_replace_me(
    #         self,
    #         type(self).Format.InfinitySettings,
    #         self.infinity_settings,
    #         "name",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self,
    #     #         type(self).Format.InfinitySettings,
    #     #         self.infinity_settings,
    #     #         "name",
    #     #         value,
    #     #     )
    #     #     self.infinity_settings.name = result
    #     # else:
    #     #     self.infinity_settings.name = value

    # =========================================================================

    percentage: float = attrs.field(
        default=0.0, validator=and_(instance_of((float, int)), ge(0.0))
    )
    """
    The percentage of the infinite fluid in the pipe, where ``1.0`` is 100%.

    :exception TypeError: If set to anything other than an number or ``None``.
    :exception ValueError: If set to a negative percentage, which is forbidden.
    """

    # @property
    # def infinite_fluid_percentage(self) -> Optional[float]:
    #     """
    #     The percentage of the infinite fluid in the pipe, where ``1.0`` is 100%.

    #     :getter: Gets the percentage full, or ``None`` if not set.
    #     :setter: Sets the percentage full. Removes the key if set to ``None``.

    #     :exception TypeError: If set to anything other than an number or ``None``.
    #     :exception ValueError: If set to a negative percentage, which is forbidden.
    #     """
    #     return self.infinity_settings.get("percentage", None)

    # @infinite_fluid_percentage.setter
    # def infinite_fluid_percentage(self, value: Optional[float]):
    #     test_replace_me(
    #         self,
    #         type(self).Format.InfinitySettings,
    #         self.infinity_settings,
    #         "percentage",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self,
    #     #         type(self).Format.InfinitySettings,
    #     #         self.infinity_settings,
    #     #         "percentage",
    #     #         value,
    #     #     )
    #     #     self.infinity_settings.percentage = result
    #     # else:
    #     #     self.infinity_settings.percentage = value

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

    # @property
    # def infinite_fluid_mode(
    #     self,
    # ) -> Literal["at-least", "at-most", "exactly", "add", "remove", None]:
    #     """
    #     The mode in which to manage the infinite fluid. Can be one of:

    #     .. code-block:: python

    #         "at-least"  # At least this much fluid
    #         "at-most"   # At most this much fluid
    #         "exactly"   # Exactly this much fluid
    #         "add"       # Add this much fluid each tick
    #         "remove"    # Remove this much fluid each tick

    #     :getter: Gets the fluid mode, or ``None`` if not set.
    #     :setter: Sets the fluid mode. Removes the key if set to ``None``.

    #     :exception TypeError: If set to anything other than a ``str`` or ``None``.
    #     :exception InvalidModeError: If set to anything other than one of the
    #         values described above.
    #     """
    #     return self.infinity_settings.get("mode", None)

    # @infinite_fluid_mode.setter
    # def infinite_fluid_mode(
    #     self, value: Literal["at-least", "at-most", "exactly", "add", "remove", None]
    # ):
    #     test_replace_me(
    #         self,
    #         type(self).Format.InfinitySettings,
    #         self.infinity_settings,
    #         "mode",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self,
    #     #         type(self).Format.InfinitySettings,
    #     #         self.infinity_settings,
    #     #         "mode",
    #     #         value,
    #     #     )
    #     #     self.infinity_settings.mode = result
    #     # else:
    #     #     self.infinity_settings.mode = value

    # =========================================================================

    def _validate_temperature(self, attr, value, mode: Optional[ValidationMode] = None):
        """
        Factorio errors if a fluid temperature is set when no fluid name is set
        while the temperature is set, or if the fluid temperature exceeds the
        allowed range for the given fluid name.
        """
        mode = mode if mode is not None else self.validate_assignment

        if mode >= ValidationMode.MINIMUM:
            # if self.fluid_name is None:
            #     msg = "Infinite fluid temperature cannot be set without infinite fluid name"
            #     raise DataFormatError(msg)
            if self.fluid_name in fluids.raw:
                print(self.fluid_name)
                min_temp, max_temp = fluids.get_temperature_range(self.fluid_name)
                print(min_temp, max_temp)
                if not (min_temp <= value <= max_temp):
                    msg = "Temperature '{}' exceeds acceptable temperature range [{}, {}] for fluid '{}'".format(
                        value, min_temp, max_temp, self.fluid_name
                    )
                    raise DataFormatError(msg)

    temperature: int64 = attrs.field(
        default=0, validator=and_(instance_of(int64), _validate_temperature)
    )
    """
    The temperature of the infinite fluid, in degrees.

    Raises :py:class:`TemperatureRangeWarning` if ``temperature`` is set to
    anything not in the range ``[0, 1000]``.

    :getter: Gets the fluid temperature, or ``None`` if not set.
    :setter: Sets the fluid temperature. Removes the key if set to ``None``.

    :exception DataFormatError: If set to anything other than a number in range.
    """

    # @property
    # def infinite_fluid_temperature(self) -> Optional[int64]:
    #     """
    #     The temperature of the infinite fluid, in degrees.

    #     Raises :py:class:`TemperatureRangeWarning` if ``temperature`` is set to
    #     anything not in the range ``[0, 1000]``.

    #     :getter: Gets the fluid temperature, or ``None`` if not set.
    #     :setter: Sets the fluid temperature. Removes the key if set to ``None``.

    #     :exception TypeError: If set to anything other than a number or ``None``.
    #     """
    #     return self.infinity_settings.get("temperature", None)

    # @infinite_fluid_temperature.setter
    # def infinite_fluid_temperature(self, value: Optional[int64]):
    #     test_replace_me(
    #         self,
    #         type(self).Format.InfinitySettings,
    #         self.infinity_settings,
    #         "temperature",
    #         value,
    #         self.validate_assignment,
    #     )
    #     # if self.validate_assignment:
    #     #     result = attempt_and_reissue(
    #     #         self,
    #     #         type(self).Format.InfinitySettings,
    #     #         self.infinity_settings,
    #     #         "temperature",
    #     #         value,
    #     #     )
    #     #     self.infinity_settings.temperature = result
    #     # else:
    #     #     self.infinity_settings.temperature = value

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


draftsman_converters.add_schema(
    {"$id": "factorio:infinity_pipe"},
    InfinityPipe,
    lambda fields: {
        ("infinity_settings", "name"): fields.fluid_name.name,
        ("infinity_settings", "percentage"): fields.percentage.name,
        ("infinity_settings", "mode"): fields.mode.name,
        ("infinity_settings", "temperature"): fields.temperature.name,
    },
)
