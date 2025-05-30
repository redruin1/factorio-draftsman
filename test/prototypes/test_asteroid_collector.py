# test_asteroid_collector.py

from draftsman.prototypes.asteroid_collector import AsteroidCollector
from draftsman.prototypes.container import Container
from draftsman.constants import Direction
from draftsman.error import DataFormatError
from draftsman.signatures import AttrsAsteroidChunkID, AttrsSimpleCondition

from draftsman.data.entities import asteroid_collectors

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_asteroid_collector():
    if len(asteroid_collectors) == 0:
        return None
    return AsteroidCollector(
        "asteroid-collector",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        circuit_enabled=True,
        circuit_condition=AttrsSimpleCondition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        bar=10,
        chunk_filter=["oxide-asteroid-chunk"],
        circuit_set_filters=True,
        read_contents=True,
        read_hands=False,
        tags={"blah": "blah"},
    )


class TestAsteroidCollector:
    def test_constructor_init(self):
        collector = AsteroidCollector(
            "asteroid-collector",
            direction=Direction.SOUTH,
            chunk_filter=["carbonic-asteroid-chunk", "metallic-asteroid-chunk"],
        )
        assert collector.to_dict() == {
            "name": "asteroid-collector",
            "position": {"x": 1.5, "y": 1.5},
            "direction": Direction.SOUTH,
            "chunk-filter": [
                {"index": 1, "name": "carbonic-asteroid-chunk"},
                {"index": 2, "name": "metallic-asteroid-chunk"},
            ],
        }

        with pytest.raises(DataFormatError):
            AsteroidCollector(chunk_filter="wrong").validate().reissue_all()

    def test_power_and_circuit_flags(self):
        for collector_name in asteroid_collectors:
            collector = AsteroidCollector(collector_name)
            assert collector.circuit_connectable == True
            assert collector.dual_circuit_connectable == False
            assert collector.power_connectable == False
            assert collector.dual_power_connectable == False

    def test_chunk_filter(self):
        ac = AsteroidCollector("asteroid-collector")

        # Test hybrid
        ac.chunk_filter = [
            "oxide-asteroid-chunk",
            {"index": 2, "name": "metallic-asteroid-chunk"},
        ]
        assert ac.to_dict()["chunk-filter"] == [
            {"index": 1, "name": "oxide-asteroid-chunk"},
            {"index": 2, "name": "metallic-asteroid-chunk"},
        ]

        ac.validate_assignment = "none"
        ac.chunk_filter = "wrong"
        assert ac.chunk_filter == "wrong"

    def test_read_contents(self):
        ac = AsteroidCollector("asteroid-collector")
        assert ac.read_contents == False

        ac.read_contents = True
        assert ac.read_contents == True

        with pytest.raises(DataFormatError):
            ac.read_contents = "wrong"
        assert ac.read_contents == True

        ac.validate_assignment = "none"
        ac.read_contents = "wrong"
        assert ac.read_contents == "wrong"

    def test_include_hands(self):
        ac = AsteroidCollector("asteroid-collector")
        assert ac.read_hands == True

        ac.read_hands = False
        assert ac.read_hands == False

        with pytest.raises(DataFormatError):
            ac.read_hands = "wrong"
        assert ac.read_hands == False

    def test_mergable_with(self):
        collector1 = AsteroidCollector("asteroid-collector")
        collector2 = AsteroidCollector("asteroid-collector", tags={"some": "stuff"})

        assert collector1.mergable_with(collector2)
        assert collector2.mergable_with(collector1)

        collector2.tile_position = (1, 1)
        assert not collector1.mergable_with(collector2)

    def test_merge(self):
        collector1 = AsteroidCollector("asteroid-collector")
        collector2 = AsteroidCollector(
            "asteroid-collector",
            tags={"some": "stuff"},
            chunk_filter=["oxide-asteroid-chunk"],
            read_contents=True,
            read_hands=False,
        )

        collector1.merge(collector2)
        del collector2

        assert collector1.tags == {"some": "stuff"}
        assert collector1.chunk_filter == [
            AttrsAsteroidChunkID(index=1, name="oxide-asteroid-chunk")
        ]
        assert collector1.read_contents == True
        assert collector1.read_hands == False

    def test_eq(self):
        collector1 = AsteroidCollector("asteroid-collector")
        collector2 = AsteroidCollector("asteroid-collector")

        assert collector1 == collector2

        # beacon1.set_item_request("speed-module-3", 2)
        collector1.tags = {"something": "else"}

        assert collector1 != collector2

        container = Container()

        assert collector1 != container
        assert collector2 != container

        # hashable
        assert isinstance(collector1, Hashable)
