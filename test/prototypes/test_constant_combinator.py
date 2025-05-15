# test_constant_combinator.py

from draftsman.constants import Direction, ValidationMode
from draftsman.entity import ConstantCombinator, constant_combinators, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalFilter, ManualSection
from draftsman.warning import (
    PureVirtualDisallowedWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_constant_combinator():
    if len(constant_combinators) == 0:
        return None
    return ConstantCombinator(
        "constant-combinator",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        enabled=False,
        sections=[
            ManualSection(
                index=1, filters=[SignalFilter(index=1, name="signal-A", count=1000)]
            )
        ],
        player_description="test",
        tags={"blah": "blah"},
    )


class TestConstantCombinator:
    def test_constructor_init(self):
        combinator = ConstantCombinator(
            "constant-combinator",
            tile_position=[0, 2],
            sections=[
                {
                    "index": 1,
                    "filters": [
                        ("signal-A", 100),
                        ("signal-B", 200),
                        ("signal-C", 300),
                    ],
                }
            ],
        )
        print(combinator.to_dict())
        assert combinator.to_dict() == {
            "name": "constant-combinator",
            "position": {"x": 0.5, "y": 2.5},
            "control_behavior": {
                "sections": {
                    "sections": [
                        {
                            "index": 1,
                            "filters": [
                                {
                                    "index": 1,
                                    "name": "signal-A",
                                    "type": "virtual",
                                    "count": 100,
                                    "comparator": "=",
                                },
                                {
                                    "index": 2,
                                    "name": "signal-B",
                                    "type": "virtual",
                                    "count": 200,
                                    "comparator": "=",
                                },
                                {
                                    "index": 3,
                                    "name": "signal-C",
                                    "type": "virtual",
                                    "count": 300,
                                    "comparator": "=",
                                },
                            ],
                        }
                    ]
                }
            },
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            ConstantCombinator(
                "this is not a constant combinator"
            ).validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            ConstantCombinator(sections="incorrect").validate().reissue_all()

    def test_json_schema(self):
        assert ConstantCombinator.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:constant-combinator",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {
                "circuit-connection-point": {
                    "type": "object",
                    "properties": {
                        "entity_id": {"$ref": "urn:uint64"},
                        "circuit_id": {"enum": [1, 2]},
                    },
                    "required": ["entity_id"],
                },
                "wire-connection-point": {
                    "properties": {
                        "entity_id": {"$ref": "urn:uint64"},
                        "wire_id": {"enum": [0, 1]},
                    },
                    "required": ["entity_id"],
                },
            },
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {
                    "$ref": "urn:factorio:position",
                },
                "direction": {"enum": list(range(8)), "default": 0},
                "connections": {
                    "type": "object",
                    "properties": {
                        "1": {
                            "type": "object",
                            "properties": {
                                "red": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/$defs/circuit-connection-point"
                                    },
                                },
                                "green": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/$defs/circuit-connection-point"
                                    },
                                },
                            },
                        },
                        "2": {
                            "type": "object",
                            "properties": {
                                "red": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/$defs/circuit-connection-point"
                                    },
                                },
                                "green": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/$defs/circuit-connection-point"
                                    },
                                },
                            },
                        },
                        "Cu0": {
                            "type": "array",
                            "items": {"$ref": "#/$defs/wire-connection-point"},
                        },
                        "Cu1": {
                            "type": "array",
                            "items": {"$ref": "#/$defs/wire-connection-point"},
                        },
                    },
                },
                "control_behavior": {
                    "type": "object",
                    "properties": {
                        "is_on": {"type": "boolean", "default": "true"},
                        "filters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "index": {"$ref": "urn:uint32"},
                                    "signal": {"$ref": "urn:factorio:signal-id"},
                                    "count": {"$ref": "urn:int32"},
                                },
                            },
                        },
                    },
                    "description": "Entity-specific structure which holds keys related to configuring how this entity acts.",
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }
        assert ConstantCombinator.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:constant-combinator",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {
                    "$ref": "urn:factorio:position",
                },
                "quality": {"$ref": "urn:factorio:quality-name"},
                "direction": {"enum": list(range(16)), "default": 0},
                "control_behavior": {
                    "type": "object",
                    "properties": {
                        "is_on": {"type": "boolean", "default": "true"},
                        "sections": {
                            "type": "object",
                            "properties": {
                                "sections": {
                                    "type": "array",
                                    "items": {"$ref": "urn:factorio:manual-section"},
                                }
                            },
                        },
                    },
                    "description": "Entity-specific structure which holds keys related to configuring how this entity acts.",
                },
                "player_description": {"type": "string"},
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }

    def test_power_and_circuit_flags(self):
        for name in constant_combinators:
            combinator = ConstantCombinator(name)
            assert combinator.power_connectable == False
            assert combinator.dual_power_connectable == False
            assert combinator.circuit_connectable == True
            assert combinator.dual_circuit_connectable == False

    def test_max_signal_count(self):
        combinator = ConstantCombinator()
        assert combinator.max_signal_count == 100_000

    def test_add_section(self):
        combinator = ConstantCombinator()

        combinator.add_section(group="Some group name", index=2)
        assert combinator.to_dict() == {
            "name": combinator.name,
            "position": combinator.position.to_dict(),
            "control_behavior": {
                "sections": {
                    "sections": [
                        {
                            "index": 3,
                            "group": "Some group name",
                        }
                    ]
                }
            },
        }

        with pytest.raises(IndexError):
            combinator.add_section(index=100)

    def test_set_signal(self):
        combinator = ConstantCombinator()
        section = combinator.add_section()
        section.set_signal(0, "signal-A", 100)
        assert section.filters == [
            SignalFilter(index=1, name="signal-A", count=100, quality="normal")
        ]

        section.set_signal(1, "signal-B", 200)
        assert section.filters == [
            SignalFilter(index=1, name="signal-A", count=100, quality="normal"),
            SignalFilter(index=2, name="signal-B", count=200, quality="normal"),
        ]

        section.set_signal(0, "signal-C", 300)
        assert section.filters == [
            SignalFilter(index=1, name="signal-C", count=300, quality="normal"),
            SignalFilter(index=2, name="signal-B", count=200, quality="normal"),
        ]

        section.set_signal(1, None)
        assert section.filters == [
            SignalFilter(index=1, name="signal-C", count=300, quality="normal")
        ]

        with pytest.raises(TypeError):
            section.set_signal(TypeError, "something")
        with pytest.raises(DataFormatError):
            section.set_signal(1, TypeError)
        with pytest.raises(DataFormatError):
            section.set_signal(1, "iron-ore", TypeError)
        # with pytest.raises(DataFormatError): # TODO: is this an error?
        #     combinator.set_signal(-1, "iron-ore", 0)

        assert combinator.max_signal_count == 100_000

        # 1.0 limitation
        # with pytest.raises(DataFormatError):
        #     combinator.set_signal(100, "iron-ore", 1000)

        # 1.0 limitation
        # combinator = ConstantCombinator("unknown-combinator", validate="none")
        # assert combinator.item_slot_count == None
        # combinator.set_signal(100, "iron-ore", 1000)
        # assert combinator.signals == [
        #     SignalFilter(index=101, signal="iron-ore", count=1000)
        # ]

        with pytest.raises(DataFormatError):
            section.filters = "incorrect thingy"

    def test_get_signal(self):
        combinator = ConstantCombinator()

        section = combinator.add_section()
        section.filters = [
            SignalFilter(
                **{
                    "index": 1,
                    "name": "signal-A",
                    "type": "virtual",
                    "comparator": "=",
                    "count": 100,
                    "max_count": 100,
                }
            )
        ]

        print(section.filters)

        signal = section.get_signal(0)
        assert signal == SignalFilter(
            **{
                "index": 1,
                "name": "signal-A",
                "type": "virtual",
                "comparator": "=",
                "count": 100,
                "max_count": 100,
            }
        )

        signal = section.get_signal(50)
        assert signal == None

    def test_issue_158(self):
        cc = ConstantCombinator(
            id="doesnt-import",
            tile_position=(0, 0),
            sections=[
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
            ],
        )
        assert cc.to_dict() == {
            "name": "constant-combinator",
            "position": {"x": 0.5, "y": 0.5},
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
