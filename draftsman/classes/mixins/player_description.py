# player_description.py

from draftsman.classes.exportable import Exportable
from draftsman.constants import ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.validators import and_, byte_length, conditional, instance_of
from draftsman.warning import DraftsmanWarning

import attrs
import warnings


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

    # @player_description.validator
    # @conditional(ValidationMode.STRICT)
    # def _player_description_validator(self, _: attrs.Attribute, value: str):
    #     if len(value.encode("utf-8")) > 500:
    #         msg = "'player_description' exceeds 500 bytes in length; will be truncated to this size when imported"
    #         warnings.warn(DraftsmanWarning(msg))


draftsman_converters.get_version((1, 0)).add_hook_fns(
    PlayerDescriptionMixin,
    lambda fields: {None: fields.player_description.name},
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    PlayerDescriptionMixin,
    lambda fields: {"player_description": fields.player_description.name},
)
