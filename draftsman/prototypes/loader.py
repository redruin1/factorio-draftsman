# loader.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    FiltersMixin,
    IOTypeMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import loaders

import attrs


@fix_incorrect_pre_init
@attrs.define
class Loader(FiltersMixin, IOTypeMixin, EnergySourceMixin, DirectionalMixin, Entity):
    """
    An entity that inserts items directly from a belt to an inventory or
    vise-versa.
    """

    @property
    def similar_entities(self) -> list[str]:
        return loaders

    # =========================================================================

    __hash__ = Entity.__hash__

