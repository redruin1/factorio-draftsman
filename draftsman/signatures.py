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
    InvalidMapperError,
    InvalidSignalError,
    IncompleteSignalError,
)
from draftsman.serialization import draftsman_converters
from draftsman.utils import encode_version, get_suggestion
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
from typing import Any, Literal, Optional, Sequence, Union
import warnings


int32 = Annotated[int, and_(ge(-(2**31)), lt(2**31))]
# TODO: description about floating point issues
int64 = Annotated[int, and_(ge(-(2**63)), lt(2**63))]
# Maximum size of Lua double before you lose integer precision
LuaDouble = Annotated[int, and_(ge(-(2**53)), lt(2**53))]

draftsman_converters.add_schema(
    {
        "$id": "urn:int32",
        "type": "integer",
        "min": -(2**31),
        "exclusiveMax": 2**31,
    }
)
draftsman_converters.add_schema(
    {
        "$id": "urn:int64",
        "type": "integer",
        "min": -(2**63),
        "exclusiveMax": 2**63,
    }
)
draftsman_converters.add_schema(
    {
        "$id": "urn:lua-double",
        "type": "integer",
        "min": -(2**53),
        "exclusiveMax": 2**53,
    }
)

uint8 = Annotated[int, and_(ge(0), lt(2**8))]
uint16 = Annotated[int, and_(ge(0), lt(2**16))]
uint32 = Annotated[int, and_(ge(0), lt(2**32))]
# TODO: description about floating point issues
uint64 = Annotated[int, and_(ge(0), lt(2**64))]

draftsman_converters.add_schema(
    {
        "$id": "urn:uint8",
        "type": "integer",
        "min": 0,
        "exclusiveMax": 2**8,
    }
)
draftsman_converters.add_schema(
    {
        "$id": "urn:uint16",
        "type": "integer",
        "min": 0,
        "exclusiveMax": 2**16,
    }
)
draftsman_converters.add_schema(
    {
        "$id": "urn:uint32",
        "type": "integer",
        "min": 0,
        "exclusiveMax": 2**32,
    }
)
draftsman_converters.add_schema(
    {
        "$id": "urn:uint64",
        "type": "integer",
        "min": 0,
        "exclusiveMax": 2**64,
    }
)


def known_name(type: str, structure: dict, issued_warning: Warning):
    """
    Validator function builder for any type of unknown name.
    """

    def validator(
        inst: Exportable,
        attr: attrs.Attribute,
        value: str,
        mode: Optional[ValidationMode] = None,
        warning_list: Optional[list] = None,
    ) -> str:
        mode = mode if mode is not None else inst.validate_assignment

        if mode >= ValidationMode.STRICT:
            if value not in structure:
                msg = "Unknown {} '{}'{}".format(
                    type, value, get_suggestion(value, structure.keys(), n=1)
                )
                if warning_list is None:
                    warnings.warn(issued_warning(msg))
                else:
                    warning_list.append(issued_warning(msg))

    return validator


ItemName = Annotated[str, known_name("item", items.raw, UnknownItemWarning)]
SignalName = Annotated[str, known_name("signal", signals.raw, UnknownSignalWarning)]
EntityName = Annotated[str, known_name("entity", entities.raw, UnknownEntityWarning)]
FluidName = Annotated[str, known_name("fluid", fluids.raw, UnknownFluidWarning)]
TileName = Annotated[str, known_name("tile", tiles.raw, UnknownTileWarning)]
RecipeName = Annotated[str, known_name("recipe", recipes.raw, UnknownRecipeWarning)]
ModuleName = Annotated[str, known_name("module", modules.raw, UnknownModuleWarning)]
QualityName = Literal[
    "normal", "uncommon", "rare", "epic", "legendary", "quality-unknown", "any"
]
draftsman_converters.add_schema(
    {
        "$id": "urn:factorio:quality-name",
        "enum": [
            "normal",
            "uncommon",
            "rare",
            "epic",
            "legendary",
            "quality-unknown",
            "any",
        ],
    }
)
SignalType = Literal[
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
class AttrsMapperID(Exportable):
    name: str = attrs.field()  # TODO: optional? # TODO: validators
    type: Literal["entity", "item"] = attrs.field(  # TODO: optional?
        validator=one_of("entity", "item")
    )
    # TODO: has quality now

    @classmethod
    def converter(cls, value):
        if isinstance(value, str):
            try:
                return cls(**signals.mapper_dict(value))  # FIXME
            except InvalidMapperError as e:
                raise InvalidMapperError(
                    "Unknown mapping target {}; either specify the full dictionary, or update your environment".format(
                        e
                    )
                ) from None
        elif isinstance(value, dict):
            return cls(**value)
        else:
            return value


AttrsMapperID.add_schema(
    {
        "$id": "urn:factorio:upgrade-planner:mapper-id",
        "properties": {
            "name": {"type": "string"},
            "type": {"enum": ["entity", "item"]},
        },
    }
)

draftsman_converters.add_hook_fns(
    AttrsMapperID,
    lambda fields: {
        "name": fields.name.name,
        "type": fields.type.name,
    },
)


@attrs.define
class AttrsMapper(Exportable):
    index: uint64 = attrs.field(validator=instance_of(uint64))
    from_: Optional[
        AttrsMapperID
    ] = attrs.field(  # TODO: this has quality + any quality + comparator
        default=None,
        converter=AttrsMapperID.converter,
        validator=instance_of(Optional[AttrsMapperID]),
    )
    to: Optional[AttrsMapperID] = attrs.field(  # TODO: this has quality
        default=None,
        converter=AttrsMapperID.converter,
        validator=instance_of(Optional[AttrsMapperID]),
    )

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(
                index=value["index"],
                from_=value.get("from", None),
                to=value.get("to", None),
            )
        else:
            return value


# TODO: versioning

AttrsMapper.add_schema(
    {
        "$id": "urn:factorio:upgrade-planner:mapper",
        "properties": {
            "index": {"$ref": "urn:uint64"},
            "from": {"$ref": "urn:factorio:upgrade-planner:mapper-id"},
            "to": {"$ref": "urn:factorio:upgrade-planner:mapper-id"},
        },
    }
)


draftsman_converters.add_hook_fns(
    AttrsMapper,
    lambda fields: {
        "index": fields.index.name,
        "from": fields.from_.name,
        "to": fields.to.name,
    },
)


@attrs.define
class AttrsSignalID(Exportable):
    """
    A signal ID.

    For convenience, a SignalID object can be constructed with just the string
    name:

    TODO

    In this case, the signal ``type`` is equivalent to the first entry in the
    return result of ``get_valid_types(name)``. For most applications, this
    defaults to ``"item"``, but notable exceptions include fluids (``"fluid"``)
    and virtual signals (``"virtual"``). In cases where signals have more than
    one valid type and you wish to use one other than the default, the full
    constructor must be used.
    """

    name: Optional[SignalName] = attrs.field(
        default=None, validator=instance_of(Optional[SignalName])
    )
    """
    Name of the signal. If omitted, the signal is treated as no signal and 
    removed on import/export cycle.
    """

    type: Literal[SignalType] = attrs.field(
        validator=one_of(SignalType), metadata={"omit": False}
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

    quality: Optional[QualityName] = attrs.field(
        default="normal", validator=or_(one_of(QualityName), is_none)
    )
    """
    Quality flag of the signal.
    """

    @classmethod
    def converter(cls, value: Any) -> "AttrsSignalID":
        """
        Attempt to convert an input string name into a SignalID representation.
        Raises a ValueError if unable to determine the type of a signal's name,
        likely if the signal is misspelled or used in a modded configuration
        that differs from Draftsman's current one.
        """
        if isinstance(value, str):
            try:
                # TODO: make function to grab default signal type
                if "item" in signals.get_signal_types(value):
                    return AttrsSignalID(name=value, type="item")
                else:
                    return AttrsSignalID(
                        name=value, type=signals.get_signal_types(value)[0]
                    )
            # return AttrsSignalID(name=value)
            except InvalidSignalError as e:
                msg = "Unknown signal name {}; either specify the full dictionary, or update your environment".format(
                    repr(value)
                )
                raise IncompleteSignalError(msg) from None
        elif isinstance(value, dict):
            return AttrsSignalID(**value)
        else:
            return value

    @type.validator
    def check_type_matches_name(
        self, attribute, value, mode: Optional[ValidationMode] = None
    ):
        mode = mode if mode is not None else self.validate_assignment
        if mode >= ValidationMode.STRICT:
            if self.name in signals.raw:
                expected_types = signals.get_signal_types(self.name)
                if value not in expected_types:
                    msg = "Known signal '{}' was given a mismatching type (expected one of {}, found '{}')".format(
                        self.name, expected_types, value
                    )
                    warnings.warn(MalformedSignalWarning(msg))


AttrsSignalID.add_schema(
    {
        "$id": "urn:factorio:signal-id",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "type": {
                "enum": [
                    "item",
                    "fluid",
                    "virtual",
                ]
            },
        },
    },
    version=(1, 0),
)

AttrsSignalID.add_schema(
    {
        "$id": "urn:factorio:signal-id",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "type": {
                "enum": [
                    "item",
                    "fluid",
                    "virtual",
                    "recipe",
                    "entity",
                    "space-location",
                    "asteroid-chunk",
                    "quality",
                ]
            },
            "quality": {
                "enum": [
                    "normal",
                    "uncommon",
                    "rare",
                    "epic",
                    "legendary",
                    "quality-unknown",
                    "any",
                ]
            },
        },
    },
    version=(2, 0),
)


draftsman_converters.get_version((1, 0)).add_hook_fns(
    AttrsSignalID,
    lambda fields: {
        "name": fields.name.name,
        "type": fields.type.name,
        None: fields.quality.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    AttrsSignalID,
    lambda fields: {
        "name": fields.name.name,
        "type": fields.type.name,
        "quality": fields.quality.name,
    },
)

# def interpret_signal_id_string_factory(cls: type, converter: cattrs.Converter):
#     parent_hook = converter.get_structure_hook(Exportable)
#     def structure_hook(v, _):
#         print("wrapped hook")
#         return AttrsSignalID(name=v) if isinstance(v, str) else parent_hook(v, _)
#     return structure_hook

# draftsman_converters.register_structure_hook_factory(
#     lambda cls: issubclass(cls, AttrsSignalID), interpret_signal_id_string_factory
# )


@attrs.define
class TargetID(Exportable):
    index: uint32 = attrs.field(  # TODO: size, 0 or 1 based
        validator=instance_of(uint32)
    )
    """
    Index of the target in the GUI, 0-based.
    """
    name: str = attrs.field(validator=instance_of(str))  # TODO: TargetName?
    """
    Name of the target.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        return value


TargetID.add_schema(
    {
        "$id": "urn:factorio:target-id",
        "type": "object",
        "properties": {"index": {"$ref": "urn:uint32"}, "name": {"type": "string"}},
    }
)

draftsman_converters.add_hook_fns(
    TargetID, lambda fields: {"index": fields.index.name, "name": fields.name.name}
)


@attrs.define
class AttrsAsteroidChunkID(Exportable):
    index: uint32 = attrs.field(validator=instance_of(uint32))
    name: str = attrs.field(validator=instance_of(str))  # TODO: AsteroidChunkName

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        else:
            return value


AttrsAsteroidChunkID.add_schema(
    {
        "$id": "urn:factorio:asteroid-chunk-id",
        "type": "object",
        "properties": {"index": {"$ref": "urn:uint32"}, "name": {"type": "string"}},
    }
)


draftsman_converters.add_hook_fns(
    AttrsAsteroidChunkID,
    lambda fields: {
        fields.index.name: "index",
        fields.name.name: "name",
    },
)


@attrs.define
class AttrsIcon(Exportable):
    signal: AttrsSignalID = attrs.field(
        converter=AttrsSignalID.converter, validator=instance_of(AttrsSignalID)
    )
    """
    Which signal icon to display.
    """
    index: uint8 = attrs.field(validator=instance_of(uint8))
    """
    Numeric index of the icon, 1-based.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        return value


AttrsIcon.add_schema(
    {
        "$id": "urn:factorio:icon",
        "type": "object",
        "properties": {
            "index": {"$ref": "urn:uint8"},
            "signal": {"$ref": "urn:factorio:signal-id"},
        },
    }
)


draftsman_converters.add_hook_fns(
    AttrsIcon,
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
class AttrsColor(Exportable):
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
    def converter(cls, value) -> "AttrsColor":
        if isinstance(value, (tuple, list)):  # TODO: sequence
            return cls(*value)
        elif isinstance(value, dict):
            return cls(**value)
        else:
            return value


AttrsColor.add_schema(
    {
        "$id": "urn:factorio:color",
        "type": "object",
        "properties": {
            "r": {"type": "number"},
            "g": {"type": "number"},
            "b": {"type": "number"},
            "a": {"oneOf": [{"type": "number"}, {"type": "null"}]},
        },
        "required": ["r", "g", "b"],
    }
)

draftsman_converters.add_hook_fns(
    AttrsColor,
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
draftsman_converters.add_schema(
    {"$id": "urn:factorio:comparator", "enum": [">", "<", "=", "≥", "≤", "≠"]}
)


@attrs.define
class AttrsSimpleCondition(Exportable):
    first_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
        metadata={"never_null": True},
    )
    comparator: Comparator = attrs.field(
        default="<",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
    )
    constant: int32 = attrs.field(default=0, validator=instance_of(int32))
    second_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
        metadata={"never_null": True},
    )

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        else:
            return value


AttrsSimpleCondition.add_schema(
    {
        "$id": "urn:factorio:simple-condition",
        "type": "object",
        "properties": {
            "first_signal": {
                "anyOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
            },
            "comparator": {"$ref": "urn:factorio:comparator"},
            "constant": {"$ref": "urn:int32"},
            "second_signal": {
                "anyOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
            },
        },
    },
)


draftsman_converters.add_hook_fns(
    AttrsSimpleCondition,
    lambda fields: {
        "first_signal": fields.first_signal.name,
        "comparator": fields.comparator.name,
        "constant": fields.constant.name,
        "second_signal": fields.second_signal.name,
    },
)


@attrs.define
class AttrsNetworkSpecification(Exportable):
    red: bool = attrs.field(default=True, validator=instance_of(bool))
    green: bool = attrs.field(default=True, validator=instance_of(bool))

    @classmethod
    def converter(cls, value):
        if isinstance(value, set):
            return cls(**{k: k in value for k in ("red", "green")})
        elif isinstance(value, dict):
            return cls(**value)
        else:
            return value


AttrsNetworkSpecification.add_schema(
    {
        "$id": "urn:factorio:network-specification",
        "type": "object",
        "properties": {"red": {"type": "boolean"}, "green": {"type": "boolean"}},
    },
)


draftsman_converters.add_hook_fns(
    AttrsNetworkSpecification,
    lambda fields: {
        "red": fields.red.name,
        "green": fields.green.name,
    },
)


# class CircuitConnectionPoint(DraftsmanBaseModel):
#     entity_id: Association.Format
#     circuit_id: Optional[Literal[1, 2]] = None


# class WireConnectionPoint(DraftsmanBaseModel):
#     entity_id: Association.Format
#     wire_id: Optional[Literal[0, 1]] = None


# class Connections(DraftsmanBaseModel):
#     # _alias_map: ClassVar[dict] = PrivateAttr(
#     #     {
#     #         "1": "Wr1",
#     #         "2": "Wr2",
#     #         "Cu0": "Cu0",
#     #         "Cu1": "Cu1",
#     #     }
#     # )

#     def export_key_values(self):
#         return {k: getattr(self, v) for k, v in self.true_model_fields().items()}

#     class CircuitConnections(DraftsmanBaseModel):
#         red: Optional[list[CircuitConnectionPoint]] = None
#         green: Optional[list[CircuitConnectionPoint]] = None

#     Wr1: Optional[CircuitConnections] = Field(CircuitConnections(), alias="1")
#     Wr2: Optional[CircuitConnections] = Field(CircuitConnections(), alias="2")
#     Cu0: Optional[list[WireConnectionPoint]] = None
#     Cu1: Optional[list[WireConnectionPoint]] = None

#     # def __getitem__(self, key):
#     #     return super().__getitem__(self._alias_map[key])

#     # def __setitem__(self, key, value):
#     #     super().__setitem__(self._alias_map[key], value)

#     # def __contains__(self, item):
#     #     return item in self._alias_map and


@attrs.define
class AttrsItemFilter(Exportable):
    index: int64 = attrs.field(
        converter=try_convert(
            lambda index: index + 1
        ),  # Convert from zero-indexed to 1-indexed
        validator=instance_of(int64),
    )
    """
    Index of the filter in the GUI, 1-indexed.
    """
    name: ItemName = attrs.field(validator=instance_of(ItemName))
    """
    Name of the item.
    """
    # TODO: determine "any" quality
    # I think that might be the true default, but theres some additional info
    # needed
    quality: QualityName = attrs.field(default="normal", validator=one_of(QualityName))
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

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        else:
            return value


AttrsItemFilter.add_schema(
    {
        "$id": "urn:factorio:item-filter",
        "type": "object",
        "properties": {
            "index": {"$ref": "urn:int64"},
            "name": {"type": "string"},
            "quality": {
                "enum": [
                    "normal",
                    "uncommon",
                    "rare",
                    "epic",
                    "legendary",
                    "quality-unknown",
                    "any",
                ]
            },
            "comparator": {"$ref": "urn:factorio:comparator"},
        },
    }
)


draftsman_converters.add_hook_fns(
    AttrsItemFilter,
    lambda fields: {
        fields.index.name: "index",
        fields.name.name: "name",
        fields.quality.name: "quality",
        fields.comparator.name: "comparator",
    },
)


@conditional(ValidationMode.PEDANTIC)
def ensure_bar_less_than_inventory_size(
    self: Exportable,
    _: attrs.Attribute,
    value: Optional[uint16],
):
    if self.inventory_size is None or value is None:
        return
    if value >= self.inventory_size:
        msg = "Bar index ({}) exceeds the container's inventory size ({})".format(
            value, self.inventory_size
        )
        warnings.warn(BarWarning(msg))


# class Bar(RootModel):
#     root: uint16

#     @model_validator(mode="after")
#     @classmethod
#     def ensure_less_than_inventory_size(cls, bar: "Bar", info: ValidationInfo):
#         if not info.context or bar is None:
#             return bar
#         if info.context["mode"] == ValidationMode.MINIMUM:
#             return bar

#         warning_list: list = info.context["warning_list"]
#         entity = info.context["entity"]
#         if entity.inventory_size and bar.root >= entity.inventory_size:
#             issue = IndexWarning(  # TODO: change warning type
#                 "Bar index ({}) exceeds the container's inventory size ({})".format(
#                     bar, entity.inventory_size
#                 ),
#             )

#             if info.context["mode"] is ValidationMode.PEDANTIC:
#                 raise issue
#             else:
#                 warning_list.append(issue)

#         return bar


# class InventoryFilters(DraftsmanBaseModel):
#     filters: Optional[list[FilterEntry]] = Field(
#         None,
#         description="""
#         Any reserved item filter slots in the container's inventory.
#         """,
#     )
#     bar: Optional[uint16] = Field(
#         None,
#         description="""
#         Limiting bar on this container's inventory.
#         """,
#     )

#     @field_validator("filters", mode="before")
#     @classmethod
#     def normalize_filters(cls, value: Any):
#         if isinstance(value, (list, tuple)):
#             result = []
#             for i, entry in enumerate(value):
#                 if isinstance(entry, str):
#                     result.append({"index": i + 1, "name": entry})
#                 else:
#                     result.append(entry)
#             return result
#         else:
#             return value

#     @field_validator("bar")
#     @classmethod
#     def ensure_less_than_inventory_size(
#         cls, bar: Optional[uint16], info: ValidationInfo
#     ):
#         return ensure_bar_less_than_inventory_size(cls, bar, info)


@attrs.define
class SignalFilter(Exportable):
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
    name: SignalName = attrs.field(  # TODO: SignalName
        validator=instance_of(SignalName)
    )
    """
    Name of the signal.
    """
    count: int32 = attrs.field(validator=instance_of(int32))
    """
    Value of the signal filter, or the lower bound of a range if ``max_count`` 
    is also specified.
    """
    type: Optional[SignalType] = attrs.field(
        validator=or_(is_none, one_of(SignalType))
        # metadata={"omit": False}
    )
    """
    Type of the signal.
    """

    @type.default
    def _(self) -> SignalType:
        try:
            return signals.get_signal_types(self.name)[0]
        except InvalidSignalError:
            return "item"

    # signal: Optional[SignalID] = Field( # 1.0
    #     None,
    #     description="""
    #     Signal to broadcast. If this value is omitted the occupied slot will
    #     behave as if no signal exists within it. Cannot be a pure virtual
    #     (logic) signal like "signal-each", "signal-any", or
    #     "signal-everything"; if such signals are set they will be removed
    #     on import.
    #     """,
    # )
    # TODO: make quality dynamic based on current environment?
    quality: QualityName = attrs.field(default="any", validator=one_of(QualityName))
    """
    Quality flag of the signal. Defaults to special "any" quality signal, rather
    than "normal" quality.
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

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        else:
            return value


SignalFilter.add_schema(
    {
        "$id": "urn:factorio:signal-filter",
        "type": "object",
        "properties": {
            "index": {"$ref": "urn:int64"},
            "name": {"type": "string"},
            "count": {"$ref": "urn:int32"},
        },
    },
    version=(1, 0),
)

draftsman_converters.get_version((1, 0)).add_hook_fns(
    SignalFilter,
    lambda fields: {
        "index": fields.index.name,
        "name": fields.name.name,
        "count": fields.count.name,
        None: fields.type.name,
        None: fields.quality.name,
        None: fields.comparator.name,
        None: fields.max_count.name,
    },
)

SignalFilter.add_schema(
    {
        "$id": "urn:factorio:signal-filter",
        "type": "object",
        "properties": {
            "index": {"$ref": "urn:int64"},
            "name": {"type": "string"},
            "type": {
                "enum": [
                    "item",
                    "fluid",
                    "virtual",
                    "recipe",
                    "entity",
                    "space-location",
                    "asteroid-chunk",
                    "quality",
                ]
            },
            "count": {"$ref": "urn:int32"},
            "quality": {"$ref": "urn:factorio:quality-name"},
            "comparator": {"$ref": "urn:factorio:comparator"},
            "max_count": {"$ref": "urn:int32"},
        },
    },
    version=(2, 0),
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


# class SignalFilter(DraftsmanBaseModel):
#     index: int64 = Field(
#         ...,
#         description="""
#         Numeric index of the signal in the combinator, 1-based. Typically the
#         index of the signal in the parent 'filters' key, but this is not
#         strictly enforced. Will result in an import error if this value exceeds
#         the maximum number of slots that this constant combinator can contain.
#         """,
#     )
#     name: str = Field(
#         ...,
#         description="""
#         Name of the signal.
#         """,
#     )
#     type: Optional[
#         Literal[
#             "virtual",
#             "item",
#             "fluid",
#             "recipe",
#             "entity",
#             "space-location",
#             "asteroid-chunk",
#             "quality",
#         ]
#     ] = Field("item", description="Type of the signal.")
#     # signal: Optional[SignalID] = Field(
#     #     None,
#     #     description="""
#     #     Signal to broadcast. If this value is omitted the occupied slot will
#     #     behave as if no signal exists within it. Cannot be a pure virtual
#     #     (logic) signal like "signal-each", "signal-any", or
#     #     "signal-everything"; if such signals are set they will be removed
#     #     on import.
#     #     """,
#     # )
#     # TODO: make this dynamic based on current environment?
#     quality: Optional[
#         Literal[
#             "normal", "uncommon", "rare", "epic", "legendary", "quality-unknown", "any"
#         ]
#     ] = Field(
#         "any",
#         description="""
#         Quality flag of the signal. If unspecified, this value is effectively
#         equal to 'any' quality level.
#         """,
#     )
#     # TODO: comparator should have a user default, but should always be exported
#     comparator: Literal[">", "<", "=", "≥", "≤", "≠"] = Field(
#         ...,
#         description="Comparison operator when deducing the quality type.",
#     )
#     count: int32 = Field(
#         ...,
#         description="""
#         Value of the signal to emit.
#         """,
#     )
#     max_count: Optional[int32] = Field(
#         None,
#         description="""
#         The maximum value of the signal to emit. Only used with logistics-type
#         requests.
#         """,
#     )

#     # Deprecated in 2.0
#     # @field_validator("index")
#     # @classmethod
#     # def ensure_index_within_range(cls, value: int64, info: ValidationInfo):
#     #     """
#     #     Factorio does not permit signal values outside the range of it's item
#     #     slot count; this method raises an error IF item slot count is known.
#     #     """
#     #     if not info.context:
#     #         return value
#     #     if info.context["mode"] <= ValidationMode.MINIMUM:
#     #         return value

#     #     entity = info.context["object"]

#     #     # If Draftsman doesn't recognize entity, early exit
#     #     if entity.item_slot_count is None:
#     #         return value

#     #     # TODO: what happens if index is 0?
#     #     if not 0 < value <= entity.item_slot_count:
#     #         raise ValueError(
#     #             "Signal 'index' ({}) must be in the range [0, {})".format(
#     #                 value, entity.item_slot_count
#     #             )
#     #         )

#     #     return value

#     @field_validator("name")
#     @classmethod
#     def ensure_not_pure_virtual(cls, value: Optional[str], info: ValidationInfo):
#         """
#         Warn if pure virtual signals (like "signal-each", "signal-any", and
#         "signal-everything") are entered inside of a constant combinator.
#         """
#         if not info.context or value is None:
#             return value
#         if info.context["mode"] <= ValidationMode.MINIMUM:
#             return value

#         warning_list: list = info.context["warning_list"]

#         if value in pure_virtual:
#             warning_list.append(
#                 PureVirtualDisallowedWarning(
#                     "Cannot set pure virtual signal '{}' in a constant combinator".format(
#                         value.name
#                     )
#                 )
#             )

#         return value


@attrs.define
class ManualSection(Exportable):
    """
    A "manually" (player) defined collection of signals, typically used for
    logistics sections as well as constant combinators signal groups.
    """

    def _index_in_range(self, attr, value, mode: Optional[ValidationMode] = None):
        mode = mode if mode is not None else self.validate_assignment

        if mode >= ValidationMode.MINIMUM:
            if not (1 <= value <= 100):
                msg = "Index ({}) must be in range [1, 100]".format(value)
                raise IndexError(msg)

    index: LuaDouble = attrs.field(
        validator=and_(instance_of(LuaDouble), _index_in_range)
    )
    """
    Location of the logistics section within the entity, 1-indexed. Hard capped
    to 100 manual sections per entity.
    """

    def _filters_converter(value: list[Any]) -> list[SignalFilter]:
        # TODO: more robust testing
        if isinstance(value, list):
            for i, entry in enumerate(value):
                if isinstance(entry, tuple):
                    value[i] = SignalFilter(
                        index=i + 1,
                        name=entry[0],
                        count=entry[1],
                    )
                else:
                    value[i] = SignalFilter.converter(entry)
            return value
        else:
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
        name: Optional[SignalName],
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
        TODO
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

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        else:
            return value


ManualSection.add_schema(
    {
        "$id": "urn:factorio:manual-section",
        "type": "object",
        "properties": {
            "index": {
                "$ref": "urn:lua-double",
                "min": 1,
                "max": 100,
            },
            "filters": {
                "type": "array",
                "items": {"$ref": "urn:factorio:signal-filter"},
                "maxItems": 1000,
            },
            "group": {"type": "string"},
            "active": {"type": "boolean"},
        },
        "required": ["index"],
    }
)

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
    quality: QualityName = attrs.field(default="any", validator=one_of(QualityName))
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


QualityFilter.add_schema(
    {
        "$id": "urn:factorio:quality-filter",
        "type": "object",
        "properties": {
            "quality": {"$ref": "urn:factorio:quality-name"},
            "comparator": {"$ref": "urn:factorio:comparator"},
        },
    }
)

draftsman_converters.add_hook_fns(
    QualityFilter,
    lambda fields: {
        "quality": fields.quality.name,
        "comparator": fields.comparator.name,
    },
)


@attrs.define
class AttrsInventoryLocation(Exportable):
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

    @classmethod
    def convert(cls, value):
        if isinstance(value, dict):
            return AttrsInventoryLocation(**value)
        else:
            return value


AttrsInventoryLocation.add_schema(
    {
        "$id": "urn:factorio:inventory-location",
        "type": "object",
        "properties": {
            "inventory": {"$ref": "urn:uint32"},
            "stack": {"$ref": "urn:uint32"},
            "count": {"$ref": "urn:uint32"},
        },
    }
)

draftsman_converters.add_hook_fns(
    AttrsInventoryLocation,
    lambda fields: {
        "inventory": fields.inventory.name,
        "stack": fields.stack.name,
        "count": fields.count.name,
    },
)


@attrs.define
class AttrsItemSpecification(Exportable):
    def _convert_inventory_location_list(value):
        if isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                res[i] = AttrsInventoryLocation.convert(elem)
            return res
        else:
            return value

    in_inventory: list[AttrsInventoryLocation] = attrs.field(
        factory=list,
        converter=_convert_inventory_location_list,
        validator=instance_of(list[AttrsInventoryLocation]),
    )
    """
    The list of all locations that the selected item should go.
    """
    grid_count: uint32 = attrs.field(default=0, validator=instance_of(uint32))
    """
    The total amount of this item being requested to the attached equipment grid,
    if applicable. Always zero if the entity has no equipment grid to request to.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return AttrsItemSpecification(**value)
        else:
            return value


AttrsItemSpecification.add_schema(
    {
        "$id": "urn:factorio:item-specification",
        "type": "object",
        "properties": {
            "in_inventory": {
                "type": "array",
                "items": {"$ref": "urn:factorio:inventory-location"},
            },
            "grid_count": {
                "$ref": "urn:uint32",
            },
        },
    }
)

draftsman_converters.add_hook_fns(
    AttrsItemSpecification,
    lambda fields: {
        fields.in_inventory.name: "in_inventory",
        fields.grid_count.name: "grid_count",
    },
)


@attrs.define
class AttrsItemID(Exportable):
    name: ItemName = attrs.field(validator=instance_of(ItemName))
    quality: QualityName = attrs.field(default="normal", validator=one_of(QualityName))

    @classmethod
    def converter(cls, value):
        if isinstance(value, str):
            return cls(name=value)
        elif isinstance(value, dict):
            return cls(**value)
        return value


AttrsItemID.add_schema(
    {
        "$id": "urn:factorio:item-id",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "quality": {"$ref": "urn:factorio:quality-name"},
        },
    }
)

draftsman_converters.add_hook_fns(
    AttrsItemID,
    lambda fields: {"name": fields.name.name, "quality": fields.quality.name},
)


@attrs.define
class AttrsItemRequest(Exportable):
    id: AttrsItemID = attrs.field(
        converter=AttrsItemID.converter, validator=instance_of(AttrsItemID)
    )
    """
    The item to request.
    """
    items: AttrsItemSpecification = attrs.field(
        factory=AttrsItemSpecification,
        converter=AttrsItemSpecification.converter,
        validator=instance_of(AttrsItemSpecification),
    )
    """
    The grids/locations each item is being requested to.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return AttrsItemRequest(**value)
        else:
            return value


AttrsItemRequest.add_schema(
    {
        "$id": "urn:factorio:item-request",
        "type": "object",
        "properties": {
            "id": {"$ref": "urn:factorio:item-id"},
            "items": {"$ref": "urn:factorio:item-specification"},
        },
    }
)


draftsman_converters.add_hook_fns(
    AttrsItemRequest,
    lambda fields: {
        fields.id.name: "id",
        fields.items.name: "items",
    },
)


@attrs.define
class AttrsInfinityFilter(Exportable):
    index: uint16 = attrs.field(validator=instance_of(uint16))
    """
    Where in the infinity containers GUI this filter will exist,
    1-based.
    """
    name: ItemName = attrs.field(validator=instance_of(ItemName))  # TODO: ItemID
    """
    The name of the item to create/remove.
    """
    count: uint32 = attrs.field(default=0, validator=instance_of(uint32))
    """
    The amount of this item to keep in the entity, as dicerned
    by 'mode'.
    """
    mode: Literal["at-least", "at-most", "exactly"] = attrs.field(
        default="at-least", validator=one_of("at-least", "at-most", "exactly")
    )
    """
    What manner in which to create or remove this item from the 
    entity. 'at-least' sets 'count' as a lower-bound, 'at-most' 
    sets 'count' as an upper-bound, and exactly makes the 
    quantity of this item match 'count' exactly.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        else:
            return value


AttrsInfinityFilter.add_schema(
    {
        "$id": "urn:factorio:infinity-filter",
        "type": "object",
        "properties": {
            "index": {"$ref": "urn:uint16"},
            "name": {"type": "string"},
            "count": {"$ref": "urn:uint32", "default": 0},
            "mode": {
                "enum": ["at-least", "at-most", "exactly"],
                "default": "at-least",
            },
        },
        "required": ["index", "name"],
    }
)


draftsman_converters.add_hook_fns(
    AttrsInfinityFilter,
    lambda fields: {
        fields.index.name: "index",
        fields.name.name: "name",
        fields.count.name: "count",
        fields.mode.name: "mode",
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
    quality: QualityName = attrs.field(
        default="normal", validator=one_of(QualityName)
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


EquipmentID.add_schema(
    {
        "$id": "urn:factorio:equipment-id",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "quality": {"$ref": "urn:factorio:quality-name"},
        },
    }
)

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

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        return value


EquipmentComponent.add_schema(
    {
        "$id": "urn:factorio:equipment-component",
        "type": "object",
        "properties": {
            "equipment": {"$ref": "urn:factorio:equipment-id"},
            "position": {"$ref": "urn:factorio:position"},
        },
        "required": ["equipment", "position"],
    }
)


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


StockConnection.add_schema(
    {
        "$id": "urn:factorio:blueprint:stock-connection",
        "type": "object",
        "properties": {
            "stock": {"$ref": "urn:uint64"},
            "front": {"$ref": "urn:uint64"},
            "back": {"$ref": "urn:uint64"},
        },
        "required": ["stock"],
    }
)


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
class FilteredInventory(Exportable):
    @property
    def inventory_size(self) -> Optional[uint16]:
        """
        The number of inventory slots that this Entity has. Equivalent to the
        ``"inventory_size"`` key in Factorio's ``data.raw``. Returns ``None`` if
        this entity's name is not recognized by Draftsman. Not exported; read
        only.
        """
        return entities.raw.get(self.name, {"inventory_size": None})["inventory_size"]

    # =========================================================================

    def _inventory_filters_converter(value):
        if isinstance(value, list):
            for i, elem in enumerate(value):
                if isinstance(elem, str):
                    value[i] = AttrsItemFilter(index=i, name=elem)
                else:
                    value[i] = AttrsItemFilter.converter(elem)
        return value

    inventory_filters: list[AttrsItemFilter] = attrs.field(
        factory=list,
        converter=_inventory_filters_converter,
        validator=instance_of(list[AttrsItemFilter]),
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

    def set_inventory_filter(
        self,
        index: int64,
        item: Optional[ItemName],
        quality: QualityName = "normal",
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
            new_entry = AttrsItemFilter(
                index=index, name=item, quality=quality, comparator=comparator
            )

        # new_filters = (
        #     self.inventory.filters if self.inventory.filters is not None else []
        # )

        # Check to see if filters already contains an entry with the same index
        found_index = None
        for i, filter in enumerate(self.inventory_filters):
            if filter.index == index + 1:  # Index already exists in the list
                if item is None:
                    # Delete the entry
                    del self.inventory_filters[i]
                else:
                    # Modify the existing value inplace
                    self.inventory_filters[i].name = item
                    self.inventory_filters[i].quality = quality
                    self.inventory_filters[i].comparator = comparator
                found_index = i
                break

        if found_index is None:
            # If no entry with the same index was found
            self.inventory_filters.append(new_entry)

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return cls(**value)
        return value


FilteredInventory.add_schema(
    {
        "$id": "urn:factorio:filtered-inventory",
        "properties": {
            "filters": {"type": "array", "items": {"$ref": "urn:factorio:item-filter"}},
            "bar": {"$ref": "urn:uint16"},
        },
    }
)


draftsman_converters.add_hook_fns(
    FilteredInventory,
    lambda fields: {
        "filters": fields.inventory_filters.name,
        "bar": fields.bar.name,
    },
)
