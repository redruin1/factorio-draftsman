# test_display_panel.py

from draftsman.constants import Direction
from draftsman.prototypes.display_panel import (
    DisplayPanel,
    display_panels,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_display_panel():
    if len(display_panels) == 0:
        return None
    return DisplayPanel(
        "display-panel",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        text="test",
        icon="signal-A",
        always_show_in_alt_mode=True,
        show_in_chart=True,
        messages=[DisplayPanel.Message(icon="signal-B", text="test2")],
        tags={"blah": "blah"},
    )


def test_constructor():
    curved_rail = DisplayPanel("display-panel")

    with pytest.warns(UnknownEntityWarning):
        DisplayPanel("unknown display panel")


def test_flags():
    for panel_name in display_panels:
        panel = DisplayPanel(panel_name)
        assert panel.power_connectable == False
        assert panel.dual_power_connectable == False
        assert panel.circuit_connectable == True
        assert panel.dual_circuit_connectable == False
