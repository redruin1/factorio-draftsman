# set_signal.py

from draftsman.blueprintable import Blueprint
from draftsman.entity import ConstantCombinator
from draftsman.data.signals import signal_dict


def main():
    # blueprint = Blueprint()
    # blueprint.entities.append("constant-combinator", tile_position = (i, 0))
    entity = ConstantCombinator()

    n_iter = 1000000
    entity._control_behavior["filters"] = [0] * entity.item_slot_count
    for i in range(n_iter):
        # entity.set_signal(i % entity.item_slot_count, "signal-A", 100)
        index = i % entity.item_slot_count
        entity._control_behavior["filters"][index] = {
            "index": index + 1,
            "signal": {"name": "signal-A", "type": "virtual"},
            "count": 100,
        }


if __name__ == "__main__":
    main()
