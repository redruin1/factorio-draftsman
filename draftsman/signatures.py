# signatures.py

from schema import Schema, Use, Optional, Or, And
from draftsman.utils import signal_dict

# TODO: separate CONTROL_BEHAVIOR into their individual signatures for each entity
# TODO: write user-friendly error messages


BOOLEAN = Schema(bool)
INTEGER = Schema(int)
STRING = Schema(str)


COLOR = Schema({
    "r": Use(float),
    "g": Use(float),
    "b": Use(float),
    "a": Use(float)
})

def normalize_color(color):
    if isinstance(color, list):
        new_color = {}
        new_color["r"] = color[0]
        new_color["g"] = color[1]
        new_color["b"] = color[2]
        try:
            new_color["a"] = color[3]
        except IndexError:
            new_color["a"] = 1.0
        return new_color
    else:
        return color
USER_COLOR = Schema(
    And(
        Use(normalize_color),
        {
            "r": Use(float),
            "g": Use(float),
            "b": Use(float),
            Optional("a"): Use(float)
        },
    )
)

# SIGNAL_ID = Schema({
#     "name": str,
#     "type": str
# })

def normalize_signal_id(name):
    if isinstance(name, str):
        return signal_dict(name)
    else:
        return name
SIGNAL_ID = Schema(
And(
    Use(normalize_signal_id),
    Or(
        {
            "name": str,
            "type": str
        },
        None
    )
))

# SIGNAL_ID_OR_CONSTANT = Schema(Or(SIGNAL_ID, int, None))
SIGNAL_ID_OR_CONSTANT = Schema(
    And(
        Use(normalize_signal_id),
        Or(
            {
                "name": str,
                "type": str
            },
            int, 
            None
        )
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
    And(
        Use(normalize_comparator),
        Or(">", "<", "=", "≥",  "≤",  "≠", None)
    )
)
OPERATION = Schema(
    And(
        Use(lambda x: x.upper() if isinstance(x, str) else x),
        Or("*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR", None))
    )

SIGNAL = Schema({
    "signal": SIGNAL_ID,
    "count": int
})

FILTER_ENTRY = Schema({
    "name": str,
    "index": int
})

ICON = Schema({
    "index": Use(int),
    "signal": SIGNAL_ID
})

ABS_POSITION = Schema({
    "x": Use(float),
    "y": Use(float)
})

GRID_POSITION = Schema([
    Use(int), 
    Use(int)
])

POSITION = Schema(
    Or(ABS_POSITION, GRID_POSITION)
)

DIRECTION = Schema(And(int, lambda x: 0 <= x <= 7))
ORIENTATION = Schema(Or(Use(float), None))
BAR = Schema(Or(Use(int), None))

CONNECTION_POINT = Schema({
    "entity_id": Or(int, str),
    Optional("circuit_id"): Or(1, 2)
})

CONNECTIONS = Schema(
And(
    Use(lambda c: {} if c is None else c), # Init to empty dict if None
    {
        Optional("1"): {
            Optional("red"): [
                CONNECTION_POINT
            ],
            Optional("green"): [
                CONNECTION_POINT
            ]
        },
        Optional("2"): {
            Optional("red"): [
                CONNECTION_POINT
            ],
            Optional("green"): [
                CONNECTION_POINT
            ]
        }
    }
))

NEIGHBOURS = Schema(
    [
        Or(int, str)
    ]
)

SIGNAL_FILTER = Schema({
    "index": int,
    "signal": SIGNAL_ID,
    "count": int
})

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
SIGNAL_FILTERS = Schema(
    And(
        Use(normalize_signal_filters),
        Or(
            [SIGNAL_FILTER],
            None
        )
    )
)

CONTROL_BEHAVIOR = Schema({
    # Circuit condition
    Optional("circuit_enable_disable"): bool,
    Optional("circuit_condition"): {
        Optional("first_signal"): SIGNAL_ID,
        Optional("second_signal"): SIGNAL_ID,
        Optional("comparator"): COMPARATOR,
        Optional("constant"): int
    },
    # Logistic condition
    Optional("connect_to_logistic_network"): bool,
    Optional("logistic_condition"): {
        Optional("first_signal"): SIGNAL_ID,
        Optional("second_signal"): SIGNAL_ID,
        Optional("comparator"): COMPARATOR,
        Optional("constant"): int
    },
    # Transport Belts
    # Inserters
    # Mining Drills
    Optional("circuit_read_hand_contents"): bool,
    Optional("circuit_read_resources"): bool,

    Optional("circuit_contents_read_mode"): int,
    Optional("circuit_hand_read_mode"): int,

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
    },
    # Decider Combinators
    Optional("decider_conditions"): {
        Optional("first_constant"): int,
        Optional("first_signal"): SIGNAL_ID,
        Optional("comparator"): COMPARATOR,
        Optional("second_constant"): int,
        Optional("second_signal"): SIGNAL_ID,
    },
    # Constant Combinators
    Optional("filters"): SIGNAL_FILTERS,
    # Programmable Speakers
    Optional("circuit_parameters"): {
        Optional("signal_value_is_pitch"): bool,
        Optional("instrument_id"): int,
        Optional("note_id"): int
    }
})

TRANSPORT_BELT_CONTROL_BEHAVIOR = Schema({})
INSERTER_CONTROL_BEHAVIOR = Schema({})
LAMP_CONTROL_BEHAVIOR = Schema({})
# TODO: every one

IO_TYPE = Schema(
    Or(
        "input",
        "output",
        None
    )
)

STACK_SIZE = Schema(int)

def normalize_inventory(filters):
    for i, entry in enumerate(filters):
        if isinstance(entry, str):
            filters[i] = {"index": i+1, "name": filters[i]}
    return filters
INVENTORY_FILTER = Schema({
    Optional("filters"): 
    And(
        Use(normalize_inventory),
        [
            FILTER_ENTRY
        ]
    ),
    Optional("bar"): int
})

REQUEST_FILTERS = Schema([
    (str, int)
])

BLUEPRINT = Schema({
    "item": "blueprint",
    Optional("label"): str,
    Optional("label_color"): COLOR,
    Optional("description"): str,
    Optional("entities"): list, # specify warning if missing
    Optional("tiles"): list,
    Optional("icons"): list,
    Optional("schedules"): list,
    Optional("version"): int,
})

BLUEPRINT_BOOK = Schema({
    "item": "blueprint_book",
    Optional("label"): str,
    Optional("label_color"): COLOR,
    Optional("blueprints"): [ # specify warning if missing
        {
            "index": int,
            "blueprint": BLUEPRINT
        }
    ],
    Optional("active_index", default = 0): int,
    Optional("version"): int
})