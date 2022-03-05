# errors.py

# Utils
class MalformedBlueprintString(Exception):
    pass

# Blueprints
class IncorrectBlueprintType(Exception):
    pass

class DuplicateIDException(Exception):
    pass

class EntityNotCircuitConnectable(Exception):
    pass

class EntityNotPowerConnectable(Exception):
    pass

# Tiles
class InvalidTileID(Exception):
    pass

# Signals
class InvalidSignalID(Exception):
    pass

# Items
class InvalidItemID(Exception):
    pass

# Entities
class InvalidEntityID(Exception):
    pass

class InvalidConditionOperation(Exception):
    pass

class InvalidArithmeticOperation(Exception):
    pass

class InvalidMode(Exception):
    pass

class InvalidWireType(Exception):
    """
    Raised when either a circuit wire is not either "red" or "green" or
    when a power wire connection type is not either "Cu0" or "Cu1".
    """
    pass

class InvalidConnectionSide(Exception):
    """
    Raised when a circuit connection is connected to a side other than "1" or 
    "2".
    """
    pass

class InvalidRecipeID(Exception):
    pass

class InvalidModuleID(Exception):
    pass

class InvalidFluidID(Exception):
    pass

# Update
class IncompatableMod(Exception):
    pass

class MissingMod(Exception):
    pass

class IncorrectModVersion(Exception):
    pass