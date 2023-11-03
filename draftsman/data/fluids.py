# fluids.py

import pickle

try:  # pragma: no coverage
    import importlib.resources as pkg_resources  # type: ignore
except ImportError:  # pragma: no coverage
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore

from draftsman import data
from draftsman.error import InvalidFluidError

with pkg_resources.open_binary(data, "fluids.pkl") as inp:
    _data = pickle.load(inp)
    raw: dict[str, dict] = _data[0]


def add_fluid(name, order, default_temperature, maximum_temperature=None, **kwargs):
    """
    Add a fluid. TODO
    """
    pass  # TODO


def get_temperature_range(fluid_name: str) -> tuple[float, float]:
    """
    Gets a tuple representing the [minimum, maximum] temperature range for the
    fluid with name ``fluid_name``. Primarily used for validation with
    InfinityPipes, but can be useful as a sanity check if fluid temperatures are
    being manually entered.

    :raises InvalidFluidError: if ``fluid_name`` is not a recognized fluid.

    :param fluid_name: The name of the fluid.
    :returns: A tuple of two floats, representing the minimum and maximum
        temperature this fluid can have, inclusive.
    """
    if fluid_name not in raw:
        raise InvalidFluidError("'{}'".format(fluid_name))

    # 'default_temperature' is required by FluidPrototype, and is equal to min
    min_temp = raw[fluid_name]["default_temperature"]

    # 'max_temperature' is optional, and defaults to 'default_temperature'
    max_temp = raw[fluid_name].get("max_temperature", min_temp)

    return (min_temp, max_temp)
