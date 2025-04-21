# test_constant_combinator.py

from draftsman.constants import Direction, ValidationMode
from draftsman.entity import ConstantCombinator, constant_combinators, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalFilter
from draftsman.warning import (
    PureVirtualDisallowedWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


class TestConstantCombinator:  # TODO: reimplement
    # def test_constructor_init(self):
    #     combinator = ConstantCombinator(
    #         "constant-combinator",
    #         tile_position=[0, 2],
    #         control_behavior={
    #             "filters": [("signal-A", 100), ("signal-B", 200), ("signal-C", 300)]
    #         },
    #     )
    #     assert combinator.to_dict() == {
    #         "name": "constant-combinator",
    #         "position": {"x": 0.5, "y": 2.5},
    #         "control_behavior": {
    #             "filters": [
    #                 {
    #                     "index": 1,
    #                     "signal": {"name": "signal-A", "type": "virtual"},
    #                     "count": 100,
    #                 },
    #                 {
    #                     "index": 2,
    #                     "signal": {"name": "signal-B", "type": "virtual"},
    #                     "count": 200,
    #                 },
    #                 {
    #                     "index": 3,
    #                     "signal": {"name": "signal-C", "type": "virtual"},
    #                     "count": 300,
    #                 },
    #             ]
    #         },
    #     }

    #     combinator = ConstantCombinator(
    #         "constant-combinator",
    #         tile_position=[0, 2],
    #         control_behavior={
    #             "filters": [
    #                 {
    #                     "index": 1,
    #                     "signal": {"name": "signal-A", "type": "virtual"},
    #                     "count": 100,
    #                 },
    #                 {"index": 2, "signal": "signal-B", "count": 200},
    #                 {
    #                     "index": 3,
    #                     "signal": {"name": "signal-C", "type": "virtual"},
    #                     "count": 300,
    #                 },
    #             ]
    #         },
    #     )
    #     assert combinator.to_dict() == {
    #         "name": "constant-combinator",
    #         "position": {"x": 0.5, "y": 2.5},
    #         "control_behavior": {
    #             "filters": [
    #                 {
    #                     "index": 1,
    #                     "signal": {"name": "signal-A", "type": "virtual"},
    #                     "count": 100,
    #                 },
    #                 {
    #                     "index": 2,
    #                     "signal": {"name": "signal-B", "type": "virtual"},
    #                     "count": 200,
    #                 },
    #                 {
    #                     "index": 3,
    #                     "signal": {"name": "signal-C", "type": "virtual"},
    #                     "count": 300,
    #                 },
    #             ]
    #         },
    #     }

    #     # Warnings
    #     with pytest.warns(UnknownKeywordWarning):
    #         ConstantCombinator(unused_keyword="whatever").validate().reissue_all()
    #     with pytest.warns(UnknownKeywordWarning):
    #         ConstantCombinator(control_behavior={"unused_key": "something"}).validate().reissue_all()
    #     with pytest.warns(UnknownEntityWarning):
    #         ConstantCombinator("this is not a constant combinator").validate().reissue_all()

    #     # Errors
    #     with pytest.raises(DataFormatError):
    #         ConstantCombinator(control_behavior="incorrect").validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in constant_combinators:
            combinator = ConstantCombinator(name)
            assert combinator.power_connectable == False
            assert combinator.dual_power_connectable == False
            assert combinator.circuit_connectable == True
            assert combinator.dual_circuit_connectable == False

    # def test_item_slot_count(self):
    #     combinator = ConstantCombinator()
    #     assert combinator.item_slot_count == 20

    # def test_set_signal(self):
    #     combinator = ConstantCombinator()
    #     combinator.set_signal(0, "signal-A", 100)
    #     assert combinator.signals == [
    #         SignalFilter(index=1, signal="signal-A", count=100)
    #     ]

    #     combinator.set_signal(1, "signal-B", 200)
    #     assert combinator.signals == [
    #         SignalFilter(index=1, signal="signal-A", count=100),
    #         SignalFilter(index=2, signal="signal-B", count=200),
    #     ]

    #     combinator.set_signal(0, "signal-C", 300)
    #     assert combinator.signals == [
    #         SignalFilter(index=1, signal="signal-C", count=300),
    #         SignalFilter(index=2, signal="signal-B", count=200),
    #     ]

    #     combinator.set_signal(1, None)
    #     assert combinator.signals == [
    #         SignalFilter(index=1, signal="signal-C", count=300)
    #     ]

    #     with pytest.raises(DataFormatError):
    #         combinator.set_signal(TypeError, "something")
    #     with pytest.raises(DataFormatError):
    #         combinator.set_signal(1, TypeError)
    #     with pytest.raises(DataFormatError):
    #         combinator.set_signal(1, "iron-ore", TypeError)
    #     # with pytest.raises(DataFormatError): # TODO: is this an error?
    #     #     combinator.set_signal(-1, "iron-ore", 0)

    #     assert combinator.item_slot_count == 20
    #     with pytest.raises(DataFormatError):
    #         combinator.set_signal(100, "iron-ore", 1000)

    #     combinator = ConstantCombinator("unknown-combinator", validate="none")
    #     assert combinator.item_slot_count == None
    #     combinator.set_signal(100, "iron-ore", 1000)
    #     assert combinator.signals == [
    #         SignalFilter(index=101, signal="iron-ore", count=1000)
    #     ]

    # def test_set_signals(self):
    #     combinator = ConstantCombinator()
    #     # Test user format
    #     combinator.signals = [("signal-A", 100), ("signal-Z", 200), ("iron-ore", 1000)]
    #     assert combinator.signals == [
    #         SignalFilter(
    #             **{
    #                 "index": 1,
    #                 "signal": {"name": "signal-A", "type": "virtual"},
    #                 "count": 100,
    #             }
    #         ),
    #         SignalFilter(
    #             **{
    #                 "index": 2,
    #                 "signal": {"name": "signal-Z", "type": "virtual"},
    #                 "count": 200,
    #             }
    #         ),
    #         SignalFilter(
    #             **{
    #                 "index": 3,
    #                 "signal": {"name": "iron-ore", "type": "item"},
    #                 "count": 1000,
    #             }
    #         ),
    #     ]

    #     # Test internal format
    #     combinator.signals = [
    #         {
    #             "index": 1,
    #             "signal": {"name": "signal-A", "type": "virtual"},
    #             "count": 100,
    #         },
    #         {"index": 2, "signal": "signal-Z", "count": 200},
    #         {
    #             "index": 3,
    #             "signal": {"name": "iron-ore", "type": "item"},
    #             "count": 1000,
    #         },
    #     ]
    #     assert combinator.signals == [
    #         SignalFilter(
    #             **{
    #                 "index": 1,
    #                 "signal": {"name": "signal-A", "type": "virtual"},
    #                 "count": 100,
    #             }
    #         ),
    #         SignalFilter(
    #             **{
    #                 "index": 2,
    #                 "signal": {"name": "signal-Z", "type": "virtual"},
    #                 "count": 200,
    #             }
    #         ),
    #         SignalFilter(
    #             **{
    #                 "index": 3,
    #                 "signal": {"name": "iron-ore", "type": "item"},
    #                 "count": 1000,
    #             }
    #         ),
    #     ]

    #     # Test clear signals
    #     combinator.signals = None
    #     assert combinator.signals == None

    #     # Test setting to pure virtual raises Warnings
    #     with pytest.warns(PureVirtualDisallowedWarning):
    #         combinator.signals = [("signal-everything", 1)]
    #     with pytest.warns(PureVirtualDisallowedWarning):
    #         combinator.signals = [("signal-anything", 1)]
    #     with pytest.warns(PureVirtualDisallowedWarning):
    #         combinator.signals = [("signal-each", 1)]

    #     with pytest.raises(DataFormatError):
    #         combinator.signals = {"something", "wrong"}

    #     combinator.validate_assignment = "none"
    #     assert combinator.validate_assignment == ValidationMode.NONE

    #     combinator.signals = {"something", "wrong"}
    #     assert combinator.signals == {"something", "wrong"}
    #     assert combinator.to_dict() == {
    #         "name": "constant-combinator",
    #         "position": {"x": 0.5, "y": 0.5},
    #         "control_behavior": {"filters": {"something", "wrong"}},
    #     }

    # def test_get_signal(self):
    #     combinator = ConstantCombinator()

    #     section = combinator.add_section()
    #     section.filters = [
    #         SignalFilter(**{
    #             "index": 1,
    #             "name": "signal-A",
    #             "type": "virtual",
    #             "comparator": "=",
    #             "count": 100,
    #             "max_count": 100
    #         })
    #     ]

    #     print(section.filters)

    #     signal = section.get_signal(0)
    #     assert signal == SignalFilter(
    #         **{
    #             "index": 1,
    #             "name": "signal-A",
    #             "type": "virtual",
    #             "comparator": "=",
    #             "count": 100,
    #             "max_count": 100
    #         }
    #     )

    #     signal = section.get_signal(50)
    #     assert signal == None

    # def test_is_on(self):
    #     combinator = ConstantCombinator()
    #     assert combinator.is_on == True

    #     combinator.is_on = False
    #     assert combinator.is_on == False

    #     combinator.is_on = True
    #     assert combinator.is_on == True

    #     combinator.is_on = None
    #     assert combinator.is_on == None

    #     with pytest.raises(DataFormatError):
    #         combinator.is_on = "wrong"

    #     # Test fix for issue #77
    #     test_json = {
    #         "entity_number": 1,
    #         "name": "constant-combinator",
    #         "position": {"x": 155.5, "y": -108.5},
    #         "direction": Direction.WEST,
    #         "control_behavior": {
    #             "filters": [
    #                 {
    #                     "signal": {"type": "item", "name": "stone"},
    #                     "count": 1,
    #                     "index": 1,
    #                 }
    #             ],
    #             "is_on": False,
    #         },
    #     }
    #     combinator = ConstantCombinator(**test_json)
    #     assert combinator.position.x == 155.5
    #     assert combinator.position.y == -108.5
    #     assert combinator.direction == Direction.WEST
    #     assert combinator.is_on == False

    #     combinator = ConstantCombinator("constant-combinator")

    #     combinator.validate_assignment = "none"
    #     assert combinator.validate_assignment == ValidationMode.NONE

    #     combinator.is_on = "incorrect"
    #     assert combinator.is_on == "incorrect"
    #     assert combinator.to_dict() == {
    #         "name": "constant-combinator",
    #         "position": {"x": 0.5, "y": 0.5},
    #         "control_behavior": {"is_on": "incorrect"},
    #     }

    # def test_mergable_with(self):
    #     comb1 = ConstantCombinator("constant-combinator")
    #     comb2 = ConstantCombinator(
    #         "constant-combinator",
    #         control_behavior={
    #             "filters": [
    #                 {
    #                     "index": 1,
    #                     "signal": {"name": "signal-A", "type": "virtual"},
    #                     "count": 100,
    #                 }
    #             ]
    #         },
    #     )

    #     assert comb1.mergable_with(comb2)
    #     assert comb2.mergable_with(comb1)

    #     comb2.tile_position = (1, 1)
    #     assert not comb1.mergable_with(comb2)

    # def test_merge(self):
    #     comb1 = ConstantCombinator("constant-combinator")
    #     comb2 = ConstantCombinator(
    #         "constant-combinator",
    #         control_behavior={
    #             "sections": {
    #                 "sections": [
    #                     {
    #                         "index": 1,
    #                         "filters": [
    #                             {
    #                                 "index": 1,
    #                                 "name": "signal-A",
    #                                 "type": "virtual",
    #                                 "count": 100,
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         },
    #     )

    #     comb1.merge(comb2)
    #     del comb2

    #     assert comb1.control_behavior == ConstantCombinator.Format.ControlBehavior(
    #         **{
    #             "sections": {
    #                 "sections": [
    #                     {
    #                         "index": 1,
    #                         "filters": [
    #                             {
    #                                 "index": 1,
    #                                 "name": "signal-A",
    #                                 "type": "virtual",
    #                                 "count": 100,
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         }
    #     )

    def test_issue_158(self):
        cc = ConstantCombinator(
            id="doesnt-import",
            tile_position=(0, 0),
            control_behavior={
                "sections": {
                    "sections": [
                        {
                            "index": 1,
                            "filters": [
                                {
                                    "index": 1,
                                    "type": "item",
                                    "name": "iron-plate",
                                    "quality": "normal",
                                    "comparator": "=",
                                    "count": 1,
                                }
                            ],
                        }
                    ]
                }
            },
        )
        assert cc.to_dict() == {
            "name": "constant-combinator",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {},
            "control_behavior": {
                "sections": {
                    "sections": [
                        {
                            "index": 1,
                            "filters": [
                                {
                                    "index": 1,
                                    "name": "iron-plate",
                                    "quality": "normal",
                                    "comparator": "=",  # Must exist, otherwise error
                                    "count": 1,
                                }
                            ],
                        }
                    ]
                }
            },
        }

    def test_eq(self):
        cc1 = ConstantCombinator("constant-combinator")
        cc2 = ConstantCombinator("constant-combinator")

        assert cc1 == cc2

        section = cc1.add_section()
        section.set_signal(0, "signal-check", 100)

        assert cc1 != cc2

        container = Container()

        assert cc1 != container
        assert cc2 != container

        # hashable
        assert isinstance(cc1, Hashable)
