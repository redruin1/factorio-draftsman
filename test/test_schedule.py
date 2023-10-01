# test_schedule.py

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.schedule import Schedule, WaitCondition, WaitConditions
from draftsman.constants import WaitConditionType, WaitConditionCompareType

import pytest
import re


class TestWaitCondition:
    def test_constructor(self):
        # Time passed
        w = WaitCondition(WaitConditionType.TIME_PASSED)
        assert w.type == "time"
        assert w.compare_type == "or"
        assert w.ticks == 1800
        assert w.condition == None

        # Inactivity
        w = WaitCondition(
            WaitConditionType.INACTIVITY, compare_type=WaitConditionCompareType.AND
        )
        assert w.type == "inactivity"
        assert w.compare_type == "and"
        assert w.ticks == 300
        assert w.condition == None

    def test_to_dict(self):
        w = WaitCondition(
            WaitConditionType.CIRCUIT_CONDITION,
            condition=("signal-A", "!=", "signal-B"),
        )
        assert w.to_dict() == {
            "type": "circuit",
            "compare_type": "or",
            "condition": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "comparator": "≠",
                "second_signal": {"name": "signal-B", "type": "virtual"},
            },
        }

        w = WaitCondition(
            WaitConditionType.CIRCUIT_CONDITION, condition=("signal-A", "<", 100)
        )
        assert w.to_dict() == {
            "type": "circuit",
            "compare_type": "or",
            "condition": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "comparator": "<",
                "constant": 100,
            },
        }

    def test_bitwise_and(self):
        # WaitCondition and WaitCondition
        full_cargo = WaitCondition(WaitConditionType.FULL_CARGO)
        inactivity = WaitCondition(WaitConditionType.INACTIVITY)

        conditions = full_cargo & inactivity
        assert isinstance(conditions, WaitConditions)
        assert len(conditions) == 2
        assert conditions == WaitConditions(
            [
                WaitCondition(WaitConditionType.FULL_CARGO),
                WaitCondition(WaitConditionType.INACTIVITY, compare_type="and"),
            ]
        )

        # WaitCondition and WaitConditions
        signal_sent = WaitCondition(
            WaitConditionType.CIRCUIT_CONDITION, condition=("signal-A", "==", 100)
        )
        sum1 = signal_sent & conditions
        assert isinstance(sum1, WaitConditions)
        assert len(sum1) == 3
        assert sum1 == WaitConditions(
            [
                WaitCondition(
                    WaitConditionType.CIRCUIT_CONDITION,
                    condition=("signal-A", "==", 100),
                ),
                WaitCondition(WaitConditionType.FULL_CARGO, compare_type="and"),
                WaitCondition(WaitConditionType.INACTIVITY, compare_type="and"),
            ]
        )

        # WaitCondition and error type
        with pytest.raises(
            ValueError,
            match="Can only perform this operation on <WaitCondition> or <WaitConditions> objects",
        ):
            signal_sent & Schedule()

        # WaitConditions and WaitCondition
        sum2 = conditions & signal_sent
        assert isinstance(sum2, WaitConditions)
        assert len(sum2) == 3
        assert sum2 == WaitConditions(
            [
                WaitCondition(WaitConditionType.FULL_CARGO),
                WaitCondition(WaitConditionType.INACTIVITY, compare_type="and"),
                WaitCondition(
                    WaitConditionType.CIRCUIT_CONDITION,
                    compare_type="and",
                    condition=("signal-A", "==", 100),
                ),
            ]
        )

        # Error type and WaitCondition
        with pytest.raises(
            ValueError,
            match="Can only perform this operation on <WaitCondition> or <WaitConditions> objects",
        ):
            Schedule() & signal_sent

    def test_bitwise_or(self):
        # WaitCondition and WaitCondition
        full_cargo = WaitCondition(WaitConditionType.FULL_CARGO)
        inactivity = WaitCondition(WaitConditionType.INACTIVITY)

        conditions = full_cargo | inactivity
        assert isinstance(conditions, WaitConditions)
        assert len(conditions) == 2
        assert conditions == WaitConditions(
            [
                WaitCondition(WaitConditionType.FULL_CARGO),
                WaitCondition(WaitConditionType.INACTIVITY),
            ]
        )

        # WaitCondition and WaitConditions
        signal_sent = WaitCondition(
            WaitConditionType.CIRCUIT_CONDITION, condition=("signal-A", "==", 100)
        )
        sum1 = signal_sent | conditions
        assert isinstance(sum1, WaitConditions)
        assert len(sum1) == 3
        assert sum1 == WaitConditions(
            [
                WaitCondition(
                    WaitConditionType.CIRCUIT_CONDITION,
                    condition=("signal-A", "==", 100),
                ),
                WaitCondition(WaitConditionType.FULL_CARGO),
                WaitCondition(WaitConditionType.INACTIVITY),
            ]
        )

        # WaitCondition and error type
        with pytest.raises(
            ValueError,
            match="Can only perform this operation on <WaitCondition> or <WaitConditions> objects",
        ):
            signal_sent | Schedule()

        # WaitConditions and WaitCondition
        sum2 = conditions | signal_sent
        assert isinstance(sum2, WaitConditions)
        assert len(sum2) == 3
        assert sum2 == WaitConditions(
            [
                WaitCondition(WaitConditionType.FULL_CARGO),
                WaitCondition(WaitConditionType.INACTIVITY),
                WaitCondition(
                    WaitConditionType.CIRCUIT_CONDITION,
                    condition=("signal-A", "==", 100),
                ),
            ]
        )

        # Error type and WaitCondition
        with pytest.raises(
            ValueError,
            match="Can only perform this operation on <WaitCondition> or <WaitConditions> objects",
        ):
            Schedule() | signal_sent

    def test_repr(self):
        w = WaitCondition(WaitConditionType.PASSENGER_PRESENT)
        assert repr(w) == "<WaitCondition>{type='passenger_present', compare_type='or'}"
        w = WaitCondition(WaitConditionType.INACTIVITY)
        assert (
            repr(w)
            == "<WaitCondition>{type='inactivity', compare_type='or', ticks=300}"
        )
        w = WaitCondition(
            WaitConditionType.ITEM_COUNT, condition=("signal-A", "=", "signal-B")
        )
        assert (
            repr(w)
            == "<WaitCondition>{type='item_count', compare_type='or', condition=('signal-A', '=', 'signal-B')}"
        )


class TestWaitConditions:
    def test_constructor(self):
        pass

    def test_to_dict(self):
        pass

    def test_len(self):
        pass

    def test_getitem(self):
        a = WaitConditions([
            WaitCondition(WaitConditionType.FULL_CARGO),
            WaitCondition(WaitConditionType.INACTIVITY, WaitConditionCompareType.AND, ticks=1000)
        ])

        assert a[0].type == WaitConditionType.FULL_CARGO
        assert a[1].type == WaitConditionType.INACTIVITY
        assert a[1].ticks == 1000

    def test_equals(self):
        # Not equivalent types
        a = WaitConditions()
        assert a != Schedule()

        # Mismatched length
        b = WaitConditions([WaitCondition(WaitConditionType.INACTIVITY)])
        assert a != b

        # Component mismatch
        a = WaitConditions([WaitCondition(WaitConditionType.TIME_PASSED)])
        assert a != b

        # True equality
        a = WaitConditions([WaitCondition(WaitConditionType.INACTIVITY)])
        assert a == b

    def test_repr(self):
        w = WaitConditions()
        assert repr(w) == "<WaitConditions>[]"


class TestSchedule:
    def test_constructor(self):
        # Default
        s = Schedule()
        assert s.locomotives == []
        assert s.stops == []

        # WaitConditions objects
        s = Schedule(
            schedule=[{"station": "some name", "wait_conditions": WaitConditions([])}]
        )
        assert s.locomotives == []
        assert s.stops == [
            {"station": "some name", "wait_conditions": WaitConditions([])}
        ]

    def test_locomotives(self):
        pass  # TODO

    def test_stops(self):
        pass  # TODO

    def test_add_locomotive(self):
        blueprint = Blueprint()
        blueprint.entities.append("locomotive", id="loco")
        s = Schedule()
        # Normal add
        s.add_locomotive(blueprint.entities["loco"])
        assert len(s.locomotives) == 1
        assert s.locomotives[0]() is blueprint.entities["loco"]

        # Duplicate add
        s.add_locomotive(blueprint.entities["loco"])
        assert len(s.locomotives) == 1
        assert s.locomotives[0]() is blueprint.entities["loco"]

        # Incorrect type
        blueprint.entities.append("wooden-chest", id="chest", tile_position=(10, 10))
        with pytest.raises(
            TypeError, match="'locomotive' must be an instance of <Locomotive>"
        ):
            s.add_locomotive(blueprint.entities["chest"])

    def test_remove_locomotive(self):
        blueprint = Blueprint()
        blueprint.entities.append("locomotive", id="loco")
        s = Schedule()
        # Normal add
        s.add_locomotive(blueprint.entities["loco"])
        assert len(s.locomotives) == 1
        assert s.locomotives[0]() is blueprint.entities["loco"]

        # Normal remove
        s.remove_locomotive(blueprint.entities["loco"])
        assert len(s.locomotives) == 0

        # Remove non-existant
        with pytest.raises(ValueError):
            s.remove_locomotive(blueprint.entities["loco"])

    def test_insert_stop(self):
        s = Schedule()

        # No wait_conditions
        s.insert_stop(0, "Station A")
        assert len(s.stops) == 1
        assert s.stops == [
            {"station": "Station A", "wait_conditions": WaitConditions()}
        ]

        full_cargo = WaitCondition(WaitConditionType.FULL_CARGO)
        inactivity = WaitCondition(WaitConditionType.INACTIVITY)

        # WaitCondition object
        s.insert_stop(1, "Station B", full_cargo)
        assert len(s.stops) == 2
        assert s.stops == [
            {"station": "Station A", "wait_conditions": WaitConditions()},
            {
                "station": "Station B",
                "wait_conditions": WaitConditions(
                    [WaitCondition(WaitConditionType.FULL_CARGO)]
                ),
            },
        ]

        # WaitConditions object
        s.insert_stop(2, "Station C", full_cargo & inactivity)
        assert len(s.stops) == 3
        assert s.stops == [
            {"station": "Station A", "wait_conditions": WaitConditions()},
            {
                "station": "Station B",
                "wait_conditions": WaitConditions(
                    [WaitCondition(WaitConditionType.FULL_CARGO)]
                ),
            },
            {
                "station": "Station C",
                "wait_conditions": WaitConditions(
                    [
                        WaitCondition(WaitConditionType.FULL_CARGO),
                        WaitCondition(WaitConditionType.INACTIVITY, compare_type="and"),
                    ]
                ),
            },
        ]

    def test_remove_stop(self):
        s = Schedule()

        full_cargo = WaitCondition(type="full")
        inactivity = WaitCondition(type="inactivity")

        s.append_stop("Station A")
        s.append_stop("Station A", wait_conditions=full_cargo)
        s.append_stop("Station A", wait_conditions=inactivity)
        assert len(s.stops) == 3
        assert s.stops == [
            {"station": "Station A", "wait_conditions": WaitConditions()},
            {"station": "Station A", "wait_conditions": WaitConditions([full_cargo])},
            {"station": "Station A", "wait_conditions": WaitConditions([inactivity])},
        ]

        # Remove with no wait_conditions
        s.remove_stop("Station A")
        assert len(s.stops) == 2
        assert s.stops == [
            {"station": "Station A", "wait_conditions": WaitConditions([full_cargo])},
            {"station": "Station A", "wait_conditions": WaitConditions([inactivity])},
        ]
        s.remove_stop("Station A")
        assert s.stops == [
            {"station": "Station A", "wait_conditions": WaitConditions([inactivity])}
        ]

        # Remove stop with wait_conditions that doesn't exist
        with pytest.raises(
            ValueError,
            match=re.escape(
                "No station with name 'Station A' and conditions '<WaitConditions>[<WaitCondition>{type='full', compare_type='or'}]' found in schedule"
            ),
        ):
            s.remove_stop("Station A", wait_conditions=full_cargo)

        # Remove stop that doesn't exist
        with pytest.raises(
            ValueError, match="No station with name 'Station B' found in schedule"
        ):
            s.remove_stop("Station B")

        # Remove with wait conditions
        s.remove_stop("Station A", wait_conditions=inactivity)
        assert len(s.stops) == 0
        assert s.stops == []

        # Remove stop that no longer exists
        with pytest.raises(
            ValueError, match="No station with name 'Station A' found in schedule"
        ):
            s.remove_stop("Station A")

    def test_to_dict(self):
        pass  # TODO

    def test_repr(self):
        s = Schedule()
        assert repr(s) == "<Schedule>{'locomotives': [], 'schedule': []}"
