# display_panel.py

"""
Manipulating the Factorio 2.0 display panel, as well as creating a (simple)
circuit-controllable text display.
"""

import string

from draftsman.blueprintable import Blueprint, BlueprintBook
from draftsman.constants import Direction
from draftsman.entity import ConstantCombinator, DisplayPanel
from draftsman.signatures import Condition


def main():
    dp = DisplayPanel("display-panel")
    assert dp.circuit_connectable == True

    dp.direction = Direction.EAST

    # Always display the message when alt-mode is enabled
    dp.always_show_in_alt_mode = True
    # Show the displayed icon on the map
    dp.show_in_chart = True

    # Configure the static apperance
    dp.icon = "signal-info"  # <- Converted into a SignalID object
    dp.text = (
        "Static text that is displayed only when not connected to a circuit network."
    )

    # Give the panel a list of conditional messages selected with "signal-A"
    dp.messages = [
        DisplayPanel.Message(
            icon="signal-info",
            text="This is an info signal.",
            condition=Condition(
                first_signal="signal-A",
                comparator="=",
                constant=1,
            ),
        ),
        DisplayPanel.Message(
            icon="signal-yellow",
            text="This is a warning signal.",
            condition=Condition(
                first_signal="signal-A",
                comparator="=",
                constant=2,
            ),
        ),
        DisplayPanel.Message(
            icon="signal-alert",
            text="This is an alert signal.",
            condition=Condition(
                first_signal="signal-A",
                comparator="=",
                constant=3,
            ),
        ),
    ]

    # We'll make a simple blueprint which is just the single display panel
    simple_blueprint = Blueprint(
        label="Simple Panel", description="A single configured display panel."
    )
    simple_blueprint.entities.append(dp)

    # Let's make something a little more complicated: A (simple) encoded text display
    string_display_bp = Blueprint(
        label="Text Display",
        description="Pass in ordered signals with ASCII values to visually display the text.",
    )

    # Define our message; we'll stick to just uppercase letters for simplicity
    text_to_display = "HELLO"
    # Each letter will be given a single consecutive signal, starting with `signal-0`
    # This limits the length of text to 10 letters, but this is good enough for illustration purposes
    input_signals = ["signal-" + str(i) for i in range(10)]
    # We also need to generate the mapping of `letter icon -> utf-8 value`
    display_icons = {
        "signal-" + letter: ord(letter)
        for letter in list(string.ascii_uppercase)
    }

    # Make a row of len(text_to_display) display panels
    display_panel = DisplayPanel("display-panel")
    for i in range(len(text_to_display)):
        display_panel.tile_position = (i, 0)
        display_panel.messages = [
            DisplayPanel.Message(
                icon=display_icon,
                condition=Condition(
                    first_signal=input_signals[i],
                    comparator="=",
                    constant=code_point,
                ),
            )
            for display_icon, code_point in display_icons.items()
        ]
        string_display_bp.entities.append(display_panel)

    # Connect all of these panels with red wires
    for i in range(len(text_to_display) - 1):
        string_display_bp.add_circuit_connection("red", i, i + 1)

    # Encode our message into a constant combinator, which we will place to the
    # left of our text display
    cc: ConstantCombinator = string_display_bp.entities.append(
        "constant-combinator", tile_position=(-3, 0), direction=Direction.EAST
    )
    signal_section = cc.add_section()
    for i, char in enumerate(text_to_display):
        signal_section.set_signal(
            index=i,
            name=input_signals[i],
            type="virtual",
            count=ord(char),
        )

    # In order to display the text, simply connect the constant combinator to
    # the display panels with a red wire.

    # Add both blueprints to a blueprint book for packaging
    book = BlueprintBook(
        active_index=0, blueprints=[simple_blueprint, string_display_bp]
    )
    print(book.to_string())


if __name__ == "__main__":
    main()
