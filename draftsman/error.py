# errors.py

# TODO: documentation!


class DraftsmanError(Exception):
    """
    Root default error for `draftsman`.
    """
    pass

# Utils
class MalformedBlueprintStringError(DraftsmanError):
    """
    """
    pass

# Blueprints
class IncorrectBlueprintTypeError(DraftsmanError):
    pass

class DuplicateIDError(DraftsmanError):
    pass

class EntityNotPowerConnectableError(DraftsmanError):
    pass

class EntityNotCircuitConnectableError(DraftsmanError):
    pass

class UnreasonablySizedBlueprintError(DraftsmanError):
    pass

# Tiles
class InvalidTileError(DraftsmanError):
    pass

# Signals
class InvalidSignalError(DraftsmanError):
    pass

# Items
class InvalidItemError(DraftsmanError):
    pass

# Entities
class InvalidEntityError(DraftsmanError):
    pass

class InvalidOperationError(DraftsmanError):
    pass

class InvalidModeError(DraftsmanError):
    pass

class InvalidWireTypeError(DraftsmanError):
    """
    Raised when either a circuit wire is not either "red" or "green" or
    when a power wire connection type is not either "Cu0" or "Cu1".
    """
    pass

class InvalidConnectionSideError(DraftsmanError):
    """
    Raised when a circuit connection is connected to a side other than "1" or 
    "2".
    """
    pass

class InvalidRecipeError(DraftsmanError):
    pass

class InvalidModuleError(DraftsmanError):
    pass

class InvalidSideError(DraftsmanError):
    """
    Raised when a Splitter's input or output priority is set to something other
    than 'left' or 'right'.
    """
    pass

class InvalidFluidError(DraftsmanError):
    pass

class BarIndexError(DraftsmanError):
    pass

class FilterIndexError(DraftsmanError):
    pass

# Update
class IncompatableModError(DraftsmanError):
    pass

class MissingModError(DraftsmanError):
    pass

class IncorrectModVersionError(DraftsmanError):
    pass