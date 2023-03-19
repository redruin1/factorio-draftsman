# memory.py
"""
Memory profiling with memory-profiler:
"""

from draftsman.blueprintable import BlueprintBook
from draftsman.data import entities, tiles

from memory_profiler import profile
from guppy import hpy


@profile
def main():
    # entities.add_entity("logistic-train-stop-input", "lamp", [[-0.2, -0.2], [0.2, 0.2]])
    # entities.add_entity("logistic-train-stop-output", "constant-combinator", [[-0.2, -0.2], [0.2, 0.2]])
    # entities.add_entity("logistic-train-stop", "train-stop", [[-0.2, -0.2], [0.2, 0.2]])
    
    #h = hpy()

    #h.setrelheap()
    with open("big_blueprint_book.txt") as file:
        bpb = BlueprintBook(file.read(), unknown="ignore") # TODO: unknown="error" | "pass"? | "ignore"

        print(bpb.label)

    #print(h.heap())


if __name__ == "__main__":
    main()