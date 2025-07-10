# test_schedule.py

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.schedule import Schedule, WaitCondition, WaitConditions
from draftsman.constants import WaitConditionType, ValidationMode
from draftsman.error import DataFormatError
import draftsman.validators
from draftsman.signatures import Condition

import pytest
import re


class TestWaitCondition:
    def test_constructor(self):
        # Time passed
        w = WaitCondition("time")
        assert w.type == "time"
        assert w.compare_type == "and"
        assert w.ticks == 1800
        assert w.condition == None

        # Inactivity
        w = WaitCondition("inactivity", compare_type="or")
        assert w.type == "inactivity"
        assert w.compare_type == "or"
        assert w.ticks == 300
        assert w.condition == None

        w = WaitCondition("circuit")
        assert w.type == "circuit"
        assert w.compare_type == "and"
        assert w.ticks == None
        assert w.condition == Condition()

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            w = WaitCondition("incorrect", compare_type="incorrect")
        assert w.type == "incorrect"
        assert w.compare_type == "incorrect"
        assert w.ticks is None
        assert w.condition is None
        assert w.to_dict() == {"type": "incorrect", "compare_type": "incorrect"}

        with pytest.raises(DataFormatError):
            w.validate().reissue_all()

    def test_to_dict(self):
        # 2.0
        w = WaitCondition(
            "circuit",
            condition=Condition(
                first_signal="signal-A", comparator="!=", second_signal="signal-B"
            ),
        )
        assert isinstance(w.condition, Condition)
        assert w.to_dict() == {
            "type": "circuit",
            # "compare_type": "or", # Default
            "condition": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "comparator": "≠",
                "second_signal": {"name": "signal-B", "type": "virtual"},
            },
        }

        w = WaitCondition(
            "circuit",
            condition=Condition(first_signal="signal-A", comparator="<", constant=100),
        )
        assert w.to_dict() == {
            "type": "circuit",
            # "compare_type": "or", # Default
            "condition": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                # "comparator": "<", # Default
                "constant": 100,
            },
        }

        # Version Specific
        w = WaitCondition(
            "circuit",
            condition=Condition(first_signal="signal-A", comparator="<", constant=100),
            station="Some Station Name",
        )
        assert w.to_dict(version=(1, 0)) == {
            "type": "circuit",
            # "compare_type": "or", # Default
            "condition": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                # "comparator": "<", # Default
                "constant": 100,
            },
        }
        assert w.to_dict(version=(2, 0)) == {
            "type": "circuit",
            # "compare_type": "or", # Default
            "condition": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                # "comparator": "<", # Default
                "constant": 100,
            },
            "station": "Some Station Name",
        }

    def test_set_type(self):
        full_cargo = WaitCondition("full")

        full_cargo.type = WaitConditionType.EMPTY_CARGO
        assert full_cargo.type == WaitConditionType.EMPTY_CARGO

        assert full_cargo == WaitCondition("empty")

        with pytest.raises(DataFormatError):
            full_cargo.type = "string, but not one of valid literals"

    def test_set_ticks(self):
        time_passed = WaitCondition("time")
        time_passed.ticks = 1000
        assert time_passed.ticks == 1000

        # You can set ticks on any WaitCondition object
        # TODO: maybe issue a warning if this is done?
        full_cargo = WaitCondition("full")
        full_cargo.ticks = 100
        assert full_cargo.ticks == 100

        with pytest.raises(DataFormatError):
            full_cargo.ticks = "incorrect"

    def test_set_condition(self):
        circuit_condition = WaitCondition("circuit")
        circuit_condition.condition = {
            "first_signal": "signal-A",
            "comparator": ">",
            "constant": 1000,
        }
        assert circuit_condition.condition == Condition(
            **{"first_signal": "signal-A", "comparator": ">", "constant": 1000}
        )

        # You can set condition on any WaitCondition object
        # TODO: maybe issue a warning if this is done?
        full_cargo = WaitCondition("full")
        full_cargo.condition = {
            "first_signal": "signal-A",
            "comparator": "==",
            "second_signal": "signal-B",
        }
        assert full_cargo.condition == Condition(
            **{
                "first_signal": "signal-A",
                "comparator": "==",
                "second_signal": "signal-B",
            }
        )

        with pytest.raises(DataFormatError):
            full_cargo.condition = "incorrect"

    def test_bitwise_and(self):
        # WaitCondition and WaitCondition
        full_cargo = WaitCondition("full")
        inactivity = WaitCondition("inactivity")

        conditions = full_cargo & inactivity
        assert isinstance(conditions, WaitConditions)
        assert len(conditions) == 2
        assert conditions == WaitConditions(
            [
                WaitCondition("full"),
                WaitCondition("inactivity", compare_type="and"),
            ]
        )

        # WaitCondition and WaitConditions
        signal_sent = WaitCondition(
            "circuit",
            condition=Condition(first_signal="signal-A", comparator="==", constant=100),
        )
        sum1 = signal_sent & conditions
        assert isinstance(sum1, WaitConditions)
        assert len(sum1) == 3
        assert sum1 == WaitConditions(
            [
                WaitCondition(
                    "circuit",
                    condition=Condition(
                        first_signal="signal-A", comparator="==", constant=100
                    ),
                ),
                WaitCondition("full", compare_type="and"),
                WaitCondition("inactivity", compare_type="and"),
            ]
        )

        # WaitCondition and error type
        with pytest.raises(
            TypeError,
            match=re.escape(
                "unsupported operand type(s) for &: 'WaitCondition' and 'Schedule'"
            ),
        ):
            signal_sent & Schedule()

        # WaitConditions and WaitCondition
        sum2 = conditions & signal_sent
        assert isinstance(sum2, WaitConditions)
        assert len(sum2) == 3
        assert sum2 == WaitConditions(
            [
                WaitCondition("full"),
                WaitCondition("inactivity", compare_type="and"),
                WaitCondition(
                    "circuit",
                    compare_type="and",
                    condition=Condition(
                        first_signal="signal-A", comparator="==", constant=100
                    ),
                ),
            ]
        )

        # Error type and WaitCondition
        with pytest.raises(
            TypeError,
            match=re.escape(
                "unsupported operand type(s) for &: 'Schedule' and 'WaitCondition'"
            ),
        ):
            Schedule() & signal_sent

    def test_bitwise_or(self):
        # WaitCondition and WaitCondition
        full_cargo = WaitCondition("full")
        inactivity = WaitCondition("inactivity")

        conditions = full_cargo | inactivity
        assert isinstance(conditions, WaitConditions)
        assert len(conditions) == 2
        assert conditions == WaitConditions(
            [
                WaitCondition("full", compare_type="and"),
                WaitCondition("inactivity", compare_type="or"),
            ]
        )

        # WaitCondition and WaitConditions
        signal_sent = WaitCondition(
            "circuit",
            condition=Condition(first_signal="signal-A", comparator="==", constant=100),
        )
        sum1 = signal_sent | conditions
        assert isinstance(sum1, WaitConditions)
        assert len(sum1) == 3
        assert sum1 == WaitConditions(
            [
                WaitCondition(
                    "circuit",
                    condition=Condition(
                        first_signal="signal-A", comparator="==", constant=100
                    ),
                ),
                WaitCondition("full", compare_type="or"),
                WaitCondition("inactivity", compare_type="or"),
            ]
        )

        # Unsupported operation
        with pytest.raises(
            TypeError,
            match="unsupported operand type(s) for |: 'WaitCondition' and 'Schedule'",
        ):
            signal_sent | Schedule()

        # WaitConditions and WaitCondition
        sum2 = conditions | signal_sent
        assert isinstance(sum2, WaitConditions)
        assert len(sum2) == 3
        assert sum2 == WaitConditions(
            [
                WaitCondition("full"),
                WaitCondition("inactivity", compare_type="or"),
                WaitCondition(
                    "circuit",
                    compare_type="or",
                    condition=Condition(
                        first_signal="signal-A", comparator="==", constant=100
                    ),
                ),
            ]
        )

        # Error type and WaitCondition
        with pytest.raises(
            TypeError,
            match="unsupported operand type(s) for |: 'Schedule' and 'WaitCondition'",
        ):
            Schedule() | signal_sent


class TestWaitConditions:
    def test_constructor(self):
        # Test dict input
        a = WaitConditions([{"type": "full"}, {"type": "inactivity"}])
        assert a == WaitConditions(
            [
                WaitCondition("full"),
                WaitCondition("inactivity"),
            ]
        )

    def test_to_dict(self):
        pass

    def test_len(self):
        pass

    def test_getitem(self):
        a = WaitConditions(
            [WaitCondition("full"), WaitCondition("inactivity", "and", ticks=1000)]
        )

        assert a[0].type == "full"
        assert a[1].type == "inactivity"
        assert a[1].ticks == 1000

    def test_equals(self):
        # Not equivalent types
        a = WaitConditions()
        assert a != Schedule()

        # Mismatched length
        b = WaitConditions([WaitCondition("inactivity")])
        assert a != b

        # Component mismatch
        a = WaitConditions([WaitCondition("time")])
        assert a != b

        # True equality
        a = WaitConditions([WaitCondition("inactivity")])
        assert a == b

    def test_repr(self):
        w = WaitConditions()
        assert repr(w) == "WaitConditions([])"


class TestSchedule:
    def test_constructor(self):
        # Default
        s = Schedule()
        assert s.locomotives == []
        assert s.stops == []

        # WaitConditions objects
        s = Schedule(
            stops=[
                Schedule.Stop(station="some name", wait_conditions=WaitConditions([]))
            ]
        )
        assert s.locomotives == []
        assert s.stops == [
            Schedule.Stop(station="some name", wait_conditions=WaitConditions([]))
        ]

        with pytest.raises(DataFormatError):
            s = Schedule(locomotives="incorrect").validate().reissue_all()

    def test_locomotives(self):
        pass  # TODO

    def test_stops(self):
        s = Schedule()
        assert s.stops == []
        with pytest.raises(DataFormatError):
            s.stops = "incorrect"
        assert s.stops == []

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
            Schedule.Stop(
                **{"station": "Station A", "wait_conditions": WaitConditions()}
            )
        ]

        full_cargo = WaitCondition("full")
        inactivity = WaitCondition("inactivity")

        # WaitCondition object
        s.insert_stop(1, "Station B", full_cargo)
        assert len(s.stops) == 2
        assert s.stops == [
            Schedule.Stop(
                **{"station": "Station A", "wait_conditions": WaitConditions()}
            ),
            Schedule.Stop(
                **{
                    "station": "Station B",
                    "wait_conditions": WaitConditions([WaitCondition("full")]),
                }
            ),
        ]

        # WaitConditions object
        s.insert_stop(2, "Station C", full_cargo & inactivity)
        assert len(s.stops) == 3
        assert s.stops == [
            Schedule.Stop(
                **{"station": "Station A", "wait_conditions": WaitConditions()}
            ),
            Schedule.Stop(
                **{
                    "station": "Station B",
                    "wait_conditions": WaitConditions([WaitCondition("full")]),
                }
            ),
            Schedule.Stop(
                **{
                    "station": "Station C",
                    "wait_conditions": WaitConditions(
                        [
                            WaitCondition("full"),
                            WaitCondition("inactivity", compare_type="and"),
                        ]
                    ),
                }
            ),
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
            Schedule.Stop(
                **{"station": "Station A", "wait_conditions": WaitConditions()}
            ),
            Schedule.Stop(
                **{
                    "station": "Station A",
                    "wait_conditions": WaitConditions([full_cargo]),
                }
            ),
            Schedule.Stop(
                **{
                    "station": "Station A",
                    "wait_conditions": WaitConditions([inactivity]),
                }
            ),
        ]

        # Remove with no wait_conditions
        s.remove_stop("Station A")
        assert len(s.stops) == 2
        assert s.stops == [
            Schedule.Stop(
                **{
                    "station": "Station A",
                    "wait_conditions": WaitConditions([full_cargo]),
                }
            ),
            Schedule.Stop(
                **{
                    "station": "Station A",
                    "wait_conditions": WaitConditions([inactivity]),
                }
            ),
        ]
        s.remove_stop("Station A")
        assert s.stops == [
            Schedule.Stop(
                **{
                    "station": "Station A",
                    "wait_conditions": WaitConditions([inactivity]),
                }
            )
        ]

        # Remove stop with wait_conditions that doesn't exist
        with pytest.raises(ValueError):
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

    def test_add_interrupt(self):
        s = Schedule()

        s.add_interrupt(
            name="Interrupt!",
            conditions=WaitCondition(WaitConditionType.FULL_CARGO)
            | WaitCondition(WaitConditionType.EMPTY_CARGO),
            targets=[],
        )
        assert s.interrupts == [
            Schedule.Interrupt(
                name="Interrupt!",
                conditions=[
                    WaitCondition(WaitConditionType.FULL_CARGO),
                    WaitCondition(WaitConditionType.EMPTY_CARGO, compare_type="or"),
                ],
                targets=[],
            ),
        ]

    def test_remove_interrupt(self):
        s = Schedule()

        s.add_interrupt(
            name="Interrupt!",
            conditions=WaitCondition(WaitConditionType.FULL_CARGO),
            targets=[],
        )
        s.add_interrupt(
            name="Interrupt!",
            conditions=WaitCondition(WaitConditionType.EMPTY_CARGO),
            targets=[],
        )
        assert s.interrupts == [
            Schedule.Interrupt(
                name="Interrupt!",
                conditions=[WaitCondition(WaitConditionType.FULL_CARGO)],
                targets=[],
            ),
            Schedule.Interrupt(
                name="Interrupt!",
                conditions=[WaitCondition(WaitConditionType.EMPTY_CARGO)],
                targets=[],
            ),
        ]

        s.remove_interrupt("Interrupt!")
        assert len(s.interrupts) == 1
        assert s.interrupts == [
            Schedule.Interrupt(
                name="Interrupt!",
                conditions=[WaitCondition(WaitConditionType.EMPTY_CARGO)],
                targets=[],
            )
        ]

        with pytest.raises(ValueError):
            s.remove_interrupt("DNE")

    def test_repr(self):
        s = Schedule()
        assert repr(s) == "Schedule(**{})"
