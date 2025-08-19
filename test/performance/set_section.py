# set_signal.py

from draftsman.data import signals
from draftsman.entity import ConstantCombinator


def main():
    entity = ConstantCombinator()
    for _ in range(100):
        entity.add_section()


if __name__ == "__main__":
    main()
