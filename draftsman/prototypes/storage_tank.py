# storage_tank.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import CircuitConnectableMixin, DirectionalMixin
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import storage_tanks

import attrs


@fix_incorrect_pre_init
@attrs.define
class StorageTank(CircuitConnectableMixin, DirectionalMixin, Entity):
    """
    An entity that stores a fluid.
    """

    @property
    def similar_entities(self) -> list[str]:
        return storage_tanks

    # =========================================================================

    __hash__ = Entity.__hash__
