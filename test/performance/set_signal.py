# set_signal.py

from draftsman.data import signals
from draftsman.entity import ConstantCombinator


entity = ConstantCombinator()
some_signals = [signal for signal in list(signals.raw.keys())[:1000]]

section = entity.add_section()


def main():
    for i in range(1000):
        section.set_signal(i, some_signals[i], count=1234)


if __name__ == "__main__":
    main()
