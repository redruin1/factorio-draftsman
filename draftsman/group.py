# group.py

# TODO: documentation!

from draftsman.entity import EntityLike


class Group(EntityLike):
    """
    Group entities together, so you can move and rotate them all as one unit.

    groups can have unique name and id:
        "grouptype1", id = "A"
        "grouptype2", id = "B"
        "grouptype3", id = "C"

    # This would only get groups with name "grouptype1"
    entities = blueprint.find_entities_filtered(name = "grouptype1")

    # This would get the one group with id "A"
    entity = blueprint.find_entity_by_id("A")
    """
    def __init__(self, name: str = "group", **kwargs):
        super(Group, self).__init__(name, **kwargs)

        self.exports = None

        self.entities = []
        if "entities" in kwargs:
            self.set_entities(kwargs["entities"])

    def set_entities(self, entities: list[EntityLike]) -> None:
        """
        """
        for entity in entities:
            # TODO: make sure that entity is actually an entity
            # TODO: calculate self.width and self.height by the min/max of the entities position/sizes
            pass
            
        self.entities = entities

    def to_dict(self):
        """
        Converts the group to JSON representation.

        Maybe return a list of dicts, and then add each one to blueprint?
        TODO: think of a more generic way of handling this
        """
        out = []
        for entity in self.entities:
            # Offset the entities position by the groups position
            out.append(entity.to_dict())
        
        return out