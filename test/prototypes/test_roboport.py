# test_roboport.py

from draftsman.constants import ValidationMode
from draftsman.entity import Roboport, roboports, Container
from draftsman.error import DataFormatError, IncompleteSignalError
from draftsman.signatures import SignalID
import draftsman.validators
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    UnknownSignalWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_roboport():
    if len(roboports) == 0:
        return None
    return Roboport(
        "roboport",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        read_logistics=False,
        read_robot_stats=True,
        available_logistic_signal="signal-A",
        total_logistic_signal="signal-B",
        available_construction_signal="signal-C",
        total_construction_signal="signal-D",
        # TODO: 2.0 features
        tags={"blah": "blah"},
    )


class TestRoboport:
    def test_constructor_init(self):
        roboport = Roboport("roboport", tile_position=[1, 1], read_logistics=False)
        assert roboport.to_dict() == {
            "name": "roboport",
            "position": {"x": 3.0, "y": 3.0},
            "control_behavior": {"read_logistics": False},
        }

        roboport = Roboport(
            "roboport",
            tile_position=[1, 1],
            read_logistics=True,
            read_robot_stats=True,
            available_logistic_signal="signal-A",
            total_logistic_signal="signal-B",
            available_construction_signal="signal-C",
            total_construction_signal="signal-D",
        )
        assert roboport.to_dict() == {
            "name": "roboport",
            "position": {"x": 3.0, "y": 3.0},
            "control_behavior": {
                # "read_logistics": True, # Default
                "read_robot_stats": True,
                "available_logistic_output_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                },
                "total_logistic_output_signal": {
                    "name": "signal-B",
                    "type": "virtual",
                },
                "available_construction_output_signal": {
                    "name": "signal-C",
                    "type": "virtual",
                },
                "total_construction_output_signal": {
                    "name": "signal-D",
                    "type": "virtual",
                },
            },
        }

        roboport = Roboport(
            "roboport",
            tile_position=[1, 1],
            read_logistics=True,
            read_robot_stats=True,
            available_logistic_signal={"name": "signal-A", "type": "virtual"},
            total_logistic_signal={"name": "signal-B", "type": "virtual"},
            available_construction_signal={"name": "signal-C", "type": "virtual"},
            total_construction_signal={"name": "signal-D", "type": "virtual"},
        )

        assert roboport.to_dict() == {
            "name": "roboport",
            "position": {"x": 3.0, "y": 3.0},
            "control_behavior": {
                # "read_logistics": True, # Default
                "read_robot_stats": True,
                "available_logistic_output_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                },
                "total_logistic_output_signal": {
                    "name": "signal-B",
                    "type": "virtual",
                },
                "available_construction_output_signal": {
                    "name": "signal-C",
                    "type": "virtual",
                },
                "total_construction_output_signal": {
                    "name": "signal-D",
                    "type": "virtual",
                },
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Roboport.from_dict(
                {"name": "roboport", "unused_keyword": "whatever"}
            ).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            Roboport("this is not a roboport").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            Roboport(tags="incorrect").validate().reissue_all()

    def test_set_read_logistics(self):
        roboport = Roboport()
        assert roboport.read_logistics == True

        roboport.read_logistics = False
        assert roboport.read_logistics == False

        with pytest.raises(DataFormatError):
            roboport.read_logistics = "incorrect"

        with draftsman.validators.disabled():
            roboport.read_logistics = "incorrect"
            assert roboport.read_logistics == "incorrect"
            assert roboport.to_dict() == {
                "name": "roboport",
                "position": {"x": 2, "y": 2},
                "control_behavior": {"read_logistics": "incorrect"},
            }

    def test_set_read_robot_stats(self):
        roboport = Roboport()
        assert roboport.read_robot_stats == False

        roboport.read_robot_stats = True
        assert roboport.read_robot_stats == True

        with pytest.raises(DataFormatError):
            roboport.read_robot_stats = "incorrect"

        with draftsman.validators.disabled():
            roboport.read_robot_stats = "incorrect"
            assert roboport.read_robot_stats == "incorrect"
            assert roboport.to_dict() == {
                "name": "roboport",
                "position": {"x": 2, "y": 2},
                "control_behavior": {"read_robot_stats": "incorrect"},
            }

    def test_set_available_logistics_signal(self):
        roboport = Roboport()
        roboport.available_logistic_signal = "signal-A"
        assert roboport.available_logistic_signal == SignalID(
            name="signal-A", type="virtual"
        )

        roboport.available_logistic_signal = {"name": "signal-A", "type": "virtual"}
        assert roboport.available_logistic_signal == SignalID(
            name="signal-A", type="virtual"
        )

        roboport.available_logistic_signal = None
        assert roboport.available_logistic_signal == None

        with pytest.warns(UnknownSignalWarning):
            roboport.available_logistic_signal = {"name": "unknown", "type": "item"}
            assert roboport.available_logistic_signal == SignalID(
                name="unknown", type="item"
            )

        with pytest.raises(DataFormatError):
            roboport.available_logistic_signal = TypeError
        with pytest.raises(IncompleteSignalError):
            roboport.available_logistic_signal = "incorrect"

    def test_set_total_logistics_signal(self):
        roboport = Roboport()
        roboport.total_logistic_signal = "signal-B"
        assert roboport.total_logistic_signal == SignalID(
            name="signal-B", type="virtual"
        )

        roboport.total_logistic_signal = {"name": "signal-B", "type": "virtual"}
        assert roboport.total_logistic_signal == SignalID(
            name="signal-B", type="virtual"
        )

        roboport.total_logistic_signal = None
        assert roboport.total_logistic_signal == None

        with pytest.warns(UnknownSignalWarning):
            roboport.total_logistic_signal = {"name": "unknown", "type": "item"}
            assert roboport.total_logistic_signal == SignalID(
                name="unknown", type="item"
            )

        with pytest.raises(DataFormatError):
            roboport.total_logistic_signal = TypeError
        with pytest.raises(IncompleteSignalError):
            roboport.total_logistic_signal = "incorrect"

    def test_set_available_construction_signal(self):
        roboport = Roboport()
        roboport.available_construction_signal = "signal-C"
        assert roboport.available_construction_signal == SignalID(
            name="signal-C", type="virtual"
        )

        roboport.available_construction_signal = {"name": "signal-C", "type": "virtual"}
        assert roboport.available_construction_signal == SignalID(
            name="signal-C", type="virtual"
        )

        roboport.available_construction_signal = None
        assert roboport.available_construction_signal == None

        with pytest.warns(UnknownSignalWarning):
            roboport.available_construction_signal = {"name": "unknown", "type": "item"}
            assert roboport.available_construction_signal == SignalID(
                name="unknown", type="item"
            )

        with pytest.raises(DataFormatError):
            roboport.available_construction_signal = TypeError
        with pytest.raises(IncompleteSignalError):
            roboport.available_construction_signal = "incorrect"

    def test_set_total_construction_signal(self):
        roboport = Roboport()
        roboport.total_construction_signal = "signal-D"
        assert roboport.total_construction_signal == SignalID(
            name="signal-D", type="virtual"
        )

        roboport.total_construction_signal = {"name": "signal-D", "type": "virtual"}
        assert roboport.total_construction_signal == SignalID(
            name="signal-D", type="virtual"
        )

        roboport.total_construction_signal = None
        assert roboport.total_construction_signal == None

        with pytest.warns(UnknownSignalWarning):
            roboport.total_construction_signal = {"name": "unknown", "type": "item"}
            assert roboport.total_construction_signal == SignalID(
                name="unknown", type="item"
            )

        with pytest.raises(DataFormatError):
            roboport.total_construction_signal = TypeError
        with pytest.raises(IncompleteSignalError):
            roboport.total_construction_signal = "incorrect"

    def test_mergable_with(self):
        roboport1 = Roboport("roboport")
        roboport2 = Roboport(
            "roboport",
            read_logistics=True,
            read_robot_stats=True,
            available_logistic_signal="signal-A",
            total_logistic_signal="signal-B",
            available_construction_signal="signal-C",
            total_construction_signal="signal-D",
            tags={"some": "stuff"},
        )

        assert roboport1.mergable_with(roboport1)

        assert roboport1.mergable_with(roboport2)
        assert roboport2.mergable_with(roboport1)

        roboport2.tile_position = (1, 1)
        assert not roboport1.mergable_with(roboport2)

    def test_merge(self):
        roboport1 = Roboport("roboport")
        roboport2 = Roboport(
            "roboport",
            read_logistics=True,
            read_robot_stats=True,
            available_logistic_signal="signal-A",
            total_logistic_signal="signal-B",
            available_construction_signal="signal-C",
            total_construction_signal="signal-D",
            tags={"some": "stuff"},
        )

        roboport1.merge(roboport2)
        del roboport2

        assert roboport1.read_logistics == True
        assert roboport1.read_robot_stats == True
        assert roboport1.available_logistic_signal == SignalID(
            name="signal-A", type="virtual"
        )
        assert roboport1.total_logistic_signal == SignalID(
            name="signal-B", type="virtual"
        )
        assert roboport1.available_construction_signal == SignalID(
            name="signal-C", type="virtual"
        )
        assert roboport1.total_construction_signal == SignalID(
            name="signal-D", type="virtual"
        )
        assert roboport1.tags == {"some": "stuff"}

        assert roboport1.to_dict(exclude_defaults=False)["control_behavior"] == {
            "read_logistics": True,
            "read_robot_stats": True,
            "available_logistic_output_signal": {
                "name": "signal-A",
                "quality": "normal",
                "type": "virtual",
            },
            "total_logistic_output_signal": {
                "name": "signal-B",
                "quality": "normal",
                "type": "virtual",
            },
            "available_construction_output_signal": {
                "name": "signal-C",
                "quality": "normal",
                "type": "virtual",
            },
            "total_construction_output_signal": {
                "name": "signal-D",
                "quality": "normal",
                "type": "virtual",
            },
        }

    def test_eq(self):
        roboport1 = Roboport("roboport")
        roboport2 = Roboport("roboport")

        assert roboport1 == roboport2

        roboport1.tags = {"some": "stuff"}

        assert roboport1 != roboport2

        container = Container()

        assert roboport1 != container
        assert roboport2 != container

        # hashable
        assert isinstance(roboport1, Hashable)
