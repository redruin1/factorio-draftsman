# heat_interface.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.warning import TemperatureRangeWarning

from draftsman.data.entities import heat_interfaces

from pydantic import ConfigDict, Field, ValidationInfo, field_validator
from typing import Any, Literal, Optional, Union


class HeatInterface(Entity):
    """
    An entity that interacts with a heat network.
    """

    class Format(Entity.Format):
        temperature: Optional[float] = Field(
            0.0,
            description="""
            The temperature of this heat interface, in degrees Celsius. Clamped
            to the range [0, 1000] on import into Factorio.
            """,
        )
        mode: Optional[
            Literal["at-least", "at-most", "exactly", "add", "remove"]
        ] = Field(
            "at-least",
            description="""
            How the interface should affect its connected heat network.
            """,
        )

        @field_validator("temperature")
        @classmethod
        def clamp_temperature(cls, value: Optional[float], info: ValidationInfo):
            if not info.context or value is None:
                return value
            if info.context["mode"] is ValidationMode.MINIMUM:
                return value

            warning_list: list = info.context["warning_list"]

            if not 0.0 <= value <= 1000.0:
                issue = TemperatureRangeWarning(
                    "Temperature '{}' exceeds allowed range [0.0, 1000.0]; will be clamped to this range on import"
                )

                if info.context["mode"] is ValidationMode.PEDANTIC:
                    raise ValueError(issue) from None
                else:
                    warning_list.append(issue)

            return value

        model_config = ConfigDict(title="HeatInterface")

    def __init__(
        self,
        name: str = heat_interfaces[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        temperature: float = 0.0,
        mode: Literal["at-least", "at-most", "exactly", "add", "remove"] = "at-least",
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
            heat_interfaces,
            position=position,
            tile_position=tile_position,
            tags=tags,
            **kwargs
        )

        self.temperature = temperature
        self.mode = mode

        self.validate_assignment = validate_assignment

        if validate:
            self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def temperature(self) -> Optional[float]:
        """
        The temperature of the interface in degrees.

        Raises :py:class:`.TemperatureRangeWarning` if set to a value not in the
        range ``[0, 1000]``.

        :getter: Gets the temperature of the interface.
        :setter: Sets the temperature of the interface
        :type: ``int``

        :exception TypeError: If set to anything other than an ``int`` or
            ``None``.
        """
        return self._root.temperature

    @temperature.setter
    def temperature(self, value: Optional[float]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "temperature", value
            )
            self._root.temperature = result
        else:
            self._root.temperature = value

    # =========================================================================

    @property
    def mode(self) -> Literal["at-least", "at-most", "exactly", "add", "remove", None]:
        """
        Manner in which to interact with the heat network. Can be one of:

        .. code-block:: python

            "at-least"  # At least this hot
            "at-most"   # At most this hot
            "exactly"   # Exactly this temperature
            "add"       # Add this temperature amount each tick
            "remove"    # Remove this temperature amount each tick
            None        # No mode set

        :getter: Gets the mode of the interface.
        :setter: Sets the mode of the interface.
        :type: ``str``

        :exception InvalidModeError: If set to anything other than one of the
            valid strings above or ``None``.
        """
        return self._root.mode

    @mode.setter
    def mode(
        self, value: Literal["at-least", "at-most", "exactly", "add", "remove", None]
    ):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "mode", value
            )
            self._root.mode = result
        else:
            self._root.mode = value

    # =========================================================================

    def merge(self, other: "HeatInterface"):
        super().merge(other)

        self.temperature = other.temperature
        self.mode = other.mode

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.temperature == other.temperature
            and self.mode == other.mode
        )
