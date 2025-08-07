# splitter.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.serialization import draftsman_converters
from draftsman.signatures import ItemIDName
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of, one_of

from draftsman.data.entities import splitters

import attrs
from typing import Literal, Optional

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

    @property
    def similar_entities(self) -> list[str]:
        return splitters

    # =========================================================================

    input_priority: Literal["left", "none", "right"] = attrs.field(
        default="none", validator=one_of("left", "none", "right")
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The side that receives input priority. Can be one of ``"left"``, ``"right"``, 
    or ``"none"``.
    """

    # =========================================================================

    output_priority: Literal["left", "none", "right"] = attrs.field(
        default="none", validator=one_of("left", "none", "right")
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The side that receives output priority. Can be one of ``"left"``, ``"right"``, 
    or ``"none"``.
    """

    # =========================================================================

    filter: Optional[ItemIDName] = attrs.field(
        default=None,
        validator=instance_of(Optional[ItemIDName]),
        metadata={"never_null": True},
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Sets the Splitter's filter. If :py:attr:`.filter` is set but 
    :py:attr:`.output_priority` is not, then the output side defaults to 
    ``"left"``.
    """

    # =========================================================================

    def merge(self, other: "Splitter"):
        super().merge(other)

        self.input_priority = other.input_priority
        self.output_priority = other.output_priority
        self.filter = other.filter

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    Splitter,
    lambda fields: {
        "input_priority": fields.input_priority.name,
        "output_priority": fields.output_priority.name,
        "filter": fields.filter.name,
    },
)
