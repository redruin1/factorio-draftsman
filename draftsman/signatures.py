# signatures.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.utils import signal_dict

from schema import Schema, Use, Optional, Or, And
import six


# TODO: separate CONTROL_BEHAVIOR into their individual signatures for each entity
# TODO: write user-friendly error messages


BOOLEAN = Schema(Or(bool, None))
INTEGER = Schema(Or(int, None))
FLOAT = Schema(Or(float, None))
STRING = Schema(Or(six.text_type, None))

AABB = Schema(Or([[Use(int), Use(int)], [Use(int), Use(int)]], None))


def normalize_color(color):
    if isinstance(color, (list, tuple)):
        new_color = {}
        new_color["r"] = color[0]
        new_color["g"] = color[1]
        new_color["b"] = color[2]
        try:
            new_color["a"] = color[3]
        except IndexError:
            new_color["a"] = 1.0
        return new_color
    elif isinstance(color, dict):
        try:
            color["a"]
        except KeyError:
            color["a"] = 1.0
        return color
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
                    error="'r' not in range [0, 255]",
                ),
                "g": And(
                    Use(float),
                    lambda x: 0 <= x <= 255,
                    error="'g' not in range [0, 255]",
                ),
                "b": And(
                    Use(float),
                    lambda x: 0 <= x <= 255,
                    error="'b' not in range [0, 255]",
                ),
                "a": And(
                    Use(float),
                    lambda x: 0 <= x <= 255,
                    error="'a' not in range [0, 255]",
                ),
            },
            None,
        ),
    )
)

# SIGNAL_ID = Schema({
#     "name": str,
#     "type": str
# })


def normalize_signal_id(name):
    if isinstance(name, six.text_type):
        return signal_dict(name)
    else:
        return name


SIGNAL_ID = Schema(
    And(
        Use(normalize_signal_id),
        Or({"name": six.text_type, "type": six.text_type}, None),
    )
)

# SIGNAL_ID_OR_CONSTANT = Schema(Or(SIGNAL_ID, int, None))
SIGNAL_ID_OR_CONSTANT = Schema(
    And(
        Use(normalize_signal_id),
        Or({"name": six.text_type, "type": six.text_type}, int, None),
    )
)


def normalize_comparator(op):
    if op == "<=":
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

SIGNAL = Schema({"signal": SIGNAL_ID, "count": int})

FILTER_ENTRY = Schema({"name": six.text_type, "index": int})

ICON = Schema({"index": Use(int), "signal": SIGNAL_ID})

ABS_POSITION = Schema({"x": Use(float), "y": Use(float)})

TILE_POSITION = Schema([Use(int), Use(int)])

# def normalize_position(pos):
#     pass
POSITION = Schema(Or(ABS_POSITION, TILE_POSITION))

# DIRECTION = Schema(And(int, lambda x: 0 <= x <= 7, error="Invalid direction"))
ORIENTATION = Schema(Or(Use(float), None))
BAR = Schema(Or(Use(int), None))

CIRCUIT_CONNECTION_POINT = Schema(
    {"entity_id": Or(int, six.text_type), Optional("circuit_id"): Or(1, 2)}
)

POWER_CONNECTION_POINT = Schema(
    {"entity_id": Or(int, six.text_type), Optional("wire_id"): Or(0, 1)}
)

CONNECTIONS = Schema(
    And(
        Use(lambda c: {} if c is None else c),  # Init to empty dict if None
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

NEIGHBOURS = Schema([Or(int, six.text_type)])

SIGNAL_FILTER = Schema({"index": int, "signal": SIGNAL_ID, "count": int})


def normalize_signal_filters(entries):
    if entries is None:
        return entries

    new_list = []
    for i, entry in enumerate(entries):
        if isinstance(entry, tuple):
            out = {"index": i + 1, "signal": entry[0], "count": entry[1]}
            new_list.append(out)
        else:
            new_list.append(entry)
    return new_list


SIGNAL_FILTERS = Schema(And(Use(normalize_signal_filters), Or([SIGNAL_FILTER], None)))

INFINITY_FILTER = Schema(
    {
        "index": int,
        "name": six.text_type,
        "count": int,
        "mode": Or("at-least", "at-most", "exactly"),
    }
)
INFINITY_FILTERS = Schema([INFINITY_FILTER])
INFINITY_CONTAINER = Schema(
    {Optional("remove_unfiltered_items"): bool, Optional("filters"): INFINITY_FILTERS}
)

INFINITY_PIPE = Schema(
    {
        Optional("name"): six.text_type,
        Optional("percentage"): int,
        Optional("mode"): Or("at-least", "at-most", "exactly", "add", "remove"),
        Optional("temperature"): int,
    }
)

PARAMETERS = Schema(
    {
        Optional("playback_volume"): float,
        Optional("playback_globally"): bool,
        Optional("allow_polyphony"): bool,
    }
)

ALERT_PARAMETERS = Schema(
    {
        Optional("show_alert"): bool,
        Optional("show_on_map"): bool,
        Optional("icon_signal_id"): SIGNAL_ID,
        Optional("alert_message"): six.text_type,
    }
)

CONDITION = Schema(
    {
        Optional("first_signal"): SIGNAL_ID,
        Optional("second_signal"): SIGNAL_ID,
        Optional("comparator"): COMPARATOR,
        Optional("constant"): int,
    }
)

CONTROL_BEHAVIOR = Schema(
    {
        # Circuit condition
        Optional("circuit_enable_disable"): bool,
        Optional("circuit_condition"): CONDITION,
        # Logistic condition
        Optional("connect_to_logistic_network"): bool,
        Optional("logistic_condition"): CONDITION,
        # Transport Belts
        Optional("circuit_read_hand_contents"): bool,
        # Mining Drills
        Optional("circuit_read_resources"): bool,
        # Inserters
        Optional("circuit_contents_read_mode"): int,
        Optional("circuit_hand_read_mode"): int,
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
            Optional("constant"): int,
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
    }
)

TRANSPORT_BELT_CONTROL_BEHAVIOR = Schema({})
INSERTER_CONTROL_BEHAVIOR = Schema({})
LAMP_CONTROL_BEHAVIOR = Schema({})
# TODO: every one

IO_TYPE = Schema(Or("input", "output", None))

STACK_SIZE = Schema(int)


def normalize_inventory(filters):
    for i, entry in enumerate(filters):
        if isinstance(entry, six.text_type):
            filters[i] = {"index": i + 1, "name": filters[i]}
    return filters


INVENTORY_FILTER = Schema(
    {
        Optional("filters"): And(Use(normalize_inventory), [FILTER_ENTRY]),
        Optional("bar"): int,
    }
)

REQUEST_FILTERS = Schema([(six.text_type, int)])

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
        Optional("locomotives"): [Or(int, six.text_type)],
        "schedule": [
            {"station": six.text_type, Optional("wait_conditions"): [WAIT_CONDITION]}
        ],
    }
)
SCHEDULES = Schema([SCHEDULE])

BLUEPRINT = Schema(
    {
        "item": "blueprint",
        Optional("label"): str,
        Optional("label_color"): COLOR,
        Optional("description"): str,
        Optional("entities"): list,  # specify warning if missing
        Optional("tiles"): list,
        Optional("icons"): list,
        Optional("schedules"): list,
        Optional("version"): int,
    }
)

BLUEPRINT_BOOK = Schema(
    {
        "item": "blueprint_book",
        Optional("label"): str,
        Optional("label_color"): COLOR,
        Optional("blueprints"): [  # specify warning if missing
            {"index": int, "blueprint": BLUEPRINT}
        ],
        Optional("active_index", default=0): int,
        Optional("version"): int,
    }
)
