# splitter.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.serialization import draftsman_converters
from draftsman.signatures import ItemName
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of, one_of

from draftsman.data.entities import splitters

import attrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union

try:
    from typing import Literal
except ImportError:  # pragma: no coverage
    from typing_extensions import Literal


@fix_incorrect_pre_init
@attrs.define
class Splitter(DirectionalMixin, Entity):
    """
    An entity that evenly splits a set of input belts between a set of output
    belts.
    """

    # class Format(DirectionalMixin.Format, Entity.Format):
    #     input_priority: Optional[
    #         Literal["left", "none", "right"]
    #     ] = Field(  # TODO: make this priority side or similar
    #         "none",
    #         description="""
    #         The side to prioritize pulling items into the splitter. 'none' means
    #         no preference.
    #         """,
    #     )
    #     output_priority: Optional[Literal["left", "none", "right"]] = Field(
    #         "none",
    #         description="""
    #         The side to prioritize pushing items out of the splitter. Obeys
    #         'filter', if set. 'none' means no preference and no filtering.
    #         """,
    #     )
    #     filter: Optional[ItemName] = Field(
    #         None,
    #         description="""
    #         The item that this splitter will filter, output on the
    #         'output_priority' side. Any item that does not exactly match this
    #         filter (when it is set) will get loaded on the opposite belt output.
    #         """,
    #     )

    #     model_config = ConfigDict(title="Splitter")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(splitters),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     input_priority: Literal["left", "none", "right"] = "none",
    #     output_priority: Literal["left", "none", "right"] = "none",
    #     filter: str = None,  # TODO: ItemID
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
    #         splitters,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.input_priority = input_priority
    #     self.output_priority = output_priority
    #     self.filter = filter

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return splitters

    # =========================================================================

    input_priority: Literal["left", "none", "right"] = attrs.field(
        default="none", validator=one_of("left", "none", "right")
    )
    """
    The input priority of the ``Splitter``. Can be one of ``"left"``,
    ``"right"``, or ``"none"``.
    """

    # @property
    # def input_priority(self) -> Literal["left", "none", "right", None]:
    #     """
    #     The input priority of the ``Splitter``. Can be one of ``"left"`` or
    #     ``"right"``.

    #     :getter: Gets the input priority.
    #     :setter: Sets the input priority.

    #     :exception TypeError: If set to anything other than a ``str`` or ``None``.
    #     :exception InvalidSideError: If set to an invalid side as specified
    #         above.
    #     """
    #     return self._root.input_priority

    # @input_priority.setter
    # def input_priority(self, value: Literal["left", "none", "right", None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "input_priority", value
    #         )
    #         self._root.input_priority = result
    #     else:
    #         self._root.input_priority = value

    # =========================================================================

    output_priority: Literal["left", "none", "right"] = attrs.field(
        default="none", validator=one_of("left", "none", "right")
    )
    """
    The output priority of the ``Splitter``. Can be one of ``"left"`` or
    ``"right"``.
    """

    # @property
    # def output_priority(self) -> Literal["left", "none", "right", None]:
    #     """
    #     The output priority of the ``Splitter``. Can be one of ``"left"`` or
    #     ``"right"``.

    #     :getter: Gets the output priority.
    #     :setter: Sets the output priority.

    #     :exception TypeError: If set to anything other than a ``str`` or ``None``.
    #     :exception InvalidSideError: If set to an invalid side as specified
    #         above.
    #     """
    #     return self._root.output_priority

    # @output_priority.setter
    # def output_priority(self, value: Literal["left", "none", "right", None]):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "output_priority", value
    #         )
    #         self._root.output_priority = result
    #     else:
    #         self._root.output_priority = value

    # =========================================================================

    filter: Optional[ItemName] = attrs.field(
        default=None, validator=instance_of(Optional[ItemName])
    )
    """
    Sets the Splitter's filter. If ``filter`` is set but ``output_priority``
    is not, then the output side defaults to ``"left"``.

    :exception TypeError: If set to anything other than a ``str`` or ``None``.
    :exception InvalidItemError: If set to an invalid item name.
    """

    # @property
    # def filter(self) -> Optional[ItemName]:
    #     """
    #     Sets the Splitter's filter. If ``filter`` is set but ``output_priority``
    #     is not, then the output side defaults to ``"left"``.

    #     :getter: Gets the splitter's item filter, or ``None`` if not set.
    #     :setter: Sets the splitter's item filter.

    #     :exception TypeError: If set to anything other than a ``str`` or ``None``.
    #     :exception InvalidItemError: If set to an invalid item name.
    #     """
    #     return self._root.filter

    # @filter.setter
    # def filter(self, value: ItemName):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "filter", value
    #         )
    #         self._root.filter = result
    #     else:
    #         self._root.filter = value

    # =========================================================================

    def merge(self, other: "Splitter"):
        super().merge(other)

        self.input_priority = other.input_priority
        self.output_priority = other.output_priority
        self.filter = other.filter

    # =========================================================================

    __hash__ = Entity.__hash__

    # def __eq__(self, other) -> bool:
    #     return (
    #         super().__eq__(other)
    #         and self.input_priority == other.input_priority
    #         and self.output_priority == other.output_priority
    #         and self.filter == other.filter
    #     )


draftsman_converters.add_schema(
    {"$id": "factorio:splitter"},
    Splitter,
    lambda fields: {
        "input_priority": fields.input_priority.name,
        "output_priority": fields.output_priority.name,
        "filter": fields.filter.name,
    },
)
