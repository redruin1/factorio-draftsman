# signatures.py

"""
Module of data formats, implemented as pydantic ``BaseModel`` instances. Used 
to validate and normalize data. Each one raises a ``ValidationError`` if the 
passed in data does not  match the data format specified, which is usually 
wrapped with a ``DataFormatError`` of some kind.

Alongside errors, all functions are set up to use a ``context`` to store 
warnings to be reissued later, since Pydantic does not support this out of the 
box.
"""


from draftsman.classes.association import Association
from draftsman.classes.exportable import Exportable
from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
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
from typing import Any, Literal, Optional, Sequence
import warnings
import weakref


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
    """
    Validator function builder for any type of unknown name.
    """

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

    .. example::

        some_signal = SignalID("iron-ore")
        assert some_signal.name == "iron-ore"
        assert some_signal.type == "item"
        assert some_signal.quality == "normal"

    Because the name ``"iron-ore"`` is known, Draftsman can pick a correct ``type``
    for it. For most applications, this defaults to ``"item"``, but notable
    exceptions include fluids (``"fluid"``) and virtual signals (``"virtual"``):

    .. example::

        assert SignalID("iron-ore").type == "item"
        assert SignalID("steam").type == "fluid"
        assert SignalID("signal-A").type == "virtual"

    In Factorio 2.0 and up, multiple SignalID's can share the same name but have
    different types. The default signal type is the first entry in the return
    result of :py:func:`get_valid_types(name)`, which in most circumstances is
    usually ``"item"``. If you want a different type than the default, it must
    be manually specified:

    .. example::

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
    def check_type_matches_name(self, _attr: attrs.Attribute, value: SignalIDType):
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
    index: uint32 = attrs.field(validator=instance_of(uint32))
    """
    Index of the target in the GUI, 0-based.
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
    index: uint32 = attrs.field(validator=instance_of(uint32))
    """
    TODO
    """
    name: str = attrs.field(validator=instance_of(str))  # TODO: AsteroidChunkName
    """
    TODO
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
    signal: SignalID = attrs.field(
        converter=SignalID.converter, validator=instance_of(SignalID)
    )
    """
    Which signal icon to display.
    """
    index: uint8 = attrs.field(validator=instance_of(uint8))
    """
    Numeric index of the icon, 1-based.
    """

    @classmethod
    def converter(cls, value, index):
        try:
            if "index" not in value:
                value["index"] = index
            return cls(**value)
        except TypeError:
            return value


draftsman_converters.add_hook_fns(
    Icon,
    lambda fields: {
        "signal": fields.signal.name,
        "index": fields.index.name,
    },
)


# def normalize_icons(value: Any):
#     if isinstance(value, str):
#         return value
#     elif isinstance(value, Sequence):
#         result = []
#         for i, signal in enumerate(value):
#             if isinstance(signal, str):
#                 result.append({"index": i + 1, "signal": signal_dict(signal)})
#             elif isinstance(signal, dict) and "type" in signal:
#                 result.append({"index": i + 1, "signal": signal})
#             else:
#                 result.append(signal)
#         return result
#     else:
#         return value


# class Icons(DraftsmanRootModel):
#     root: list[Icon] = Field(
#         ...,
#         max_length=4,
#         description="""
#         The list of all icons used by this object. Hard-capped to 4 entries
#         total; having more than 4 will raise an error in import.
#         """,
#     )

#     @model_validator(mode="before")
#     def normalize_icons(cls, value: Any):
#         if isinstance(value, Sequence):
#             result = [None] * len(value)
#             for i, signal in enumerate(value):
#                 if isinstance(signal, str):
#                     result[i] = {"index": i + 1, "signal": signal}
#                 else:
#                     result[i] = signal
#             return result
#         else:
#             return value


@attrs.define(hash=True)
class Color(Exportable):
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
    index: int64 = attrs.field(
        converter=try_convert(
            lambda index: index + 1
        ),  # Convert from zero-indexed to 1-indexed
        validator=instance_of(int64),
    )
    """
    Index of the filter in the GUI, 1-indexed.
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
    """
    comparator: Comparator = attrs.field(
        default="=",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
    )
    """
    Comparator if filtering a range of different qualities.
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
    of :py:class:`.ConstantCombinator`s.
    """

    index: int64 = attrs.field(
        # TODO: handle indexes properly
        # I want to perform the + 1 step inside of the Exportable object so
        # that if it fails due to invalid type it gets wrapped by the error
        # handler, but it introduces overlap between "importing from dict" and
        # "constructing python object"
        # This makes mes think that the true ideal would be to customize cattrs
        # so that the value only changes on import/export (but that means the
        # cattrs side needs to be more error robust)
        # converter=try_convert(lambda index: index + 1),
        validator=instance_of(int64),
    )
    """
    Numeric index of the signal in the combinator, 1-based. Typically the 
    index of the signal in the parent 'filters' key, but this is not 
    strictly enforced. 
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
        # metadata={"omit": False}
    )
    """
    Type of the signal.
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
    """
    comparator: Comparator = attrs.field(
        default="=",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
        metadata={"omit": False},
    )
    """
    Comparison operator when deducing the quality type.
    """
    max_count: Optional[int32] = attrs.field(
        default=None,
        validator=instance_of(Optional[int32]),
        metadata={"never_null": True},
    )
    """
    The maximum amount of the signal to request of the signal to emit. Only used
    (currently) with logistics-type requests.
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
    logistics sections as well as constant combinators signal groups.
    """

    index: LuaDouble = attrs.field(validator=instance_of(LuaDouble))
    """
    Location of the logistics section within the entity, 1-indexed. Hard capped
    to 100 manual sections per entity.
    """

    @index.validator
    @conditional(ValidationMode.MINIMUM)
    def _index_validator(self, attr, value):
        """
        Can only have 100 signal sections per entity.
        """
        if not (1 <= value <= 100):
            msg = "Index ({}) must be in range [1, 100]".format(value)
            raise IndexError(msg)

    def _filters_converter(value: list[Any]) -> list[SignalFilter]:
        if isinstance(value, list):
            for i, entry in enumerate(value):
                if isinstance(entry, tuple):
                    value[i] = SignalFilter(
                        index=i + 1,
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
    overwrite the one specified here.
    """

    active: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not this logistic section is currently enabled in this entity.
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
        """
        if name is not None:
            new_entry = SignalFilter(
                index=index + 1,  # TODO: perform this transformation on export
                name=name,
                type=type if type is not None else NOTHING,
                quality=quality,
                comparator="=",
                count=count,
            )

        # Check to see if filters already contains an entry with the same index
        existing_index = None
        for i, signal_filter in enumerate(self.filters):
            if index + 1 == signal_filter.index:  # Index already exists in the list
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
        Get the :py:data:`.SIGNAL_FILTER` ``dict`` entry at a particular index,
        if it exists.

        :param index: The index of the signal to analyze.

        :returns: A ``dict`` that conforms to :py:data:`.SIGNAL_FILTER`, or
            ``None`` if nothing was found at that index.
        """
        return next(
            (item for item in self.filters if item.index == index + 1),
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


# class Section(DraftsmanBaseModel):
#     index: uint32  # TODO: 0-based or 1-based?
#     filters: Optional[list[SignalFilter]] = []
#     group: Optional[str] = Field(
#         None,
#         description="Name of this particular signal section group.",
#     )

#     def set_signal(
#         self,
#         index: int64,
#         name: Union[str, None],
#         count: int32 = 0,
#         quality: Literal[
#             "normal",
#             "uncommon",
#             "rare",
#             "epic",
#             "legendary",
#             "quality-unknown",
#             "any",
#         ] = "normal",
#         type: Optional[str] = None,
#     ) -> None:
#         try:
#             new_entry = SignalFilter(
#                 index=index,
#                 name=name,
#                 type=type,
#                 quality=quality,
#                 comparator="=",
#                 count=count,
#             )
#             new_entry.index += 1
#         except ValidationError as e:
#             raise DataFormatError(e) from None

#         new_filters = [] if self.filters is None else self.filters

#         # Check to see if filters already contains an entry with the same index
#         existing_index = None
#         for i, signal_filter in enumerate(new_filters):
#             if index + 1 == signal_filter["index"]:  # Index already exists in the list
#                 if name is None:  # Delete the entry
#                     del new_filters[i]
#                 else:
#                     new_filters[i] = new_entry
#                 existing_index = i
#                 break

#         if existing_index is None:
#             new_filters.append(new_entry)

#     def get_signal(self, index):
#         """
#         Get the :py:data:`.SIGNAL_FILTER` ``dict`` entry at a particular index,
#         if it exists.

#         :param index: The index of the signal to analyze.

#         :returns: A ``dict`` that conforms to :py:data:`.SIGNAL_FILTER`, or
#             ``None`` if nothing was found at that index.
#         """
#         if not self.filters:
#             return None

#         return next(
#             (item for item in self.filters if item["index"] == index + 1),
#             None,
#         )

#     @field_validator("filters", mode="before")
#     @classmethod
#     def normalize_input(cls, value: Any):
#         if isinstance(value, list):
#             for i, entry in enumerate(value):
#                 if isinstance(entry, tuple):
#                     # TODO: perhaps it would be better to modify the format so
#                     # you must specify the signal type... or maybe not...
#                     signal_types = get_signal_types(entry[0])
#                     filter_type = (
#                         "item" if "item" in signal_types else next(iter(signal_types))
#                     )
#                     value[i] = {
#                         "index": i + 1,
#                         "name": entry[0],
#                         "type": filter_type,
#                         "comparator": "=",
#                         "count": entry[1],
#                     }

#         return value

#     model_config = ConfigDict(validate_assignment=True)


# class SignalSection(Section):
#     filters: Optional[list[SignalFilter]] = []


# class RequestSection(Section):
#     filters: Optional[list[RequestFilter]] = []


# class QualityFilter(DraftsmanBaseModel):
#     quality: Optional[QualityName] = Field(
#         "any", description="""The quality of the signal to compare against."""
#     )
#     comparator: Optional[Literal[">", "<", "=", "≥", "≤", "≠"]] = Field(
#         "=",
#         description="""The comparison operator to use when evaluating signal comparisons.""",
#     )

#     @field_validator("comparator", mode="before")
#     @classmethod
#     def normalize_comparator_python_equivalents(cls, input: Any):
#         conversions = {"==": "=", ">=": "≥", "<=": "≤", "!=": "≠"}
#         if input in conversions:
#             return conversions[input]
#         else:
#             return input


@attrs.define
class QualityFilter(Exportable):
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
    inventory: uint32 = attrs.field(validator=instance_of(uint32))
    """
    Which inventory this item sits in, 1-indexed.
    """
    stack: uint32 = attrs.field(validator=instance_of(uint32))
    """
    Which slot in the inventory this item sits in, 0-indexed.
    """
    count: Optional[uint32] = attrs.field(
        default=1, validator=instance_of(Optional[uint32])
    )
    """
    The amount of that item to request to that slot. Defaults to 1 if 
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
    The list of all locations that the selected item should go.
    """
    grid_count: uint32 = attrs.field(default=0, validator=instance_of(uint32))
    """
    The total amount of this item being requested to the attached equipment grid,
    if applicable. Always zero if the entity has no equipment grid to request to.
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
    name: ItemIDName = attrs.field(validator=instance_of(ItemIDName))
    quality: QualityID = attrs.field(default="normal", validator=one_of(QualityID))

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
    id: ItemID = attrs.field(converter=ItemID.converter, validator=instance_of(ItemID))
    """
    The item to request.
    """
    items: ItemInventoryPositions = attrs.field(
        factory=ItemInventoryPositions,
        converter=ItemInventoryPositions.converter,
        validator=instance_of(ItemInventoryPositions),
    )
    """
    The grids/locations each item is being requested to.
    """


draftsman_converters.add_hook_fns(
    BlueprintInsertPlan,
    lambda fields: {
        fields.id.name: "id",
        fields.items.name: "items",
    },
)


# class Sections(DraftsmanBaseModel):
#     # class Section(DraftsmanBaseModel):
#     #     index: uint32
#     #     filters: Optional[list[SignalFilter]] = []
#     #     group: Optional[str] = Field(
#     #         None,
#     #         description="Name of this particular signal section group.",
#     #     )

#     #     def set_signal(
#     #         self,
#     #         index: int64,
#     #         name: Union[str, None],
#     #         count: int32 = 0,
#     #         quality: Literal[
#     #             "normal",
#     #             "uncommon",
#     #             "rare",
#     #             "epic",
#     #             "legendary",
#     #             "quality-unknown",
#     #             "any",
#     #         ] = "normal",
#     #         type: Optional[str] = None,
#     #     ) -> None:
#     #         try:
#     #             new_entry = SignalFilter(
#     #                 index=index,
#     #                 name=name,
#     #                 type=type,
#     #                 quality=quality,
#     #                 comparator="=",
#     #                 count=count,
#     #             )
#     #             new_entry.index += 1
#     #         except ValidationError as e:
#     #             raise DataFormatError(e) from None

#     #         new_filters = [] if self.filters is None else self.filters

#     #         # Check to see if filters already contains an entry with the same index
#     #         existing_index = None
#     #         for i, signal_filter in enumerate(new_filters):
#     #             if (
#     #                 index + 1 == signal_filter["index"]
#     #             ):  # Index already exists in the list
#     #                 if name is None:  # Delete the entry
#     #                     del new_filters[i]
#     #                 else:
#     #                     new_filters[i] = new_entry
#     #                 existing_index = i
#     #                 break

#     #         if existing_index is None:
#     #             new_filters.append(new_entry)

#     #     def get_signal(self, index):
#     #         """
#     #         Get the :py:data:`.SIGNAL_FILTER` ``dict`` entry at a particular index,
#     #         if it exists.

#     #         :param index: The index of the signal to analyze.

#     #         :returns: A ``dict`` that conforms to :py:data:`.SIGNAL_FILTER`, or
#     #             ``None`` if nothing was found at that index.
#     #         """
#     #         if not self.filters:
#     #             return None

#     #         return next(
#     #             (item for item in self.filters if item["index"] == index + 1),
#     #             None,
#     #         )

#     #     @field_validator("filters", mode="before")
#     #     @classmethod
#     #     def normalize_input(cls, value: Any):
#     #         if isinstance(value, list):
#     #             for i, entry in enumerate(value):
#     #                 if isinstance(entry, tuple):
#     #                     value[i] = {
#     #                         "index": i + 1,
#     #                         "name": entry[0],
#     #                         "type": next(iter(get_signal_types(entry[0]))),
#     #                         "comparator": "=",
#     #                         "count": entry[1],
#     #                         "max_count": entry[1],
#     #                     }

#     #         return value

#     #     model_config = ConfigDict(validate_assignment=True)

#     sections: Optional[list[Section]] = Field([], description="""TODO""")

#     def __getitem__(self, key):
#         # Custom getitem for this thing specfically
#         # return self.sections[key]
#         if isinstance(key, str):
#             return next(section for section in self.sections if section.group == key)
#         else:
#             return self.sections[key]


@attrs.define
class EquipmentID(Exportable):
    name: str = attrs.field()  # TODO: validators, EquipmentName
    """
    The name of the equipment.
    """
    quality: QualityID = attrs.field(
        default="normal", validator=one_of(QualityID)
    )  # TODO: validators
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
    equipment: EquipmentID = attrs.field(
        converter=EquipmentID.converter, validator=instance_of(EquipmentID)
    )
    """
    The type of equipment to add.
    """

    position: Vector = attrs.field(
        converter=lambda v: Vector.from_other(v, type_cast=int),
        validator=instance_of(Vector),
    )
    """
    The integer coordinate of the top leftmost tile in which this item sits, 
    0-based.
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
    # TODO: all of these should probably have converters which take EntityLikes and wrap them with Association
    stock: Association = attrs.field(
        # TODO: validators
    )
    front: Optional[Association] = attrs.field(default=None)
    back: Optional[Association] = attrs.field(default=None)


# TODO: test
draftsman_converters.add_hook_fns(  # pragma: no branch
    StockConnection,
    lambda fields: {
        "stock": fields.stock.name,
        "front": fields.front.name,
        "back": fields.back.name,
    },
)


@attrs.define
class Inventory(Exportable):
    _parent: Optional[weakref.ref] = attrs.field(
        default=None,
        init=False,
        repr=False,
        eq=False,
    )

    _size_func = attrs.field(init=False, repr=False, eq=False)

    def _set_parent(
        self, entity: Any, old_inventory: "Inventory", size_func=None
    ):
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
        this entity's name is not recognized by Draftsman. Not exported; read
        only.
        """
        return self._size_func(self._parent())

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

    :getter: Gets the bar location of the inventory, or ``None`` if not set.
    :setter: Sets the bar location of the inventory. Removes the entry from
        the ``inventory`` object.

    :exception TypeError: If set to anything other than an ``int`` or
        ``None``.
    :exception IndexError: If the set value lies outside of the range
        ``[0, 65536)``.
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
            if filter.index == index + 1:  # Index already exists in the list
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
    name: EntityID = attrs.field(validator=instance_of(EntityID))
    """
    Name of the entity.
    """
    quality: Literal[None, QualityID] = attrs.field(
        default=None,
        validator=one_of(Literal[None, QualityID]),
        metadata={"never_null": True},
    )
    """
    Quality flag of the entity. Defaults to special "any" quality signal if not
    specified.
    """
    comparator: Comparator = attrs.field(
        default="=",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
        metadata={"omit": False},
    )
    """
    Comparison operator when deducing the quality type.
    """
