# rocket_silo.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import RequestItemsMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import uint32

from draftsman.data.entities import rocket_silos

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class RocketSilo(RequestItemsMixin, Entity):
    """
    An entity that produces rockets, usually used in research.
    """

    class Format(RequestItemsMixin.Format, Entity.Format):
        auto_launch: Optional[bool] = Field(
            False,
            description="""
            Whether or not this silo is configured to automatically launch 
            itself when cargo is present inside of it.
            """,
        )

        model_config = ConfigDict(title="RocketSilo")

    def __init__(
        self,
        name: str = rocket_silos[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        items: dict[str, uint32] = {},
        auto_launch: bool = False,
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
            rocket_silos,
            position=position,
            tile_position=tile_position,
            items=items,
            tags=tags,
            **kwargs
        )

        self.auto_launch = auto_launch

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def auto_launch(self) -> Optional[bool]:
        """
        Whether or not to automatically launch the rocket when it's cargo is
        full.

        :getter: Gets whether or not to automatically launch.
        :setter: Sets whether or not to automatically launch.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self._root.auto_launch

    @auto_launch.setter
    def auto_launch(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "auto_launch", value
            )
            self._root.auto_launch = result
        else:
            self._root.auto_launch = value

    # =========================================================================

    def merge(self, other: "RocketSilo"):
        super(RocketSilo, self).merge(other)

        self.auto_launch = other.auto_launch

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.auto_launch == other.auto_launch
