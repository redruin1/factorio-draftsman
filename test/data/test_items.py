# test_items.py

from draftsman.data import items

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

    def test_modify_existing_item(self):
        pass

    def test_get_stack_size(self):
        assert items.get_stack_size("artillery-shell") == 1
        assert items.get_stack_size("nuclear-fuel") == 1
        assert items.get_stack_size("rocket-fuel") == 20
        assert items.get_stack_size("iron-ore") == 50
        assert items.get_stack_size("iron-plate") == 100
        assert items.get_stack_size("electronic-circuit") == 200
        assert items.get_stack_size("space-science-pack") == 200

        # TODO: should this raise an error instead?
        assert items.get_stack_size("unknown!") == None
