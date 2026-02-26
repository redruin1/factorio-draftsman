"""
Requested by a conversation on Discord. Creates a set of connected inserters
with a slightly changing circuit condition, but multiplied by 900. Perfect
example of the type of problems Draftsman is suited to solve.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.entity import Inserter

activation_signal = "signal-anything"

bp = Blueprint(label="900 Inserters")
inserter = Inserter("stack-inserter", quality="epic", direction=Direction.NORTH)

for i in range(900):
    inserter.tile_position = (i, 0)
    inserter.circuit_enabled = True
    inserter.set_circuit_condition(activation_signal, ">", i)
    bp.entities.append(inserter)
    try:
        bp.add_circuit_connection("red", bp.entities[i - 1], bp.entities[i])
    except IndexError:
        pass

print(bp.to_string())
