# fluids.py

import pickle

import importlib.resources as pkg_resources

from draftsman import data
from draftsman.error import InvalidFluidError

with pkg_resources.open_binary(data, "fluids.pkl") as inp:
    _data = pickle.load(inp)
    raw: dict[str, dict] = _data[0]


def add_fluid(name: str, order: str = None, **kwargs):
    """
    Add a new fluid, or modify the properties of an existing fluid. Useful for
    simulating a modded environment without having to fully supply an entire
    mod configuration for simple scripts.
    """
    existing_data = raw.get(name, {})
    default_temperature = existing_data.get(
        "default_temperature", kwargs.get("default_temperature", 25)
    )
    raw[name] = {
        **existing_data,
        "type": "fluid",
        "name": name,
        "order": order if order is not None else "",
        "default_temperature": default_temperature,
        **kwargs,
    }
    # TODO: this should also update signals
    # TODO: what if the user sets auto-barrel to true in this function? Ideally
    # it would also generate barreling recipes and update them accordingly


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
