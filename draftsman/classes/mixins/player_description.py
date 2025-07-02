# player_description.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import and_, byte_length, instance_of

import attrs


@attrs.define(slots=False)
class PlayerDescriptionMixin(Exportable):
    """
    Allows the entity to have a player-given description, similar to blueprints
    or blueprint books. Used by all combinators.
    """

    player_description: str = attrs.field(
        default="",
        converter=lambda v: "" if v is None else v,
        validator=and_(instance_of(str), byte_length(500)),
    )
    """
    The user-facing description given to this entity, usually for documentation 
    purposes.
    """


draftsman_converters.get_version((1, 0)).add_hook_fns(
    PlayerDescriptionMixin,
    lambda fields: {None: fields.player_description.name},
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    PlayerDescriptionMixin,
    lambda fields: {"player_description": fields.player_description.name},
)
