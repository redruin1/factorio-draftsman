# simple_entity_with_owner.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import uint16
from draftsman.utils import get_first

from draftsman.data.entities import simple_entities_with_owner

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class SimpleEntityWithOwner(DirectionalMixin, Entity):
    """
    A generic entity owned by some other entity.
    """

    class Format(DirectionalMixin.Format, Entity.Format):
        variation: Optional[uint16] = Field(
            1,  # I think this is the default
            description="""
            The graphical variation of this entity. Used in many decorative 
            objects, though (currently) only mods like Text-Plates utilize this 
            in blueprint strings.
            """,
        )

        model_config = ConfigDict(title="SimpleEntityWithOwner")

    def __init__(
        self,
        name: Optional[str] = get_first(simple_entities_with_owner),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        tags: dict[str, Any] = {},
        variation: uint16 = 1,
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        self._root: __class__.Format

        super().__init__(
            name,
            simple_entities_with_owner,
            position=position,
            tile_position=tile_position,
            direction=direction,
            tags=tags,
            **kwargs
        )

        self.variation = variation

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def variation(self) -> Optional[uint16]:
        """
        The number representing the graphical variation of the entity.

        :type: ``uint16``
        """
        return self._root.variation

    @variation.setter
    def variation(self, value: Optional[uint16]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "variation", value
            )
            self._root.variation = result
        else:
            self._root.variation = value