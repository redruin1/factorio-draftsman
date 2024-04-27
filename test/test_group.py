# test_group.py

from draftsman import __factorio_version_info__
from draftsman.classes.association import Association
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.entity_list import EntityList
from draftsman.classes.group import Group
from draftsman.classes.schedule import Schedule, WaitCondition, WaitConditions
from draftsman.classes.schedule_list import ScheduleList
from draftsman.classes.vector import Vector
from draftsman.constants import Direction, WaitConditionType
from draftsman.entity import *
from draftsman.error import (
    DraftsmanError,
    DataFormatError,
    InvalidWireTypeError,
    InvalidConnectionSideError,
    EntityNotPowerConnectableError,
    EntityNotCircuitConnectableError,
    RotationError,
    InvalidAssociationError,
    MalformedBlueprintStringError,
    IncorrectBlueprintTypeError,
)
from draftsman.signatures import Connections
from draftsman.utils import encode_version, AABB
from draftsman.warning import (
    ConnectionSideWarning,
    ConnectionDistanceWarning,
    GridAlignmentWarning,
    OverlappingObjectsWarning,
)

import pytest


class TestGroup:
    def test_default_constructor(self):
        group = Group("default")
        assert group.id == "default"
        assert group.name == "group"
        assert group.type == "group"
        assert group.get() == []

    def test_constructor_init(self):
        entity_list = [
            Furnace("stone-furnace"),
            Container("wooden-chest", tile_position=(4, 0)),
            ProgrammableSpeaker("programmable-speaker", tile_position=(8, 0)),
        ]
        group = Group(
            name="groupA",
            type="custom_type",
            id="test_group",
            position={"x": 124.4, "y": 1.645},
            entities=entity_list,
        )
        assert group.name == "groupA"
        assert group.type == "custom_type"
        assert group.id == "test_group"
        assert group.position == Vector(124.4, 1.645)

        # Initialize from string with entities
        test_string = "0eNqdkttqwzAMht9F187IwVk23/YxSig5aK0gcYLtLAvB7z45ZaW0gbHdGNn6/euT0Ap1N+FoSDtQK1AzaAvquIKls6668OaWEUEBOexBgK76cDNVWxnwAki3+AUq8aUA1I4c4dVguywnPfU1GhY8fBUwDpbVgw412CHNXnIBC6iIA+/Fk0N6cxiHGU1kZ3LNZc9os4kZjrvR2IScDcnDFN+jUQuKtTMZ3OI49HCYkl807HstfbKucszzUXUWd4CzG3CPLU19hB3DGGqicehwBzz9mUDCE3iiT8JhsH3Ek4zEao10vtTDZML4ZbnDI//Kk/2LJ9vhycow222F1N3GCfhEY7eK6Vsii/e0yHMp8+LV+2+Mw9xY"
        group = Group(name="test", position=(1, 1), string=test_string)
        assert group.name == "test"
        assert group.type == "group"
        assert group.id == None
        assert group.position == Vector(1.0, 1.0)
        # Verify contents
        assert len(group.entities) == 4
        assert isinstance(group.entities[0], Radar)
        assert isinstance(group.entities[1], PowerSwitch)
        assert isinstance(group.entities[2], ElectricPole)
        assert isinstance(group.entities[3], ElectricPole)
        assert (
            group.entities[2].connections["1"]["red"][0]["entity_id"]()
            is group.entities[3]
        )
        assert (
            group.entities[3].connections["1"]["red"][0]["entity_id"]()
            is group.entities[2]
        )
        assert group.entities[2].neighbours[0]() is group.entities[3]
        assert group.entities[3].neighbours[0]() is group.entities[2]

        # Initialize from blueprint string with entities and schedules
        test_string_with_schedules = "0eNqVk91uwjAMhd/F1xmiLf2928WeYkIotB5Ya5MqSdkQ6rvPIWxFiImi3NSNz+c4OT7Bth2wN6QcVCegWisL1fsJLO2UbP0/d+wRKiCHHQhQsvORkdTCKIBUg99QRaN4KGl1rTvt6IBXwnhcC0DlyBGGwufguFFDt0XD5Ht6Ab22LNHKV2PMS5SUizSLUwFHqMqcC2hDjJIhabnIU3/EG3j8B7eOO9rt3cu5sTv8VTKhGzJYh934DjV5ghrNpq7mU5NyNjV9gprPpmZPUNN/qOwLW++xGdqLMab393F0tR8M+/vW8PqmHBr2tPVO+ZLkNmzr5lw3oBjUS4Obi0+14bzLt6POqxzVn5wbFcul7+9GIFUzKUhJPvSB+590yWPZx9DyBK39EmFSqqtZFHBAY8NVFNEqL+M8y9IiK4px/AGk8DmW"
        group = Group(name="test", position=(2, 2), string=test_string_with_schedules)
        assert group.name == "test"
        assert group.type == "group"
        assert group.id == None
        assert group.position == Vector(2.0, 2.0)
        assert len(group.entities) == 6
        assert group.entities == EntityList(
            initlist=[
                Locomotive("locomotive", position=(-137.5625, 99.0), orientation=0.75),
                StraightRail(
                    "straight-rail", position=(-141, 99), direction=Direction.EAST
                ),
                StraightRail(
                    "straight-rail", position=(-139, 99), direction=Direction.EAST
                ),
                StraightRail(
                    "straight-rail", position=(-137, 99), direction=Direction.EAST
                ),
                StraightRail(
                    "straight-rail", position=(-135, 99), direction=Direction.EAST
                ),
                StraightRail(
                    "straight-rail", position=(-133, 99), direction=Direction.EAST
                ),
            ]
        )
        assert len(group.schedules) == 1
        assert group.schedules[0].locomotives[0]() is group.entities[0]
        assert group.schedules[0].stops == [
            Schedule.Format.Stop(
                **{
                    "station": "AEnterprise",
                    "wait_conditions": WaitConditions(
                        [
                            WaitCondition(type="time", compare_type="or", ticks=1800),
                            WaitCondition(
                                type="inactivity", compare_type="and", ticks=300
                            ),
                            WaitCondition(type="full", compare_type="and"),
                        ]
                    ),
                }
            )
        ]

        # Initialize from blueprint string with no entities
        empty_blueprint_string = "0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTUxMTU3q60FAHmbE1Y="
        group = Group(string=empty_blueprint_string)
        assert len(group.entities) == 0
        assert group.entities._root == []

        # Errors
        with pytest.raises(TypeError):
            Group(unused_keyword="whatever")

        with pytest.raises(TypeError):
            Group(name=TypeError)

        with pytest.raises(TypeError):
            Group(type=TypeError)

        with pytest.raises(TypeError):
            Group(id=TypeError)

        with pytest.raises(TypeError):
            Group(position="incorrect")

        with pytest.raises(TypeError):  # TODO: maybe change this?
            Group(entities=InvalidEntityError)

        with pytest.raises(TypeError):
            Group("test", entities=["incorrect"])

        with pytest.raises(MalformedBlueprintStringError):
            Group(string="incorrect")
        with pytest.raises(IncorrectBlueprintTypeError):
            Group(
                string="0eNqrVkrKKU0tKMrMK4lPys/PVrKqRogUK1lFI3FBcpklqblKVkhiOkplqUXFmfl5SlZGFoYm5pZG5qamJiam5ma1OkqZeSmpFUpWBrWxOhg6dcHW6SglJpdklqXGw5TiMa8WAEeOOPY="
            )

    def test_set_name(self):
        group = Group("test")
        group.name = "something other than group"
        assert group.name == "something other than group"

        with pytest.raises(TypeError):
            group.name = None
        with pytest.raises(TypeError):
            group.name = TypeError

    def test_set_type(self):
        group = Group("test")
        group.type = "something other than group"
        assert group.type == "something other than group"

        with pytest.raises(TypeError):
            group.type = None
        with pytest.raises(TypeError):
            group.type = TypeError

    def test_set_id(self):
        group = Group("test")
        group.id = "something else"
        assert group.id == "something else"

        group.id = None
        assert group.id == None

        with pytest.raises(TypeError):
            group.id = TypeError

        # Test key map modification
        blueprint = Blueprint()
        blueprint.entities.append(group)

        blueprint.entities[0].id = "another_thing"
        assert blueprint.entities[0].id == "another_thing"
        assert blueprint.entities[0] is blueprint.entities["another_thing"]

        # Test key map removal on set to None
        blueprint.entities[0].id = None
        assert blueprint.entities[0].id == None
        assert not ("another_thing" in blueprint.entities)

    def test_set_position(self):
        group = Group("test")
        group.position = (10, 10)
        assert group.position == Vector(10.0, 10.0)
        group.position = {"x": 1.5, "y": 2.5}
        assert group.position == Vector(1.5, 2.5)

        blueprint = Blueprint()
        blueprint.entities.append(group)

        with pytest.raises(DraftsmanError):
            blueprint.entities[0].position = (1, 1)

    def test_set_collision_mask(self):
        group = Group("test")
        group.collision_mask = {"entities", "something-else"}
        assert group.collision_mask == {"entities", "something-else"}
        group.collision_mask = None
        assert group.collision_mask == set()

        with pytest.raises(TypeError):
            group.collision_mask = TypeError

    def test_set_entities(self):
        group = Group("test")
        # List case
        group.entities = [
            Furnace("stone-furnace"),
            Container("wooden-chest", tile_position=(4, 0)),
            ProgrammableSpeaker("programmable-speaker", tile_position=(8, 0)),
        ]
        assert isinstance(group.entities, EntityList)
        # None case
        group.entities = None
        assert isinstance(group.entities, EntityList)
        assert group.entities._root == []
        # EntityList case
        group2 = Group("test2")
        group2.entities = group.entities
        assert isinstance(group2.entities, EntityList)
        assert group2.entities._root == []

        group.entities = [
            Furnace("stone-furnace"),
            Container("wooden-chest", tile_position=(4, 0)),
            ProgrammableSpeaker("programmable-speaker", tile_position=(8, 0)),
        ]
        group2.entities = group.entities
        assert isinstance(group2.entities, EntityList)
        assert group2.entities is not group.entities

        with pytest.raises(TypeError):
            group2.entities = TypeError
        with pytest.raises(TypeError):
            group2.entities = [TypeError]

    def test_insert_entity(self):
        group = Group("test")
        substation1 = ElectricPole("substation", id="A")
        substation2 = ElectricPole("substation", tile_position=(10, 10), id="B")
        power_switch = PowerSwitch("power-switch", tile_position=(5, 5), id="C")
        # substation1.add_power_connection(substation2)
        # substation2.add_circuit_connection("red", substation1)
        # power_switch.add_power_connection(substation2, 2)

        group.entities.append(substation1)
        group.entities.append(substation2)
        group.entities.append(power_switch)

        group.add_power_connection("A", "B")
        group.add_circuit_connection("red", "A", "B")
        group.add_power_connection("C", "B", 2)

        # Ensure that associations remain correct (global)
        assert group.entities[0].to_dict() == {
            "name": "substation",
            "position": {"x": 1.0, "y": 1.0},
            "neighbours": [Association(group.entities["B"])],
            "connections": {
                "1": {"red": [{"entity_id": Association(group.entities["B"])}]}
            },
        }
        assert group.entities[1].to_dict() == {
            "name": "substation",
            "position": {"x": 11.0, "y": 11.0},
            "neighbours": [Association(group.entities["A"])],
            "connections": {
                "1": {"red": [{"entity_id": Association(group.entities["A"])}]},
            },
        }
        assert group.entities[2].to_dict() == {
            "name": "power-switch",
            "position": {"x": 6.0, "y": 6.0},
            "connections": {
                "Cu1": [{"entity_id": Association(group.entities["B"]), "wire_id": 0}]
            },
        }

        # Ensure that popping resolves associations in the returned entities

        with pytest.raises(TypeError):
            group.entities.append(TypeError)

    def test_set_entity(self):
        group = Group("test")
        group.entities.append(Furnace(id="A"))
        assert isinstance(group.entities["A"], Furnace)
        assert group.entities["A"] is group.entities[0]

        group.entities[0] = Container(id="B")
        assert isinstance(group.entities[0], Container)
        assert group.entities["B"] is group.entities[0]

        with pytest.raises(KeyError):
            group.entities["A"]

    def test_remove_entity(self):
        group = Group("test")
        container_1 = Container("steel-chest", id="A")
        container_2 = Container("steel-chest", tile_position=(3, 0), id="B")
        group.entities.append(container_1)
        group.entities.append(container_2)
        group.add_circuit_connection("red", "A", "B")

        assert group.entities[0].to_dict() == {
            "name": "steel-chest",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {
                "1": {"red": [{"entity_id": Association(group.entities[1])}]}
            },
        }
        result = group.entities.pop()
        assert result.to_dict() == {
            "name": "steel-chest",
            "position": {"x": 3.5, "y": 0.5},
            "connections": {
                "1": {"red": [{"entity_id": Association(group.entities[0])}]}
            },
        }

    def test_set_schedules(self):
        # Regular list
        group = Group()
        group.schedules = []
        assert isinstance(group.schedules, ScheduleList)

        group.entities.append("locomotive", id="test_train")

        # ScheduleList
        schedule = Schedule()
        schedule.add_locomotive(group.entities["test_train"])
        schedule.append_stop("station_name", WaitCondition("inactivity", ticks=600))
        group.schedules = ScheduleList([schedule])
        assert isinstance(group.schedules, ScheduleList)
        assert group.schedules[0].locomotives[0]() is group.entities[0]
        assert group.schedules[0].stops == [
            Schedule.Format.Stop(
                **{
                    "station": "station_name",
                    "wait_conditions": WaitConditions(
                        [WaitCondition("inactivity", ticks=600)]
                    ),
                }
            )
        ]

        # None
        group.schedules = None
        assert isinstance(group.schedules, ScheduleList)
        assert group.schedules == ScheduleList()
        assert len(group.schedules) == 0

        with pytest.raises(TypeError):
            group.schedules = dict()

        with pytest.raises(DataFormatError):
            group.schedules = ["incorrect", "format"]

    def test_power_connections(self):
        group = Group("test")
        substation1 = ElectricPole("substation", id="1")
        substation2 = ElectricPole("substation", id="2", tile_position=(2, 0))
        power_switch = PowerSwitch(id="p", tile_position=(4, 0))
        group.entities = [substation1, substation2, power_switch]

        # Normal operation
        group.add_power_connection("1", "2")
        assert group.entities["1"].neighbours == [Association(group.entities["2"])]
        assert group.entities["2"].neighbours == [Association(group.entities["1"])]
        # Inverse, but redundant case
        group.add_power_connection("2", "1")
        assert group.entities["1"].neighbours == [Association(group.entities["2"])]
        assert group.entities["2"].neighbours == [Association(group.entities["1"])]

        # Dual power connectable case
        group.add_power_connection("1", "p")
        assert group.entities["1"].neighbours == [Association(group.entities["2"])]
        assert group.entities["p"].to_dict()["connections"] == {
            "Cu0": [{"entity_id": Association(group.entities["1"]), "wire_id": 0}]
        }
        # Inverse, but redundant case
        group.add_power_connection("p", "1")
        assert group.entities["1"].neighbours == [Association(group.entities["2"])]
        assert group.entities["p"].to_dict()["connections"] == {
            "Cu0": [{"entity_id": Association(group.entities["1"]), "wire_id": 0}]
        }
        # Redundant case
        group.add_power_connection("2", "p")
        group.add_power_connection("2", "p")
        assert group.entities["2"].neighbours == [Association(group.entities["1"])]
        assert group.entities["p"].to_dict()["connections"] == {
            "Cu0": [
                {"entity_id": Association(group.entities["1"]), "wire_id": 0},
                {"entity_id": Association(group.entities["2"]), "wire_id": 0},
            ]
        }
        group.add_power_connection("p", "2", side=2)
        assert group.entities["p"].to_dict()["connections"] == {
            "Cu0": [
                {"entity_id": Association(group.entities["1"]), "wire_id": 0},
                {"entity_id": Association(group.entities["2"]), "wire_id": 0},
            ],
            "Cu1": [{"entity_id": Association(group.entities["2"]), "wire_id": 0}],
        }

        # Warnings
        with pytest.warns(ConnectionDistanceWarning):
            other = ElectricPole(position=[100, 0], id="other")
            group.entities.append(other)
            group.add_power_connection("1", "other")

        # Errors
        with pytest.raises(EntityNotPowerConnectableError):
            group.entities.append(
                "transport-belt", id="whatever", tile_position=(10, 0)
            )
            group.add_power_connection("whatever", "2")

        with pytest.raises(DraftsmanError):
            group.entities.append("power-switch", id="p2", tile_position=(0, 10))
            group.add_power_connection("p", "p2")

        # Make sure correct even after errors
        assert group.entities["1"].neighbours == [
            Association(group.entities["2"]),
            Association(group.entities["other"]),
        ]
        assert group.entities["p"].to_dict()["connections"] == {
            "Cu0": [
                {"entity_id": Association(group.entities["1"]), "wire_id": 0},
                {"entity_id": Association(group.entities["2"]), "wire_id": 0},
            ],
            "Cu1": [{"entity_id": Association(group.entities["2"]), "wire_id": 0}],
        }

        # Test removing
        # Redundant case
        group.remove_power_connection("1", "2")
        group.remove_power_connection("1", "2")
        assert group.entities["1"].neighbours == [Association(group.entities["other"])]
        assert group.entities["2"].neighbours == []

        # Remove power switch connection that does not exist
        group.remove_power_connection("1", "p")
        group.remove_power_connection("1", "p")
        assert group.entities["1"].neighbours == [Association(group.entities["other"])]
        assert group.entities["p"].to_dict()["connections"] == {
            "Cu0": [{"entity_id": Association(group.entities["2"]), "wire_id": 0}],
            "Cu1": [{"entity_id": Association(group.entities["2"]), "wire_id": 0}],
        }

        group.add_power_connection("1", "p")
        group.remove_power_connection("p", "2", side=1)
        group.remove_power_connection("p", "2", side=1)
        group.remove_power_connection("p", "1")
        group.remove_power_connection("p", "1")
        assert group.entities["p"].to_dict()["connections"] == {
            "Cu1": [{"entity_id": Association(group.entities["2"]), "wire_id": 0}]
        }
        group.remove_power_connection("2", "p", 2)
        group.remove_power_connection("2", "p", 2)
        assert power_switch.connections == Connections()

        # TODO: test setting connection by reference

    def test_add_circuit_connection(self):
        group = Group("test")
        container1 = Container("steel-chest", id="c1", tile_position=[-1, 0])
        container2 = Container("steel-chest", id="c2", tile_position=[1, 0])
        group.entities.append(container1)
        group.entities.append(container2)

        group.add_circuit_connection("red", "c1", "c2")
        assert group.entities["c1"].to_dict() == {
            "name": "steel-chest",
            "position": {"x": -0.5, "y": 0.5},
            "connections": {
                "1": {"red": [{"entity_id": Association(group.entities["c2"])}]}
            },
        }
        assert group.entities["c2"].to_dict() == {
            "name": "steel-chest",
            "position": {"x": 1.5, "y": 0.5},
            "connections": {
                "1": {"red": [{"entity_id": Association(group.entities["c1"])}]}
            },
        }
        # Test duplicate connection
        group.add_circuit_connection("red", "c1", "c2")
        assert group.entities["c1"].to_dict() == {
            "name": "steel-chest",
            "position": {"x": -0.5, "y": 0.5},
            "connections": {
                "1": {"red": [{"entity_id": Association(group.entities["c2"])}]}
            },
        }
        assert group.entities["c2"].to_dict() == {
            "name": "steel-chest",
            "position": {"x": 1.5, "y": 0.5},
            "connections": {
                "1": {"red": [{"entity_id": Association(group.entities["c1"])}]}
            },
        }

        # set_connections to None
        group.entities["c1"].connections = {}
        assert group.entities["c1"].connections == Connections()

        # Test when the same side and color dict already exists
        container3 = Container("wooden-chest", id="test")
        group.entities.append(container3)
        group.add_circuit_connection("red", "c2", "test")
        assert group.entities["c2"].to_dict() == {
            "name": "steel-chest",
            "position": {"x": 1.5, "y": 0.5},
            "connections": {
                "1": {
                    "red": [
                        {"entity_id": Association(group.entities["c1"])},
                        {"entity_id": Association(group.entities["test"])},
                    ]
                }
            },
        }

        # Test multiple connection points
        group2 = Group("test2")
        arithmetic_combinator = ArithmeticCombinator(id="a")
        decider_combinator = DeciderCombinator(id="d", tile_position=(1, 0))
        group2.entities.append(arithmetic_combinator)
        group2.entities.append(decider_combinator)

        group2.add_circuit_connection("green", "a", "a", 1, 2)
        group2.add_circuit_connection("red", "d", "a", 1, 2)
        assert group2.entities["a"].to_dict()["connections"] == {
            "1": {
                "green": [
                    {
                        "entity_id": Association(group2.entities["a"]),
                        "circuit_id": 2,
                    }
                ]
            },
            "2": {
                "green": [
                    {
                        "entity_id": Association(group2.entities["a"]),
                        "circuit_id": 1,
                    }
                ],
                "red": [
                    {
                        "entity_id": Association(group2.entities["d"]),
                        "circuit_id": 1,
                    }
                ],
            },
        }
        assert group2.entities["d"].to_dict()["connections"] == {
            "1": {
                "red": [
                    {
                        "entity_id": Association(group2.entities["a"]),
                        "circuit_id": 2,
                    }
                ]
            }
        }

        # Warnings
        # Warn if source or target side is not 1 on entity that is not dual
        # connectable
        with pytest.warns(ConnectionSideWarning):
            group.add_circuit_connection("green", "c1", "c2", 1, 2)
        with pytest.warns(ConnectionSideWarning):
            group.add_circuit_connection("green", "c1", "c2", 2, 1)
        # Warn if connection being made is over too long a distance
        with pytest.warns(ConnectionDistanceWarning):
            group.entities.append("wooden-chest", tile_position=(100, 100))
            group.add_circuit_connection("green", "c2", -1)

        # Errors
        with pytest.raises(InvalidWireTypeError):
            group.add_circuit_connection("wrong", "c1", "c2")

        with pytest.raises(KeyError):
            group.add_circuit_connection("red", KeyError, "c2")
        with pytest.raises(KeyError):
            group.add_circuit_connection("red", "c1", KeyError)

        # with self.assertRaises(ValueError):
        #     container_with_no_id = Container()
        #     container1.add_circuit_connection("red", container_with_no_id)

        with pytest.raises(InvalidConnectionSideError):
            group.add_circuit_connection("red", "c1", "c2", "fish", 2)
        with pytest.raises(InvalidConnectionSideError):
            group.add_circuit_connection("red", "c1", "c2", 2, "fish")

        with pytest.raises(EntityNotCircuitConnectableError):
            not_circuit_connectable = Splitter(
                "fast-splitter", id="no error pls", tile_position=(0, 5)
            )
            group.entities.append(not_circuit_connectable)
            group.add_circuit_connection("red", "c1", "no error pls")

        # TODO: test setting connection by reference

    def test_remove_circuit_connection(self):
        group = Group("test")
        container1 = Container("wooden-chest", id="testing1", tile_position=[0, 0])
        container2 = Container("wooden-chest", id="testing2", tile_position=[1, 0])
        group.entities = [container1, container2]

        # Null case
        group.remove_circuit_connection("red", "testing1", "testing2")
        assert container1.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
        }
        assert container2.to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 1.5, "y": 0.5},
        }

        # Normal Operation
        group.add_circuit_connection("red", "testing1", "testing2")
        group.add_circuit_connection("green", "testing2", "testing1")
        group.remove_circuit_connection("red", "testing1", "testing2")
        assert group.entities["testing1"].to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {
                "1": {"green": [{"entity_id": Association(group.entities["testing2"])}]}
            },
        }
        assert group.entities["testing2"].to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 1.5, "y": 0.5},
            "connections": {
                "1": {"green": [{"entity_id": Association(group.entities["testing1"])}]}
            },
        }

        # Redundant operation
        group.remove_circuit_connection("red", "testing1", "testing1")
        assert group.entities["testing1"].to_dict() == {
            "name": "wooden-chest",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {
                "1": {"green": [{"entity_id": Association(group.entities["testing2"])}]}
            },
        }
        # Test multiple connection points
        group2 = Group("test")
        arithmetic_combinator = ArithmeticCombinator(id="a")
        decider_combinator = DeciderCombinator(id="d", tile_position=(1, 0))
        constant_combinator = ConstantCombinator(id="c", tile_position=(2, 0))
        group2.entities = [
            arithmetic_combinator,
            decider_combinator,
            constant_combinator,
        ]

        group2.add_circuit_connection("green", "a", "d")
        group2.add_circuit_connection("green", "a", "d", 1, 2)
        group2.add_circuit_connection("green", "a", "a", 1, 2)
        group2.add_circuit_connection("red", "a", "d", 2, 1)
        group2.add_circuit_connection("red", "a", "d", 2, 2)
        group2.add_circuit_connection("red", "c", "d", 1, 2)

        group2.remove_circuit_connection("green", "a", "d")
        group2.remove_circuit_connection("green", "a", "d", 1, 2)
        group2.remove_circuit_connection("green", "a", "a", 1, 2)
        group2.remove_circuit_connection("red", "a", "d", 2, 1)
        group2.remove_circuit_connection("red", "a", "d", 2, 2)

        assert "connections" not in group2.entities["a"].to_dict()
        assert group2.entities["d"].to_dict()["connections"] == {
            "2": {"red": [{"entity_id": Association(group2.entities["c"])}]}
        }
        assert group2.entities["c"].to_dict()["connections"] == {
            "1": {
                "red": [
                    {
                        "entity_id": Association(group2.entities["d"]),
                        "circuit_id": 2,
                    }
                ]
            }
        }

        # Errors
        with pytest.raises(InvalidWireTypeError):
            group.remove_circuit_connection("wrong", "testing1", "testing2")

        with pytest.raises(KeyError):
            group.remove_circuit_connection("red", KeyError, "testing2")
        with pytest.raises(KeyError):
            group.remove_circuit_connection("red", "testing1", KeyError)

        with pytest.raises(InvalidConnectionSideError):
            group.remove_circuit_connection("red", "testing1", "testing2", "fish", 2)
        with pytest.raises(InvalidConnectionSideError):
            group.remove_circuit_connection("red", "testing2", "testing1", 2, "fish")

        # TODO: test setting connection by reference

    def test_global_position(self):
        group = Group("test")
        group.entities.append("transport-belt")
        assert group.position == Vector(0, 0)
        assert group.position.to_dict() == {"x": 0, "y": 0}
        assert group.entities[0].position == Vector(0.5, 0.5)
        assert group.entities[0].position.to_dict() == {"x": 0.5, "y": 0.5}
        assert group.entities[0].global_position == Vector(0.5, 0.5)
        assert group.entities[0].global_position.to_dict() == {"x": 0.5, "y": 0.5}
        group.position = (4, 4)
        assert group.position == Vector(4, 4)
        assert group.entities[0].position == Vector(0.5, 0.5)
        assert group.entities[0].global_position == Vector(4.5, 4.5)

    def test_get_world_bounding_box(self):
        group = Group("test")

        # None case
        bounding_box = group.get_world_bounding_box()
        assert bounding_box is None

        # Normal case
        group.entities.append("transport-belt")
        group.entities.append("transport-belt", tile_position=(5, 5))
        bounding_box = group.get_world_bounding_box()
        assert round(abs(bounding_box.top_left[0] - 0.1), 7) == 0
        assert round(abs(bounding_box.top_left[1] - 0.1), 7) == 0
        assert round(abs(bounding_box.bot_right[0] - 5.9), 7) == 0
        assert round(abs(bounding_box.bot_right[1] - 5.9), 7) == 0

        # Offset position
        group.entities.pop()
        group.position = (3, 3)
        bounding_box = group.get_world_bounding_box()
        assert round(abs(bounding_box.top_left[0] - 3.1), 7) == 0
        assert round(abs(bounding_box.top_left[1] - 3.1), 7) == 0
        assert round(abs(bounding_box.bot_right[0] - 3.9), 7) == 0
        assert round(abs(bounding_box.bot_right[1] - 3.9), 7) == 0

        # Removed (None) case
        group.entities.pop()
        bounding_box = group.get_world_bounding_box()
        assert bounding_box is None
        assert group.collision_set == CollisionSet([])

    def test_get_dimensions(self):
        group = Group("test")
        assert group.get_dimensions() == (0, 0)

        group.entities.append("transport-belt")
        group.entities.append("transport-belt", tile_position=(5, 5))
        assert group.get_dimensions() == (6, 6)

        group.entities.append("transport-belt", tile_position=(3, 3))
        assert group.get_dimensions() == (6, 6)

    def test_entity_overlapping(self):
        group = Group("test")
        group.entities.append("transport-belt")
        # 2 entities in the same Group
        with pytest.warns(OverlappingObjectsWarning):
            group.entities.append("transport-belt")
        group.entities.pop()  # Remove the extra transport belt

        # Group in Blueprint
        blueprint = Blueprint()
        blueprint.entities.append("transport-belt")

        with pytest.warns(OverlappingObjectsWarning):
            blueprint.entities.append(group)
        blueprint.entities.pop()

        # Group in Group
        group2 = Group("test2")
        group2.entities.append("transport-belt")
        with pytest.warns(OverlappingObjectsWarning):
            group.entities.append(group2)

        # Group in Group in Blueprint
        with pytest.warns(OverlappingObjectsWarning):
            blueprint.entities.append(group)

    def test_disable_entity_overlapping_warning(self):
        group = Group("test")
        group.entities.append("transport-belt")
        group.entities.validate_assignment = "none"
        group.entities.append("transport-belt")  # No warning
        assert len(group.entities) == 2

        group.entities.validate_assignment = "strict"
        with pytest.warns(OverlappingObjectsWarning):
            group.entities.append("transport-belt")

    def test_double_grid_aligned(self):
        group = Group("test")
        group.entities.append("transport-belt")
        assert group.double_grid_aligned == False

        group.entities.append("straight-rail", tile_position=(2, 0))
        assert group.double_grid_aligned == True

    def test_rotatable(self):
        group = Group("test")
        assert group.rotatable == True

    def test_flippable(self):
        group = Group("test")
        group.entities.append("transport-belt")
        assert group.flippable == True

        # TODO
        # group.entities.append("pumpjack", tile_position = (10, 10))
        # self.assertEqual(group.flippable, False)

    def test_flags(self):
        group = Group("test")
        assert group.flags == set()
        group.entities.append("transport-belt")
        assert group.flags == set()

    def test_mergable_with(self):
        group1 = Group()
        group2 = Group()
        assert not group1.mergable_with(group2)  # Always false

    def test_merge(self):
        # Test group merging
        group1 = Group()
        group2 = Group()
        group1.merge(group2)  # Should do nothing

        # Test subentity merging
        group = Group()
        group.entities.append("accumulator")
        group.entities.append("accumulator", merge=True)
        assert len(group.entities) == 1
        assert group.entities[0].to_dict() == {
            "name": "accumulator",
            "position": {"x": 1.0, "y": 1.0},
        }

        # Single entity in group overlap case
        blueprint = Blueprint()
        group = Group()
        group.entities.append("accumulator")
        blueprint.entities.append(group)

        assert len(group.entities) == 1
        assert group.entities._root == [group.entities[0]]
        assert len(blueprint.entities) == 1
        assert blueprint.entities._root == [blueprint.entities[0]]
        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "entity_number": 1,
                    "name": "accumulator",
                    "position": {"x": 1.0, "y": 1.0},
                }
            ],
            "version": encode_version(*__factorio_version_info__),
        }

        blueprint.entities.append(group, merge=True)
        assert len(blueprint.entities) == 2
        assert blueprint.get_world_bounding_box() == AABB(
            0.09999999999999998, 0.09999999999999998, 1.9, 1.9
        )
        assert isinstance(blueprint.entities[0], Group)
        assert len(blueprint.entities[0].entities) == 1
        assert blueprint.entities[0].get_world_bounding_box() == AABB(
            0.09999999999999998, 0.09999999999999998, 1.9, 1.9
        )  # bruh moment
        assert isinstance(blueprint.entities[1], Group)
        assert len(blueprint.entities[1].entities) == 0
        assert blueprint.entities[1].get_world_bounding_box() == None

        assert blueprint.to_dict()["blueprint"] == {
            "item": "blueprint",
            "entities": [
                {
                    "entity_number": 1,
                    "name": "accumulator",
                    "position": {"x": 1.0, "y": 1.0},
                }
            ],
            "version": encode_version(*__factorio_version_info__),
        }

    def test_get(self):
        # Regular case
        # TODO

        # Nested group case
        subgroup = Group("subgroup")
        subgroup.entities.append("express-transport-belt", id="test")
        group = Group("parent")
        group.entities.append(subgroup)
        assert group.get() == [group.entities[("subgroup", "test")]]
        # Note that this messes with the entities position afterward:
        # this is prevented in Blueprint.to_dict by making a copy of itself and
        # using that instead of the original data

    def test_deepcopy(self):
        group = Group()
        group.entities.append("wooden-chest")
        group.entities.append("inserter", tile_position=(0, 1))
        group.entities.append("small-electric-pole", tile_position=(1, 0))
        group.add_circuit_connection("red", 0, 1)
        group.entities.append("power-switch", tile_position=(1, 1))
        group.add_power_connection(2, 3, side=1)
        group.entities.append("locomotive", id="loco", tile_position=(0, 0))
        schedule = Schedule()
        schedule.add_locomotive(group.entities["loco"])
        schedule.append_stop("ore", WaitCondition("full"))
        schedule.append_stop("dropoff", WaitCondition("empty"))
        group.schedules = [schedule]

        blueprint = Blueprint()
        blueprint.entities.append(group, copy=False)

        # Make sure entities' parents are correct
        assert group.entities[0].parent is group
        assert group.entities[1].parent is group
        assert group.entities[2].parent is group
        # Make sure connections are preserved
        assert (
            group.entities[0].connections["1"]["red"][0]["entity_id"]()
            is group.entities[1]
        )
        assert (
            group.entities[1].connections["1"]["red"][0]["entity_id"]()
            is group.entities[0]
        )
        assert (
            group.entities[3].connections["Cu0"][0]["entity_id"]() is group.entities[2]
        )
        # Make sure schedule associations are preserved
        assert group.schedules[0].locomotives[0]() is group.entities["loco"]
        # Make sure the parent is correct
        assert group.parent is blueprint

        import copy

        group_copy = copy.deepcopy(group)

        # Make sure entities' parents are correct
        assert group_copy.entities[0].parent is group_copy
        assert group_copy.entities[1].parent is group_copy
        assert group_copy.entities[2].parent is group_copy
        # Make sure connections are preserved
        assert (
            group_copy.entities[0].connections["1"]["red"][0]["entity_id"]()
            is group_copy.entities[1]
        )
        assert (
            group_copy.entities[1].connections["1"]["red"][0]["entity_id"]()
            is group_copy.entities[0]
        )
        assert (
            group_copy.entities[3].connections["Cu0"][0]["entity_id"]()
            is group_copy.entities[2]
        )
        # Make sure schedule associations are preserved
        assert group_copy.schedules[0].locomotives[0]() is group_copy.entities["loco"]
        # Make sure parent of the copied group is reset to None
        assert group_copy.parent is None
        # Make sure the hashmap was copied properly and are not equivalent
        assert group.entities.spatial_map is not group_copy.entities.spatial_map

        # Test invalid association
        blueprint.entities.append("steel-chest", tile_position=(5, 5))
        blueprint.add_circuit_connection("red", (0, 1), 1)
        with pytest.raises(InvalidAssociationError):
            copy.deepcopy(group)

    def test_with_blueprint(self):
        blueprint = Blueprint()
        blueprint.entities.append("inserter")

        group = Group("test")
        group.entities.append("inserter", tile_position=(1, 1))
        group2 = Group("test2")
        group2.entities.append(group)
        blueprint.entities.append(group2)

        blueprint.add_circuit_connection("red", 0, ("test2", "test", 0))
        self.maxDiff = None
        assert blueprint.to_dict() == {
            "blueprint": {
                "item": "blueprint",
                "entities": [
                    {
                        "name": "inserter",
                        "position": {"x": 0.5, "y": 0.5},
                        "connections": {"1": {"red": [{"entity_id": 2}]}},
                        "entity_number": 1,
                    },
                    {
                        "name": "inserter",
                        "position": {"x": 1.5, "y": 1.5},
                        "connections": {"1": {"red": [{"entity_id": 1}]}},
                        "entity_number": 2,
                    },
                ],
                "version": encode_version(*__factorio_version_info__),
            }
        }

    # =========================================================================

    def test_translate(self):
        group = Group("test")
        group.entities.append("wooden-chest", tile_position=(10, 10))

        group.translate(-5, -5)

        assert group.entities[0].tile_position == Vector(5, 5)

        group.entities.append("straight-rail")
        assert group.double_grid_aligned == True

        with pytest.warns(GridAlignmentWarning):
            group.translate(1, 1)

    def test_rotate(self):
        group = Group("test")
        group.entities.append("wooden-chest")
        group.entities.append("wooden-chest", tile_position=(4, 4))
        group.entities.append("boiler", tile_position=(1, 1))  # looking North

        group.rotate(2)

        assert group.entities[0].tile_position == Vector(-1, 0)
        assert group.entities[1].tile_position == Vector(-5, 4)
        assert group.entities[2].tile_position == Vector(-3, 1)
        assert group.entities[2].direction == 2

        with pytest.raises(RotationError):
            group.rotate(1)

    def test_flip(self):
        group = Group("test")
        group.entities.append("wooden-chest")
        group.entities.append("wooden-chest", tile_position=(4, 4))
        group.entities.append("boiler", tile_position=(1, 1))  # looking North

        group.flip()  # horizontal

        assert group.entities[0].tile_position == Vector(-1, 0)
        assert group.entities[1].tile_position == Vector(-5, 4)
        assert group.entities[2].tile_position == Vector(-4, 1)
        assert group.entities[2].direction == 0

        group.flip("vertical")

        assert group.entities[0].tile_position == Vector(-1, -1)
        assert group.entities[1].tile_position == Vector(-5, -5)
        assert group.entities[2].tile_position == Vector(-4, -3)
        assert group.entities[2].direction == 4

        with pytest.raises(ValueError):
            group.flip("incorrectly")
