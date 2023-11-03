# test_constant_combinator.py

from draftsman.constants import Direction
from draftsman.entity import ConstantCombinator, constant_combinators, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalFilter
from draftsman.warning import PureVirtualDisallowedWarning, UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestConstantCombinator:
    def test_constructor_init(self):
        combinator = ConstantCombinator(
            "constant-combinator",
            tile_position=[0, 2],
            control_behavior={
                "filters": [("signal-A", 100), ("signal-B", 200), ("signal-C", 300)]
            },
        )
        assert combinator.to_dict() == {
            "name": "constant-combinator",
            "position": {"x": 0.5, "y": 2.5},
            "control_behavior": {
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    },
                    {
                        "index": 2,
                        "signal": {"name": "signal-B", "type": "virtual"},
                        "count": 200,
                    },
                    {
                        "index": 3,
                        "signal": {"name": "signal-C", "type": "virtual"},
                        "count": 300,
                    },
                ]
            },
        }

        combinator = ConstantCombinator(
            "constant-combinator",
            tile_position=[0, 2],
            control_behavior={
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    },
                    {"index": 2, "signal": "signal-B", "count": 200},
                    {
                        "index": 3,
                        "signal": {"name": "signal-C", "type": "virtual"},
                        "count": 300,
                    },
                ]
            },
        )
        assert combinator.to_dict() == {
            "name": "constant-combinator",
            "position": {"x": 0.5, "y": 2.5},
            "control_behavior": {
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    },
                    {
                        "index": 2,
                        "signal": {"name": "signal-B", "type": "virtual"},
                        "count": 200,
                    },
                    {
                        "index": 3,
                        "signal": {"name": "signal-C", "type": "virtual"},
                        "count": 300,
                    },
                ]
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            ConstantCombinator(unused_keyword="whatever")
        with pytest.warns(UnknownKeywordWarning):
            ConstantCombinator(control_behavior={"unused_key": "something"})
        with pytest.warns(UnknownEntityWarning):
            ConstantCombinator("this is not a constant combinator")

        # Errors
        with pytest.raises(DataFormatError):
            ConstantCombinator(control_behavior="incorrect")

    def test_flags(self):
        for name in constant_combinators:
            combinator = ConstantCombinator(name)
            assert combinator.power_connectable == False
            assert combinator.dual_power_connectable == False
            assert combinator.circuit_connectable == True
            assert combinator.dual_circuit_connectable == False

    def test_item_slot_count(self):
        combinator = ConstantCombinator()
        assert combinator.item_slot_count == 20

    def test_set_signal(self):
        combinator = ConstantCombinator()
        combinator.set_signal(0, "signal-A", 100)
        assert combinator.signals == [
            SignalFilter(
                index=1,
                signal="signal-A",
                count=100
            )
        ]
        
        combinator.set_signal(1, "signal-B", 200)
        assert combinator.signals == [
            SignalFilter(
                index=1,
                signal="signal-A",
                count=100
            ),
            SignalFilter(
                index=2,
                signal="signal-B",
                count=200
            )
        ]

        combinator.set_signal(0, "signal-C", 300)
        assert combinator.signals == [
            SignalFilter(
                index=1,
                signal="signal-C",
                count=300
            ),
            SignalFilter(
                index=2,
                signal="signal-B",
                count=200
            )
        ]

        combinator.set_signal(1, None)
        assert combinator.signals == [
            SignalFilter(
                index=1,
                signal="signal-C",
                count=300
            )
        ]

        with pytest.raises(TypeError): # TODO: FIXME
            combinator.set_signal(TypeError, "something")
        with pytest.raises(DataFormatError):
            combinator.set_signal(1, TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_signal(1, "iron-ore", TypeError)
        # with pytest.raises(DataFormatError): # TODO
        #     combinator.set_signal(-1, "iron-ore", 0)

    def test_set_signals(self):
        combinator = ConstantCombinator()
        # Test user format
        combinator.signals = [("signal-A", 100), ("signal-Z", 200), ("iron-ore", 1000)]
        assert combinator.signals == [
            SignalFilter(**{
                "index": 1,
                "signal": {"name": "signal-A", "type": "virtual"},
                "count": 100,
            }),
            SignalFilter(**{
                "index": 2,
                "signal": {"name": "signal-Z", "type": "virtual"},
                "count": 200,
            }),
            SignalFilter(**{
                "index": 3,
                "signal": {"name": "iron-ore", "type": "item"},
                "count": 1000,
            }),
        ]

        # Test internal format
        combinator.signals = [
            {
                "index": 1,
                "signal": {"name": "signal-A", "type": "virtual"},
                "count": 100,
            },
            {"index": 2, "signal": "signal-Z", "count": 200},
            {
                "index": 3,
                "signal": {"name": "iron-ore", "type": "item"},
                "count": 1000,
            },
        ]
        assert combinator.signals == [
            SignalFilter(**{
                "index": 1,
                "signal": {"name": "signal-A", "type": "virtual"},
                "count": 100,
            }),
            SignalFilter(**{
                "index": 2,
                "signal": {"name": "signal-Z", "type": "virtual"},
                "count": 200,
            }),
            SignalFilter(**{
                "index": 3,
                "signal": {"name": "iron-ore", "type": "item"},
                "count": 1000,
            }),
        ]

        # Test clear signals
        combinator.signals = None
        assert combinator.signals == None

        # Test setting to pure virtual raises Warnings
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.signals = [("signal-everything", 1)]
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.signals = [("signal-anything", 1)]
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.signals = [("signal-each", 1)]

        with pytest.raises(DataFormatError):
            combinator.signals = {"something", "wrong"}

    def test_get_signal(self):
        combinator = ConstantCombinator()
        signal = combinator.get_signal(0)
        assert signal == None

        combinator.signals = [("signal-A", 100), ("signal-Z", 200), ("iron-ore", 1000)]
        print(combinator.signals)
        signal = combinator.get_signal(0)
        assert signal == SignalFilter(**{
            "index": 1,
            "signal": {"name": "signal-A", "type": "virtual"},
            "count": 100,
        })

        signal = combinator.get_signal(50)
        assert signal == None

    def test_is_on(self):
        combinator = ConstantCombinator()
        assert combinator.is_on == True

        combinator.is_on = False
        assert combinator.is_on == False

        combinator.is_on = True
        assert combinator.is_on == True

        combinator.is_on = None
        assert combinator.is_on == None

        with pytest.raises(DataFormatError):
            combinator.is_on = "wrong"

        # Test fix for issue #77
        test_json = {
            "entity_number": 1,
            "name": "constant-combinator",
            "position": {"x": 155.5, "y": -108.5},
            "direction": 6,
            "control_behavior": {
                "filters": [
                    {
                        "signal": {"type": "item", "name": "stone"},
                        "count": 1,
                        "index": 1,
                    }
                ],
                "is_on": False,
            },
        }
        combinator = ConstantCombinator(**test_json)
        assert combinator.position.x == 155.5
        assert combinator.position.y == -108.5
        assert combinator.direction == Direction.WEST
        assert combinator.is_on == False

    def test_mergable_with(self):
        comb1 = ConstantCombinator("constant-combinator")
        comb2 = ConstantCombinator(
            "constant-combinator",
            control_behavior={
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    }
                ]
            },
        )

        assert comb1.mergable_with(comb2)
        assert comb2.mergable_with(comb1)

        comb2.tile_position = (1, 1)
        assert not comb1.mergable_with(comb2)

    def test_merge(self):
        comb1 = ConstantCombinator("constant-combinator")
        comb2 = ConstantCombinator(
            "constant-combinator",
            control_behavior={
                "filters": [
                    {
                        "index": 1,
                        "signal": {"name": "signal-A", "type": "virtual"},
                        "count": 100,
                    }
                ]
            },
        )

        print(comb1.control_behavior)
        print(comb2.control_behavior)

        comb1.merge(comb2)
        del comb2

        assert comb1.control_behavior == ConstantCombinator.Format.ControlBehavior(**{
            "filters": [
                {
                    "index": 1,
                    "signal": {"name": "signal-A", "type": "virtual"},
                    "count": 100,
                }
            ]
        })

    def test_eq(self):
        generator1 = ConstantCombinator("constant-combinator")
        generator2 = ConstantCombinator("constant-combinator")

        assert generator1 == generator2

        generator1.set_signal(0, "signal-check", 100)

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
