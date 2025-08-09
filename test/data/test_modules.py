# test_modules.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.data import mods, modules

import pytest


class TestModuleData:
    def test_categories_sorted(self):
        assert modules.categories["speed"] == [
            "speed-module",
            "speed-module-2",
            "speed-module-3",
        ]
        assert modules.categories["productivity"] == [
            "productivity-module",
            "productivity-module-2",
            "productivity-module-3",
        ]
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            assert modules.categories["effectivity"] == [
                "effectivity-module",
                "effectivity-module-2",
                "effectivity-module-3",
            ]
        else:
            assert modules.categories["efficiency"] == [
                "efficiency-module",
                "efficiency-module-2",
                "efficiency-module-3",
            ]
            assert modules.categories["quality"] == [
                "quality-module",
                "quality-module-2",
                "quality-module-3",
            ]

    def test_add_module(self):
        with pytest.raises(TypeError):
            modules.add_module("new-productivity-module", "unknown-category")
        if "quality" in mods.versions:
            assert len(modules.categories) == 4
        else:
            assert len(modules.categories) == 3

        modules.add_module("new-productivity-module", "productivity")
        assert modules.raw["new-productivity-module"] == {
            "name": "new-productivity-module",
            "category": "productivity",
            "effect": {},
            "tier": 0,
        }

        # Cleanup so we don't affect any of the other tests
        del modules.raw["new-productivity-module"]
        del modules.categories["productivity"][-1]

    def test_add_module_category(self):
        modules.add_module_category("new-module-category")
        if "quality" in mods.versions:
            assert len(modules.categories) == 5
        else:
            assert len(modules.categories) == 4
        assert modules.categories["new-module-category"] == []

        # Cleanup so we don't affect any of the other tests
        del modules.categories["new-module-category"]
