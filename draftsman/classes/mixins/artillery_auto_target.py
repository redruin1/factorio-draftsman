# artillery_auto_target.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs


@attrs.define(slots=False)
class ArtilleryAutoTargetMixin(Exportable):
    """
    Gives the entity the "artillery_auto_targeting" parameter. Used by artillery
    turrets and artillery wagons.
    """

    auto_target: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this artillery turret should automatically target enemy
    structures within range.
    """


draftsman_converters.add_hook_fns(
    ArtilleryAutoTargetMixin,
    lambda fields: {"artillery_auto_targeting": fields.auto_target.name},
)
