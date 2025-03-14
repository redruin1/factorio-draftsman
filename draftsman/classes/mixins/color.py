# color.py

from draftsman.classes.exportable import attempt_and_reissue, test_replace_me
from draftsman.signatures import Color, normalize_color

from pydantic import (
    BaseModel,
    Field,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)
from typing import Any, Optional, Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class ColorMixin:
    """
    Gives the entity an editable color.
    """

    class Format(BaseModel):
        color: Optional[Color] = Field(
            None,
            description="""
            The color modifier used to alter this entity's appearence.            
            """,
        )

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        self._root: __class__.Format

        super().__init__(name, similar_entities, **kwargs)

        self.color = kwargs.get("color", None)

    # =========================================================================

    @property
    def color(self) -> Color:
        """
        The color of the Entity.

        The ``color`` attribute exists in a dict format with the "r", "g",
        "b", and an optional "a" keys. The color can be specified like that, or
        it can be specified more succinctly as a sequence of 3-4 numbers,
        representing the colors in that order.

        The value of each of the numbers (according to Factorio spec) can be
        either in the range of [0.0, 1.0] or [0, 255]; if all the numbers are
        <= 1.0, the former range is used, and the latter otherwise. If "a" is
        omitted, it defaults to 1.0 or 255 when imported, depending on the
        range of the other numbers.

        :getter: Gets the color of the Entity, or ``None`` if not set.
        :setter: Sets the color of the Entity.

        :exception DataFormatError: If the set ``color`` does not match the
            above specification.
        """
        return self._root.color

    @color.setter
    def color(self, value: Union[list[float], Color]):
        # value = normalize_color(value)
        test_replace_me(
            self,
            type(self).Format,
            self._root,
            "color",
            value,
            self.validate_assignment,
        )
        # if self.validate_assignment:
        #     result = attempt_and_reissue(
        #         self, type(self).Format, self._root, "color", value
        #     )
        #     self._root.color = result
        # else:
        #     self._root.color = value

    # =========================================================================

    def merge(self, other: "Entity"):
        super().merge(other)

        self.color = other.color

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.color == other.color
