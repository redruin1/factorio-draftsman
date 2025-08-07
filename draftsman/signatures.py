# signatures.py

"""
Module of common, "general" data formats.
"""

from draftsman.classes.association import Association
from draftsman.classes.exportable import Exportable
from draftsman.classes.vector import Vector
from draftsman.constants import InventoryType, ValidationMode
from draftsman.data import entities, fluids, items, signals, tiles, recipes, modules
from draftsman.error import (
    InvalidSignalError,
    IncompleteSignalError,
)
from draftsman.serialization import draftsman_converters
from draftsman.utils import get_suggestion
from draftsman.validators import (
    and_,
    lt,
    ge,
    one_of,
    is_none,
    or_,
    instance_of,
    try_convert,
    conditional,
)
from draftsman.warning import (
    BarWarning,
    MalformedSignalWarning,
    UnknownEntityWarning,
    UnknownFluidWarning,
    UnknownItemWarning,
    UnknownSignalWarning,
    UnknownTileWarning,
    UnknownRecipeWarning,
    UnknownModuleWarning,
)

from typing_extensions import Annotated

import attrs
from attrs import NOTHING
from typing import Any, Callable, Literal, Optional, Sequence, TypeVar, get_args
import warnings
import weakref

# Flag type to indicate that this item should be reduced to
OneIndexed = TypeVar("OneIndexed")
# def check_func(cls):
#     return OneIndexed in get_args(cls)

draftsman_converters.register_structure_hook_func(
    lambda cls: OneIndexed in get_args(cls), lambda v, _: v - 1
)
draftsman_converters.register_unstructure_hook_func(
    lambda cls: OneIndexed in get_args(cls), lambda v: v + 1
)

int32 = Annotated[int, and_(ge(-(2**31)), lt(2**31))]
# TODO: description about floating point issues
int64 = Annotated[int, and_(ge(-(2**63)), lt(2**63))]
# Maximum size of Lua double before you lose integer precision
LuaDouble = Annotated[int, and_(ge(-(2**53)), lt(2**53))]

uint8 = Annotated[int, and_(ge(0), lt(2**8))]
uint16 = Annotated[int, and_(ge(0), lt(2**16))]
uint32 = Annotated[int, and_(ge(0), lt(2**32))]
# TODO: description about floating point issues
uint64 = Annotated[int, and_(ge(0), lt(2**64))]


def known_name(type: str, structure: dict, issued_warning: Warning):
    @conditional(ValidationMode.STRICT)
    def validator(
        _inst: Exportable,
        _attr: attrs.Attribute,
        value: str,
    ) -> str:
        if value not in structure:
            msg = "Unknown {} '{}'{}".format(
                type, value, get_suggestion(value, structure.keys(), n=1)
            )
            warnings.warn(issued_warning(msg))

    return validator


ItemIDName = Annotated[str, known_name("item", items.raw, UnknownItemWarning)]
SignalIDName = Annotated[str, known_name("signal", signals.raw, UnknownSignalWarning)]
EntityID = Annotated[str, known_name("entity", entities.raw, UnknownEntityWarning)]
FluidID = Annotated[str, known_name("fluid", fluids.raw, UnknownFluidWarning)]
TileID = Annotated[str, known_name("tile", tiles.raw, UnknownTileWarning)]
RecipeID = Annotated[str, known_name("recipe", recipes.raw, UnknownRecipeWarning)]
ModuleID = Annotated[str, known_name("module", modules.raw, UnknownModuleWarning)]
QualityID = Literal[
    "normal", "uncommon", "rare", "epic", "legendary", "quality-unknown"
]
SignalIDType = Literal[
    "virtual",
    "item",
    "fluid",
    "recipe",
    "entity",
    "space-location",
    "asteroid-chunk",
    "quality",
]
ArithmeticOperation = Literal[
    "*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR"
]


@attrs.define
class SignalID(Exportable):
    """
    A signal ID, composed of a name, a signal type, and an optional quality.

    For convenience, a SignalID object can be constructed with just the string
    name, *if* the current Draftsman environment recognizes the name:

    .. code-block:: python

        some_signal = SignalID("iron-ore")

        assert some_signal.name == "iron-ore"
        assert some_signal.type == "item"
        assert some_signal.quality == "normal"

    In certain cases, you can even omit the ``SignalID`` constructor entirely in
    obvious cases:

    .. code-block:: python

        condition = Condition()
        condition.first_signal = "iron-ore"

        assert type(condition.first_signal) is SignalID
        assert condition.first_signal.name == "iron-ore"
        assert condition.first_signal.type == "item"
        assert condition.first_signal.quality == "normal"

    Because the name ``"iron-ore"`` is known, Draftsman can pick a correct ``type``
    for it. For most applications, this defaults to ``"item"``, but notable
    exceptions include fluids (``"fluid"``) and virtual signals (``"virtual"``):

    .. code-block:: python

        assert SignalID("iron-ore").type == "item"
        assert SignalID("steam").type == "fluid"
        assert SignalID("signal-A").type == "virtual"

    In Factorio 2.0 and up, multiple SignalID's can share the same name but have
    different types. The default signal type is the first entry in the return
    result of :py:func:`.get_valid_types`, which in most circumstances is
    usually ``"item"``. If you want a different type than the default, it must
    be manually specified using the constructor:

    .. code-block:: python

        SignalID("assembling-machine") # type="item"
        SignalID("assembling-machine", type="entity")
        SignalID("assembling-machine", type="recipe")

    If the name is not recognized by the current environment, the type will be
    unabled to be deduced, and so must be specified for signals of unknown
    origin:

    .. doctest::

        >>> SignalID("who knows!")
        Traceback: most recent call last
        ...
        IncompleteSignalError
        >>> SignalID("who knows!", type="item")
        SignalID(name="who knows!", type="item", quality="normal")
    """

    name: Optional[SignalIDName] = attrs.field(
        default=None, validator=instance_of(Optional[SignalIDName])
    )
    """
    Name of the signal. If omitted, the signal is treated as no signal and 
    removed on import/export cycle.
    """

    type: SignalIDType = attrs.field(
        validator=one_of(SignalIDType), metadata={"omit": False}
    )
    """
    Category of the signal.
    """

    @type.default
    def _(self):
        try:
            return signals.get_signal_types(self.name)[0]
        except InvalidSignalError:
            return "item"

    quality: Optional[QualityID] = attrs.field(
        default="normal", validator=or_(one_of(QualityID), is_none)
    )
    """
    Quality flag of the signal.
    """

    @classmethod
    def converter(cls, value: Any) -> "SignalID":
        """
        Attempt to convert an input string name into a SignalID representation.
        Raises a ValueError if unable to determine the type of a signal's name,
        likely if the signal is misspelled or used in a modded configuration
        that differs from Draftsman's current one.
        """
        if isinstance(value, str):
            try:
                if "item" in signals.get_signal_types(value):
                    return cls(name=value, type="item")
                else:
                    return cls(name=value, type=signals.get_signal_types(value)[0])
            except InvalidSignalError:
                msg = "Unknown signal name {}; either specify the full dictionary, or update your environment".format(
                    repr(value)
                )
                raise IncompleteSignalError(msg) from None
        elif isinstance(value, dict):
            return cls(**value)
        else:
            return value

    @type.validator
    @conditional(ValidationMode.STRICT)
    def _check_type_matches_name(self, _attr: attrs.Attribute, value: SignalIDType):
        if self.name in signals.raw:
            expected_types = signals.get_signal_types(self.name)
            if value not in expected_types:
                msg = "Known signal '{}' was given a mismatching type (expected one of {}, found '{}')".format(
                    self.name, expected_types, value
                )
                warnings.warn(MalformedSignalWarning(msg))


draftsman_converters.get_version((1, 0)).add_hook_fns(
    SignalID,
    lambda fields: {
        "name": fields.name.name,
        "type": fields.type.name,
        None: fields.quality.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    SignalID,
    lambda fields: {
        "name": fields.name.name,
        "type": fields.type.name,
        "quality": fields.quality.name,
    },
)


@attrs.define
class SignalIDBase(Exportable):
    """
    A :py:class:`.SignalID` but without any quality definition. Used by
    :py:class:`.SelectorCombinator`.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    name: Optional[SignalIDName] = attrs.field(
        default=None, validator=instance_of(Optional[SignalIDName])
    )
    """
    Name of the signal. If omitted, the signal is treated as no signal and 
    removed on import/export cycle.
    """

    type: Literal[SignalIDType] = attrs.field(
        validator=one_of(SignalIDType), metadata={"omit": False}
    )
    """
    Category of the signal.
    """

    @type.default
    def _(self):
        try:
            return signals.get_signal_types(self.name)[0]
        except InvalidSignalError:
            msg = "Unknown signal name {}; either specify the full dictionary, or update your environment".format(
                repr(self.name)
            )
            raise IncompleteSignalError(msg) from None

    @classmethod
    def converter(cls, value):
        if isinstance(value, str):
            return cls(name=value)
        elif isinstance(value, dict):
            return cls(**value)
        else:
            return value


draftsman_converters.add_hook_fns(
    SignalIDBase, lambda fields: {"name": fields.name.name, "type": fields.type.name}
)


@attrs.define
class TargetID(Exportable):
    """
    An object representing an entry in a target priorities list in turrets.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    index: uint32 = attrs.field(validator=instance_of(uint32))
    """
    Index of the target in the GUI.
    """
    name: str = attrs.field(validator=instance_of(str))  # TODO: TargetName?
    """
    Name of the target.
    """


draftsman_converters.add_hook_fns(
    TargetID, lambda fields: {"index": fields.index.name, "name": fields.name.name}
)


@attrs.define
class AsteroidChunkID(Exportable):
    """
    An object representing an entry in a chunk filters list in asteroid
    collectors.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    index: uint32 = attrs.field(validator=instance_of(uint32))
    """
    Index of the asteroid chunk in the filter UI.
    """
    name: str = attrs.field(validator=instance_of(str))  # TODO: AsteroidChunkName
    """
    Name of the asteroid chunk to filter.
    """


draftsman_converters.add_hook_fns(
    AsteroidChunkID,
    lambda fields: {
        fields.index.name: "index",
        fields.name.name: "name",
    },
)


@attrs.define
class Icon(Exportable):
    """
    A visual icon used for all :py:class:`.Blueprintable` classes.
    """

    index: Annotated[uint8, OneIndexed] = attrs.field(validator=instance_of(uint8))
    """
    Numeric index of the icon.
    """
    signal: SignalID = attrs.field(
        converter=SignalID.converter, validator=instance_of(SignalID)
    )
    """
    Which signal icon to display.
    """


draftsman_converters.add_hook_fns(
    Icon,
    lambda fields: {
        "index": fields.index.name,
        "signal": fields.signal.name,
    },
)


@attrs.define(hash=True)
class Color(Exportable):
    """
    A object representing a RGBA color.

    The value of each attribute (according to Factorio spec) can be
    either in the range of [0.0, 1.0] or [0, 255]; if all the numbers are
    <= 1.0, the former range is used, and the latter otherwise. If "a" is
    omitted, it defaults to 1.0 or 255 when imported, depending on the
    range of the other numbers.
    """

    # TODO: better validators
    r: float = attrs.field(validator=[attrs.validators.ge(0), attrs.validators.le(255)])
    g: float = attrs.field(validator=[attrs.validators.ge(0), attrs.validators.le(255)])
    b: float = attrs.field(validator=[attrs.validators.ge(0), attrs.validators.le(255)])
    a: Optional[float] = attrs.field(default=None)

    @a.validator
    def _(self, attribute: attrs.Attribute, value: Any):
        if value is None:
            return
        if not (0 <= value <= 255):
            raise ValueError("value {} outside of range [0, 255]".format(value))

    @classmethod
    def converter(cls, value) -> "Color":
        if isinstance(value, Sequence) and not isinstance(value, str):
            return cls(*value)
        elif isinstance(value, dict):
            return cls(**value)
        else:
            return value


draftsman_converters.add_hook_fns(
    Color,
    lambda fields: {
        "r": fields.r.name,
        "g": fields.g.name,
        "b": fields.b.name,
        "a": fields.a.name,
    },
)


def normalize_comparator(value):
    conversions = {"==": "=", ">=": "≥", "<=": "≤", "!=": "≠"}
    if value in conversions:
        return conversions[value]
    else:
        return value


Comparator = Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="]
# draftsman_converters.register_unstructure_hook(
#     Comparator, lambda inst: normalize_comparator(inst)
# )


@attrs.define
class Condition(Exportable):
    """
    A "simple" condition object, used for all logistic conditions as well as
    almost all circuit conditions. The only circuit condition case that does
    not use this object is :py:class:`.DeciderCombinator.Condition`.
    """

    first_signal: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    The signal in the leftmost slot of the condition.
    """
    comparator: Comparator = attrs.field(
        default="<",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
    )
    """
    The comparison operation to perform
    """
    constant: int32 = attrs.field(default=0, validator=instance_of(int32))
    """
    The constant value in the rightmost slot of the condition. Occupies the same
    spot as :py:attr:`.second_signal`. If both are specified, this value is 
    overridden.
    """
    second_signal: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    The signal in the rightmost slot of the condition. Occupies the same spot as
    :py:attr:`.constant`. If both are specified, this value takes precedence.
    """


draftsman_converters.add_hook_fns(
    Condition,
    lambda fields: {
        "first_signal": fields.first_signal.name,
        "comparator": fields.comparator.name,
        "constant": fields.constant.name,
        "second_signal": fields.second_signal.name,
    },
)


@attrs.define
class CircuitNetworkSelection(Exportable):
    """
    A definition of which circuit networks to consider when pulling values for
    circuit operations.

    Can be specified as either:

    * A class instance::

        CircuitNetworkSelection(red=True, green=False)

    * A ``dict``::

        {"red": True, "green": False}

    * Or a ``set``::

        {"red"}
    """

    red: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to pull values from the red circuit wire.
    """
    green: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to pull values from the green circuit wire.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, set):
            return cls(**{k: k in value for k in ("red", "green")})
        elif isinstance(value, dict):
            return cls(**value)
        else:
            return value


draftsman_converters.add_hook_fns(
    CircuitNetworkSelection,
    lambda fields: {
        "red": fields.red.name,
        "green": fields.green.name,
    },
)


@attrs.define
class ItemFilter(Exportable):
    """
    A object representing a particular item with a quality or a range of
    qualities, used for things like :py:attr:`.Inserter.filters`.
    """

    index: Annotated[int64, OneIndexed] = attrs.field(
        validator=instance_of(int64),
    )
    """
    Index of the filter in the GUI.
    """

    name: ItemIDName = attrs.field(validator=instance_of(ItemIDName))
    """
    Name of the item.
    """

    quality: Literal[None, QualityID] = attrs.field(
        default="normal", validator=one_of(Literal[None, QualityID])
    )
    """
    Quality flag of the item.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    comparator: Comparator = attrs.field(
        default="=",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
    )
    """
    Comparator if filtering a range of multiple qualities.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """


draftsman_converters.add_hook_fns(
    ItemFilter,
    lambda fields: {
        "index": fields.index.name,
        "name": fields.name.name,
        "quality": fields.quality.name,
        "comparator": fields.comparator.name,
    },
)


@conditional(ValidationMode.PEDANTIC)
def ensure_bar_less_than_inventory_size(
    self: "Inventory",
    _: attrs.Attribute,
    value: Optional[uint16],
):
    if self.size is None or value is None:
        return
    if value >= self.size:
        msg = "Bar index ({}) exceeds the container's inventory size ({})".format(
            value, self.size
        )
        warnings.warn(BarWarning(msg))


@attrs.define
class SignalFilter(Exportable):
    """
    An object that specifies a single signal or a range of signal types. Used as
    filters for logistics requests, as well as the signal specifications inside
    of :py:class:`.ConstantCombinator`.
    """

    index: Annotated[int64, OneIndexed] = attrs.field(
        validator=instance_of(int64),
    )
    """
    Numeric index of the signal in the combinator. Typically the index of the 
    signal in the parent 'filters' key, but this is not strictly enforced. 
    """

    name: SignalIDName = attrs.field(validator=instance_of(SignalIDName))
    """
    Name of the signal.
    """

    count: int32 = attrs.field(validator=instance_of(int32))
    """
    Value of the signal filter, or the lower bound of a range if ``max_count`` 
    is also specified.
    """

    type: Optional[SignalIDType] = attrs.field(
        validator=or_(is_none, one_of(SignalIDType))
    )
    """
    Type of the signal.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    @type.default
    def _(self) -> SignalIDType:
        try:
            return signals.get_signal_types(self.name)[0]
        except InvalidSignalError:
            return "item"

    quality: Literal[None, QualityID] = attrs.field(
        default=None,
        validator=one_of(Literal[None, QualityID]),
        metadata={"never_null": True},
    )
    """
    Quality flag of the signal. Defaults to special "any" quality signal if not
    specified.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    comparator: Comparator = attrs.field(
        default="=",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
        metadata={"omit": False},
    )
    """
    Comparison operator when deducing the quality type.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    max_count: Optional[int32] = attrs.field(
        default=None,
        validator=instance_of(Optional[int32]),
        metadata={"never_null": True},
    )
    """
    The maximum amount of the signal to request of the signal to emit. Only used
    (currently) with logistics-type requests.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    # Deprecated in 2.0
    # @field_validator("index")
    # @classmethod
    # def ensure_index_within_range(cls, value: int64, info: ValidationInfo):
    #     """
    #     Factorio does not permit signal values outside the range of it's item
    #     slot count; this method raises an error IF item slot count is known.
    #     """
    #     if not info.context:
    #         return value
    #     if info.context["mode"] <= ValidationMode.MINIMUM:
    #         return value

    #     entity = info.context["object"]

    #     # If Draftsman doesn't recognize entity, early exit
    #     if entity.item_slot_count is None:
    #         return value

    #     # TODO: what happens if index is 0?
    #     if not 0 < value <= entity.item_slot_count:
    #         raise ValueError(
    #             "Signal 'index' ({}) must be in the range [0, {})".format(
    #                 value, entity.item_slot_count
    #             )
    #         )

    #     return value

    # TODO: move to ConstantCombinator
    # @field_validator("name")
    # @classmethod
    # def ensure_not_pure_virtual(cls, value: Optional[str], info: ValidationInfo):
    #     """
    #     Warn if pure virtual signals (like "signal-each", "signal-any", and
    #     "signal-everything") are entered inside of a constant combinator.
    #     """
    #     if not info.context or value is None:
    #         return value
    #     if info.context["mode"] <= ValidationMode.MINIMUM:
    #         return value

    #     warning_list: list = info.context["warning_list"]

    #     if value in pure_virtual:
    #         warning_list.append(
    #             PureVirtualDisallowedWarning(
    #                 "Cannot set pure virtual signal '{}' in a constant combinator".format(
    #                     value.name
    #                 )
    #             )
    #         )

    #     return value


draftsman_converters.get_version((1, 0)).add_hook_fns(
    SignalFilter,
    lambda fields: {
        "index": fields.index.name,
        "name": fields.name.name,
        "count": fields.count.name,
        # None: fields.type.name,
        # None: fields.quality.name,
        # None: fields.comparator.name,
        # None: fields.max_count.name,
    },
)


@attrs.define
class _ExportSignalFilter:
    type: str = "item"


draftsman_converters.get_version((2, 0)).add_hook_fns(
    SignalFilter,
    lambda fields: {
        "index": fields.index.name,
        "name": fields.name.name,
        "count": fields.count.name,
        "type": fields.type.name,
        "quality": fields.quality.name,
        "comparator": fields.comparator.name,
        "max_count": fields.max_count.name,
    },
    lambda fields, converter: {
        "index": fields.index.name,
        "name": fields.name.name,
        "count": fields.count.name,
        "type": attrs.fields(_ExportSignalFilter).type,
        "quality": fields.quality.name,
        "comparator": fields.comparator.name,
        "max_count": fields.max_count.name,
    },
)


@attrs.define
class ManualSection(Exportable):
    """
    A "manually" (player) defined collection of signals, typically used for
    logistic request sections as well as constant combinator signal groups.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    index: Annotated[LuaDouble, OneIndexed] = attrs.field(
        validator=instance_of(LuaDouble)
    )
    """
    Location of the logistics section within the entity. Hard capped to 100 
    sections per entity.
    """

    @index.validator
    @conditional(ValidationMode.MINIMUM)
    def _index_validator(self, attr, value):
        """
        Can only have 100 signal sections per entity.
        """
        if not (0 <= value < 100):
            msg = "Index ({}) must be in range [0, 100)".format(value)
            raise IndexError(msg)

    def _filters_converter(value: list[Any]) -> list[SignalFilter]:
        if isinstance(value, list):
            for i, entry in enumerate(value):
                if isinstance(entry, tuple):
                    value[i] = SignalFilter(
                        index=i,
                        name=entry[0],
                        count=entry[1],
                    )
        return value

    filters: list[SignalFilter] = attrs.field(
        factory=list,
        converter=_filters_converter,
        validator=instance_of(list[SignalFilter]),
    )
    """
    List of item requests for this section.
    """

    group: str = attrs.field(
        default="",
        converter=lambda v: "" if v is None else v,
        validator=instance_of(str),
    )
    """
    Name of this section group. Once named, this group will become registered 
    within the save it is imported into. If a logistic section with the given
    name already exists within the save, the one that exists in the save will 
    overwrite any sections more recently specified.
    """

    active: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this logistic section is currently enabled and contributing
    it's output.
    """

    def set_signal(
        self,
        index: int64,
        name: Optional[SignalIDName],
        count: int32 = 0,
        quality: Literal[
            "normal",
            "uncommon",
            "rare",
            "epic",
            "legendary",
            "quality-unknown",
            "any",
        ] = "normal",
        type: Optional[str] = None,
    ) -> None:
        """
        Sets the particular signal at any given point.

        :param index: The index of the signal in the GUI.
        :param name: The name of the signal.
        :param count: The amount of the item/the value to output.
        :param quality: The quality of the signal.
        :param type: The internal type of the signal.
        """
        if name is not None:
            new_entry = SignalFilter(
                index=index,
                name=name,
                type=type if type is not None else NOTHING,
                quality=quality,
                comparator="=",
                count=count,
            )

        # Check to see if filters already contains an entry with the same index
        existing_index = None
        for i, signal_filter in enumerate(self.filters):
            if index == signal_filter.index:  # Index already exists in the list
                if name is None:  # Delete the entry
                    del self.filters[i]
                else:
                    self.filters[i] = new_entry
                existing_index = i
                break

        if existing_index is None:
            self.filters.append(new_entry)

    def get_signal(self, index: int64) -> Optional[SignalFilter]:
        """
        Get the :py:class:`.SignalFilter` entry at a particular index, if it
        exists.

        :param index: The index of the signal to analyze.

        :returns: A :py:class:`.SignalFilter` instance, or ``None`` if nothing
        was found at that index.
        """
        return next(
            (item for item in self.filters if item.index == index),
            None,
        )

    # @field_validator("filters", mode="before")
    # @classmethod
    # def normalize_input(cls, value: Any):
    #     if isinstance(value, list):
    #         for i, entry in enumerate(value):
    #             if isinstance(entry, tuple):
    #                 # TODO: perhaps it would be better to modify the format so
    #                 # you must specify the signal type... or maybe not...
    #                 signal_types = get_signal_types(entry[0])
    #                 filter_type = (
    #                     "item" if "item" in signal_types else next(iter(signal_types))
    #                 )
    #                 value[i] = {
    #                     "index": i + 1,
    #                     "name": entry[0],
    #                     "type": filter_type,
    #                     "comparator": "=",
    #                     "count": entry[1],
    #                 }

    #     return value


draftsman_converters.add_hook_fns(
    ManualSection,
    lambda fields: {
        fields.index.name: "index",
        fields.filters.name: "filters",
        fields.group.name: "group",
        fields.active.name: "active",
    },
)


@attrs.define
class QualityFilter(Exportable):
    """
    An object used to select particular qualities; used by
    :py:attr:`.SelectorCombinator.quality_filter`.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    quality: Literal[None, QualityID] = attrs.field(
        default=None,
        validator=one_of(Literal[None, QualityID]),
        metadata={"never_null": True},
    )
    """
    The signal quality to compare against.
    """

    comparator: Comparator = attrs.field(
        default="=",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
    )
    """
    The comparison operation to perform.
    """


draftsman_converters.add_hook_fns(
    QualityFilter,
    lambda fields: {
        "quality": fields.quality.name,
        "comparator": fields.comparator.name,
    },
)


@attrs.define
class InventoryPosition(Exportable):
    """
    An object which represents a particular inventory slot inside of an entity.

    .. seealso::

        :py:class:`.BlueprintInsertPlan`

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    inventory: InventoryType = attrs.field(
        converter=InventoryType, validator=instance_of(InventoryType)
    )
    """
    Which inventory this item sits in. As of Factorio 2.0, entities can have 
    multiple internal inventories which can be separately delivered to, such as
    inputs, outputs, ammo storage, trash slots, etc.
    """

    stack: uint32 = attrs.field(validator=instance_of(uint32))
    """
    Which slot in the inventory this item sits in.
    """

    count: Optional[uint32] = attrs.field(
        default=1, validator=instance_of(Optional[uint32])
    )
    """
    The amount of the item to request to that slot. Defaults to 1 if 
    omitted.
    """


draftsman_converters.add_hook_fns(
    InventoryPosition,
    lambda fields: {
        "inventory": fields.inventory.name,
        "stack": fields.stack.name,
        "count": fields.count.name,
    },
)


@attrs.define
class ItemInventoryPositions(Exportable):
    """
    An object which holds a list of all positions an item should be requested to
    inside of an entity, as well as a count of how many of that item exist in an
    attached equipment grid.

    .. seealso::

        :py:class:`.BlueprintInsertPlan`

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    def _convert_inventory_location_list(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                res[i] = InventoryPosition.converter(elem)
            return res
        else:
            return value

    in_inventory: list[InventoryPosition] = attrs.field(
        factory=list,
        converter=_convert_inventory_location_list,
        validator=instance_of(list[InventoryPosition]),
    )
    """
    The list of all unique :py:class:`.InventoryPosition` s that the item should 
    go.
    """

    grid_count: uint32 = attrs.field(default=0, validator=instance_of(uint32))
    """
    The total amount of this item being requested to the attached equipment grid,
    if applicable. Always zero if the entity has no equipment grid to request to.

    The positions of the item in the equipment grid is defined elsewhere in the
    :py:attr:`~.EquipmentGridMixin.equipment` attribute.
    """


draftsman_converters.add_hook_fns(
    ItemInventoryPositions,
    lambda fields: {
        fields.in_inventory.name: "in_inventory",
        fields.grid_count.name: "grid_count",
    },
)


@attrs.define
class ItemID(Exportable):
    """
    An object representing a particular item. Used by
    :py:attr:`BlueprintInsertPlan.id`.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    name: ItemIDName = attrs.field(validator=instance_of(ItemIDName))
    """
    The name of the item.
    """

    quality: QualityID = attrs.field(default="normal", validator=one_of(QualityID))
    """
    The quality of the item.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, str):
            return cls(name=value)
        elif isinstance(value, dict):
            return cls(**value)
        return value


draftsman_converters.add_hook_fns(
    ItemID,
    lambda fields: {"name": fields.name.name, "quality": fields.quality.name},
)


@attrs.define
class BlueprintInsertPlan(Exportable):
    """
    An object that represents a set of construction requests for a particular
    item.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    id: ItemID = attrs.field(converter=ItemID.converter, validator=instance_of(ItemID))
    """
    The item and quality of that item to request on construction.
    """

    items: ItemInventoryPositions = attrs.field(
        factory=ItemInventoryPositions,
        converter=ItemInventoryPositions.converter,
        validator=instance_of(ItemInventoryPositions),
    )
    """
    The equipment grids/inventories each item is being requested to.
    """


draftsman_converters.add_hook_fns(
    BlueprintInsertPlan,
    lambda fields: {
        fields.id.name: "id",
        fields.items.name: "items",
    },
)


@attrs.define
class EquipmentID(Exportable):
    """
    An object representing a particular type of equipment.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    name: str = attrs.field(validator=instance_of(str))  # TODO: EquipmentName
    """
    The name of the equipment.
    """

    quality: QualityID = attrs.field(default="normal", validator=one_of(QualityID))
    """
    The quality of the quipment
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, str):
            return cls(name=value)
        if isinstance(value, dict):
            return cls(**value)
        return value


draftsman_converters.add_hook_fns(
    EquipmentID,
    lambda fields: {
        "name": fields.name.name,
        "quality": fields.quality.name,
    },
)


@attrs.define
class EquipmentComponent(Exportable):
    """
    An object representing a piece of equipment and it's location in an attached
    equipment grid.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    equipment: EquipmentID = attrs.field(
        converter=EquipmentID.converter, validator=instance_of(EquipmentID)
    )
    """
    The type of equipment to add.
    """

    position: Vector = attrs.field(  # TODO: maybe tile_position?
        converter=lambda v: Vector.from_other(v, type_cast=int),
        validator=instance_of(Vector),
    )
    """
    The integer coordinate of the top leftmost tile in which this item sits.
    """


draftsman_converters.add_hook_fns(
    EquipmentComponent,
    lambda fields: {
        "equipment": fields.equipment.name,
        "position": fields.position.name,
    },
)


@attrs.define
class StockConnection(Exportable):
    """
    A structure representing a train coupling between wagons.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    stock: Association = attrs.field(
        converter=lambda v: v if isinstance(v, (Association, int)) else Association(v),
        # TODO: validators
    )
    """
    What rolling stock's connections are being defined.
    """
    front: Optional[Association] = attrs.field(
        converter=lambda v: (
            v if v is None or isinstance(v, (Association, int)) else Association(v)
        ),
        default=None,
        # TODO: validators
    )
    """
    What rolling stock is connected at the front of :py:attr:`.stock`.
    """
    back: Optional[Association] = attrs.field(
        converter=lambda v: (
            v if v is None or isinstance(v, (Association, int)) else Association(v)
        ),
        default=None,
        # TODO: validators
    )
    """
    What rolling stock is connected at the back of :py:attr:`.stock`.
    """


draftsman_converters.add_hook_fns(
    StockConnection,
    lambda fields: {
        "stock": fields.stock.name,
        "front": fields.front.name,
        "back": fields.back.name,
    },
)


@attrs.define
class Inventory(Exportable):
    """
    An object which represents an inventory - stores metadata related to it's
    internal :py:attr:`.size`, and allows to set it's :py:attr:`.filters` and
    limiting :py:attr:`.bar` all in one place.

    .. NOTE::

        On certain entities, setting some of these attributes will have no
        on the serialized output. Consult each entity attribute for details.
    """

    _parent: Optional[weakref.ref] = attrs.field(
        default=None,
        init=False,
        repr=False,
        eq=False,
    )

    _size_func: Callable = attrs.field(
        default=lambda _: None, init=False, repr=True, eq=False
    )

    def _set_parent(self, entity: Any, old_inventory: "Inventory", size_func=None):
        if old_inventory is not None:
            old_inventory._parent = None
        self._parent = weakref.ref(entity)
        self._size_func = size_func
        return self

    @property
    def size(self) -> Optional[uint16]:
        """
        The number of inventory slots that this Entity has. Equivalent to the
        ``"inventory_size"`` key in Factorio's ``data.raw``. Returns ``None`` if
        this entity's name is not recognized by Draftsman.
        """
        return self._size_func(self._parent if self._parent is None else self._parent())

    # =========================================================================

    def _filters_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    value[i] = ItemFilter(index=i, name=elem)
                else:
                    value[i] = elem
        return value

    filters: list[ItemFilter] = attrs.field(
        factory=list,
        converter=_filters_converter,
        validator=instance_of(list[ItemFilter]),
    )
    """
    The list of filters applied to this entity's inventory slots.
    """

    # =========================================================================

    bar: Optional[uint16] = attrs.field(
        default=None,
        validator=and_(
            instance_of(Optional[uint16]), ensure_bar_less_than_inventory_size
        ),
    )
    """
    The limiting bar of the inventory. Used to prevent a the final-most
    slots in the inventory from accepting items.

    Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
    exceeds the Entity's ``inventory_size`` attribute.
    """

    # =========================================================================

    def set_filter(
        self,
        index: int64,
        item: Optional[ItemIDName],
        quality: QualityID = "normal",
        comparator: Comparator = "=",
    ):
        """
        Sets the item filter at a particular index. If ``item`` is set to
        ``None``, the item filter at that location is removed.

        :param index: The index of the filter to set.
        :param item: The string name of the item to filter.

        :exception TypeError: If ``index`` is not an ``int`` or if ``item`` is
            neither a ``str`` nor ``None``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception IndexError: If ``index`` lies outside the range
            ``[0, inventory_size)``.
        """
        if item is not None:
            new_entry = ItemFilter(
                index=index, name=item, quality=quality, comparator=comparator
            )

        # Check to see if filters already contains an entry with the same index
        found_index = None
        for i, filter in enumerate(self.filters):
            if filter.index == index:  # Index already exists in the list
                if item is None:
                    # Delete the entry
                    del self.filters[i]
                else:
                    # Modify the existing value inplace
                    self.filters[i] = new_entry
                found_index = i
                break

        if found_index is None:
            # If no entry with the same index was found
            # self.filters.append(new_entry)
            self.filters += [new_entry]


draftsman_converters.add_hook_fns(
    Inventory,
    lambda fields: {
        "filters": fields.filters.name,
        "bar": fields.bar.name,
    },
)


@attrs.define
class EntityFilter(Exportable):
    """
    A object representing a filter of a particular entity with a quality or a
    range of qualities.
    """

    name: EntityID = attrs.field(validator=instance_of(EntityID))
    """
    Name of the entity.
    """

    index: Optional[uint64] = attrs.field(default=None, validator=instance_of(uint64))
    """
    Position of the filter in the GUI.
    """

    quality: QualityID = attrs.field(
        default="normal",
        validator=one_of(QualityID),
        metadata={"never_null": True},
    )
    """
    Quality flag of the entity. Defaults to special "any" quality signal if not
    specified.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """

    comparator: Comparator = attrs.field(
        default="=",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
        metadata={"omit": False},
    )
    """
    Comparison operator to use when deducing the range of qualities to select.

    .. versionadded:: 3.0.0 (Factorio 2.0)
    """


draftsman_converters.add_hook_fns(
    EntityFilter,
    lambda fields: {
        "name": fields.name.name,
        "index": fields.index.name,
        "quality": fields.quality.name,
        "comparator": fields.comparator.name,
    },
)


@attrs.define
class TileFilter(Exportable):
    """
    An object representing the filter of a particular tile.
    """

    index: Optional[uint64] = attrs.field(validator=instance_of(uint64))
    """
    Position of the filter in the GUI.
    """

    name: TileID = attrs.field(validator=instance_of(TileID))
    """
    The name of a valid deconstructable tile.
    """


draftsman_converters.add_hook_fns(
    EntityFilter,
    lambda fields: {
        "index": fields.index.name,
        "name": fields.name.name,
    },
)
