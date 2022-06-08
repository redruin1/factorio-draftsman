# signatures.py
# -*- encoding: utf-8 -*-

"""
Module of data formats, implemented as ``Schema`` objects. Used to validate and
normalize data. Each one raises a ``SchemaError`` if the passed in data does not 
match the data format specified, which is usually wrapped with ``DraftsmanError``.
"""


from __future__ import unicode_literals

from draftsman.classes.association import Association
from draftsman.data.signals import signal_dict

from builtins import int
from schema import Schema, Use, Optional, Or, And
import six
import weakref


# TODO: separate CONTROL_BEHAVIOR into their individual signatures for each entity
# TODO: write user-friendly error messages


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
        return signal_dict(six.text_type(name))
    else:
        return name


SIGNAL_ID = Schema(
    And(
        Use(normalize_signal_id, error="unknown input signal id"),
        {"name": six.text_type, "type": six.text_type},
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
            Optional("playback_volume"): float,
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

CONTROL_BEHAVIOR = Schema(
    And(
        Use(lambda x: {} if x is None else x),  # Convert to empty dict if None
        {
            # Circuit condition
            Optional("circuit_enable_disable"): bool,
            Optional("circuit_condition"): CONDITION,
            # Logistic condition
            Optional("connect_to_logistic_network"): bool,
            Optional("logistic_condition"): CONDITION,
            # Transport Belts + Inserters
            Optional("circuit_read_hand_contents"): bool,
            # Mining Drills
            Optional("circuit_read_resources"): bool,
            # Inserters
            Optional("circuit_hand_read_mode"): int,
            # Transport belts
            Optional("circuit_contents_read_mode"): int,
            # Filter inserters
            Optional("circuit_mode_of_operation"): int,
            Optional("circuit_set_stack_size"): bool,
            Optional("stack_control_input_signal"): SIGNAL_ID,
            # Train Stops
            Optional("read_from_train"): bool,
            Optional("read_stopped_train"): bool,
            Optional("train_stopped_signal"): SIGNAL_ID,
            Optional("set_trains_limit"): bool,
            Optional("trains_limit_signal"): SIGNAL_ID,
            Optional("read_trains_count"): bool,
            Optional("trains_count_signal"): SIGNAL_ID,
            # Rail signals
            Optional("red_output_signal"): SIGNAL_ID,
            Optional("yellow_output_signal"): SIGNAL_ID,
            Optional("green_output_signal"): SIGNAL_ID,
            Optional("blue_output_signal"): SIGNAL_ID,
            # Roboports
            Optional("read_logistics"): bool,
            Optional("read_robot_stats"): bool,
            Optional("available_logistic_output_signal"): SIGNAL_ID,
            Optional("total_logistic_output_signal"): SIGNAL_ID,
            Optional("available_construction_output_signal"): SIGNAL_ID,
            Optional("total_construction_output_signal"): SIGNAL_ID,
            # Lamps
            Optional("use_colors"): bool,
            # Arithmetic Combinators
            Optional("arithmetic_conditions"): {
                Optional("first_constant"): int,
                Optional("first_signal"): SIGNAL_ID,
                Optional("operation"): OPERATION,
                Optional("second_constant"): int,
                Optional("second_signal"): SIGNAL_ID,
                Optional("output_signal"): SIGNAL_ID,
            },
            # Decider Combinators
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
            # Constant Combinators
            Optional("filters"): SIGNAL_FILTERS,
            # Programmable Speakers
            Optional("circuit_parameters"): {
                Optional("signal_value_is_pitch"): bool,
                Optional("instrument_id"): int,
                Optional("note_id"): int,
            },
            # Accumulators
            Optional("output_signal"): SIGNAL_ID,
        },
    )
)

# TRANSPORT_BELT_CONTROL_BEHAVIOR = Schema({})
# INSERTER_CONTROL_BEHAVIOR = Schema({})
# LAMP_CONTROL_BEHAVIOR = Schema({})
# # TODO: every one


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
