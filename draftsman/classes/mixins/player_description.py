# player_description.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field

from typing import Optional


@attrs.define(slots=False)
class PlayerDescriptionMixin(Exportable):
    """
    Allows the entity to have a player-given description, similar to blueprints
    or blueprint books. Used by all combinators.
    """

    player_description: Optional[str] = attrs.field(
        default=None, validator=instance_of(Optional[str])  # TODO: validate length
    )
    """
    The user-facing description given to this entity, usually for documentation 
    purposes.
    """


PlayerDescriptionMixin.add_schema({}, version=(1, 0))

draftsman_converters.get_version((1, 0)).add_hook_fns(
    # {"$id": "factorio:player_description_mixin"},
    PlayerDescriptionMixin,
    lambda fields: {None: fields.player_description.name},
)

PlayerDescriptionMixin.add_schema(
    {"properties": {"player_description": {"type": "string"}}}, version=(2, 0)
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    # {"$id": "factorio:player_description_mixin"},
    PlayerDescriptionMixin,
    lambda fields: {"player_description": fields.player_description.name},
)
