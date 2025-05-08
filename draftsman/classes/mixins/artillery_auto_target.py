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

    # class Format(BaseModel):
    #     artillery_auto_targeting: Optional[bool] = Field(
    #         True,
    #         description="""
    #         Whether or not this turret automatically targets enemy structures
    #         in its range.
    #         """,
    #     )

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     super().__init__(name, similar_entities, **kwargs)

    #     self.auto_target = kwargs.get("artillery_auto_targeting", None)

    # =========================================================================

    auto_target: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this artillery turret should automatically target enemy
    structures within range.
    """

    # @property
    # def auto_target(self) -> bool:
    #     """
    #     TODO
    #     """
    #     return self._root.artillery_auto_targeting

    # @auto_target.setter
    # def auto_target(self, value: Optional[bool]) -> None:
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self,
    #             self.Format,
    #             self._root,
    #             "artillery_auto_targeting",
    #             value,
    #         )
    #         self._root.artillery_auto_targeting = result
    #     else:
    #         self._root.artillery_auto_targeting = value

ArtilleryAutoTargetMixin.add_schema(
    {
        "properties": {
            "artillery_auto_targeting": {"type": "boolean"}
        }
    }
)


draftsman_converters.add_hook_fns(
    ArtilleryAutoTargetMixin,
    lambda fields: {"artillery_auto_targeting": fields.auto_target.name},
)
