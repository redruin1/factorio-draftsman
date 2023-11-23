# association.py

from pydantic import Field, WrapValidator
from pydantic_core import core_schema

from typing import TYPE_CHECKING, Annotated, Any
import weakref

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


class Association(weakref.ref):
    """
    A loose wrapper around weakref that permits deepcopying. Used to represent
    wire and circuit connections, as well as associating train entities with
    specific schedules. Leads to better memory management, more flexibilty when
    creating blueprints, and better visual representation.
    """

    Format = Annotated[
        int,
        Field(ge=0, lt=2**64),
        WrapValidator(
            lambda value, handler: value
            if isinstance(value, Association)
            else handler(value)
        ),
    ]

    def __init__(self, entity: "Entity"):
        super(Association, self).__init__(entity)

    def __eq__(self, other: Any):
        """
        Checking the equality of two Associations checks to make sure that they
        point to the exact same entity in memory, which is important for entity
        resolution. However, entity comparisons themselves are on a per value
        basis. For example:

        .. code-block:: python

            entity1 = Container()
            entity2 = Container()
            # Both entities are "value-equivalent"
            assert entity1 == entity2
            # But they're in different places in memory (entity1 is not entity2)
            assert Association(entity1) != Association(entity2)

        This differs from traditional `ref.weakref` behavior, which instead
        checks for equality between the referenced objects.
        """
        if isinstance(other, Association):
            return self() is other()  # TODO: think about
        else:
            return False

    def __ne__(self, other: Any):
        # Have to manually override this since we're inheriting a builtin
        return not self == other

    def __deepcopy__(self, _: dict) -> "Association":
        """
        Deepcopying an association doesn't actually copy it; it just returns a
        reference to the original association.
        """
        return self

    def __repr__(self) -> str:  # pragma: no coverage
        if self() is None:
            return "<Association to None>"

        return "<Association to {0}{1} at 0x{2:016X}>".format(
            type(self()).__name__,
            " '{}'".format(self().id) if self().id is not None else "",
            id(self()),
        )

    # @classmethod
    # def __get_pydantic_core_schema__(cls, _):
    #     return core_schema.int_schema()
