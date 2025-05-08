# player_description.py

from draftsman.serialization import draftsman_converters
from draftsman.validators import instance_of

import attrs
from pydantic import BaseModel, Field

from typing import Optional


@attrs.define(slots=False)
class PlayerDescriptionMixin:
    """
    Allows the entity to have a player-given description, similar to blueprints
    or blueprint books. Used by all combinators.
    """

    # class Format(BaseModel):
    #     player_description: Optional[str] = Field(
    #         None,
    #         description="""
    #         The user-facing description given to this entity. Supports rich text
    #         and item icons.
    #         """,
    #     )

    # def __init__(self, name, similar_entities, **kwargs):
    #     self._root: __class__.Format

    #     super().__init__(name, similar_entities, **kwargs)

    #     self.player_description = kwargs.get("player_description", None)

    # =========================================================================

    player_description: Optional[str] = attrs.field(
        default=None, validator=instance_of(Optional[str])  # TODO: validate length
    )
    """
    The user-facing description given to this entity, usually for documentation 
    purposes.
    """

    # @property
    # def player_description(self) -> Optional[str]:
    #     """
    #     The user-facing description given to this entity, usually for in-game
    #     documentation purposes.
    #     """
    #     return self._root.player_description

    # @player_description.setter
    # def player_description(self, value: Optional[str]):
    #     # TODO: validation
    #     self._root.player_description = value
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             type(self).Format,
    #             self._root,
    #             "player_description",
    #             value,
    #         )
    #         self._root.player_description = result
    #     else:
    #         self._root.player_description = value


draftsman_converters.get_version((1, 0)).add_hook_fns(
    # {"$id": "factorio:player_description_mixin"},
    PlayerDescriptionMixin,
    lambda fields: {None: fields.player_description.name},
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    # {"$id": "factorio:player_description_mixin"},
    PlayerDescriptionMixin,
    lambda fields: {"player_description": fields.player_description.name},
)
