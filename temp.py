
import draftsman as factorio
from draftsman.entity import *
from draftsman.signatures import POSITION_SCHEMA
import pyperclip

def main():
    # Valid
    fast_belt = TransportBelt("fast-transport-belt", 
        position = [0, 0], direction = Direction.EAST,
        connections = {
            "1": {
                "green": [
                    {"entity_id": 1}
                ]
            }
        },
        control_behavior = {
            "circuit_enable_disable": True,
            "circuit_condition": {
                "first_signal": "signal-blue",
                "comparator": "=",
                "second_signal": "signal-blue"
            },
            "connect_to_logistic_network": True,
            "logistic_condition": {
                "first_signal": "fast-underground-belt",
                "comparator": ">=",
                "constant": 0
            },
            "circuit_read_hand_contents": False,
            "circuit_contents_read_mode": ModeOfOperation.NONE
        }
    )
    print(fast_belt.to_dict())
    #fast_belt.set_control_behavior({"whatever": "lmao"})
    print(fast_belt.control_behavior)



if __name__ == "__main__":
    main()