.. py:currentmodule:: draftsman.signatures

:py:mod:`~draftsman.signatures`
===============================

.. automodule:: draftsman.signatures

.. py:data:: INTEGER
    
    Accepts an integer. 
    Normalizes the type to ``futureint`` on Python 2.

.. py:data:: INTEGER_OR_NONE

    Accepts an integer, or ``None``. 
    Normalizes the type to ``futureint`` on Python 2. 

.. py:data:: STRING

    Accepts a string. 
    Normalizes the type to a ``unicode`` string on Python 2.

.. py:data:: STRING_OR_NONE

    Accepts a string, or ``None``. 
    Normalizes the type to a ``unicode`` string on Python 2.

.. py:data:: AABB

    Accepts data of the format ``[[float, float], [float, float]]``, or ``None``.
    Used to store an axis-aligned bounding box where the first pair is the minimum coordinate and the second pair is the maximum coordinate.

.. py:data:: COLOR

    Used to store color data for Blueprint labels, Locomotive colors, etc.
    Accepts data of the format 

        ``{"r": float, "g": float, "b": float, Optional("a"): float}``

    or

        ``[float, float, float, Optional(float)]``

    or ``None``.
    The second format is automatically normalized to the first.
    Raises an error if any of the floating point values are not in the range ``[0.0, 255.0]``.

.. py:data:: SIGNAL_ID

    The name and type of a signal, used for either circuits or item filters.
    Accepts data of the format

        ``{"name": signal_name, "type": Or("item", "fluid", "virtual")}``

    or just the ``signal_name``. 
    All members are normalized to ``unicode`` strings on Python 2.

.. py:data:: SIGNAL_ID_OR_NONE

    Same as :py:data:`SIGNAL_ID`, but can also be ``None`` instead.

.. py:data:: SIGNAL_ID_OR_CONSTANT

    Same as :py:data:`SIGNAL_ID`, but can also be a 32-bit ``int`` instead.

.. py:data:: COMPARATOR

    The comparison operations, used in circuit conditions and :py:class:`.DeciderCombinator`.
    Can be one of:

    .. code-block:: python
    
        {">", "<", "=", "≥", "≤", "≠", None}
    
    or expressed as Python language equivalents:

    .. code-block:: python

        {">", "<", "==", ">=", "<=", "!=", None}

    Entries in the second format are automatically converted to the first format.

.. py:data:: OPERATION

    The arithmetic operations, used in :py:class:`.ArithmeticCombinator`.
    Can be one of:

    .. code-block:: python

        {"*", "/", "+", "-", "%", "^", "<<", ">>", "AND", "OR", "XOR", None}

    Strings specified in lowercase are automatically converted to uppercase on validation.

.. py:data:: CONDITION

    A general circuit condition, used for circuit conditions and logistic conditions.
    
    .. code-block:: python

        {
            Optional("first_signal"): SIGNAL_ID,
            Optional("second_signal"): SIGNAL_ID,
            Optional("comparator"): COMPARATOR,
            Optional("constant"): int,
        }

.. py:data:: ICON

    The format of a Blueprint or BlueprintBook icon, which helps visually distinguish them.
    
    .. code-block:: python

        {
            "index": int,
            "signal": SIGNAL_ID,
        }

    Raises an error if ``"index"`` is not in the range ``[1, 4]``.

.. py:data:: ICONS

    A list of :py:data:`ICON` objects, or ``None``. 
    Can be specified as:

    .. code-block:: python

        [{"index": int, "signal": {"name": signal_name, "type": signal_type}}, ...]

    Or more succinctly as:

    .. code-block:: python

        [signal_name, signal_name, ...]

    where the signal types are inferred and their index is the signal's position in the original list.
    Raises an error if the length of the list is greater than 4.

.. py:data:: ASSOCIATION

    A way of specifying a reference between two entities. 
    Used primarily in wire/circuit connections, but also used in Locomotive train schedules as well.
    Specified as:

    .. code-block:: python

        Or(int, EntityLike)

    The Factorio blueprint string format uses ``ints`` to determine what entity it's talking about, where the value represents the index of the entity in the master entities list.
    However, this is not very flexible when actively creating a blueprint, as inserting an entity at the beginning of the list destroys the meaning of all connections after it.
    Alternatively, Draftsman supports association by reference, where you pass the ``EntityLike`` that you want to link to directly.
    This solves the aforementioned problem, and allows you to query the connected entity in such a way that it always stays up to date.
    When a Blueprint is exported, these associations are converted to regular integers just-in-time to comply with the format.

.. py:data:: CIRCUIT_CONNECTION_POINT

    A single circuit connection object. 
    Must point to another entity via ``"entity_id"``; can optionally specify what side of the entity that it connects to, if that entity has multiple connection points.

    .. code-block:: python

        {"entity_id": ASSOCIATION, Optional("circuit_id"): Or(1, 2)}

.. py:data:: POWER_CONNECTION_POINT

    A single power connection object.
    Used exclusively for ``PowerSwitch`` in the base game, as copper wire connections.
    Must point to an entity via ``"entity_id"``; can optionally specify what power side of the target entity is connected to, though in practice this is always ``0``.

    .. code-block:: python

        {"entity_id": ASSOCIATION, Optional("wire_id"): Or(0, 1)}

    .. NOTE::

        Because copper wire connections exist in the connections structure, they actually dont count towards power pole neighbours.
        This means that you can have as many copper wire connection points as you want, even if a power pole is already connected to 5 others.

.. py:data:: CONNECTIONS

    The format of an entity's circuit connections.

    .. code-block:: python

        {
            Optional("1"): {
                Optional("red"):   [CIRCUIT_CONNECTION_POINT, ...],
                Optional("green"): [CIRCUIT_CONNECTION_POINT, ...],
            },
            Optional("2"): {
                Optional("red"):   [CIRCUIT_CONNECTION_POINT, ...],
                Optional("green"): [CIRCUIT_CONNECTION_POINT, ...],
            },
            Optional("Cu0"): [POWER_CONNECTION_POINT, ...],
            Optional("Cu1"): [POWER_CONNECTION_POINT, ...],
        }

    ``"1"`` or ``"2"`` specifies the side of the host entity that is connected; this defaults to ``"1"`` on entities that have only one connection point.
    ``"red"`` or ``"green"`` specify the color of the connected wire on that particular side.
    Each entry is a list of one or more connection points, as specified above.
    If ``None`` is passed in, the validation will default to an empty ``dict``.

.. py:data:: NEIGHBOURS

    The format of an entity's power-pole neighbours. This is only used in :py:class:`.ElectricPole`.

    .. code-block:: python

        [ASSOCIATION, ...]

    If ``None`` is passed in, the validation will default to an empty ``list``.

.. py:data:: SIGNAL_FILTER

    Format for signal values, used by :py:class:`.ConstantCombinator`.

    .. code-block:: python

        {
            "index": int,           # The location of the entry
            "signal": SIGNAL_ID,    # Which signal
            "count": int            # Value of the signal
        }

.. py:data:: SIGNAL_FILTERS

    Format for a set of signal values, used by :py:class:`.ConstantCombinator`.
    Can be specified in the format:

    .. code-block:: python

        [SIGNAL_FILTER, ...]

    Or, more succinctly:

    .. code-block:: python

        [(signal_name, signal_count), (str, int), ...]

    Where the ``"index"`` of an entry defaults to the index of the tuple in the list.
    Validation of the second format gets converted to the first format.

.. py:data:: INFINITY_FILTER

    A filter entry in a :py:class:`.InfinityContainer`.

    .. code-block:: python

        {
            "index": int,   # Which slot in the container
            "name": STRING, # Name of the item
            "count": int,   # Amount of the item
            "mode": Or("at-least", "at-most", "exactly") # Mode of behavior
        }

    ``"index"`` is the location in the container, ``"name"`` is the name of the item to filter, ``"count"`` is the amount, and ``"mode"`` is the manner in which the particular filter behaves.

.. py:data:: INFINITY_FILTERS

    A set of filter entries in a :py:class:`.InfinityContainer`.

    .. code-block:: python

        [INFINITY_FILTER, ...]

.. py:data:: INFINITY_CONTAINER

    Data format specifically for the :py:class:`.InfinityContainer` class.

    .. code-block:: python

        {
            Optional("remove_unfiltered_items"): bool, 
            Optional("filters"): INFINITY_FILTERS
        }

.. py:data:: INFINITY_PIPE

    Data format specifically for the :py:class:`.InfinityPipe` class.

    .. code-block:: python

        {
            Optional("name"): STRING,
            Optional("percentage"): int, # Where 100 is 100%
            Optional("mode"): Or("at-least", "at-most", "exactly", "add", "remove"),
            Optional("temperature"): int, # In the range [0, 1000]
        }

.. py:data:: PARAMETERS

    Parameters structure for :py:class:`.ProgrammableSpeaker`.

    .. code-block:: python

        {
            Optional("playback_volume"): float,
            Optional("playback_globally"): bool,
            Optional("allow_polyphony"): bool, # Allows multiple sounds to play at once
        }

.. py:data:: ALERT_PARAMETERS

    Alert parameters structure for :py:class:`.ProgrammableSpeaker`.

    .. code-block:: python

        {
            Optional("show_alert"): bool,
            Optional("show_on_map"): bool,
            Optional("icon_signal_id"): SIGNAL_ID, # Icon to show on alert
            Optional("alert_message"): six.text_type,
        }

.. py:data:: CONTROL_BEHAVIOR

    Control behavior structure.

    .. NOTE::

        Currently this is used for all entities with a control behavior.
        Ideally a each entity type would have a unique control behavior constant, but for now they exist as a single constant.

    .. code-block:: python

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

.. py:data:: FILTER_ENTRY

    Item filter entry. Used in :py:class:`.FilterInserter` and :py:class:`.Loader`.

    .. code-block:: python

        {
            "index": int
            "name": STRING, 
        }

.. py:data:: FILTERS

    Set of item filters. Used in :py:class:`.FilterInserter` and :py:class:`.Loader`.
    Can be specified in the format:

    .. code-block:: python

        [FILTER_ENTRY, ...]

    Or, more succinctly as:

    .. code-block:: python

        [item_name, str, ...]

    where the filter's ``"index"`` is determined by it's position in the list.
    Validation of the second format is automatically converted to the first format.

.. py:data:: INVENTORY_FILTER

    Set of item filters for an inventory object, used in :py:class:`.CargoWagon`.

    .. code-block:: python

        {
            Optional("filters"): FILTERS,
            Optional("bar"): int,
        }

    If ``None`` is passed in, the validation will default to an empty ``dict``.

.. py:data:: REQUEST_FILTERS

    List of request filters.

    .. NOTE::

        This is most likely to change in a future version.

    .. code-block:: python

        [(STRING, int), ...]

.. py:data:: WAIT_CONDITION

    A train schedule wait-condition.

    .. code-block:: python

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
            "compare_type": Or("or", "and"),    # Comparison with the previous wait-condition
            Optional("ticks"): int,             # Amount of time to wait if specified
            Optional("condition"): CONDITION,   # Circuit condition if specified
        }

.. py:data:: SCHEDULE

    A train schedule.

    .. code-block:: python

        {
            Optional("locomotives"): [ASSOCIATION, ...],
            "schedule": [
                {
                    "station": STRING, 
                    Optional("wait_conditions"): [WAIT_CONDITION, ...]
                }
            ],
        }

.. py:data:: SCHEDULES

    A set of train schedules.

    .. code-block:: python

        [SCHEDULE, ...]