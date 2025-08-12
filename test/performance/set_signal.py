# set_signal.py

from draftsman.blueprintable import Blueprint
from draftsman.data import signals
from draftsman.entity import ConstantCombinator
from draftsman.data.signals import signal_dict


def main():
    entity = ConstantCombinator()
    some_signals = [signal for signal in signals.raw.keys()[0:1000]]

    n_iter = 1000000
    section = entity.add_section()
    for i in range(n_iter):
        index = i % 1000
        section.set_signal(index, some_signals[index], count=1234)
        if index == 999:
            section = entity.add_section()


if __name__ == "__main__":
    main()
