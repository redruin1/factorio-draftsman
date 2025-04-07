# memory.py
"""
Memory profiling with memory-profiler:
"""

from draftsman.blueprintable import BlueprintBook
from draftsman.data import entities, tiles

from memory_profiler import profile
from guppy import hpy

import os


# @profile
def main():
    entities.add_entity("logistic-train-stop-input", "lamp", [[-0.2, -0.2], [0.2, 0.2]])
    entities.add_entity("logistic-train-stop-output", "constant-combinator", [[-0.2, -0.2], [0.2, 0.2]])
    entities.add_entity("logistic-train-stop", "train-stop", [[-0.2, -0.2], [0.2, 0.2]])

    dirname = os.path.dirname(__file__)

    h = hpy()

    h.setrelheap()
    with open(os.path.join(dirname, "big_blueprint_book.txt")) as file:
        bpb = BlueprintBook.from_string(file.read())
        # bpb = BlueprintBook(
        #     file.read(), unknown="ignore"
        # )  # TODO: unknown="error" | "pass"? | "ignore"
        # print(bpb.blueprints)
        # print(bpb.to_dict())

    print(h.heap())


if __name__ == "__main__":
    main()
