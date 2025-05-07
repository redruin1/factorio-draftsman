# test_entities.py

from draftsman.data.entities import get_default_collision_mask

def test_default_collision_mask():
    assert get_default_collision_mask("gate") == {
        "item-layer",
        "object-layer",
        "player-layer",
        "water-tile",
        "train-layer",
    }
    assert get_default_collision_mask("heat-pipe") == {"object-layer", "floor-layer", "water-tile"}
    assert get_default_collision_mask("land-mine") == {"object-layer", "water-tile"} 
    assert get_default_collision_mask("linked-belt") == {
        "object-layer",
        "item-layer",
        "transport-belt-layer",
        "water-tile",
    }
    assert get_default_collision_mask("loader") == {
        "object-layer",
        "item-layer",
        "transport-belt-layer",
        "water-tile",
    }
    assert get_default_collision_mask("straight-rail") == {
        "item-layer",
        "object-layer",
        "rail-layer",
        "floor-layer",
        "water-tile",
    }
    assert get_default_collision_mask("rail-signal") == {"floor-layer", "rail-layer", "item-layer"}
    assert get_default_collision_mask("locomotive") == {"train-layer"}
    assert get_default_collision_mask("splitter") == {
        "object-layer",
        "item-layer",
        "transport-belt-layer",
        "water-tile",
    }
    assert get_default_collision_mask("transport-belt") == {
        "object-layer",
        "floor-layer",
        "transport-belt-layer",
        "water-tile",
    }
    assert get_default_collision_mask("underground-belt") == {
        "object-layer",
        "item-layer",
        "transport-belt-layer",
        "water-tile",
    }