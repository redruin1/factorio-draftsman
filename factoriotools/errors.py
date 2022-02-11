# errors.py

# Utils
class MalformedBlueprintString(Exception):
    pass

# Blueprints
class IncorrectBlueprintType(Exception):
    pass

class DuplicateIDException(Exception):
    pass

# Tiles
class InvalidTileID(Exception):
    pass

# Signals
class InvalidSignalID(Exception):
    pass

# Entities
class InvalidEntityID(Exception):
    pass

# Update
class IncompatableMod(Exception):
    pass

class MissingMod(Exception):
    pass

class IncorrectModVersion(Exception):
    pass