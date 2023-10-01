# signatures.py
# -*- encoding: utf-8 -*-

"""
Module of data formats, implemented as ``Schema`` objects. Used to validate and
normalize data. Each one raises a ``SchemaError`` if the passed in data does not 
match the data format specified, which is usually wrapped with ``DraftsmanError``.
"""


from __future__ import unicode_literals

from draftsman.classes.association import Association
from draftsman.data.signals import signal_dict, mapper_dict

from typing_extensions import Annotated

from enum import Enum
from pydantic import BaseModel, RootModel, model_validator, model_serializer, Field
from schema import Schema, Use, Optional, Or, And
from typing import Optional as TrueOptional  # TODO: fixme
from typing import Literal, Any
import six
import sys
import types
import typing

try:
    from typing import get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import get_args, get_origin


if sys.version_info >= (3, 10):

    def _is_union(origin):
        return origin is typing.Union or origin is types.UnionType

else:

    def _is_union(origin):
        return origin is typing.Union


def recursive_construct(model_class: BaseModel, **input_data) -> BaseModel:
    def handle_annotation(annotation: type, value: Any):
        # print(annotation, value)
        try:
            if issubclass(annotation, BaseModel):
                # print("yes!")
                return recursive_construct(annotation, **value)
        except Exception as e:
            # print(type(e).__name__, e)
            # print("issue with BaseModel".format(annotation))
            pass
        try:
            if issubclass(annotation, RootModel):
                # print("rootyes!")
                return recursive_construct(annotation, root=value)
        except Exception as e:
            # print(type(e).__name__, e)
            # print("issue with RootModel")
            pass

        origin = get_origin(annotation)
        # print(origin)

        if origin is None:
            return value
        elif _is_union(origin):
            # print("optional")
            args = get_args(annotation)
            for arg in args:
                # print("\t", arg)
                result = handle_annotation(arg, value)
                # print("union result: {}".format(result))
                if result != value:
                    # print("early exit")
                    return result
            # Otherwise
            # print("otherwise")
            return value
        elif origin is typing.Literal:
            # print("literal")
            return value
        elif isinstance(origin, (str, bytes)):
            # print("string")
            return value
        elif issubclass(origin, typing.Tuple):
            # print("tuple")
            args = get_args(annotation)
            if isinstance(args[-1], type(Ellipsis)):
                # format: tuple[T, ...]
                member_type = args[0]
                return tuple(handle_annotation(member_type, v) for v in value)
            else:
                # format: tuple[A, B, C]
                return tuple(handle_annotation(member_type, value[i]) for i, member_type in enumerate(args))
        elif issubclass(origin, typing.Sequence):
            # print("list")
            member_type = get_args(annotation)[0]
            # print(member_type)
            # print(value)
            result = [handle_annotation(member_type, v) for v in value]
            # print("result: {}".format(result))
            return result
        else:
            return value

    m = model_class.__new__(model_class)
    fields_values: dict[str, typing.Any] = {}
    defaults: dict[str, typing.Any] = {} 
    for name, field in model_class.model_fields.items():
        # print("\t", name, field.annotation)
        if field.alias and field.alias in input_data:
            fields_values[name] = handle_annotation(field.annotation, input_data.pop(field.alias))
        elif name in input_data:
            result = handle_annotation(field.annotation, input_data.pop(name))
            # print("outer_result: {}".format(result))
            fields_values[name] = result
        elif not field.is_required():
            # print("\tdefault")
            defaults[name] = field.get_default(call_default_factory=True)
    _fields_set = set(fields_values.keys())
    fields_values.update(defaults)

    # print(fields_values)

    _extra: dict[str, typing.Any] | None = None
    if model_class.model_config.get('extra') == 'allow':
        _extra = {}
        for k, v in input_data.items():
            _extra[k] = v
    else:
        fields_values.update(input_data)
    object.__setattr__(m, '__dict__', fields_values)
    object.__setattr__(m, '__pydantic_fields_set__', _fields_set)
    if not model_class.__pydantic_root_model__:
        object.__setattr__(m, '__pydantic_extra__', _extra)

    if model_class.__pydantic_post_init__:
        m.model_post_init(None)
    elif not model_class.__pydantic_root_model__:
        # Note: if there are any private attributes, cls.__pydantic_post_init__ would exist
        # Since it doesn't, that means that `__pydantic_private__` should be set to None
        object.__setattr__(m, '__pydantic_private__', None)

    return m


# class BaseModel(PydanticBaseModel):
#     """
#     Here we patch Pydantic's base model so that we can support a recursive 
#     `model_construct()`. Hopefully this change gets implemented upstream, but 
#     if not/until then this modification enables this behavior

#     Make sure if you create new blueprint-likes to use THIS version of BaseModel
#     instead of Pydantic's default!
#     """
#     @classmethod
#     def model_construct(cls, _fields_set=None, _recursive=False, **values):
#         print("model construct {}".format(cls.__name__))
#         m = cls.__new__(cls)
#         fields_values: dict[str, typing.Any] = {}
#         defaults: dict[str, typing.Any] = {} 
#         for name, field in cls.model_fields.items():
#             print("\t", name, field.annotation)
#             if field.alias and field.alias in values:
#                 value = values.pop(field.alias)
#                 if _recursive:
#                     value = _recursive_model_construct(field.annotation, value)
#                 fields_values[name] = value
#             elif name in values:
#                 value = values.pop(name)
#                 if _recursive:
#                     value = _recursive_model_construct(field.annotation, value)
#                 fields_values[name] = value
#             elif not field.is_required():
#                 defaults[name] = field.get_default(call_default_factory=True)
#         if _fields_set is None:
#             _fields_set = set(fields_values.keys())
#         fields_values.update(defaults)

#         _extra: dict[str, typing.Any] | None = None
#         if cls.model_config.get('extra') == 'allow':
#             _extra = {}
#             for k, v in values.items():
#                 _extra[k] = v
#         else:
#             fields_values.update(values)
#         object.__setattr__(m, '__dict__', fields_values)
#         object.__setattr__(m, '__pydantic_fields_set__', _fields_set)
#         if not cls.__pydantic_root_model__:
#             object.__setattr__(m, '__pydantic_extra__', _extra)

#         if cls.__pydantic_post_init__:
#             m.model_post_init(None)
#         elif not cls.__pydantic_root_model__:
#             # Note: if there are any private attributes, cls.__pydantic_post_init__ would exist
#             # Since it doesn't, that means that `__pydantic_private__` should be set to None
#             object.__setattr__(m, '__pydantic_private__', None)

#         return m


# class RootModel(PydanticRootModel):
#     """
#     Because we also use `RootModel`, we need to overwrite this method as well
#     """
#     @classmethod
#     def model_construct(cls, root, _fields_set = None, _recursive=False):
#         print("root recurse")
#         # Redirect to our patched model
#         return BaseModel.model_construct(
#             root=root, _fields_set=_fields_set, _recursive=_recursive
#         )


# def _recursive_model_construct(annotation: type | None, value: typing.Any):
#     # No annotation? Early exit
#     if annotation is None:
#         return value
#     # Try treating the entire annotation as a BaseModel
#     try:
#         if issubclass(annotation, BaseModel):
#             print("yes!")
#             return annotation.model_construct(**value, _recursive=True)
#     except Exception as e:
#         print(type(e).__name__, e)
#         print("issue with BaseModel '{}'".format(annotation))
#         pass
#     # Try also treating the entire annotation as a RootModel
#     try:
#         if issubclass(annotation, RootModel):
#             return annotation.model_construct(value, _recursive=True)
#     except Exception as e:
#         print(type(e).__name__, e)
#         print("Issue with RootModel '{}'".format(annotation))
#         pass

#     # If that doesn't work, we might have a special type we need to explode
#     origin = get_origin(annotation)
#     # Early-exit so that issubclass() doesn't throw
#     print("origin: {}".format(origin))
#     if origin is None:
#         print("No origin")
#         print("returning '{}'".format(value))
#         return value
#     elif _is_union(origin):  # or origin is types.UnionType:
#         print("union")
#         # TODO: union_mode/discriminators?
#         for possible_type in get_args(annotation):
#             # The following could also probably be more explicit
#             print("possible_type: ", possible_type)
#             try:
#                 if issubclass(possible_type, BaseModel):
#                     return possible_type.model_construct(**value, _recursive=True)
#             except Exception as e:
#                 print(type(e), e)
#                 print("failed to recurse '{}'".format(annotation))
#                 pass
#             # Try also treating the entire annotation as a RootModel
#             try:
#                 if issubclass(possible_type, RootModel):
#                     return possible_type.model_construct(value, _recursive=True)
#             except Exception as e:
#                 print(e)
#                 print("failed to recurse '{}'".format(annotation))
#                 pass
            
#         print("none of the union members matched!")
#     elif origin is typing.Literal:
#         print("literal")
#         return value
#     elif isinstance(origin, (str, bytes)):
#         print("string")
#         return value
#     elif issubclass(origin, typing.Tuple):
#         print("tuple")
#         args = get_args(annotation)
#         if isinstance(args[-1], type(Ellipsis)):
#             # format: tuple[T, ...]
#             member_type = args[0]
#             return tuple(_recursive_model_construct(member_type, v) for v in value)
#         else:
#             # format: tuple[A, B, C]
#             return tuple(_recursive_model_construct(member_type, value[i]) for i, member_type in enumerate(args))
#     elif issubclass(origin, typing.Sequence):
#         print("sequence")
#         member_type = get_args(annotation)[0]
#         print(member_type)
#         print(value)
#         return [_recursive_model_construct(member_type, v) for v in value]
#     elif issubclass(origin, typing.Mapping):
#         print("mapping")
#         # Unsure if we need to explode key_type as well as value_type
#         key_type, value_type = get_args(annotation)
#         return {k: _recursive_model_construct(value_type, v) for k, v in value.items()}

#     print("returning '{}'".format(value))
#     # If none of the above, return the unchanged value
#     return value


int32 = Annotated[int, Field(..., ge=-2**31, lt=2**31)]

uint16 = Annotated[int, Field(..., ge=0, lt=2**16)]
uint32 = Annotated[int, Field(..., ge=0, lt=2**32)]
uint64 = Annotated[int, Field(..., ge=0, lt=2**64)] # TODO: description about floating point issues

INTEGER = Schema(int)
INTEGER_OR_NONE = Schema(Or(int, None))

STRING = Schema(
    And(
        Use(lambda x: six.text_type(x) if isinstance(x, six.string_types) else x),
        six.text_type,
    )
)
STRING_OR_NONE = Schema(Or(STRING, None))

BOOL_OR_NONE = Schema(Or(bool, None))

AABB = Schema(Or([[Use(float), Use(float)], [Use(float), Use(float)]], None))


def normalize_color(color):
    if isinstance(color, (list, tuple)):
        new_color = {}
        new_color["r"] = color[0]
        new_color["g"] = color[1]
        new_color["b"] = color[2]
        try:
            new_color["a"] = color[3]
        except IndexError:
            pass
        return new_color
    else:
        return color


COLOR = Schema(
    And(
        Use(normalize_color),
        Or(
            {
                "r": And(
                    Use(float),
                    lambda x: 0 <= x <= 255,
                    error="Invalid 'r' value",
                ),
                "g": And(
                    Use(float),
                    lambda x: 0 <= x <= 255,
                    error="Invalid 'g' value",
                ),
                "b": And(
                    Use(float),
                    lambda x: 0 <= x <= 255,
                    error="Invalid 'b' value",
                ),
                Optional("a"): And(
                    Use(float),
                    lambda x: 0 <= x <= 255,
                    error="Invalid 'a' value",
                ),
            },
            None,
        ),
    )
)


def normalize_signal_id(name):
    if isinstance(name, six.string_types):
        return signal_dict(name)
    else:
        return name


SIGNAL_ID = Schema(
    And(
        Use(normalize_signal_id, error="unknown input signal id"),
        {Optional("name"): six.text_type, "type": six.text_type},
    )
)

SIGNAL_ID_OR_NONE = Schema(
    And(
        Use(normalize_signal_id, error="unknown input signal id"),
        Or({"name": six.text_type, "type": six.text_type}, None),
    )
)

SIGNAL_ID_OR_CONSTANT = Schema(
    And(
        Use(normalize_signal_id, error="unknown input signal id"),
        Or({"name": six.text_type, "type": six.text_type}, int, None),
    )
)


def normalize_mapping_id(input):
    if isinstance(input, six.string_types):
        return mapper_dict(input)
    else:
        return input


MAPPING_ID_OR_NONE = Schema(
    And(
        Use(normalize_mapping_id, error="unknown input mapping id"),
        Or({"name": six.text_type, "type": six.text_type}, None),
    )
)


def normalize_comparator(op):
    if op == "==":
        return "="
    elif op == "<=":
        return "≤"
    elif op == ">=":
        return "≥"
    elif op == "!=":
        return "≠"
    else:
        return op


COMPARATOR = Schema(
    And(Use(normalize_comparator), Or(">", "<", "=", "≥", "≤", "≠", None))
)

OPERATION = Schema(
    And(
        Use(lambda x: x.upper() if isinstance(x, six.text_type) else x),
        Or("*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR", None),
    )
)

CONDITION = Schema(
    {
        Optional("first_signal"): SIGNAL_ID,
        Optional("second_signal"): SIGNAL_ID,
        Optional("comparator"): COMPARATOR,
        Optional("constant"): int,
    }
)

ICON = Schema(
    {
        "index": And(Use(int), lambda x: 1 <= x <= 4, error="invalid index"),
        "signal": SIGNAL_ID,
    }
)


def normalize_icons(icons):
    for i, icon in enumerate(icons):
        if isinstance(icon, six.string_types):
            icons[i] = {"index": i + 1, "signal": signal_dict(icon)}
    return icons


ICONS = Schema(And(Use(normalize_icons), Or([ICON], None)))

ASSOCIATION = Schema(Or(int, Association))

CIRCUIT_CONNECTION_POINT = Schema(
    {"entity_id": ASSOCIATION, Optional("circuit_id"): Or(1, 2)}
)

POWER_CONNECTION_POINT = Schema(
    {"entity_id": ASSOCIATION, Optional("wire_id"): Or(0, 1)}
)

CONNECTIONS = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            Optional("1"): {
                Optional("red"): [CIRCUIT_CONNECTION_POINT],
                Optional("green"): [CIRCUIT_CONNECTION_POINT],
            },
            Optional("2"): {
                Optional("red"): [CIRCUIT_CONNECTION_POINT],
                Optional("green"): [CIRCUIT_CONNECTION_POINT],
            },
            Optional("Cu0"): [POWER_CONNECTION_POINT],
            Optional("Cu1"): [POWER_CONNECTION_POINT],
        },
    )
)

NEIGHBOURS = Schema(And(Use(lambda x: [] if x is None else x), [ASSOCIATION]))

SIGNAL_FILTER = Schema({"index": int, "signal": SIGNAL_ID, "count": int})


def normalize_signal_filters(entries):
    new_list = []
    for i, entry in enumerate(entries):
        if isinstance(entry, tuple):
            out = {"index": i + 1, "signal": entry[0], "count": entry[1]}
            new_list.append(out)
        else:
            new_list.append(entry)
    return new_list


SIGNAL_FILTERS = Schema(And(Use(normalize_signal_filters), [SIGNAL_FILTER]))

INFINITY_FILTER = Schema(
    {
        "index": int,
        "name": STRING,
        "count": int,
        "mode": Or("at-least", "at-most", "exactly"),
    }
)
INFINITY_FILTERS = Schema([INFINITY_FILTER])
INFINITY_CONTAINER = Schema(
    And(
        Use(lambda x: {} if x is None else x),
        {
            Optional("remove_unfiltered_items"): bool,
            Optional("filters"): INFINITY_FILTERS,
        },
    )
)

INFINITY_PIPE = Schema(
    And(
        Use(lambda x: {} if x is None else x),
        {
            Optional("name"): STRING,
            Optional("percentage"): int,
            Optional("mode"): Or("at-least", "at-most", "exactly", "add", "remove"),
            Optional("temperature"): int,
        },
    )
)

PARAMETERS = Schema(
    And(
        Use(lambda x: {} if x is None else x),
        {
            Optional("playback_volume"): Use(float),
            Optional("playback_globally"): bool,
            Optional("allow_polyphony"): bool,
        },
    )
)

ALERT_PARAMETERS = Schema(
    And(
        Use(lambda x: {} if x is None else x),
        {
            Optional("show_alert"): bool,
            Optional("show_on_map"): bool,
            Optional("icon_signal_id"): SIGNAL_ID,
            Optional("alert_message"): six.text_type,
        },
    )
)

LOGISTIC_MODE_OF_OPERATION = Schema(Or(0, 1))

# CONTROL_BEHAVIOR = Schema(
#     And(
#         Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
#         {
#             # Circuit condition
#             Optional("circuit_enable_disable"): bool,
#             Optional("circuit_condition"): CONDITION,
#             # Logistic condition
#             Optional("connect_to_logistic_network"): bool,
#             Optional("logistic_condition"): CONDITION,
#             # Transport Belts + Inserters
#             Optional("circuit_read_hand_contents"): bool,
#             # Mining Drills
#             Optional("circuit_read_resources"): bool,
#             # Inserters
#             Optional("circuit_hand_read_mode"): int,
#             # Transport belts
#             Optional("circuit_contents_read_mode"): int,
#             # Filter inserters
#             Optional("circuit_mode_of_operation"): int,
#             Optional("circuit_set_stack_size"): bool,
#             Optional("stack_control_input_signal"): SIGNAL_ID,
#             # Train Stops
#             Optional("read_from_train"): bool,
#             Optional("read_stopped_train"): bool,
#             Optional("train_stopped_signal"): SIGNAL_ID,
#             Optional("set_trains_limit"): bool,
#             Optional("trains_limit_signal"): SIGNAL_ID,
#             Optional("read_trains_count"): bool,
#             Optional("trains_count_signal"): SIGNAL_ID,
#             Optional("send_to_train"): bool,
#             # Rail signals
#             Optional("red_output_signal"): SIGNAL_ID,
#             Optional("yellow_output_signal"): SIGNAL_ID,
#             Optional("green_output_signal"): SIGNAL_ID,
#             Optional("blue_output_signal"): SIGNAL_ID,
#             # Roboports
#             Optional("read_logistics"): bool,
#             Optional("read_robot_stats"): bool,
#             Optional("available_logistic_output_signal"): SIGNAL_ID,
#             Optional("total_logistic_output_signal"): SIGNAL_ID,
#             Optional("available_construction_output_signal"): SIGNAL_ID,
#             Optional("total_construction_output_signal"): SIGNAL_ID,
#             # Lamps
#             Optional("use_colors"): bool,
#             # Arithmetic Combinators
#             Optional("arithmetic_conditions"): {
#                 Optional("first_constant"): int,
#                 Optional("first_signal"): SIGNAL_ID,
#                 Optional("operation"): OPERATION,
#                 Optional("second_constant"): int,
#                 Optional("second_signal"): SIGNAL_ID,
#                 Optional("output_signal"): SIGNAL_ID,
#             },
#             # Decider Combinators
#             Optional("decider_conditions"): {
#                 Optional("constant"): int,
#                 Optional("first_constant"): int,
#                 Optional("first_signal"): SIGNAL_ID,
#                 Optional("comparator"): COMPARATOR,
#                 Optional("second_constant"): int,
#                 Optional("second_signal"): SIGNAL_ID,
#                 Optional("output_signal"): SIGNAL_ID,
#                 Optional("copy_count_from_input"): bool,
#             },
#             # Constant Combinators
#             Optional("filters"): SIGNAL_FILTERS,
#             # Programmable Speakers
#             Optional("circuit_parameters"): {
#                 Optional("signal_value_is_pitch"): bool,
#                 Optional("instrument_id"): int,
#                 Optional("note_id"): int,
#             },
#             # Accumulators
#             Optional("output_signal"): SIGNAL_ID,
#         },
#     )
# )

ACCUMULATOR_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            Optional("output_signal"): SIGNAL_ID,
        },
    )
)

ARITHMETIC_COMBINATOR_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            Optional("arithmetic_conditions"): {
                Optional("first_constant"): int,
                Optional("first_signal"): SIGNAL_ID,
                Optional("operation"): OPERATION,
                Optional("second_constant"): int,
                Optional("second_signal"): SIGNAL_ID,
                Optional("output_signal"): SIGNAL_ID,
            },
        },
    )
)

CONSTANT_COMBINATOR_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {Optional("filters"): SIGNAL_FILTERS, Optional("is_on"): bool},
    )
)

DECIDER_COMBINATOR_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            Optional("decider_conditions"): {
                Optional("constant"): int,
                Optional("first_constant"): int,
                Optional("first_signal"): SIGNAL_ID,
                Optional("comparator"): COMPARATOR,
                Optional("second_constant"): int,
                Optional("second_signal"): SIGNAL_ID,
                Optional("output_signal"): SIGNAL_ID,
                Optional("copy_count_from_input"): bool,
            },
        },
    )
)

FILTER_INSERTER_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Logistic condition
            Optional("connect_to_logistic_network"): bool,
            Optional("logistic_condition"): CONDITION,
            # Inserter
            Optional("circuit_read_hand_contents"): bool,
            Optional("circuit_hand_read_mode"): int,
            Optional("circuit_mode_of_operation"): int,
            Optional("circuit_set_stack_size"): bool,
            Optional("stack_control_input_signal"): SIGNAL_ID,
        },
    )
)

INSERTER_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Logistic condition
            Optional("connect_to_logistic_network"): bool,
            Optional("logistic_condition"): CONDITION,
            # Inserter
            Optional("circuit_read_hand_contents"): bool,
            Optional("circuit_hand_read_mode"): int,
            Optional("circuit_mode_of_operation"): int,
            Optional("circuit_set_stack_size"): bool,
            Optional("stack_control_input_signal"): SIGNAL_ID,
        },
    )
)

LAMP_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            Optional("circuit_condition"): CONDITION,
            Optional("logistic_condition"): CONDITION,
            Optional("use_colors"): bool,
        },
    )
)

LOGISTIC_BUFFER_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_mode_of_operation"): LOGISTIC_MODE_OF_OPERATION,
        },
    )
)

LOGISTIC_REQUESTER_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_mode_of_operation"): LOGISTIC_MODE_OF_OPERATION,
        },
    )
)

MINING_DRILL_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Logistic condition
            Optional("connect_to_logistic_network"): bool,
            Optional("logistic_condition"): CONDITION,
            # Mining Drills
            Optional("circuit_read_resources"): bool,
        },
    )
)

OFFSHORE_PUMP_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Logistic condition
            Optional("connect_to_logistic_network"): bool,
            Optional("logistic_condition"): CONDITION,
        },
    )
)

POWER_SWITCH_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Logistic condition
            Optional("connect_to_logistic_network"): bool,
            Optional("logistic_condition"): CONDITION,
        },
    )
)

PROGRAMMABLE_SPEAKER_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Programmable Speaker
            Optional("circuit_parameters"): {
                Optional("signal_value_is_pitch"): bool,
                Optional("instrument_id"): int,
                Optional("note_id"): int,
            },
        },
    )
)

PUMP_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
        },
    )
)

RAIL_SIGNAL_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_close_signal"): bool,
            Optional("circuit_read_signal"): bool,
            Optional("circuit_condition"): CONDITION,
            # Rail Signal
            Optional("red_output_signal"): SIGNAL_ID,
            Optional("orange_output_signal"): SIGNAL_ID,
            Optional("green_output_signal"): SIGNAL_ID,
        },
    )
)

RAIL_CHAIN_SIGNAL_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            Optional("red_output_signal"): SIGNAL_ID,
            Optional("orange_output_signal"): SIGNAL_ID,
            Optional("green_output_signal"): SIGNAL_ID,
            Optional("blue_output_signal"): SIGNAL_ID,
        },
    )
)

ROBOPORT_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Roboport
            Optional("read_logistics"): bool,
            Optional("read_robot_stats"): bool,
            Optional("available_logistic_output_signal"): SIGNAL_ID,
            Optional("total_logistic_output_signal"): SIGNAL_ID,
            Optional("available_construction_output_signal"): SIGNAL_ID,
            Optional("total_construction_output_signal"): SIGNAL_ID,
        },
    )
)

TRAIN_STOP_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Logistic condition
            Optional("connect_to_logistic_network"): bool,
            Optional("logistic_condition"): CONDITION,
            # Train Stop
            Optional("read_from_train"): bool,
            Optional("read_stopped_train"): bool,
            Optional("train_stopped_signal"): SIGNAL_ID,
            Optional("set_trains_limit"): bool,
            Optional("trains_limit_signal"): SIGNAL_ID,
            Optional("read_trains_count"): bool,
            Optional("trains_count_signal"): SIGNAL_ID,
            Optional("send_to_train"): bool,
        },
    )
)

TRANSPORT_BELT_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Logistic condition
            Optional("connect_to_logistic_network"): bool,
            Optional("logistic_condition"): CONDITION,
            # Transport Belts
            Optional("circuit_read_hand_contents"): bool,
            Optional("circuit_contents_read_mode"): int,
        },
    )
)

WALL_CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Wall
            Optional("circuit_open_gate"): bool,
            Optional("circuit_read_sensor"): bool,
            Optional("output_signal"): SIGNAL_ID,
        },
    )
)


def normalize_inventory(filters):
    for i, entry in enumerate(filters):
        if isinstance(entry, six.string_types):
            filters[i] = {"index": i + 1, "name": filters[i]}
    return filters


FILTER_ENTRY = Schema({"index": int, "name": STRING})
FILTERS = Schema(And(Use(normalize_inventory), [FILTER_ENTRY]))
INVENTORY_FILTER = Schema(
    And(
        Use(lambda x: {} if x is None else x),
        {
            Optional("filters"): FILTERS,
            Optional("bar"): int,
        },
    )
)


def normalize_request(filters):
    for i, entry in enumerate(filters):
        if isinstance(entry, tuple):
            filters[i] = {"index": i + 1, "name": entry[0], "count": entry[1]}
    return filters


REQUEST_FILTERS = Schema(
    And(normalize_request, [{"index": int, "name": STRING, "count": int}])
)  # TODO: change this

WAIT_CONDITION = Schema(
    {
        "type": Or(
            "time",
            "inactivity",
            "full",
            "empty",
            "item_count",
            "circuit",
            "robots_inactive",
            "fluid_count",
            "passenger_present",
            "passenger_not_present",
        ),
        "compare_type": Or("or", "and"),
        Optional("ticks"): int,
        Optional("condition"): CONDITION,
    }
)
SCHEDULE = Schema(
    {
        Optional("locomotives"): [ASSOCIATION],
        "schedule": [
            {"station": STRING, Optional("wait_conditions"): [WAIT_CONDITION]}
        ],
    }
)
SCHEDULES = Schema([SCHEDULE])


def normalize_mappers(mappers):
    if mappers is None:
        return mappers
    for i, mapper in enumerate(mappers):
        if isinstance(mapper, (tuple, list)):
            mappers[i] = {"index": i}
            if mapper[0]:
                mappers[i]["from"] = mapper_dict(mapper[0])
            if mapper[1]:
                mappers[i]["to"] = mapper_dict(mapper[1])
    return mappers


MAPPERS = Schema(
    And(
        Use(normalize_mappers),
        Or(
            [
                {
                    Optional("from"): MAPPING_ID_OR_NONE,
                    Optional("to"): MAPPING_ID_OR_NONE,
                    "index": int,
                }
            ],
            None,
        ),
    )
)


# =============================================================================
# Beyond be dragons

signal_schema = {  # TODO: rename
    "$id": "SIGNAL_DICT",  # TODO: rename
    "title": "Signal dict",
    "description": "JSON object that represents a signal. Used in the circuit network, but also used for blueprintable icons.",
    "type": "object",
    "properties": {
        "name": {
            "description": "Must be a name recognized by Factorio, or will error on import. Surprisingly, can actually be omitted; in that case will result in an empty signal.",
            "type": "string",
        },
        "type": {
            "description": "Must be one of the following values, or will error on import.",
            "type": "string",
            "enum": ["item", "fluid", "virtual"],
        },
    },
    "required": ["type"],
    "additionalProperties": False,
    "draftsman_conversion": lambda key, value: (key, normalize_signal_id(value)),
}


mapper_schema = {  # TODO: rename
    "$id": "MAPPER_DICT",  # TODO: rename
    "title": "Mapper dict",
    "description": "JSON object that represents a mapper. Used in Upgrade Planners to describe their function.",
    "type": "object",
    "properties": {
        "name": {
            "description": "Must be a name recognized by Factorio, or will error on import.",
            "type": "string",
        },
        "type": {
            "description": "Must be one of the following values, or will error on import. Item refers to modules, entity refers to everything else (as far as I've investigated; modded objects might change this behavior, but I have yet to take the time to find out)",
            "type": "string",
            "enum": ["item", "entity"],
        },
    },
    "required": ["name", "type"],
    "additionalProperties": False,
    "draftsman_conversion": lambda key, value: (key, normalize_mapping_id(value)),
}


# TODO: move this
class MapperType(str, Enum):
    entity = "entity"
    item = "item"


class MapperID(BaseModel):
    name: str
    type: MapperType


class Mapper(BaseModel):
    to: MapperID | None = None
    from_: MapperID | None = Field(None, alias="from")  # Damn you Python
    index: uint64


class Mappers(RootModel):
    root: list[Mapper] | None

    # @validator("__root__", pre=True)
    # def normalize_mappers(cls, mappers):
    #     if mappers is None:
    #         return mappers
    #     for i, mapper in enumerate(mappers):
    #         if isinstance(mapper, (tuple, list)):
    #             mappers[i] = {"index": i}
    #             if mapper[0]:
    #                 mappers[i]["from"] = mapping_dict(mapper[0])
    #             if mapper[1]:
    #                 mappers[i]["to"] = mapping_dict(mapper[1])
    #     return mappers

class SignalID(BaseModel):
    name: TrueOptional[str]  # Anyone's guess as to _why_ this is optional
    type: str

    @model_serializer
    def normalize(self):
        if isinstance(self, str):
            # If self is a string, then we try and convert to a dict
            # If the string is unknown, we cannot possibly know the type of this
            # signal, so this function raises an InvalidSignalError
            return signal_dict(self)
        else:
            return {"name": self.name, "type": self.type}


class Icon(BaseModel):
    signal: SignalID
    index: int # TODO dimension


class Icons(RootModel):
    root: list[Icon] | None = Field(..., max_length=4)

    # @root_validator(pre=True)
    @model_validator(mode="before")
    def normalize_icons(cls, icons):
        if icons is None:
            return icons
        for i, icon in enumerate(icons):
            if isinstance(icon, six.string_types):
                icons[i] = {"index": i + 1, "signal": signal_dict(icon)}
        return icons


class Color(BaseModel):
    r: int | float = Field(..., ge=0, le=255)
    g: int | float = Field(..., ge=0, le=255)
    b: int | float = Field(..., ge=0, le=255)
    a: int | float | None = Field(None, ge=0, le=255)

    @model_serializer
    def normalize(self): # FIXME: scuffed
        if isinstance(self, (list, tuple)):
            new_color = {}
            new_color["r"] = self[0]
            new_color["g"] = self[1]
            new_color["b"] = self[2]
            try:
                new_color["a"] = self[3]
            except IndexError:
                pass
            return new_color
        elif isinstance(self, dict):
            return {k: v for k, v in self.items() if v is not None}
        else:
            return {k: v for k, v in self.__dict__.items() if v is not None}



class Position(BaseModel):
    x: float | int
    y: float | int

    @model_validator(mode="before")
    def model_validator(cls, data):
        # likely a Vector
        try:
            return data.to_dict()
        except AttributeError:
            return data
        
# TODO: maybe a FloatPosition/IntPosition split for entities and tiles?

class WaitCondition(BaseModel):
    type: str
    compare_type: str
    ticks: int | None = None # TODO dimension
    condition: dict | None = None # TODO: correct annotation


class Stop(BaseModel):
    station: str
    wait_conditions: list[WaitCondition]


class EntityFilter(BaseModel):
    name: str
    index: uint64


class TileFilter(BaseModel):
    name: str
    index: uint64


class CircuitConnectionPoint(BaseModel):
    entity_id: int # TODO: dimension
    circuit_id: Literal[1, 2] | None = None


class WireConnectionPoint(BaseModel):
    entity_id: int # TODO: dimension
    wire_id: Literal[0, 1] | None = None


class Connections(BaseModel):
    class CircuitConnections(BaseModel):
        red: list[CircuitConnectionPoint] | None = None
        green: list[CircuitConnectionPoint] | None = None

    Wr1: CircuitConnections | None = Field(None, alias="1")
    Wr2: CircuitConnections | None = Field(None, alias="2")
    Cu0: list[WireConnectionPoint] | None = None
    Cu1: list[WireConnectionPoint] | None = None


# factorio_comparator_choices = {">", "<", "=", "≥", "≤", "≠"}
# python_comparator_choices = {"==", "<=", ">=", "!="}
class Comparator(RootModel):
    root: Literal[">", "<", "=", "≥", "≤", "≠"]

    @model_serializer
    def normalize(self):
        conversions = {
            "==": "=", 
            ">=": "≥", 
            "<=": "≤", 
            "!=": "≠"
        }
        if self.root in conversions:
            return conversions[self.root]
        else:
            return self.root


class Condition(BaseModel):
    first_signal: SignalID | None = None
    second_signal: SignalID | None = None
    comparator: Comparator | None = None
    constant: int32 | None = None


class Filters(RootModel):
    class FilterEntry(BaseModel):
        index: int | None = None # TODO: dimension, optional?
        name: str | None = None # TODO: optional?

    root: list[FilterEntry] | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_validate(cls, input):
        result = []
        for i, entry in enumerate(input):
            if isinstance(entry, str):
                result.append({"index": i + 1, "name": entry})
            else:
                result.append(entry)
        return result

    @model_serializer
    def normalize_construct(self):
        result = []
        for i, entry in enumerate(self.root):
            if isinstance(entry, str):
                result.append({"index": i + 1, "name": entry})
            else:
                result.append(entry)
        return result


class InventoryFilters(BaseModel):
    filters: Filters | None = None
    bar: uint16 | None = None


class RequestFilters(RootModel):
    class Request(BaseModel):
        index: int # TODO dimension, optional?
        name: str # TODO: optional?
        count: int # TODO dimension, optional?

    root: list[Request]

    @model_validator(mode="before")
    @classmethod
    def normalize_validate(cls, input):
        result = []
        for i, entry in enumerate(input):
            if isinstance(entry, (tuple, list)):
                result.append({"index": i + 1, "name": entry[0], "count": entry[1]})
            else:
                result.append(entry)
        return result

    @model_serializer
    def normalize_construct(self):
        result = []
        for i, entry in enumerate(self.root):
            if isinstance(entry, (tuple, list)):
                result.append({"index": i + 1, "name": entry[0], "count": entry[1]})
            else:
                result.append(entry)
        return result


class SignalFilters(RootModel):
    class SignalFilter(BaseModel):
        index: int # TODO: dimension, optional?
        signal: SignalID # TODO: optional?
        count: int # TODO: dimension, optional?

    root: list[SignalFilter]

    @model_serializer
    def normalize(self):
        new_list = []
        for i, entry in enumerate(self.root):
            if isinstance(entry, tuple):
                # out = {"index": i + 1, "signal": entry[0], "count": entry[1]}
                out = self.SignalFilter.model_construct(
                    index=i + 1,
                    signal=entry[0], 
                    count=entry[1]
                ).model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True,
                )
                new_list.append(out)
            else:
                new_list.append(entry)
        return new_list