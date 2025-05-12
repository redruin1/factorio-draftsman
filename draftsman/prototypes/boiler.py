# boiler.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ItemRequestMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import fix_incorrect_pre_init
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import boilers

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@fix_incorrect_pre_init
@attrs.define
class Boiler(ItemRequestMixin, EnergySourceMixin, DirectionalMixin, Entity):
    """
    An entity that uses a fuel to convert a fluid (usually water) to another
    fluid (usually steam).
    """

    # TODO: ensure fuel requests to this entity match it's allowed fuel categories

    @property
    def similar_entities(self) -> list[str]:
        return boilers

    # =========================================================================

    __hash__ = Entity.__hash__
