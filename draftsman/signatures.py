# signatures.py

from schema import Schema, Use, Optional, Or, And

# Note: All data is only checked right before casting to blueprint string

COLOR_SCHEMA = Schema({
    "r": Use(float),
    "g": Use(float),
    "b": Use(float),
    "a": Use(float)
})

SIGNAL_ID_SCHEMA = Schema({
    "name": str,
    "type": str
})

SIGNAL_SCHEMA = Schema({
    "signal": SIGNAL_ID_SCHEMA,
    "count": int
})

SIGNAL_FILTER_ENTRY_SCHEMA = Schema({
    # TODO
})

ICON_SCHEMA = Schema({
    "index": Use(int),
    "signal": SIGNAL_ID_SCHEMA
})

INTEGER_SCHEMA = Schema(Use(int))

STRING_SCHEMA = Schema(str)

VEC_SCHEMA = Schema({
    "x": Use(float),
    "y": Use(float)
})

IVEC_SCHEMA = Schema([
    Use(int),
    Use(int)
])

GRID_POSITION_SCHEMA = Schema([
    Use(int), 
    Use(int)
])


POSITION_SCHEMA = Schema(
    Or(GRID_POSITION_SCHEMA, VEC_SCHEMA)
)

BAR_SCHEMA = Schema(
    int
)

CONNECTION_POINT_SCHEMA = Schema({
    "entity_id": Or(int, str),
    Optional("circuit_id"): Or(1, 2)
})

CONNECTIONS_SCHEMA = Schema({
    Optional("1"): {
        Optional("red"): [
            CONNECTION_POINT_SCHEMA
        ],
        Optional("green"): [
            CONNECTION_POINT_SCHEMA
        ]
    },
    Optional("2"): {
        Optional("red"): [
            CONNECTION_POINT_SCHEMA
        ],
        Optional("green"): [
            CONNECTION_POINT_SCHEMA
        ]
    }
})

DIRECTION_SCHEMA = Schema(And(int, lambda x: 0 <= x <= 7))

# TODO: normalization here!
CONTROL_BEHAVIOR_SCHEMA = Schema({
    Optional("circuit_enable_disable"): bool,
    Optional("circuit_condition"): {
        Optional("first_signal"): Or(str, SIGNAL_ID_SCHEMA),
        Optional("second_signal"): Or(str, SIGNAL_ID_SCHEMA),
        Optional("comparator"): str,
        Optional("constant"): int
    },
    Optional("connect_to_logistic_network"): bool,
    Optional("logistic_condition"): {
        Optional("first_signal"): Or(str, SIGNAL_ID_SCHEMA),
        Optional("second_signal"): Or(str, SIGNAL_ID_SCHEMA),
        Optional("comparator"): str,
        Optional("constant"): int
    },
    Optional("circuit_read_hand_contents"): bool,
    Optional("circuit_read_resources"): bool,

    Optional("circuit_contents_read_mode"): int,
    Optional("circuit_hand_read_mode"): int,

    Optional("circuit_set_stack_size"): bool,
    Optional("stack_control_input_signal"): Or(str, SIGNAL_ID_SCHEMA)
})

STACK_SIZE_SCHEMA = Schema(int)

BLUEPRINT_SCHEMA = Schema({
    "item": "blueprint",
    Optional("label"): str,
    Optional("label_color"): COLOR_SCHEMA,
    Optional("description"): str,
    Optional("entities"): list, # specify warning if missing
    Optional("tiles"): list,
    Optional("icons"): list,
    Optional("schedules"): list,
    Optional("version"): int,
})

BLUEPRINT_BOOK_SCHEMA = Schema({
    "item": "blueprint_book",
    Optional("label"): str,
    Optional("label_color"): COLOR_SCHEMA,
    Optional("blueprints"): [ # specify warning if missing
        {
            "index": int,
            "blueprint": BLUEPRINT_SCHEMA
        }
    ],
    Optional("active_index", default = 0): int,
    Optional("version"): int
})