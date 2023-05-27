# test_environment.py

import pytest

from draftsman.data import mods


@pytest.fixture(scope="session", autouse=True)
def ensure_no_mods():
    # If there's more than one mod, then it must be a modded configuration
    if len(mods.mod_list) != 1:  # pragma: no coverage
        pytest.exit(
            "Modded Draftsman configuration detected; tests will almost certainly fail. Run `drafstman-update --no-mods` to reset back to vanilla before running tests."
        )
