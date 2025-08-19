# blueprintbook.py

"""
Contains the :py:class:`.BlueprintBook` class for easily creating and
manipulating Factorio blueprint books.

.. seealso::

    `<https://wiki.factorio.com/Blueprint_string_format>`_
"""

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.deconstruction_planner import DeconstructionPlanner
from draftsman.classes.upgrade_planner import UpgradePlanner
from draftsman.serialization import draftsman_converters
from draftsman.signatures import uint16
from draftsman.validators import instance_of

import attrs
import cattrs
from collections.abc import MutableSequence
from typing import Any, Iterable, Literal, Sequence, overload


class BlueprintableList(MutableSequence):
    """
    List of Blueprintable instances.
    """

    def __init__(
        self,
        initlist: Sequence[dict | Blueprintable] = [],
    ):
        from draftsman.blueprintable import get_blueprintable_from_JSON  # FIXME: cursed

        self.data: list[Blueprintable] = []
        for elem in initlist:
            if isinstance(elem, dict):
                self.append(get_blueprintable_from_JSON(elem))
            else:
                self.append(elem)

    def insert(self, idx: int, value: Blueprintable):
        # Make sure the blueprintable is valid
        self.check_blueprintable(value)

        self.data.insert(idx, value)

    @overload
    def __getitem__(self, idx: int) -> Blueprintable: 
        ...
    @overload
    def __getitem__(self, idx: slice) -> list[Blueprintable]: 
        ...
    def __getitem__(self, idx):
        return self.data[idx]

    @overload
    def __setitem__(self, idx: int, value: Blueprintable) -> None: 
        ...
    @overload
    def __setitem__(self, idx: slice, value: Iterable[Blueprintable]) -> None: 
        ...
    def __setitem__(self, idx, value):
        if isinstance(idx, slice):
            for v in value:
                self.check_blueprintable(v)
            self.data[idx] = [v for v in value]
        else:
            self.check_blueprintable(value)
            self.data[idx] = value

    def __delitem__(self, idx: int | slice) -> None:
        del self.data[idx]

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return "BlueprintableList({})".format(repr(self.data))

    def check_blueprintable(self, blueprintable):
        if not isinstance(
            blueprintable,
            (Blueprint, DeconstructionPlanner, UpgradePlanner, BlueprintBook),
        ):
            raise TypeError(
                "Entry into BlueprintableList must be one of (Blueprint, "
                "DeconstructionPlanner, UpgradePlanner, BlueprintBook)"
            )

    def __eq__(self, other: Any):
        if not isinstance(other, BlueprintableList):
            return NotImplemented
        return self.data == other.data


draftsman_converters.register_structure_hook(
    BlueprintableList, lambda d, _: BlueprintableList(d)
)


def blueprintable_list_unstructure_factory(_: type, converter: cattrs.Converter):
    def unstructure_hook(inst):
        res = [None] * len(inst)
        for i, elem in enumerate(inst):
            # d = converter.unstructure(elem)
            d = elem.to_dict()  # TODO: this is a problem because we lose the
            # information stored in converter; plus, what arguments would you
            # call `to_dict()` with here?
            if "index" not in d:
                d["index"] = i
            res[i] = d

        return res

    return unstructure_hook


draftsman_converters.register_unstructure_hook_factory(
    lambda cls: issubclass(cls, BlueprintableList),
    blueprintable_list_unstructure_factory,
)


@attrs.define
class BlueprintBook(Blueprintable):
    """
    Factorio Blueprint Book class. Contains a list of :py:class:`.Blueprintable`
    objects as well as some of it's own metadata.
    """

    @property
    def root_item(self) -> Literal["blueprint_book"]:
        return "blueprint_book"

    # =========================================================================

    # TODO: should be an evolve
    item: str = attrs.field(
        default="blueprint-book",
        validator=instance_of(str),
        metadata={
            "omit": False,
        },
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Always the name of the corresponding Factorio item to this blueprintable
    instance. Read only.
    """

    # =========================================================================

    active_index: uint16 = attrs.field(
        default=0, validator=instance_of(uint16), metadata={"omit": False}
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The currently selected Blueprintable in the BlueprintBook, or in other words
    the Blueprintable with the matching :py:class:`~.Blueprintable.index`.
    """

    # =========================================================================

    def _set_blueprints(self, _: attrs.Attribute, value: Any):
        if value is None:
            return BlueprintableList()
        elif isinstance(value, BlueprintableList):
            return BlueprintableList(value.data)
        else:
            return BlueprintableList(value)

    blueprints: BlueprintableList = attrs.field(
        on_setattr=_set_blueprints,
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    The list of blueprintable objects within this blueprint book. Can also be 
    specified as a regular list:

    .. doctest::

        >>> from draftsman.blueprintable import *
        >>> bpb = BlueprintBook()
        >>> bpb.blueprints = [Blueprint(), DeconstructionPlanner(), UpgradePlanner()]
        >>> assert len(bpb.blueprints) == 3
    """

    @blueprints.default
    def _blueprints_default(self):
        return BlueprintableList()


draftsman_converters.add_hook_fns(
    BlueprintBook,
    lambda fields: {
        ("blueprint_book", "item"): fields.item.name,
        ("blueprint_book", "label"): fields.label.name,
        ("blueprint_book", "label_color"): fields.label_color.name,
        ("blueprint_book", "description"): fields.description.name,
        ("blueprint_book", "icons"): fields.icons.name,
        ("blueprint_book", "version"): fields.version.name,
        ("blueprint_book", "active_index"): fields.active_index.name,
        ("blueprint_book", "blueprints"): fields.blueprints.name,
    },
)
