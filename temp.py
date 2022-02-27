
import draftsman as factorio
from draftsman.entity import *
from draftsman.errors import InvalidSignalID
from draftsman.entity import signal_dict
from schema import Schema, And, Use, Or, SchemaError
import pyperclip

def main():
    blueprint = factorio.Blueprint()

    substation = ElectricPole("substation", id = "1")
    power_switch = PowerSwitch(id = "2")

    substation.add_power_connection(power_switch)
    #power_switch.add_power_connection(substation)

    print(substation)
    print(power_switch)

if __name__ == "__main__":
    main()