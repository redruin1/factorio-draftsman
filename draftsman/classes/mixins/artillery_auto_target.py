# artillery_auto_target.py

from draftsman.classes.exportable import attempt_and_reissue

from pydantic import BaseModel, Field
from typing import Optional


class ArtilleryAutoTargetMixin:
    """
    Gives the entity the "artillery_auto_targeting" parameter. Used by artillery
    turrets and artillery wagons.
    """

    class Format(BaseModel):
        artillery_auto_targeting: Optional[bool] = Field(
            True,
            description="""
            Whether or not this turret automatically targets enemy structures 
            in its range.
            """,
        )

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        super().__init__(name, similar_entities, **kwargs)

        self.auto_target = kwargs.get("artillery_auto_targeting", None)

    # =========================================================================

    @property
    def auto_target(self) -> bool:
        """
        TODO
        """
        return self._root.artillery_auto_targeting

    @auto_target.setter
    def auto_target(self, value: Optional[bool]) -> None:
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self.Format,
                self._root,
                "artillery_auto_targeting",
                value,
            )
            self._root.artillery_auto_targeting = result
        else:
            self._root.artillery_auto_targeting = value
