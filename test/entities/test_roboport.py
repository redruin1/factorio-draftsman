# test_roboport.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Roboport, roboports
from draftsman.error import InvalidEntityError, InvalidSignalError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class RoboportTesting(unittest.TestCase):
    def test_constructor_init(self):
        roboport = Roboport(
            "roboport", tile_position=[1, 1], control_behavior={"read_logistics": True}
        )
        assert roboport.to_dict() == {
            "name": "roboport",
            "position": {"x": 3.0, "y": 3.0},
            "control_behavior": {"read_logistics": True},
        }

        roboport = Roboport(
            "roboport",
            tile_position=[1, 1],
            control_behavior={
                "read_logistics": True,
                "read_robot_stats": True,
                "available_logistic_output_signal": "signal-A",
                "total_logistic_output_signal": "signal-B",
                "available_construction_output_signal": "signal-C",
                "total_construction_output_signal": "signal-D",
            },
        )
        self.maxDiff = None
        assert roboport.to_dict() == {
            "name": "roboport",
            "position": {"x": 3.0, "y": 3.0},
            "control_behavior": {
                "read_logistics": True,
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
            control_behavior={
                "read_logistics": True,
                "read_robot_stats": True,
                "available_logistic_output_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                },
                "total_logistic_output_signal": {"name": "signal-B", "type": "virtual"},
                "available_construction_output_signal": {
                    "name": "signal-C",
                    "type": "virtual",
                },
                "total_construction_output_signal": {
                    "name": "signal-D",
                    "type": "virtual",
                },
            },
        )
        self.maxDiff = None
        assert roboport.to_dict() == {
            "name": "roboport",
            "position": {"x": 3.0, "y": 3.0},
            "control_behavior": {
                "read_logistics": True,
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
        with pytest.warns(DraftsmanWarning):
            Roboport("roboport", unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            Roboport("this is not a roboport")
        with pytest.raises(DataFormatError):
            Roboport(control_behavior={"unused_key": "something"})

    def test_set_read_logistics(self):
        roboport = Roboport()
        roboport.read_logistics = True
        assert roboport.read_logistics == True
        assert roboport.control_behavior == {"read_logistics": True}
        roboport.read_logistics = None
        assert roboport.control_behavior == {}
        with pytest.raises(TypeError):
            roboport.read_logistics = "incorrect"

    def test_set_read_robot_stats(self):
        roboport = Roboport()
        roboport.read_robot_stats = True
        assert roboport.read_robot_stats == True
        assert roboport.control_behavior == {"read_robot_stats": True}
        roboport.read_robot_stats = None
        assert roboport.control_behavior == {}
        with pytest.raises(TypeError):
            roboport.read_robot_stats = "incorrect"

    def test_set_available_logistics_signal(self):
        roboport = Roboport()
        roboport.available_logistic_signal = "signal-A"
        assert roboport.available_logistic_signal == {
            "name": "signal-A",
            "type": "virtual",
        }
        assert roboport.control_behavior == {
            "available_logistic_output_signal": {
                "name": "signal-A",
                "type": "virtual",
            }
        }
        roboport.available_logistic_signal = {"name": "signal-A", "type": "virtual"}
        assert roboport.control_behavior == {
            "available_logistic_output_signal": {
                "name": "signal-A",
                "type": "virtual",
            }
        }
        roboport.available_logistic_signal = None
        assert roboport.control_behavior == {}
        with pytest.raises(TypeError):
            roboport.available_logistic_signal = TypeError
        with pytest.raises(InvalidSignalError):
            roboport.available_logistic_signal = "incorrect"

    def test_set_total_logistics_signal(self):
        roboport = Roboport()
        roboport.total_logistic_signal = "signal-B"
        assert roboport.total_logistic_signal == {"name": "signal-B", "type": "virtual"}
        assert roboport.control_behavior == {
            "total_logistic_output_signal": {"name": "signal-B", "type": "virtual"}
        }
        roboport.total_logistic_signal = {"name": "signal-B", "type": "virtual"}
        assert roboport.control_behavior == {
            "total_logistic_output_signal": {"name": "signal-B", "type": "virtual"}
        }
        roboport.total_logistic_signal = None
        assert roboport.control_behavior == {}
        with pytest.raises(TypeError):
            roboport.total_logistic_signal = TypeError
        with pytest.raises(InvalidSignalError):
            roboport.total_logistic_signal = "incorrect"

    def test_set_available_construction_signal(self):
        roboport = Roboport()
        roboport.available_construction_signal = "signal-C"
        assert roboport.available_construction_signal == {
            "name": "signal-C",
            "type": "virtual",
        }
        assert roboport.control_behavior == {
            "available_construction_output_signal": {
                "name": "signal-C",
                "type": "virtual",
            }
        }
        roboport.available_construction_signal = {"name": "signal-C", "type": "virtual"}
        assert roboport.control_behavior == {
            "available_construction_output_signal": {
                "name": "signal-C",
                "type": "virtual",
            }
        }
        roboport.available_construction_signal = None
        assert roboport.control_behavior == {}
        with pytest.raises(TypeError):
            roboport.available_construction_signal = TypeError
        with pytest.raises(InvalidSignalError):
            roboport.available_construction_signal = "incorrect"

    def test_set_total_construction_signal(self):
        roboport = Roboport()
        roboport.total_construction_signal = "signal-D"
        assert roboport.total_construction_signal == {
            "name": "signal-D",
            "type": "virtual",
        }
        assert roboport.control_behavior == {
            "total_construction_output_signal": {
                "name": "signal-D",
                "type": "virtual",
            }
        }
        roboport.total_construction_signal = {"name": "signal-D", "type": "virtual"}
        assert roboport.control_behavior == {
            "total_construction_output_signal": {
                "name": "signal-D",
                "type": "virtual",
            }
        }
        roboport.total_construction_signal = None
        assert roboport.control_behavior == {}
        with pytest.raises(TypeError):
            roboport.total_construction_signal = TypeError
        with pytest.raises(InvalidSignalError):
            roboport.total_construction_signal = "incorrect"

    def test_mergable_with(self):
        roboport1 = Roboport("roboport")
        roboport2 = Roboport(
            "roboport",
            control_behavior={
                "read_logistics": True,
                "read_robot_stats": True,
                "available_logistic_output_signal": "signal-A",
                "total_logistic_output_signal": "signal-B",
                "available_construction_output_signal": "signal-C",
                "total_construction_output_signal": "signal-D",
            },
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
            control_behavior={
                "read_logistics": True,
                "read_robot_stats": True,
                "available_logistic_output_signal": "signal-A",
                "total_logistic_output_signal": "signal-B",
                "available_construction_output_signal": "signal-C",
                "total_construction_output_signal": "signal-D",
            },
            tags={"some": "stuff"},
        )

        roboport1.merge(roboport2)
        del roboport2

        assert roboport1.control_behavior == {
            "read_logistics": True,
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
        }
        assert roboport1.tags == {"some": "stuff"}
