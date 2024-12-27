# asteroid_collector.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    CircuitSetFiltersMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode, Direction
from draftsman.signatures import DraftsmanBaseModel, ChunkID
from draftsman.utils import get_first

from draftsman.data.entities import asteroid_collectors

from pydantic import ConfigDict, Field, field_validator
from typing import Any, Literal, Optional, Union


class AsteroidCollector(
    CircuitSetFiltersMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity which collects asteroid chunks in space.
    """

    class Format(
        CircuitSetFiltersMixin.Format,
        CircuitConditionMixin.Format,
        CircuitEnableMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        DirectionalMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            CircuitSetFiltersMixin.ControlFormat,
            CircuitConditionMixin.ControlFormat,
            CircuitEnableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            circuit_read_contents: Optional[bool] = False # TODO
            include_hands: Optional[bool] = Field(
                True,
                description="""
                Whether or not to include chunks currently in the collectors 
                arms when broadcasting the contained amount to connected circuit 
                networks.
                """
            )

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        result_inventory: None = Field( # TODO: what is this?
            None,
            alias="result-inventory",
            description="TODO"
        )

        chunk_filter: Optional[list[ChunkID]] = Field(
            [],
            alias="chunk-filter",
            description="""
            Fixed set of asteroid chunk filters. Superceeded by circuit network 
            filters, if enabled.
            """
        )

        @field_validator("chunk_filter", mode="before")
        @classmethod
        def convert_from_str(cls, value: Any):
            try:
                result = []
                for i, elem in enumerate(value):
                    if isinstance(elem, str):
                        result.append({"index": i+1, "name": elem})
                    else:
                        result.append(elem)
                return result
            except:
                return value

        model_config = ConfigDict(title="AsteroidCollector")

    # =========================================================================

    def __init__(
        self,
        name: Optional[str] = get_first(asteroid_collectors),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        result_inventory = None,
        chunk_filter: list[ChunkID] = [],
        control_behavior: Format.ControlBehavior = {},
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        Construct a new asteroid collector.

        TODO
        """

        super().__init__(
            name,
            asteroid_collectors,
            position=position,
            tile_position=tile_position,
            direction=direction,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        # self.result_inventory = result_inventory
        self.chunk_filter = chunk_filter

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def result_inventory(self) -> None:
        """
        TODO
        """
        return self._root.result_inventory
    
    # =========================================================================

    @property
    def chunk_filter(self) -> Optional[list[ChunkID]]:
        """
        TODO
        """
        return self._root.chunk_filter
    
    @chunk_filter.setter
    def chunk_filter(self, value: Optional[list[ChunkID]]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "chunk_filter", value
            )
            self._root.chunk_filter = result
        else:
            self._root.chunk_filter = value

    # =========================================================================

    @property
    def read_contents(self) -> Optional[bool]:
        """
        Whether or not this Entity is set to read it's contents to a circuit
        network.

        :getter: Gets the value of ``read_contents``, or ``None`` if not set.
        :setter: Sets the value of ``read_contents``.

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.circuit_read_contents

    @read_contents.setter
    def read_contents(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.ControlBehavior,
                self.control_behavior,
                "circuit_read_contents",
                value,
            )
            self.control_behavior.circuit_read_contents = result
        else:
            self.control_behavior.circuit_read_contents = value

    # =========================================================================

    @property
    def include_hands(self) -> Optional[bool]:
        """
        Whether or not this Entity is set to read it's contents to a circuit
        network.

        :getter: Gets the value of ``include_hands``, or ``None`` if not set.
        :setter: Sets the value of ``include_hands``.

        :exception TypeError: If set to anything other than a ``bool`` or
            ``None``.
        """
        return self.control_behavior.include_hands

    @include_hands.setter
    def include_hands(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format.ControlBehavior,
                self.control_behavior,
                "include_hands",
                value,
            )
            self.control_behavior.include_hands = result
        else:
            self.control_behavior.include_hands = value
