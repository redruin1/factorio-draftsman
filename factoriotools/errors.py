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

# Update
class IncompatableMod(Exception):
    pass

class MissingMod(Exception):
    pass

class IncorrectModVersion(Exception):
    pass