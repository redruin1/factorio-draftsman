# reactor.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import BurnerEnergySourceMixin, RequestItemsMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import get_first

from draftsman.data.entities import reactors

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class Reactor(BurnerEnergySourceMixin, RequestItemsMixin, Entity):
    """
    An entity that converts a fuel into thermal energy.
    """

    class Format(
        BurnerEnergySourceMixin.Format, RequestItemsMixin.Format, Entity.Format
    ):
        model_config = ConfigDict(title="Reactor")

    def __init__(
        self,
        name: Optional[str] = get_first(reactors),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        items: dict[str, uint32] = {},
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        super().__init__(
            name,
            reactors,
            position=position,
            tile_position=tile_position,
            items=items,
            tags=tags,
            **kwargs
        )

        # TODO: technically, a reactor can have more than just a burnable energy
        # source; it could have any type of energy source other than heat as
        # input. Thus, we need to make sure that the attributes from
        # BurnerEnergySourceMixin are only used in the correct configuration

        self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def allowed_items(self) -> Optional[set[str]]:
        return self.allowed_fuel_items

    # =========================================================================

    __hash__ = Entity.__hash__
