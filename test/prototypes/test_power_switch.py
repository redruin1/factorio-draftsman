# test_power_switch.py

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.entity import PowerSwitch, power_switches, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestPowerSwitch:
    def test_constructor_init(self):
        switch = PowerSwitch("power-switch", tile_position=[0, 0], switch_state=True)
        assert switch.to_dict() == {
            "name": "power-switch",
            "position": {"x": 1.0, "y": 1.0},
            "switch_state": True,
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            PowerSwitch(unused_keyword="whatever").validate().reissue_all()
        with pytest.warns(UnknownKeywordWarning):
            PowerSwitch(
                control_behavior={"unused_key": "something"}
            ).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            PowerSwitch("this is not a power switch").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            PowerSwitch(control_behavior="incorrect").validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for name in power_switches:
            power_switch = PowerSwitch(name)
            assert power_switch.power_connectable == True
            assert power_switch.dual_power_connectable == True
            assert power_switch.circuit_connectable == True
            assert power_switch.dual_circuit_connectable == False

    def test_circuit_wire_max_distance(self):
        assert PowerSwitch("power-switch").circuit_wire_max_distance == 10.0

    def test_switch_state(self):
        power_switch = PowerSwitch()
        power_switch.switch_state = False
        assert power_switch.switch_state == False
        power_switch.switch_state = None
        assert power_switch.switch_state == None
        # TODO: move to validate
        # with pytest.raises(TypeError):
        #     power_switch.switch_state = TypeError

    def test_mergable_with(self):
        switch1 = PowerSwitch("power-switch")
        switch2 = PowerSwitch("power-switch", switch_state=True, tags={"some": "stuff"})

        assert switch1.mergable_with(switch1)

        assert switch1.mergable_with(switch2)
        assert switch2.mergable_with(switch1)

        switch2.tile_position = (1, 1)
        assert not switch1.mergable_with(switch2)

    def test_merge(self):
        switch1 = PowerSwitch("power-switch")
        switch2 = PowerSwitch("power-switch", switch_state=True, tags={"some": "stuff"})

        switch1.merge(switch2)
        del switch2

        assert switch1.switch_state == True
        assert switch1.tags == {"some": "stuff"}

        # Test power switch connections
        group_left = Group("left")
        group_left.entities.append("small-electric-pole", tile_position=(-2, 0))
        group_left.entities.append("power-switch")
        group_left.add_power_connection(0, 1, side_2="input")
        print("left wires:", group_left.wires)

        group_right = Group("right")
        group_right.entities.append("power-switch")
        group_right.entities.append("small-electric-pole", tile_position=(4, 0))
        group_right.add_power_connection(0, 1, side_1="output")
        print("right wires:", group_right.wires)

        blueprint = Blueprint()
        blueprint.entities.append(group_left)
        print("added left wires:", blueprint.entities[0].wires)
        blueprint.entities.append(group_right, merge=True)
        print("added right wires:", blueprint.entities[1].wires)

        assert len(blueprint.entities) == 2
        assert len(blueprint.entities[0].entities) == 2
        assert len(blueprint.entities[1].entities) == 1
        assert blueprint.to_dict()["blueprint"]["entities"] == [
            {
                "entity_number": 1,
                "name": "small-electric-pole",
                "position": {"x": -1.5, "y": 0.5},
            },
            {
                "entity_number": 2,
                "name": "power-switch",
                "position": {"x": 1.0, "y": 1.0},
            },
            {
                "entity_number": 3,
                "name": "small-electric-pole",
                "position": {"x": 4.5, "y": 0.5},
            },
        ]
        assert blueprint.to_dict()["blueprint"]["wires"] == [[1, 5, 2, 5], [2, 6, 3, 5]]

        # Test self overlapping
        group = Group()
        group.entities.append("small-electric-pole", tile_position=(-2, 0))
        group.entities.append("power-switch")
        group.add_power_connection(0, 1, side_2="input")

        blueprint = Blueprint()
        blueprint.entities.append(group)
        blueprint.entities.append(group, merge=True)

        assert len(blueprint.entities) == 2
        assert len(blueprint.entities[0].entities) == 2
        assert len(blueprint.entities[1].entities) == 0
        assert blueprint.to_dict()["blueprint"]["entities"] == [
            {
                "entity_number": 1,
                "name": "small-electric-pole",
                "position": {"x": -1.5, "y": 0.5},
            },
            {
                "entity_number": 2,
                "name": "power-switch",
                "position": {"x": 1.0, "y": 1.0},
            },
        ]
        assert blueprint.to_dict()["blueprint"]["wires"] == [[1, 5, 2, 5]]

    def test_eq(self):
        switch1 = PowerSwitch("power-switch")
        switch2 = PowerSwitch("power-switch")

        assert switch1 == switch2

        switch1.tags = {"some": "stuff"}

        assert switch1 != switch2

        container = Container()

        assert switch1 != container
        assert switch2 != container

        # hashable
        assert isinstance(switch1, Hashable)
