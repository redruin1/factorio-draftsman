# ltn_train_stop.py

"""
Example of a custom Entity subclass. For those unfamiliar with LTN, Logistics
Train Stops are actually collections of 3 entities; the train stop itself, an
input lamp, and an ouput combinator. These entities are added and removed as a
group, so it makes sense to treat them all as a single entity.

In game, this process is simple, as you can just place the stop itself and the
sub-entities will automatically be placed and removed for you, even from 
blueprints. A problem arises, however, if you want to connect the input and/or 
output to something entirely from script, as those entities do not exist before
the blueprint is placed. In this case, you would want to handle the placement of
these sub-entities yourself, which would either require importing from an 
existing blueprint string (janky) or placing the input and output entities by 
hand (tedius).

Alternatively, you can use this class instead, which moves and orients the 
input and output entities based on the position and direction of the parent
train stop every time they are modified. The sub-entities are accessable as
`ltn_stop.input` and `ltn_stop.output`.
"""

from draftsman.classes.blueprint import Blueprint, EntityList
from draftsman.classes.entity_like import EntityLike

# from draftsman.classes.entitylist import EntityList
from draftsman.constants import Direction
from draftsman.entity import TrainStop, ConstantCombinator, Lamp
from draftsman.error import MissingModError

import draftsman.data.mods

from typing import Union


class LogisticTrainStop(TrainStop):
    """
    Wrapper around the LTN Train Stop.
    """

    def __init__(self, name="logistic-train-stop", **kwargs):
        # type: (str, **dict) -> None
        # Because these entities are located inside of the Train stop itself,
        # we don't have to worry about separate collision areas other than the
        # parent train stop, so we don't need to bother with SpatialHashMap
        self.input = Lamp("logistic-train-stop-input", id="input")
        self.output = ConstantCombinator("logistic-train-stop-output", id="output")
        # We create an EntityList so that the parent can access via
        self.entities = EntityList(self, [self.input, self.output])

        # We initialize the base, which will call this classes implementations
        # of position, tile_position, and direction
        super(LogisticTrainStop, self).__init__(name, similar_entities=[name], **kwargs)

    @TrainStop.position.setter
    def position(self, value):
        # type: (Union[dict, list, tuple]) -> None
        # Concerning syntax, but necessary
        super(LogisticTrainStop, type(self)).position.fset(self, value)
        self._adjust_sub_entities()

    @TrainStop.tile_position.setter
    def tile_position(self, value):
        # type: (Union[dict, list, tuple]) -> None
        super(LogisticTrainStop, type(self)).tile_position.fset(self, value)
        self._adjust_sub_entities()

    @TrainStop.direction.setter
    def direction(self, value):
        # type: (Direction) -> None
        super(LogisticTrainStop, type(self)).direction.fset(self, value)
        self._adjust_sub_entities()

    def on_entity_insert(self, _):
        pass

    def get(self):
        # type: () -> list[EntityLike]
        """
        Return a list of the parent train stop, as well as the input and output
        entities.
        """
        # self.input._id = (self.id, self.input.id)
        # self.output._id = (self.id, self.output.id)
        return [super(LogisticTrainStop, self), self.input, self.output]

    def _adjust_sub_entities(self):
        # type: () -> None
        """
        Adjust the position and orientation of the input and output entities.
        """
        # A quirk of the initialization process:
        # On very first init, direction attribute might not be set yet; it gets
        # re-attempted when it goes through the DirectionalMixin
        # If it hasn't, wait until it has before attempting to move sub-entities
        if not hasattr(self, "direction"):
            return

        input_offset_dict = {0: [1, 0], 2: [1, 1], 4: [0, 1], 6: [0, 0]}
        output_offset_dict = {0: [0, 0], 2: [1, 0], 4: [1, 1], 6: [0, 1]}
        stop_position = [self.tile_position["x"], self.tile_position["y"]]

        offset = input_offset_dict[self.direction]
        self.input.tile_position = (
            stop_position[0] + offset[0],
            stop_position[1] + offset[1],
        )

        offset = output_offset_dict[self.direction]
        self.output.tile_position = (
            stop_position[0] + offset[0],
            stop_position[1] + offset[1],
        )
        self.output.direction = self.direction


def main():
    # This script will only work if we have the LTN mod installed and enabled,
    # so we check to make sure that's met before starting
    if not draftsman.data.mods.mod_list.get("LogisticTrainNetwork", False):
        raise MissingModError("LogisticTrainNetwork")

    blueprint = Blueprint()

    train_stop = LogisticTrainStop(tile_position=(4, 0), direction=Direction.EAST)
    # To illustrate that the base class is also working
    train_stop.id = "ltn_stop"
    train_stop.color = (0, 0, 0)
    train_stop.station = "test"
    blueprint.entities.append(train_stop)

    blueprint.entities.append("medium-electric-pole", id="test")
    blueprint.add_circuit_connection("red", "test", ("ltn_stop", "input"))
    blueprint.add_circuit_connection("green", "test", ("ltn_stop", "output"))

    print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":
    main()
