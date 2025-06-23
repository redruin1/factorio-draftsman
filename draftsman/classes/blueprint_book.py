# blueprintbook.py

"""
.. code-block:: python

    {
        "blueprint_book": {
            "item": "blueprint-book", # The associated item with this structure
            "label": str, # A user given name for this blueprint book planner
            "label_color": { # The overall color of the label
                "r": float[0.0, 1.0] or int[0, 255], # red
                "g": float[0.0, 1.0] or int[0, 255], # green
                "b": float[0.0, 1.0] or int[0, 255], # blue
                "a": float[0.0, 1.0] or int[0, 255]  # alpha (optional)
            }
            "icons": [ # A set of signals to act as visual identification
                {
                    "signal": {"name": str, "type": str}, # Name and type of signal
                    "index": int, # In range [1, 4], starting top-left and moving across
                },
                ... # Up to 4 icons total
            ],
            "description": str, # A user given description for this blueprint book
            "version": int, # The encoded version of Factorio this planner was created 
                            # with/designed for (64 bits)
            "active_index": int, # The currently selected blueprint in "blueprints"
            "blueprints": [ # A list of all Blueprintable objects this book contains
                {
                    {
                        "item": "blueprint",
                        ... # Any associated Blueprint key/values
                    },
                    "index": int # Index in the Blueprint Book
                }, # or
                {
                    {
                        "item": "deconstruction-planner",
                        ... # Any associated DeconstructionPlanner key/values
                    }, 
                    "index": int # Index in the Blueprint Book
                }, # or
                {
                    {
                        "item": "upgrade-planner",
                        ... # Any associated UpgradePlanner key/values
                    },
                    "index": int # Index in the Blueprint Book
                }, # or
                {
                    {
                        "item": "blueprint-book",
                        ... # Any above key/values
                    },
                    "index": int # Index in the Blueprint Book
                }
            ]
        }
    }
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
from typing import Any, Literal, Union


class BlueprintableList(MutableSequence):
    """
    List of Blueprintable instances.
    """

    def __init__(
        self,
        initlist: list[Union[dict, Blueprintable]] = [],
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

    def __getitem__(
        self, idx: Union[int, slice]
    ) -> Union[Blueprintable, MutableSequence[Blueprintable]]:
        return self.data[idx]

    def __setitem__(self, idx: Union[int, slice], value: Blueprintable) -> None:
        self.check_blueprintable(value)

        self.data[idx] = value

    def __delitem__(self, idx: Union[int, slice]) -> None:
        del self.data[idx]

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return "<BlueprintableList>{}".format(repr(self.data))

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

    item: str = attrs.field(
        default="blueprint-book",
        # TODO: validators
        metadata={
            "omit": False,
        },
    )
    # TODO: description

    # =========================================================================

    active_index: uint16 = attrs.field(default=0, validator=instance_of(uint16))
    """
    The currently selected Blueprintable in the BlueprintBook. Zero-indexed,
    from ``0`` to ``len(blueprint_book.blueprints) - 1``.

    :getter: Gets the index of the currently selected blueprint or blueprint
        book.
    :setter: Sets the index of the currently selected blueprint or blueprint
        book. If the value is ``None``, ``active_index`` defaults to ``0``.

    :exception TypeError: If set to anything other than an ``int`` or
        ``None``.
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
    The list of Blueprintable objects within this BlueprintBook.

    :exception TypeError: If set to anything other than ``list`` or
        ``None``.
    """

    @blueprints.default
    def _blueprints_default(self):
        return BlueprintableList()


# TODO: versioning

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
