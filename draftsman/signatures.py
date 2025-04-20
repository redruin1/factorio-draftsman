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
from draftsman.data.signals import (
    signal_dict,
    mapper_dict,
    get_signal_types,
    pure_virtual,
)
from draftsman.data import entities, fluids, items, signals, tiles, recipes
from draftsman.error import (
    InvalidMapperError,
    InvalidSignalError,
    IncompleteSignalError,
    DataFormatError,
)
from draftsman.serialization import draftsman_converters
from draftsman.utils import encode_version, get_suggestion
from draftsman.validators import and_, lt, ge, one_of, is_none, or_, instance_of
from draftsman.warning import (
    BarWarning,
    MalformedSignalWarning,
    PureVirtualDisallowedWarning,
    UnknownEntityWarning,
    UnknownFluidWarning,
    UnknownKeywordWarning,
    UnknownItemWarning,
    UnknownSignalWarning,
    UnknownTileWarning,
    UnknownRecipeWarning
)

from typing_extensions import Annotated

import attrs
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetJsonSchemaHandler,
    RootModel,
    ValidationInfo,
    ValidationError,
    ValidatorFunctionWrapHandler,
    field_validator,
    model_validator,
)
from pydantic.functional_validators import AfterValidator
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from textwrap import dedent
from thefuzz import process
from typing import Any, Literal, Optional, Sequence, Union
import warnings


# TODO: might make sense to move this into another file, so other files can use
# them without recursive imports
int32 = Annotated[int, and_(ge(-(2**31)), lt(2**31))]
# TODO: description about floating point issues
int64 = Annotated[int, and_(ge(-(2**63)), lt(2**63))]  

uint8 = Annotated[int, and_(ge(0), lt(2**8))]
uint16 = Annotated[int, and_(ge(0), lt(2**16))]
uint32 = Annotated[int, and_(ge(0), lt(2**32))]
# TODO: description about floating point issues
uint64 = Annotated[int, and_(ge(0), lt(2**64))]


def known_name(type: str, structure: dict, issued_warning: Warning):
    """
    Validator function builder for any type of unknown name.
    """

    def validator(inst: Exportable, attr: attrs.Attribute, value: str, mode: Optional[ValidationMode] = None) -> str:
        mode = mode if mode is not None else inst.validate_assignment

        if mode >= ValidationMode.STRICT:
            if value not in structure:
                msg = "Unknown {} '{}'{}".format(
                    type, value, get_suggestion(value, structure.keys(), n=1)
                )
                warnings.warn(issued_warning(msg))

    return validator


ItemName = Annotated[
    str, known_name("item", items.raw, UnknownItemWarning)
]
SignalName = Annotated[
    str, known_name("signal", signals.raw, UnknownSignalWarning)
]
EntityName = Annotated[
    str, known_name("entity", entities.raw, UnknownEntityWarning)
]
FluidName = Annotated[
    str, known_name("fluid", fluids.raw, UnknownFluidWarning)
]
TileName = Annotated[
    str, known_name("tile", tiles.raw, UnknownTileWarning)
]
RecipeName = Annotated[
    str, known_name("recipe", recipes.raw, UnknownRecipeWarning)
]
QualityName = Literal["normal", "uncommon", "rare", "epic", "legendary", "quality-unknown", "any"]


class DraftsmanBaseModel(BaseModel):
    """
    A custom wrapper around Pydantic's ``BaseModel``.

    Includes things like arbitrary construction, warning of unused attributes,
    and adds getters and setters so that it blends in more seamlessly with
    unvalidated dicts.
    """

    @classmethod
    # @lru_cache(maxsize=None)  # maybe excessive...
    # def get_model_aliases(cls) -> list[str]:
    #     """
    #     Similar to ``cls.model_fields``, but converts everything to their
    #     aliases if present.
    #     """
    #     return [
    #         v.alias if v.alias is not None else k for k, v in cls.model_fields.items()
    #     ]
    def true_model_fields(cls):
        return {
            (v.alias if v.alias is not None else k): k
            for k, v in cls.model_fields.items()
        }

    @field_validator("*", mode="wrap")
    def construct_fields(
        cls, value: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ):
        if info.context and "construction" in info.context:
            try:
                return handler(value)
            except ValidationError:
                return value
            # TODO: swap the above with just returning the value
            # Currently we're doing the validation twice, first a minimum pass to coerce
            # everything we can to their respective BaseModels, and the second time to
            # actually validate all the data and run the custom validation functions
            # Ideally, this could all happen in one step if we copy the code from
            # validate/add the "construction" keyword to the context of validate
        else:
            return handler(value)

    @model_validator(mode="after")
    def warn_unused_arguments(self, info: ValidationInfo):
        """
        Populates the warning list when an input BaseModel is given a field it
        does not recognize. Because Factorio (seems to) permit extra keys, doing
        so will issue warnings instead of exceptions.
        """
        if not info.context:
            return self
        if info.context["mode"] <= ValidationMode.MINIMUM:
            return self

        obj = info.context["object"]

        # If we're creating a generic `Entity` (in the case where Draftsman
        # cannot really know what entity is being imported) then we don't want
        # to issue the following warnings, since we don't want to make
        # assertions where we don't have enough information
        if obj.unknown:
            return self

        # We also only want to issue this particular warning if we're setting an
        # assignment of a subfield, or if we're doing a full scale `validate()`
        # function call
        if type(obj).Format is type(self) and info.context["assignment"]:
            return self

        if self.model_extra:
            warning_list: list = info.context["warning_list"]

            warning_list.append(
                UnknownKeywordWarning(
                    "'{}' object has no attribute(s) {}; allowed fields are {}".format(
                        self.model_config.get("title", type(self).__name__),
                        list(self.model_extra.keys()),
                        list(self.true_model_fields().keys()),
                    )
                )
            )

        return self

    # Permit accessing via indexing
    def __getitem__(self, key):
        return getattr(self, self.true_model_fields().get(key, key))

    def __setitem__(self, key, value):
        setattr(self, self.true_model_fields().get(key, key), value)

    def __contains__(self, key: str) -> bool:
        return self.true_model_fields().get(key, key) in self.__dict__

    # Add a number of dict-like functions:
    def get(self, key, default):
        return self.__dict__.get(self.true_model_fields().get(key, key), default)

    # Strip indentation and newlines from description strings when generating
    # JSON schemas
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)

        def normalize_description(input_obj: str) -> str:
            if "description" in input_obj:
                input_obj["description"] = dedent(input_obj["description"]).strip()

        normalize_description(json_schema)
        if "properties" in json_schema:  # Maybe not needed?
            for property_spec in json_schema["properties"].values():
                normalize_description(property_spec)
        # if "items" in json_schema: # Maybe not needed?
        #     normalize_description(json_schema["items"])

        return json_schema

    # Factorio seems to be permissive when it comes to extra keys, so we allow
    # them and issue warnings if desired
    model_config = ConfigDict(
        extra="allow",
        revalidate_instances="always",
        populate_by_name=True,  # Allow to pass either internal or alias to constructor
    )


class MapperID(DraftsmanBaseModel):
    name: str  # TODO: optional?
    type: Literal["entity", "item"] = Field(
        ...,
        description="""
        The type of mapping taking place; can be one of 'entity' for entity
        replacement or 'item' for item (typically module) replacement.
        """,
    )  # TODO: optional?

    @model_validator(mode="before")
    @classmethod
    def init_from_string(cls, value: Any):
        """
        Attempt to convert an input string name into a dict representation.
        Raises a ValueError if unable to determine the type of a signal's name,
        likely if the signal is misspelled or used in a modded configuration
        that differs from Draftsman's current one.
        """
        if isinstance(value, str):
            try:
                return mapper_dict(value)
            except InvalidMapperError as e:
                raise ValueError(
                    "Unknown mapping target {}; either specify the full dictionary, or update your environment".format(
                        e
                    )
                ) from None
        else:
            return value


class Mapper(DraftsmanBaseModel):
    # _alias_map: ClassVar[dict] = PrivateAttr(
    #     {"from": "from_", "to": "to", "index": "index"}
    # )

    from_: Optional[MapperID] = Field(
        None,
        alias="from",
        description="""
        Entity/Item to replace with 'to'. Remains blank in the GUI if omitted.
        """,
    )
    to: Optional[MapperID] = Field(
        None,
        description="""
        Entity/item to replace 'from'. Remains blank in the GUI if omitted.
        """,
    )
    index: uint64 = Field(
        ...,
        description="""
        Numeric index of the mapping in the UpgradePlanner's GUI, 0-based. 
        Value defaults to the index of this mapping in the parent 'mappers' list,
        but this behavior is not strictly enforced.
        """,
    )

    # Add the dict-like `get` function
    # def get(self, key, default):
    #     return super().get(self._alias_map[key], default)

    # def __getitem__(self, key):
    #     return super().__getitem__(self._alias_map[key])

    # def __setitem__(self, key, value):
    #     super().__setitem__(self._alias_map[key], value)


# class Mappers(DraftsmanRootModel):
#     root: list[Mapper]

#     # @model_validator(mode="before")
#     # @classmethod
#     # def normalize_mappers(cls, value: Any):
#     #     if isinstance(value, Sequence):
#     #         for i, mapper in enumerate(value):
#     #             if isinstance(value, (tuple, list)):
#     #                 value[i] = {"index": i}
#     #                 if mapper[0]:
#     #                     value[i]["from"] = mapper_dict(mapper[0])
#     #                 if mapper[1]:
#     #                     value[i]["to"] = mapper_dict(mapper[1])

#     # @validator("__root__", pre=True)
#     # def normalize_mappers(cls, mappers):
#     #     if mappers is None:
#     #         return mappers
#     #     for i, mapper in enumerate(mappers):
#     #         if isinstance(mapper, (tuple, list)):
#     #             mappers[i] = {"index": i}
#     #             if mapper[0]:
#     #                 mappers[i]["from"] = mapping_dict(mapper[0])
#     #             if mapper[1]:
#     #                 mappers[i]["to"] = mapping_dict(mapper[1])
#     #     return mappers


class SignalID(DraftsmanBaseModel):
    name: Optional[SignalName] = Field(
        ...,
        description="""
        Name of the signal. If omitted, the signal is treated as no signal and 
        removed on import/export cycle.
        """,
    )
    type: Literal[
        "virtual",
        "item",
        "fluid",
        "recipe",
        "entity",
        "space-location",
        "asteroid-chunk",
        "quality",
    ] = Field("item", description="""Category of the signal.""")
    quality: Optional[
        Literal[
            "normal", "uncommon", "rare", "epic", "legendary", "quality-unknown", "any"
        ]
    ] = Field(
        "normal",
        description="""
        Quality flag of the signal.
        """,
    )

    @model_validator(mode="before")
    @classmethod
    def init_from_string(cls, input):
        """
        Attempt to convert an input string name into a dict representation.
        Raises a ValueError if unable to determine the type of a signal's name,
        likely if the signal is misspelled or used in a modded configuration
        that differs from Draftsman's current one.
        """
        if isinstance(input, str):
            try:
                return signal_dict(input)
            except InvalidSignalError as e:
                raise ValueError(
                    "Unknown signal name {}; either specify the full dictionary, or update your environment".format(
                        e
                    )
                ) from None
        else:
            return input

    # TODO: add routine to create SignalID from tuple like ("epic", "signal-A")?

    # @field_validator("name")
    # @classmethod
    # def check_name_recognized(cls, value: str, info: ValidationInfo):
    #     """
    #     We might be provided with a signal which has all the information
    #     necessary to pass validation, but will be otherwise unrecognized by
    #     Draftsman (in it's current configuration at least). Issue a warning
    #     for every unknown signal.
    #     """
    #     # TODO: check a table to make sure we don't warn about the same unknown
    #     # signal multiple times
    #     if not info.context:
    #         return value
    #     if info.context["mode"] is ValidationMode.MINIMUM:
    #         return value

    #     warning_list: list = info.context["warning_list"]

    #     if value not in signals.raw:
    #         issue = UnknownSignalWarning(
    #             "Unknown signal '{}'{}".format(
    #                 value, get_suggestion(value, signals.raw.keys(), n=1)
    #             )
    #         )

    #         if info.context["mode"] is ValidationMode.PEDANTIC:
    #             raise ValueError(issue) from None
    #         else:
    #             warning_list.append(issue)

    #     return value

    @model_validator(mode="after")
    @classmethod
    def check_type_matches_name(cls, value: "SignalID", info: ValidationInfo):
        """
        Idiot-check to make sure that the ``type`` of a known signal actually
        corresponds to it's ``name``; prevents silly mistakes like::

            {"name": "signal-A", "type": "fluid"}
        """
        if not info.context:
            return value
        if info.context["mode"] <= ValidationMode.MINIMUM:
            return value

        warning_list: list = info.context["warning_list"]

        if value["name"] in signals.raw:
            expected_types = get_signal_types(value["name"])
            if value["type"] not in expected_types:
                warning_list.append(
                    MalformedSignalWarning(
                        "Known signal '{}' was given a mismatching type (expected one of {}, found '{}')".format(
                            value["name"], expected_types, value["type"]
                        )
                    )
                )

        return value

    # @model_serializer
    # def serialize_signal_id(self):
    #     """
    #     Try exporting the object as a dict if it was set as a string. Useful if
    #     someone sets a signal to it's name without running validation at any
    #     point, this method will convert it to it's correct output (provided it
    #     can determine it's type).
    #     """
    #     if isinstance(self, str):
    #         try:
    #             return signal_dict(self)
    #         except InvalidSignalError as e:
    #             raise ValueError(
    #                 "Unknown signal name {}; either specify the full dictionary, or update your environment to include it"
    #                 .format(e)
    #             ) from None
    #     else:
    #         return {"name": self["name"], "type": self["type"]}


@attrs.define
class AttrsSignalID(Exportable):
    name: Optional[SignalName] = attrs.field(
        default=None
        # TODO: validators
    )
    """
    Name of the signal. If omitted, the signal is treated as no signal and 
    removed on import/export cycle.
    """
    type: Literal[
        "virtual",
        "item",
        "fluid",
        "recipe",
        "entity",
        "space-location",
        "asteroid-chunk",
        "quality",
    ] = attrs.field(
        default="item"
    )  # TODO: validators, name-specific default
    """
    Category of the signal.
    """
    quality: Optional[QualityName] = attrs.field(
        default="normal",
        validator=or_(one_of(QualityName), is_none)
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
                if "item" in get_signal_types(value):
                    return AttrsSignalID(name=value, type="item")
                else:
                    return AttrsSignalID(
                        name=value, type=next(iter(get_signal_types(value)))
                    )
            except InvalidSignalError as e:
                msg = "Unknown signal name {}; either specify the full dictionary, or update your environment".format(
                    repr(value)
                )
                raise IncompleteSignalError(msg) from None
        elif isinstance(value, dict):
            return AttrsSignalID(**value)
        else:
            return value

    @name.validator
    def check_name_recognized(
        self, attribute, value, mode: Optional[ValidationMode] = None
    ):
        mode = mode if mode is not None else self.validate_assignment
        if mode >= ValidationMode.STRICT:
            if value not in signals.raw:
                msg = "Unknown {} '{}'{}".format(
                    type(self).__name__,
                    value,
                    get_suggestion(value, signals.raw.keys(), n=1),
                )
                warnings.warn(UnknownSignalWarning(msg))

    @type.validator
    def check_type_matches_name(
        self, attribute, value, mode: Optional[ValidationMode] = None
    ):
        mode = mode if mode is not None else self.validate_assignment
        if mode >= ValidationMode.STRICT:
            if self.name in signals.raw:
                expected_types = get_signal_types(self.name)
                if value not in expected_types:
                    msg = "Known signal '{}' was given a mismatching type (expected one of {}, found '{}')".format(
                        self.name, expected_types, value
                    )
                    warnings.warn(MalformedSignalWarning(msg))


draftsman_converters.get_version((1, 0)).add_schema(
    {
        "$id": "factorio:signal_id_v1.0"
        # TODO
    },
    AttrsSignalID,
    lambda fields: {
        fields.name.name: "name",
        fields.type.name: "type",
        fields.quality.name: None,
    },
)

draftsman_converters.get_version((2, 0)).add_schema(
    {
        "$id": "factorio:signal_id_v2.0"
        # TODO
    },
    AttrsSignalID,
    lambda fields: {
        fields.name.name: "name",
        fields.type.name: "type",
        fields.quality.name: "quality",
    },
)


class TargetID(DraftsmanBaseModel):
    index: uint32 = Field(..., description="TODO")  # TODO: size
    name: str = Field(..., description="TODO")  # TODO: TargetName?


class AsteroidChunkID(DraftsmanBaseModel):
    index: uint32 = Field(..., description="TODO")  # TODO: size
    name: str = Field(..., description="TODO")  # TODO: ChunkName?


class Icon(DraftsmanBaseModel):
    signal: SignalID = Field(..., description="""Which signal's icon to display.""")
    index: uint8 = Field(
        ..., description="""Numerical index of the icon, 1-based."""
    )  # TODO: is it numerical order which determines appearance, or order in parent list?

    @classmethod
    def resolve_shorthand(cls, value):
        try:
            result = []
            for i, signal in enumerate(value):
                if isinstance(signal, str):
                    result.append({"index": i + 1, "signal": signal})
                else:
                    result.append(signal)
            return result
        except Exception:
            return value

        # if isinstance(value, Sequence):
        #     result = [None] * len(value)
        #     for i, signal in enumerate(value):
        #         if isinstance(signal, str):
        #             result[i] = signal_dict(signal)
        #         else:
        #             result[i] = signal
        #     return result
        # else:
        #     return value


@attrs.define
class AttrsIcon:
    signal: AttrsSignalID = attrs.field()  # TODO: validators
    """
    Which signal icon to display.
    """
    index: uint8 = attrs.field()
    """
    Numeric index of the icon, 1-based.
    """


def normalize_icons(value: Any):
    if isinstance(value, str):
        return value
    elif isinstance(value, Sequence):
        result = []
        for i, signal in enumerate(value):
            if isinstance(signal, str):
                result.append({"index": i + 1, "signal": signal_dict(signal)})
            elif isinstance(signal, dict) and "type" in signal:
                result.append({"index": i + 1, "signal": signal})
            else:
                result.append(signal)
        return result
    else:
        return value


def normalize_version(value: Any):
    try:
        return encode_version(*value)
    except Exception:
        return value


def normalize_color(value: Any):
    try:
        color_dict = {}
        color_dict["r"] = value[0]
        color_dict["g"] = value[1]
        color_dict["b"] = value[2]
        try:
            color_dict["a"] = value[3]
        except IndexError:
            pass
        return color_dict
    except Exception:
        return value


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
class AttrsColor:
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
    def from_sequence(cls, sequence: Sequence) -> "AttrsColor":
        return cls(*sequence)

    @classmethod
    def converter(cls, value) -> "AttrsColor":
        if isinstance(value, AttrsColor):
            return value
        elif isinstance(value, (tuple, list)):  # TODO: sequence
            return cls.from_sequence(value)
        elif isinstance(value, dict):
            return cls(**value)
        else:
            msg = "{} can not be interpreted as a {}".format(repr(value), cls.__name__)
            raise DataFormatError("Explode")


class Color(DraftsmanBaseModel):
    r: float = Field(..., ge=0, le=255)
    g: float = Field(..., ge=0, le=255)
    b: float = Field(..., ge=0, le=255)
    a: Optional[float] = Field(None, ge=0, le=255)

    @model_validator(mode="before")
    @classmethod
    def normalize_from_sequence(cls, value: Any):
        if isinstance(value, (list, tuple)):
            new_color = {}
            new_color["r"] = value[0]
            new_color["g"] = value[1]
            new_color["b"] = value[2]
            try:
                new_color["a"] = value[3]
            except IndexError:
                pass
            return new_color
        else:
            return value

    # @model_serializer
    # def normalize(self):  # FIXME: scuffed
    #     if isinstance(self, (list, tuple)):
    #         new_color = {}
    #         new_color["r"] = self[0]
    #         new_color["g"] = self[1]
    #         new_color["b"] = self[2]
    #         try:
    #             new_color["a"] = self[3]
    #         except IndexError:
    #             pass
    #         return new_color
    #     elif isinstance(self, dict):
    #         return {k: v for k, v in self.items() if v is not None}
    #     else:
    #         return {k: v for k, v in self.__dict__.items() if v is not None}


class FloatPosition(DraftsmanBaseModel):
    x: float
    y: float

    @model_validator(mode="before")
    @classmethod
    def model_validator(cls, data):
        # likely a Vector or Primitive vector
        try:
            data = Vector.from_other(data, float)
            return data.to_dict()
        except TypeError:
            return data


class IntPosition(DraftsmanBaseModel):
    x: int
    y: int

    @model_validator(mode="before")
    @classmethod
    def model_validator(cls, data):
        # likely a Vector or Primitive vector
        try:
            data = Vector.from_other(data, int)
            return data.to_dict()
        except TypeError:
            return data


# factorio_comparator_choices = {">", "<", "=", "≥", "≤", "≠"}
# python_comparator_choices = {"==", "<=", ">=", "!="}
# class Comparator(DraftsmanRootModel):
#     root: Literal[">", "<", "=", "≥", "≤", "≠"]

#     @model_validator(mode="before")
#     @classmethod
#     def normalize(cls, input: str):
#         conversions = {"==": "=", ">=": "≥", "<=": "≤", "!=": "≠"}
#         if input in conversions:
#             return conversions[input]
#         else:
#             return input

# @model_serializer
# def normalize(self):
#     conversions = {
#         "==": "=",
#         ">=": "≥",
#         "<=": "≤",
#         "!=": "≠"
#     }
#     if self.root in conversions:
#         return conversions[self.root]
#     else:
#         return self.root


class NetworkSpecification(DraftsmanBaseModel):
    red: Optional[bool] = Field(
        True, description="Whether or not inputs from the red wire are permitted."
    )

    green: Optional[bool] = Field(
        True, description="Whether or not inputs from the green wire are permitted."
    )

    @model_validator(mode="before")
    @classmethod
    def convert_from_set(cls, value: Any):
        if isinstance(value, set):
            return {elem: False for elem in ("red", "green") if elem not in value}
        else:
            return value


def normalize_comparator(value):
    conversions = {"==": "=", ">=": "≥", "<=": "≤", "!=": "≠"}
    if value in conversions:
        return conversions[value]
    else:
        return value


Comparator = Literal[">", "<", "=", "==", "≥", ">=", "≤", "<=", "≠", "!="]
draftsman_converters.register_unstructure_hook(
    Comparator, lambda inst: normalize_comparator(inst)
)


@attrs.define
class AttrsSimpleCondition:
    first_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        # TODO: validators
    )
    comparator: Comparator = attrs.field(
        default="<",
        # converter=normalize_comparator
        # TODO: validators
    )
    constant: int32 = attrs.field(default=0)
    second_signal: Optional[AttrsSignalID] = attrs.field(default=None)

    @classmethod
    def converter(cls, value):
        if isinstance(value, cls):
            return value
        elif isinstance(value, dict):
            return cls(**value)
        else:
            return value


class Condition(
    DraftsmanBaseModel
):  # TODO: split into SimpleCondition (no circuit network selection) and CombinatorCondition (circuit network selection)
    first_signal: Optional[SignalID] = Field(
        None,
        description="""
        The first signal to specify for this condition. A null value results
        in an empty slot.
        """,
    )
    first_signal_networks: Optional[NetworkSpecification] = Field(
        NetworkSpecification(red=True, green=True),
        description="Wire input specification for the first signal, if present.",
    )
    comparator: Optional[Literal[">", "<", "=", "≥", "≤", "≠"]] = Field(
        "<",
        description="""
        The comparison operation to perform, where 'first_signal' is on the left
        and 'second_signal' or 'constant' is on the right.
        """,
    )
    constant: Optional[int32] = Field(
        0,
        description="""
        A constant value to compare against. Can only be set in the
        rightmost condition slot. The rightmost slot will be empty if neither
        'constant' nor 'second_signal' are set.
        """,
    )
    second_signal: Optional[SignalID] = Field(
        None,
        description="""
        The second signal of the condition, if applicable. Takes 
        precedence over 'constant', if both are set at the same time.
        """,
    )
    second_signal_networks: Optional[NetworkSpecification] = Field(
        NetworkSpecification(red=True, green=True),
        description="Wire input specification for the second signal, if present.",
    )

    @model_validator(mode="before")
    @classmethod
    def convert_sequence_to_condition(cls, value: Any):
        if isinstance(value, Sequence):
            result = {
                "first_signal": value[0],
                "comparator": value[1],
            }
            if isinstance(value[2], int):
                result["constant"] = value[2]
            else:
                result["second_signal"] = value[2]
            return result
        else:
            return value

    # @field_validator("first_signal_networks", "second_signal_networks", mode="before")
    # @classmethod
    # def convert_from_set(cls, value: Any):
    #     if isinstance(value, set):
    #         return {elem: True for elem in value}
    #     else:
    #         return value

    @field_validator("comparator", mode="before")
    @classmethod
    def normalize_comparator_python_equivalents(cls, input: Any):
        conversions = {"==": "=", ">=": "≥", "<=": "≤", "!=": "≠"}
        if input in conversions:
            return conversions[input]
        else:
            return input


class EntityFilter(DraftsmanBaseModel):
    name: EntityName = Field(
        ...,
        description="""
        The name of a valid deconstructable entity.
        """,
    )
    index: Optional[uint64] = Field(
        description="""
        Position of the filter in the DeconstructionPlanner, 0-based. Seems to 
        behave more like a sorting key rather than a numeric index; if omitted, 
        entities will be sorted by their Factorio order when imported instead
        of specific slots in the GUI, contrary to what index would seem to imply.
        """
    )


class TileFilter(DraftsmanBaseModel):
    name: TileName = Field(
        ...,
        description="""
        The name of a valid deconstructable tile.
        """,
    )
    index: Optional[uint64] = Field(
        description="""
        Position of the filter in the DeconstructionPlanner, 0-based. Seems to 
        behave more like a sorting key rather than a numeric index; if omitted, 
        entities will be sorted by their Factorio order when imported instead
        of specific slots in the GUI, contrary to what index would seem to imply.
        """
    )


class CircuitConnectionPoint(DraftsmanBaseModel):
    entity_id: Association.Format
    circuit_id: Optional[Literal[1, 2]] = None


class WireConnectionPoint(DraftsmanBaseModel):
    entity_id: Association.Format
    wire_id: Optional[Literal[0, 1]] = None


class Connections(DraftsmanBaseModel):
    # _alias_map: ClassVar[dict] = PrivateAttr(
    #     {
    #         "1": "Wr1",
    #         "2": "Wr2",
    #         "Cu0": "Cu0",
    #         "Cu1": "Cu1",
    #     }
    # )

    def export_key_values(self):
        return {k: getattr(self, v) for k, v in self.true_model_fields().items()}

    class CircuitConnections(DraftsmanBaseModel):
        red: Optional[list[CircuitConnectionPoint]] = None
        green: Optional[list[CircuitConnectionPoint]] = None

    Wr1: Optional[CircuitConnections] = Field(CircuitConnections(), alias="1")
    Wr2: Optional[CircuitConnections] = Field(CircuitConnections(), alias="2")
    Cu0: Optional[list[WireConnectionPoint]] = None
    Cu1: Optional[list[WireConnectionPoint]] = None

    # def __getitem__(self, key):
    #     return super().__getitem__(self._alias_map[key])

    # def __setitem__(self, key, value):
    #     super().__setitem__(self._alias_map[key], value)

    # def __contains__(self, item):
    #     return item in self._alias_map and


# class Filters(DraftsmanRootModel):
class FilterEntry(DraftsmanBaseModel):
    index: int64 = Field(
        ..., description="""Numeric index of a filter entry, 1-based."""
    )
    name: ItemName = Field(..., description="""Name of the item to filter.""")

    @field_validator("index")
    @classmethod
    def ensure_within_filter_count(cls, value: int, info: ValidationInfo):
        """ """
        if not info.context:
            return value
        if info.context["mode"] <= ValidationMode.MINIMUM:
            return value

        entity = info.context["object"]

        if entity.filter_count is not None and value > entity.filter_count:
            raise ValueError(
                "'{}' exceeds the allowable range for filter slot indices [0, {}) for this entity ('{}')".format(
                    value, entity.filter_count, entity.name
                )
            )

        return value

    # root: list[FilterEntry]

    # @model_validator(mode="before")
    # @classmethod
    # def normalize_validate(cls, value: Any):
    #     if isinstance(value, (list, tuple)):
    #         result = []
    #         for i, entry in enumerate(value):
    #             if isinstance(entry, str):
    #                 result.append({"index": i + 1, "name": entry})
    #             else:
    #                 result.append(entry)
    #         return result
    #     else:
    #         return value

    # @model_serializer
    # def normalize_construct(self):
    #     result = []
    #     for i, entry in enumerate(self.root):
    #         if isinstance(entry, str):
    #             result.append({"index": i + 1, "name": entry})
    #         else:
    #             result.append(entry)
    #     return result


class ItemFilter(DraftsmanBaseModel):
    index: int64 = Field(
        ..., description="""Numeric index of a filter entry, 1-based."""
    )
    name: ItemName = Field(..., description="""Name of the item to filter.""")
    quality: Optional[
        Literal[
            "normal", "uncommon", "rare", "epic", "legendary", "quality-unknown", "any"
        ]
    ] = Field(
        "any",
        description="""
        Quality flag of the signal. If unspecified, this value is effectively 
        equal to 'any' quality level.
        """,
    )
    comparator: Optional[Literal[">", "<", "=", "≥", "≤", "≠"]] = Field(
        None, description="Comparison operator when deducing the quality type."
    )


def ensure_bar_less_than_inventory_size(
    cls, value: Optional[uint16], info: ValidationInfo
):
    if not info.context or value is None:
        return value
    if info.context["mode"] <= ValidationMode.STRICT:
        return value

    warning_list: list = info.context["warning_list"]
    entity = info.context["object"]
    if entity.inventory_size and value >= entity.inventory_size:
        warning_list.append(
            BarWarning(
                "Bar index ({}) exceeds the container's inventory size ({})".format(
                    value, entity.inventory_size
                ),
            )
        )

    return value


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


# class RequestFilters(DraftsmanRootModel):
class RequestFilter(DraftsmanBaseModel):
    index: int64 = Field(
        ..., description="""Numeric index of the logistics request, 1-based."""
    )
    name: ItemName = Field(
        ..., description="""The name of the item to request from logistics."""
    )
    count: Optional[int64] = Field(
        1,
        description="""
        The amount of the item to request. Optional on import to Factorio, 
        but always included on export from Factorio. If omitted, will 
        default to a count of 1.
        """,
    )

    # root: list[Request]

    # @model_validator(mode="before")
    # @classmethod
    # def normalize_validate(cls, value: Any):
    #     if value is None:
    #         return value

    #     result = []
    #     if isinstance(value, list):
    #         for i, entry in enumerate(value):
    #             if isinstance(entry, (tuple, list)):
    #                 result.append({"index": i + 1, "name": entry[0], "count": entry[1]})
    #             else:
    #                 result.append(entry)
    #         return result
    #     else:
    #         return value

    # @model_serializer
    # def normalize_construct(self):
    #     result = []
    #     for i, entry in enumerate(self.root):
    #         if isinstance(entry, (tuple, list)):
    #             result.append({"index": i + 1, "name": entry[0], "count": entry[1]})
    #         else:
    #             result.append(entry)
    #     return result


class SignalFilter(DraftsmanBaseModel):
    index: int64 = Field(
        ...,
        description="""
        Numeric index of the signal in the combinator, 1-based. Typically the 
        index of the signal in the parent 'filters' key, but this is not 
        strictly enforced. Will result in an import error if this value exceeds 
        the maximum number of slots that this constant combinator can contain.
        """,
    )
    name: str = Field(
        ...,
        description="""
        Name of the signal.
        """,
    )
    type: Optional[
        Literal[
            "virtual",
            "item",
            "fluid",
            "recipe",
            "entity",
            "space-location",
            "asteroid-chunk",
            "quality",
        ]
    ] = Field("item", description="Type of the signal.")
    # signal: Optional[SignalID] = Field(
    #     None,
    #     description="""
    #     Signal to broadcast. If this value is omitted the occupied slot will
    #     behave as if no signal exists within it. Cannot be a pure virtual
    #     (logic) signal like "signal-each", "signal-any", or
    #     "signal-everything"; if such signals are set they will be removed
    #     on import.
    #     """,
    # )
    # TODO: make this dynamic based on current environment?
    quality: Optional[
        Literal[
            "normal", "uncommon", "rare", "epic", "legendary", "quality-unknown", "any"
        ]
    ] = Field(
        "any",
        description="""
        Quality flag of the signal. If unspecified, this value is effectively 
        equal to 'any' quality level.
        """,
    )
    comparator: Optional[Literal[">", "<", "=", "≥", "≤", "≠"]] = Field(
        "=", description="Comparison operator when deducing the quality type."
    )
    count: int32 = Field(
        ...,
        description="""
        Value of the signal to emit.
        """,
    )
    max_count: Optional[int32] = Field(
        None,
        description="""
        The maximum value of the signal to emit. Only used with logistics-type
        requests.
        """,
    )

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

    @field_validator("name")
    @classmethod
    def ensure_not_pure_virtual(cls, value: Optional[str], info: ValidationInfo):
        """
        Warn if pure virtual signals (like "signal-each", "signal-any", and
        "signal-everything") are entered inside of a constant combinator.
        """
        if not info.context or value is None:
            return value
        if info.context["mode"] <= ValidationMode.MINIMUM:
            return value

        warning_list: list = info.context["warning_list"]

        if value in pure_virtual:
            warning_list.append(
                PureVirtualDisallowedWarning(
                    "Cannot set pure virtual signal '{}' in a constant combinator".format(
                        value.name
                    )
                )
            )

        return value


class Section(DraftsmanBaseModel):
    index: uint32  # TODO: 0-based or 1-based?
    filters: Optional[list[SignalFilter]] = []
    group: Optional[str] = Field(
        None,
        description="Name of this particular signal section group.",
    )

    def set_signal(
        self,
        index: int64,
        name: Union[str, None],
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
        try:
            new_entry = SignalFilter(
                index=index,
                name=name,
                type=type,
                quality=quality,
                comparator="=",
                count=count,
            )
            new_entry.index += 1
        except ValidationError as e:
            raise DataFormatError(e) from None

        new_filters = [] if self.filters is None else self.filters

        # Check to see if filters already contains an entry with the same index
        existing_index = None
        for i, signal_filter in enumerate(new_filters):
            if index + 1 == signal_filter["index"]:  # Index already exists in the list
                if name is None:  # Delete the entry
                    del new_filters[i]
                else:
                    new_filters[i] = new_entry
                existing_index = i
                break

        if existing_index is None:
            new_filters.append(new_entry)

    def get_signal(self, index):
        """
        Get the :py:data:`.SIGNAL_FILTER` ``dict`` entry at a particular index,
        if it exists.

        :param index: The index of the signal to analyze.

        :returns: A ``dict`` that conforms to :py:data:`.SIGNAL_FILTER`, or
            ``None`` if nothing was found at that index.
        """
        if not self.filters:
            return None

        return next(
            (item for item in self.filters if item["index"] == index + 1),
            None,
        )

    @field_validator("filters", mode="before")
    @classmethod
    def normalize_input(cls, value: Any):
        if isinstance(value, list):
            for i, entry in enumerate(value):
                if isinstance(entry, tuple):
                    # TODO: perhaps it would be better to modify the format so
                    # you must specify the signal type... or maybe not...
                    signal_types = get_signal_types(entry[0])
                    filter_type = (
                        "item" if "item" in signal_types else next(iter(signal_types))
                    )
                    value[i] = {
                        "index": i + 1,
                        "name": entry[0],
                        "type": filter_type,
                        "comparator": "=",
                        "count": entry[1],
                    }

        return value

    model_config = ConfigDict(validate_assignment=True)


# class SignalSection(Section):
#     filters: Optional[list[SignalFilter]] = []


# class RequestSection(Section):
#     filters: Optional[list[RequestFilter]] = []


class QualityFilter(DraftsmanBaseModel):
    quality: Optional[QualityName] = Field("any", description="""The quality of the signal to compare against.""")
    comparator: Optional[Literal[">", "<", "=", "≥", "≤", "≠"]] = Field(
        "=",
        description="""The comparison operator to use when evaluating signal comparisons.""",
    )

    @field_validator("comparator", mode="before")
    @classmethod
    def normalize_comparator_python_equivalents(cls, input: Any):
        conversions = {"==": "=", ">=": "≥", "<=": "≤", "!=": "≠"}
        if input in conversions:
            return conversions[input]
        else:
            return input


@attrs.define
class AttrsItemSpecification(Exportable):
    class InventryLocation(Exportable):
        inventory: uint32
        """
        Which inventory this item sits in, 1-indexed.
        """
        stack: uint32
        """
        Which slot in the inventory this item sits in, 0-indexed.
        """
        count: Optional[uint32] = attrs.field(
            default=1,
            validator=instance_of(Optional[uint32])
        )
        """
        The amount of that item to request to that slot. Defaults to 1 if 
        omitted.
        """

    in_inventory: list[InventryLocation] = attrs.field(
        factory=list,
        # TODO: validators
    )
    """
    The list of all locations that the selected item should go.
    """
    grid_count: uint32 = attrs.field(
        default=0,
        validator=instance_of(uint32)
    )
    """
    The total amount of items being requested to all locations.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, dict):
            return AttrsItemSpecification(**value)
        else:
            return value


class ItemSpecification(DraftsmanBaseModel):
    class InventoryLocation(DraftsmanBaseModel):
        inventory: uint32 = Field(  # TODO: size
            ..., description="Which inventory this item sits in, 1-indexed."
        )
        stack: uint32 = Field(  # TODO: size
            ...,
            description="Which slot in the inventory it lies in, 0-indexed.",
        )
        count: Optional[uint32] = Field(  # TODO: size
            1, description="The amount of the item to request to that slot."
        )

    in_inventory: Optional[list[InventoryLocation]] = Field(
        [], description="Which slots this item should occupy"
    )
    grid_count: Optional[uint32] = Field(
        0, description="The amount to request to the associated grid."
    )


@attrs.define
class AttrsItemRequest(Exportable):
    id: AttrsSignalID = attrs.field(
        converter=AttrsSignalID.converter,
        validator=instance_of(AttrsSignalID)
    )
    """
    The item to request.
    """
    items: AttrsItemSpecification = attrs.field(
        factory=AttrsItemSpecification,
        converter=AttrsItemSpecification.converter,
        validator=instance_of(AttrsItemSpecification)
    )
    """
    The grids/locations each item is being requested to.
    """


class ItemRequest(DraftsmanBaseModel):
    id: SignalID = Field(..., description="The name of the item to request.")
    items: ItemSpecification = Field(
        ...,
        description="""
        A list of all requested items and their locations within the 
        entity.
        """,
    )


class Sections(DraftsmanBaseModel):
    # class Section(DraftsmanBaseModel):
    #     index: uint32
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
    #             if (
    #                 index + 1 == signal_filter["index"]
    #             ):  # Index already exists in the list
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
    #                     value[i] = {
    #                         "index": i + 1,
    #                         "name": entry[0],
    #                         "type": next(iter(get_signal_types(entry[0]))),
    #                         "comparator": "=",
    #                         "count": entry[1],
    #                         "max_count": entry[1],
    #                     }

    #         return value

    #     model_config = ConfigDict(validate_assignment=True)

    sections: Optional[list[Section]] = Field([], description="""TODO""")

    def __getitem__(self, key):
        # Custom getitem for this thing specfically
        # return self.sections[key]
        if isinstance(key, str):
            return next(section for section in self.sections if section.group == key)
        else:
            return self.sections[key]
