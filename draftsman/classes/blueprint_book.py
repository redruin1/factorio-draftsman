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

from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.deconstruction_planner import DeconstructionPlanner
from draftsman.classes.exportable import ValidationResult, attempt_and_reissue
from draftsman.classes.upgrade_planner import UpgradePlanner
from draftsman.constants import ValidationMode
from draftsman.error import DataFormatError
from draftsman.signatures import Color, DraftsmanBaseModel, Icon, uint16, uint64
from draftsman.utils import encode_version, reissue_warnings
from draftsman.warning import DraftsmanWarning, IndexWarning

from collections.abc import MutableSequence
from pydantic import (
    ConfigDict,
    Field,
    PrivateAttr,
    ValidatorFunctionWrapHandler,
    ValidationInfo,
    field_validator,
    ValidationError,
)
from typing import Any, Literal, Optional, Sequence, Union


class BlueprintableList(MutableSequence):
    """
    List of Blueprintable instances. "Blueprintable" in this context means
    either a Blueprint object or a BlueprintBook, as BlueprintBook objects
    can exist inside other BlueprintBook instances.
    """

    def __init__(
        self,
        initlist: list[Union[dict, Blueprintable]] = [],
    ):
        self.data: list[Blueprintable] = []
        for elem in initlist:
            if isinstance(elem, dict):
                # fmt: off
                if "blueprint" in elem:
                    self.append(
                        Blueprint(elem)
                    )
                elif "deconstruction_planner" in elem:
                    self.append(
                        DeconstructionPlanner(elem)
                    )
                elif "upgrade_planner" in elem:
                    self.append(
                        UpgradePlanner(elem)
                    )
                elif "blueprint_book" in elem:
                    self.append(
                        BlueprintBook(elem)
                    )
                else:
                    raise DataFormatError(
                        "Dictionary input cannot be resolved to a blueprintable"
                    )
                # fmt: on
            else:
                self.append(elem)

    def insert(self, idx: int, value: Blueprintable):
        # Make sure the blueprintable is valid
        self.check_blueprintable(value)

        self.data.insert(idx, value)

    def __getitem__(self, idx: Union[int, slice]) -> Union[Any, MutableSequence[Any]]:
        return self.data[idx]

    def __setitem__(self, idx: Union[int, slice], value: Any) -> None:
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


class BlueprintBook(Blueprintable):
    """
    Factorio Blueprint Book class. Contains a list of :py:class:`.Blueprintable`
    objects as well as some of it's own metadata.
    """

    # =========================================================================
    # Format
    # =========================================================================

    class Format(DraftsmanBaseModel):
        _blueprints: BlueprintableList = PrivateAttr()

        class BlueprintBookObject(DraftsmanBaseModel):
            item: Literal["blueprint-book"] = Field(
                ...,
                description="""
                The item that this BlueprintBookItem object is associated with. 
                Always equivalent to 'blueprint-book'.
                """,
            )
            label: Optional[str] = Field(
                None,
                description="""
                A string title for this BlueprintBook.
                """,
            )
            label_color: Optional[Color] = Field(
                None,
                description="""
                The color to draw the label of this blueprint book with, if 
                'label' is present. Defaults to white if omitted.
                """,
            )
            description: Optional[str] = Field(
                None,
                description="""
                A string description given to this BlueprintBook.
                """,
            )
            icons: Optional[list[Icon]] = Field(
                None,
                description="""
                A set of signal pictures to associate with this BlueprintBook.
                """,
                max_length=4,
            )
            active_index: Optional[uint16] = Field(
                0,
                description="""
                The numerical index of the currently selected blueprint in the
                blueprint book.
                """,
            )
            version: Optional[uint64] = Field(
                None,
                description="""
                What version of Factorio this UpgradePlanner was made 
                in/intended for. Specified as 4 unsigned 16-bit numbers combined, 
                representing the major version, the minor version, the patch 
                number, and the internal development version respectively. The 
                most significant digits correspond to the major version, and the 
                least to the development number. 
                """,
            )

            blueprints: list[
                Union[
                    Blueprint.Format,
                    DeconstructionPlanner.Format,
                    UpgradePlanner.Format,
                    "BlueprintBook.Format",
                ]
            ] = Field(
                [],
                description="""
                The list of blueprint-like objects enclosed within this 
                blueprint book. Can contain blueprints, deconstruction planners, 
                upgrade planners, or even other blueprint books. If multiple 
                blueprint-like objects share the same 'index', the last one 
                which was added at that index is imported into the book.
                """,
            )

        blueprint_book: BlueprintBookObject
        index: Optional[uint16] = Field(
            None,
            description="""
            The index of the blueprint inside a parent BlueprintBook's blueprint
            list. Only meaningful when this object is inside a BlueprintBook.
            """,
        )

        model_config = ConfigDict(title="BlueprintBook")

    # =========================================================================
    # Constructors
    # =========================================================================

    @reissue_warnings
    def __init__(
        self,
        blueprint_book: Optional[Union[str, dict]] = None,
        index: Optional[uint16] = None,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
    ):
        """
        Creates a ``BlueprintBook`` class. Will load the data from
        ``blueprint_book`` if provided, otherwise initializes with defaults.

        :param blueprint_book: Either a Factorio-format blueprint string or a
            ``dict`` object with the desired keys in the correct format.
        """
        self._root: BlueprintBook.Format

        super().__init__(
            root_item="blueprint_book",
            root_format=self.Format.BlueprintBookObject,
            item="blueprint-book",
            init_data=blueprint_book,
            index=index,
            blueprints=[],
            active_index=0,
        )

        self.validate_assignment = validate_assignment

    @reissue_warnings
    def setup(
        self,
        label: Optional[str] = None,
        label_color: Optional[Color] = None,
        description: Optional[str] = None,
        icons: Optional[list[Icon]] = None,
        version: Optional[uint64] = encode_version(*__factorio_version_info__),
        active_index: Optional[uint16] = 0,
        blueprints: Union[BlueprintableList, list[Blueprintable], list[dict]] = [],
        index: Optional[uint16] = None,
        **kwargs
    ):
        # self._root = {}

        # self._root["item"] = "blueprint-book"
        kwargs.pop("item", None)

        self.label = label
        self.label_color = label_color
        self.description = description
        self.icons = icons
        self.active_index = active_index

        self.version = version
        self.index = index
        # if "version" in kwargs:
        #     self.version = kwargs.pop("version")
        # else:
        #     self.version = encode_version(*__factorio_version_info__)

        # self.blueprints = blueprints
        # if "blueprints" in kwargs:
        #     # self._root[self._root_item]["blueprints"] = BlueprintableList(
        #     #     kwargs.pop("blueprints"), unknown=unknown
        #     # )
        #     self._root._blueprints = BlueprintableList(kwargs.pop("blueprints"))
        # else:
        #     # self._root[self._root_item]["blueprints"] = BlueprintableList()
        #     self._root._blueprints = BlueprintableList()

        if isinstance(blueprints, BlueprintableList):
            self._root._blueprints = BlueprintableList(blueprints.data)
        else:
            self._root._blueprints = BlueprintableList(blueprints)

        # A bit scuffed, but
        for kwarg, value in kwargs.items():
            self._root[kwarg] = value

    # =========================================================================
    # BlueprintBook properties
    # =========================================================================

    @property
    def label_color(self) -> Optional[Color]:
        """
        The color of the BlueprintBook's label.

        The ``label_color`` parameter exists in a dict format with the "r", "g",
        "b", and an optional "a" keys. The color can be specified like that, or
        it can be specified more succinctly as a sequence of 3-4 numbers,
        representing the colors in that order.

        The value of each of the numbers (according to Factorio spec) can be
        either in the range of [0.0, 1.0] or [0, 255]; if all the numbers are
        <= 1.0, the former range is used, and the latter otherwise. If "a" is
        omitted, it defaults to 1.0 or 255 when imported, depending on the
        range of the other numbers.

        :getter: Gets the color of the label, or ``None`` if not set.
        :setter: Sets the label color of the BlueprintBook.

        :exception DataFormatError: If the input ``label_color`` does not match
            the above specification.

        :example:

        .. code-block:: python

            blueprint.label_color = (127, 127, 127)
            print(blueprint.label_color)
            # {'r': 127.0, 'g': 127.0, 'b': 127.0}
        """
        return self._root[self._root_item].get("label_color", None)

    @label_color.setter
    def label_color(self, value: Optional[Color]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self._root_format,
                self._root[self._root_item],
                "label_color",
                value,
            )
            self._root[self._root_item]["label_color"] = result
        else:
            self._root[self._root_item]["label_color"] = value

    def set_label_color(self, r, g, b, a=None):  # TODO: remove
        """
        TODO
        """
        try:
            self._root[self._root_item]["label_color"] = Color(r=r, g=g, b=b, a=a)
        except ValidationError as e:
            raise DataFormatError from e

    # =========================================================================

    @property
    def active_index(self) -> Optional[uint16]:
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
        return self._root[self._root_item].get("active_index", None)

    @active_index.setter
    def active_index(self, value: Optional[uint16]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                self._root_format,
                self._root[self._root_item],
                "active_index",
                value,
            )
            self._root[self._root_item]["active_index"] = result
        else:
            self._root[self._root_item]["active_index"] = value

    # =========================================================================

    @property
    def blueprints(self) -> BlueprintableList:
        """
        The list of Blueprints or BlueprintBooks contained within this
        BlueprintBook.

        :getter: Gets the list of Blueprintables.
        :setter: Sets the list of Blueprintables. The list is initialized empty
            if set to ``None``.

        :exception TypeError: If set to anything other than ``list`` or
            ``None``.
        """
        # return self._root[self._root_item]["blueprints"]
        return self._root._blueprints

    @blueprints.setter
    def blueprints(self, value: Union[list, BlueprintableList, None]):
        if value is None:
            # self._root[self._root_item]["blueprints"] = BlueprintableList()
            self._root._blueprints = BlueprintableList()
        elif isinstance(value, BlueprintableList):
            self._root._blueprints = value
        elif isinstance(value, list):
            # self._root[self._root_item]["blueprints"] = BlueprintableList(value)
            self._root._blueprints = BlueprintableList(value)
        else:
            raise DataFormatError(
                "'blueprints' must be a BlueprintableList, a list, or None"
            )

    # =========================================================================
    # Utility functions
    # =========================================================================

    def validate(
        self,
        mode: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        force: bool = False,
    ) -> ValidationResult:
        mode = ValidationMode(mode)

        output = ValidationResult([], [])

        if mode is ValidationMode.NONE and not force:  # (self.is_valid and not force):
            return output

        context: dict[str, Any] = {
            "mode": mode,
            "object": self,
            "warning_list": [],
            "assignment": False,
        }

        try:
            # self.Format(**self._root, position=self.global_position, entity_number=0)
            # self._root.position = self.global_position
            result = self.Format.model_validate(
                self._root, strict=True, context=context
            )
            # Reassign private attributes
            result._blueprints = self._root._blueprints
            # Acquire the newly converted data
            self._root = result
        except ValidationError as e:
            output.error_list.append(DataFormatError(e))

        output.warning_list += context["warning_list"]

        # Inspect every sub-blueprint and concatenate all errors and warnings
        for blueprintable in self.blueprints:
            subresult = blueprintable.validate(mode, force)
            output.error_list.extend(subresult.error_list)
            output.warning_list.extend(subresult.warning_list)

        # if len(output.error_list) == 0:
        #     # Set the `is_valid` attribute
        #     # This means that if mode="pedantic", an entity that issues only
        #     # warnings will still not be considered valid
        #     super().validate()

        return output

    def to_dict(self, exclude_none: bool = True, exclude_defaults: bool = True) -> dict:
        """
        Returns the blueprint as a dictionary. Intended for getting the
        precursor to a Factorio blueprint string before encoding and compression
        takes place.

        :returns: The dict representation of the BlueprintBook.
        """
        # Create a copy, omitting blueprints because that part is special
        result = super().to_dict(
            exclude_none=exclude_none, exclude_defaults=exclude_defaults
        )

        # Transform blueprints
        converted_blueprints = []
        for i, blueprintable in enumerate(self.blueprints):
            blueprintable_entry = blueprintable.to_dict(
                exclude_none=exclude_none, exclude_defaults=exclude_defaults
            )
            # Users can manually customize index, we only override if none is found
            if "index" not in blueprintable_entry:
                blueprintable_entry["index"] = i
            converted_blueprints.append(blueprintable_entry)

        result[self._root_item]["blueprints"] = converted_blueprints

        # out_model = BlueprintBook.Format.model_construct(
        #     **{self._root_item: root_copy}, _recursive=True
        # )

        # out_dict = out_model.model_dump(
        #     by_alias=True,
        #     exclude_none=True,
        #     exclude_defaults=True,
        #     warnings=False  # Ignore warnings until model_construct is recursive
        # )

        if len(result[self._root_item]["blueprints"]) == 0:
            del result[self._root_item]["blueprints"]

        return result
