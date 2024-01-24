# infinity_pipe.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import DraftsmanBaseModel, int64, FluidName
from draftsman.utils import get_first

from draftsman.data.entities import infinity_pipes
from draftsman.data import fluids

import copy
from pydantic import ConfigDict, Field, model_validator
from typing import Any, Literal, Optional, Union


class InfinityPipe(Entity):
    """
    An entity used to create an infinite amount of any fluid at any temperature.
    """

    class Format(Entity.Format):
        class InfinitySettings(DraftsmanBaseModel):
            name: Optional[FluidName] = Field(
                None,
                description="""
                The fluid to infinitely generate or consume.
                """,
            )
            percentage: Optional[float] = Field(
                0.0,
                ge=0.0,
                description="""
                Desired fill-level to keep the pipe at of the selected fluid.
                Described as a float in the range [0.0, 1.0], where 1.0 is 100%.
                Cannot be negative.
                """,
            )
            mode: Optional[
                Literal["at-least", "at-most", "exactly", "add", "remove"]
            ] = Field(
                "at-least",
                description="""
                What action to perform when connected to a fluid network.
                """,
            )
            temperature: Optional[int64] = Field(
                None,
                description="""
                The temperature with which to keep the fluid at, in degrees 
                Celsius. Factorio will error if this value exceeds the minimum
                or maximum temperature for a specified fluid, or if temperature
                is specified but no fluid name is specified.
                
                Note: he datatype defined for both 'default_temperature' and 
                'maximum_temperature' is defined as a double, but the format
                that the blueprint string uses seems to be a integer of some 
                kind. For now, the range is defined as a int64, but this might
                not be quite correct.""",
            )

            @model_validator(mode="after")
            def validate_temperature_range(self):
                """
                Factorio errors if a fluid temperature is set when no fluid name
                is set, or if the fluid temperature exceeds the allowed range
                for the set fluid name.
                """
                if self.temperature is not None:
                    if self.name is None:
                        raise ValueError(
                            "Infinite fluid temperature cannot be set without infinite fluid name"
                        )
                    elif self.name is not None and self.name in fluids.raw:
                        min_temp, max_temp = fluids.get_temperature_range(self.name)
                        if not min_temp <= self.temperature <= max_temp:
                            raise ValueError(
                                "Temperature '{}' exceeds acceptable temperature range [{}, {}] for fluid '{}'".format(
                                    self.temperature, min_temp, max_temp, self.name
                                )
                            )

                return self

        infinity_settings: Optional[InfinitySettings] = InfinitySettings()

        model_config = ConfigDict(title="InfinityPipe")

    def __init__(
        self,
        name: Optional[str] = get_first(infinity_pipes),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        infinity_settings: Format.InfinitySettings = {},
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        self._root: __class__.Format

        super().__init__(
            name,
            infinity_pipes,
            position=position,
            tile_position=tile_position,
            tags=tags,
            **kwargs
        )

        self.infinity_settings = infinity_settings

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def infinity_settings(self) -> Optional[Format.InfinitySettings]:
        """
        The settings that control the manner in which what fluid is spawned or
        removed.

        :getter: Gets the ``infinity_settings`` of the ``InfinityPipe``.
        :setter: Sets the ``infinity_settings`` of the ``InfinityPipe``.
            Defaults to an empty ``dict`` if set to ``None``.
        :type: :py:data:`.INFINITY_PIPE`

        :exception DataFormatError: If set to anything that does not match the
            :py:data:`.INFINITY_PIPE` format.
        """
        return self._root.infinity_settings

    @infinity_settings.setter
    def infinity_settings(self, value: Optional[Format.InfinitySettings]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "infinity_settings", value
            )
            self._root.infinity_settings = result
        else:
            self._root.infinity_settings = value

    # =========================================================================

    @property
    def infinite_fluid_name(self) -> Optional[str]:
        """
        Sets the name of the infinite fluid.

        :getter: Gets the infinite fluid name, or ``None`` if not set.
        :setter: Sets the infinite fluid name. Removes the key if set to ``None``.
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        :exception InvalidFluidError: If set to an invalid fluid name.
        """
        return self.infinity_settings.get("name", None)

    @infinite_fluid_name.setter
    def infinite_fluid_name(self, value: Optional[str]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.InfinitySettings,
                self.infinity_settings,
                "name",
                value,
            )
            self.infinity_settings.name = result
        else:
            self.infinity_settings.name = value

    # =========================================================================

    @property
    def infinite_fluid_percentage(self) -> Optional[float]:
        """
        The percentage of the infinite fluid in the pipe, where ``1.0`` is 100%.

        :getter: Gets the percentage full, or ``None`` if not set.
        :setter: Sets the percentage full. Removes the key if set to ``None``.
        :type: float

        :exception TypeError: If set to anything other than an number or ``None``.
        :exception ValueError: If set to a negative percentage, which is forbidden.
        """
        return self.infinity_settings.get("percentage", None)

    @infinite_fluid_percentage.setter
    def infinite_fluid_percentage(self, value: Optional[float]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.InfinitySettings,
                self.infinity_settings,
                "percentage",
                value,
            )
            self.infinity_settings.percentage = result
        else:
            self.infinity_settings.percentage = value

    # =========================================================================

    @property
    def infinite_fluid_mode(
        self,
    ) -> Literal["at-least", "at-most", "exactly", "add", "remove", None]:
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
        :type: ``str``

        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        :exception InvalidModeError: If set to anything other than one of the
            values described above.
        """
        return self.infinity_settings.get("mode", None)

    @infinite_fluid_mode.setter
    def infinite_fluid_mode(
        self, value: Literal["at-least", "at-most", "exactly", "add", "remove", None]
    ):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.InfinitySettings,
                self.infinity_settings,
                "mode",
                value,
            )
            self.infinity_settings.mode = result
        else:
            self.infinity_settings.mode = value

    # =========================================================================

    @property
    def infinite_fluid_temperature(self) -> Optional[int64]:
        """
        The temperature of the infinite fluid, in degrees.

        Raises :py:class:`TemperatureRangeWarning` if ``temperature`` is set to
        anything not in the range ``[0, 1000]``.

        :getter: Gets the fluid temperature, or ``None`` if not set.
        :setter: Sets the fluid temperature. Removes the key if set to ``None``.
        :type: ``int``

        :exception TypeError: If set to anything other than a number or ``None``.
        """
        return self.infinity_settings.get("temperature", None)

    @infinite_fluid_temperature.setter
    def infinite_fluid_temperature(self, value: Optional[int64]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.InfinitySettings,
                self.infinity_settings,
                "temperature",
                value,
            )
            self.infinity_settings.temperature = result
        else:
            self.infinity_settings.temperature = value

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
        self.infinity_settings = {
            "name": name,
            "percentage": percentage,
            "mode": mode,
            "temperature": temperature,
        }

    def merge(self, other: "InfinityPipe"):
        super().merge(other)

        self.infinity_settings = copy.deepcopy(other.infinity_settings)

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other) and self.infinity_settings == other.infinity_settings
        )
