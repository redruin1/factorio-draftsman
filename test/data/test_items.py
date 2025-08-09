# test_items.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.data import items, mods

import copy
import pytest


class TestItemsData:
    def test_add_item(self):
        # Clone original so we can return to it afterward
        # TODO: theres gotta be a better way than this bs
        orig_raw = copy.deepcopy(items.raw)
        orig_subgroups = copy.deepcopy(items.subgroups)
        orig_groups = copy.deepcopy(items.groups)

        # Add item group
        items.add_group(name="new-item-group")
        assert "new-item-group" in items.groups
        assert items.groups["new-item-group"] == {
            "type": "item-group",
            "name": "new-item-group",
            "order": "",
            "subgroups": [],
        }

        # Add item subgroup
        items.add_subgroup(name="new-item-subgroup", group="new-item-group")
        assert "new-item-subgroup" in items.subgroups
        assert items.subgroups["new-item-subgroup"] == {
            "type": "item-subgroup",
            "name": "new-item-subgroup",
            "order": "",
            "items": [],
        }
        assert (
            items.subgroups["new-item-subgroup"]
            in items.groups["new-item-group"]["subgroups"]
        )
        assert (
            items.groups["new-item-group"]["subgroups"][0]
            is items.subgroups["new-item-subgroup"]
        )

        with pytest.raises(TypeError):
            items.add_subgroup(name="fail-new-item-subgroup", group="nonexistant")

        assert "nonexistant" not in items.groups
        assert "fail-new-item-subgroup" not in items.subgroups

        # Add item
        items.add_item(name="new-item", stack_size=100, subgroup="new-item-subgroup")
        assert "new-item" in items.raw
        assert items.raw["new-item"] == {
            "type": "item",
            "name": "new-item",
            "stack_size": 100,
            "order": "",
            "subgroup": "new-item-subgroup",
        }
        assert items.raw["new-item"] in items.subgroups["new-item-subgroup"]["items"]
        assert items.subgroups["new-item-subgroup"]["items"][0] is items.raw["new-item"]

        with pytest.raises(TypeError):
            items.add_item(name="fail-new-item", stack_size=100, subgroup="nonexistant")

        assert "nonexistant" not in items.subgroups
        assert "fail-new-item" not in items.raw

        del items.raw["new-item"]
        del items.subgroups["new-item-subgroup"]["items"][0]
        del items.subgroups["new-item-subgroup"]
        del items.groups["new-item-group"]["subgroups"][0]
        del items.groups["new-item-group"]

    def test_get_stack_size(self):
        assert items.get_stack_size("artillery-shell") == 1
        assert items.get_stack_size("nuclear-fuel") == 1
        assert items.get_stack_size("iron-ore") == 50
        assert items.get_stack_size("iron-plate") == 100
        assert items.get_stack_size("electronic-circuit") == 200
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            assert items.get_stack_size("rocket-fuel") == 10
            assert items.get_stack_size("space-science-pack") == 2_000
        else:
            assert items.get_stack_size("rocket-fuel") == 20
            assert items.get_stack_size("space-science-pack") == 200

        # TODO: should this raise an error instead?
        assert items.get_stack_size("unknown!") == None

    @pytest.mark.skipif(
        mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0),
        reason="Weight is a 2.0 concept",
    )
    def test_get_weight(self):
        # Unrecognized
        assert items.get_weight("unknown thingy") is None
        # Cursor item
        assert items.get_weight("copy-paste-tool") == 0
        # Weight manually specified
        assert items.get_weight("iron-ore") == 2000
        # Item with no recipe
        assert items.get_weight("burner-generator") == 100
        # Item with fluid ingredients
        assert items.get_weight("accumulator") == 20_000
        # Not simple result
        assert items.get_weight("stone-brick") == 2_000
        # Floored size
        assert items.get_weight("electronic-circuit") == 500
