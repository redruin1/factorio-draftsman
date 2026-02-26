"""
Creates a blueprint that calculates the sqrt of `signal-I` and gives the output
on `signal-O` with a time complexity of 1 tick. Handles the entire positive
integer range.

The footprint of the generated blueprint is dependent on the total number of
unique signals in your environment - more signals, fewer total combinators in
order to cover the whole range.

Requirements:
    [Optional] pyperclip
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.data import signals
from draftsman.entity import ConstantCombinator, DeciderCombinator

try:
    import pyperclip
except ImportError:
    pyperclip = None


def main():
    bp = Blueprint()

    unique_signals = []
    for signal_name in signals.raw:
        if signal_name in {
            "signal-item-parameter",
            "signal-fuel-parameter",
            "signal-fluid-parameter",
            "signal-signal-parameter",
            "signal-unknown",
        }:
            continue
        if signal_name in signals.pure_virtual:
            continue
        for signal_type in signals.type_of[signal_name]:
            for signal_quality in signals.quality:
                unique_signals.append((signal_name, signal_quality, signal_type))

    def add_row(dc, cc):
        bp.entities.append(cc, id=f"cc_{num_ccs}", tile_position=(0, num_ccs))
        bp.entities.append(dc, id=f"dc_{num_ccs}", tile_position=(1, num_ccs))
        bp.add_circuit_connection(
            "green", entity_1=f"cc_{num_ccs}", entity_2=f"dc_{num_ccs}"
        )
        try:
            bp.add_circuit_connection(
                "red", entity_1=f"dc_{num_ccs - 1}", entity_2=f"dc_{num_ccs}"
            )
            bp.add_circuit_connection(
                "red",
                entity_1=f"dc_{num_ccs - 1}",
                side_1="output",
                entity_2=f"dc_{num_ccs}",
                side_2="output",
            )
        except KeyError:
            pass

    import math

    num_squares = math.floor(math.sqrt(2**31 - 1))

    dc = DeciderCombinator("decider-combinator", direction=Direction.EAST)
    Input = DeciderCombinator.Input
    Output = DeciderCombinator.Output
    dc.conditions = [Input("signal-each", {"green"}) <= Input("signal-I", {"red"})]
    dc.outputs = [Output("signal-O", copy_count_from_input=False)]

    num_signals = len(unique_signals)
    cc = ConstantCombinator("constant-combinator", direction=Direction.EAST)
    section = cc.add_section()
    signal_count = 0
    total_count = 0
    num_ccs = 0
    for i in range(1, num_squares + 1):
        square = i * i
        index = signal_count % 1000
        signal_name, signal_quality, signal_type = unique_signals[total_count]
        section.set_signal(index, signal_name, square, signal_quality, signal_type)
        total_count += 1
        signal_count += 1

        if signal_count == 1000:
            section = cc.add_section()
            signal_count = 0

        if total_count >= num_signals:
            add_row(dc, cc)

            cc.sections = []
            section = cc.add_section()
            total_count = 0
            signal_count = 0
            num_ccs += 1

    if len(cc.sections) > 0:
        add_row(dc, cc)

    if pyperclip is not None:
        pyperclip.copy(bp.to_string())
        print("Copied to clipboard.")
    else:
        with open("examples/output/sqrt_lut.blueprint", "w") as file:
            file.write(bp.to_string())
        print("Wrote 'examples/output/sqrt_lut.blueprint'")


if __name__ == "__main__":
    main()
