# serialization.py

import attrs
import cattrs
from cattrs.gen._shared import find_structure_handler

import functools
from typing import Any, Callable

MASTER_CONVERTER = cattrs.Converter(omit_if_default=False)
MASTER_CONVERTER_OMIT_NONE = cattrs.Converter(omit_if_default=False)
MASTER_CONVERTER_OMIT_DEFAULTS = cattrs.Converter(omit_if_default=True)
MASTER_CONVERTER_OMIT_NONE_DEFAULTS = cattrs.Converter(omit_if_default=True)

# TODO: minimize boilerplate here


# @MASTER_CONVERTER.register_structure_hook_factory(attrs.has)
def regular_structure_factory(cls, converter):
    def resolve_location(sd, location):
        """
        Try and grab a nested key from a `location` tuple, and return the value
        if found.
        """
        while len(location) > 1:
            sd = sd[location[0]]
            location = location[1:]
        return sd[location[0]]

    def structure_hook(d, _):
        res = {}
        # print("d", d)
        for attr in attrs.fields(cls):
            # print("attr.name", attr.name)
            attr: attrs.Attribute
            # print(attr)
            if not attr.init:
                continue
            location = attr.metadata.get("location", (attr.name,))
            if location is None:
                continue
            # sd = d
            # while len(location) > 1:
            #     sd = sd[location[0]]
            #     location = location[1:]
            # print(sd)
            # Try getting the attribute from the input dict; If it fails, it's
            # either a default or an error which will be caught later
            try:
                value = resolve_location(d, location)
            except KeyError:
                continue
            # If the input object has its own special structuring hook, use that
            # print("value", value)
            handler = find_structure_handler(attr, attr.type, converter)
            if handler is not None:
                res[attr.name] = handler(value, attr.type)
            else:
                res[attr.name] = value
        return cls(**res)

    return structure_hook


MASTER_CONVERTER.register_structure_hook_factory(attrs.has, regular_structure_factory)


@MASTER_CONVERTER.register_unstructure_hook_factory(attrs.has)
def regular_unstructure_factory(cls: Any, converter: cattrs.Converter) -> Callable:
    def unstructure_hook(inst: attrs.AttrsInstance) -> dict:
        res = {}
        for attr in attrs.fields(type(inst)):
            attr: attrs.Attribute
            cattrs_hook = converter.get_unstructure_hook(attr.type)
            value = getattr(inst, attr.name)
            unstructured_value = cattrs_hook(value)
            if not attr.metadata.get("omit", False):
                location = attr.metadata.get("location", (attr.name,))
                r = res
                for i, loc in enumerate(location):
                    # print(i, loc)
                    # print(res)
                    if i < len(location) - 1:
                        if loc not in r:
                            r[loc] = {}
                        r = r[loc]
                    else:
                        r[loc] = unstructured_value
                        break
                # res[attr.name] = unstructured_value
        return res

    return unstructure_hook


@MASTER_CONVERTER_OMIT_NONE.register_unstructure_hook_factory(attrs.has)
def omit_none_unstructure_factory(cls: Any, converter: cattrs.Converter) -> Callable:
    def unstructure_hook(inst: attrs.AttrsInstance) -> dict:
        res = {}
        for attr in attrs.fields(type(inst)):
            attr: attrs.Attribute
            cattrs_hook = converter.get_unstructure_hook(attr.type)
            value = getattr(inst, attr.name)
            unstructured_value = cattrs_hook(value)
            if unstructured_value is not None and not attr.metadata.get("omit", False):
                location = attr.metadata.get("location", (attr.name,))
                r = res
                for i, loc in enumerate(location):
                    # print(i, loc)
                    # print(res)
                    if i < len(location) - 1:
                        if loc not in r:
                            r[loc] = {}
                        r = r[loc]
                    else:
                        r[loc] = unstructured_value
                        break
                # res[attr.name] = unstructured_value
        return res

    return unstructure_hook


def is_default(self: attrs.AttrsInstance, attribute: attrs.Attribute, value: Any):
    if isinstance(attribute.default, attrs.Factory):
        if attribute.default.takes_self:
            return value == attribute.default.factory(self)
        else:
            return value == attribute.default.factory()
    else:
        return attribute.default == value


@MASTER_CONVERTER_OMIT_DEFAULTS.register_unstructure_hook_factory(attrs.has)
def omit_default_unstructure_factory(cls: Any, converter: cattrs.Converter) -> Callable:
    def unstructure_hook(inst: attrs.AttrsInstance) -> dict:
        res = {}
        for attr in attrs.fields(type(inst)):
            attr: attrs.Attribute
            cattrs_hook = converter.get_unstructure_hook(attr.type)
            value = getattr(inst, attr.name)
            unstructured_value = cattrs_hook(value)
            if not (
                is_default(inst, attr, value)
                and not attr.metadata.get("omit", None) is False
            ):
                location = attr.metadata.get("location", (attr.name,))
                r = res
                for i, loc in enumerate(location):
                    # print(i, loc)
                    # print(res)
                    if i < len(location) - 1:
                        if loc not in r:
                            r[loc] = {}
                        r = r[loc]
                    else:
                        r[loc] = unstructured_value
                        break
                # res[attr.name] = unstructured_value
        return res

    return unstructure_hook


@MASTER_CONVERTER_OMIT_NONE_DEFAULTS.register_unstructure_hook_factory(attrs.has)
def omit_none_default_unstructure_factory(
    cls: Any, converter: cattrs.Converter
) -> Callable:
    def unstructure_hook(inst: attrs.AttrsInstance) -> dict:
        res = {}
        for attr in attrs.fields(type(inst)):
            attr: attrs.Attribute
            cattrs_hook = converter.get_unstructure_hook(attr.type)
            value = getattr(inst, attr.name)
            # print(attr.name)
            # print(type(inst))
            # print(value)
            unstructured_value = cattrs_hook(value)
            if attr.metadata.get("omit", None) is False or (
                value is not None and not is_default(inst, attr, value)
            ):
                location = attr.metadata.get("location", (attr.name,))
                r = res
                for i, loc in enumerate(location):
                    # print(i, loc)
                    # print(res)
                    if i < len(location) - 1:
                        if loc not in r:
                            r[loc] = {}
                        r = r[loc]
                    else:
                        r[loc] = unstructured_value
                        break
                # res[attr.name] = unstructured_value
        return res

    return unstructure_hook


# TODO
# def _explicit_exclude(obj):
#     excluded = {attr.name for attr in attrs.fields(obj) if not attr.metadata.get("excluded", True)}
#     r = {k: v for k, v in MASTER_CONVERTER.get_unstructure_hook(obj)() if k not in excluded and v is not None}


class DraftsmanConverters:
    def __init__(self):
        self.converters: dict[
            tuple[tuple[int, ...]], dict[tuple[bool, bool], cattrs.Converter]
        ] = {}

    def add_version(self, version) -> cattrs.Converter:
        self.converters[version] = {
            # (exclude_none, exclude_defaults)
            (False, False): MASTER_CONVERTER.copy(),
            (True, False): MASTER_CONVERTER_OMIT_NONE.copy(),
            (False, True): MASTER_CONVERTER_OMIT_DEFAULTS.copy(),
            (True, True): MASTER_CONVERTER_OMIT_NONE_DEFAULTS.copy(),
        }

    def register_structure_hook(self, *args, **kwargs):
        for version in self.converters.values():
            for _, converter in version.items():
                converter.register_structure_hook(*args, **kwargs)

    def register_structure_hook_factory(self, *args, **kwargs):
        for version in self.converters.values():
            for _, converter in version.items():
                converter.register_structure_hook_factory(*args, **kwargs)

    def register_unstructure_hook(self, *args, **kwargs):
        for version in self.converters.values():
            for _, converter in version.items():
                converter.register_unstructure_hook(*args, **kwargs)

    def register_unstructure_hook_factory(self, *args, **kwargs):
        for version in self.converters.values():
            for _, converter in version.items():
                converter.register_unstructure_hook_factory(*args, **kwargs)

    # @functools.cache
    # def __getitem__(self, item: tuple[int, ...]) -> cattrs.Converter:
    #     if item in self.converters:
    #         return self.converters[item]
    #     # Otherwise, get the version just "below" the specified version
    #     converters_with_item = [*self.converters.keys(), item]
    #     sorted_versions = list(sorted(converters_with_item))
    #     converter_to_use = sorted_versions[sorted_versions.index(item) - 1]
    #     return self.converters[converter_to_use]

    @functools.cache
    def get(
        self, version: tuple, exclude_none: bool = False, exclude_defaults: bool = False
    ):
        if version not in self.converters:
            # Get the version just "below" the specified version
            sorted_versions = list(sorted([*self.converters.keys(), version]))
            # print("sorted_versions", sorted_versions)
            try:
                version = sorted_versions[sorted_versions.index(version) - 1]
            except KeyError:
                raise ValueError("No converter exists for version {}".format(version))
            # print("selected_version", version)
        return self.converters[version][(exclude_none, exclude_defaults)]


draftsman_converters = DraftsmanConverters()
draftsman_converters.add_version((1, 0))
draftsman_converters.add_version((2, 0))


class exported_property(property):
    pass


# def exported_property(**kwargs):
#     def inner(cls):
#         pass
#     result = exported_property
#     result.extra = kwargs
#     return result


def finalize_fields(cls, fields: list[attrs.Attribute]) -> list[attrs.Attribute]:
    """
    Iterate over the "locations" in each field metadata and resolve any lambdas
    to fixed values.
    """
    # print([field.name for field in fields])
    for index, field in enumerate(fields):
        if field.metadata is not None and "location" in field.metadata:
            if field.metadata["location"] is None:
                continue
            new_metadata = dict(field.metadata)
            # print(new_metadata)
            l = list(new_metadata["location"])
            for i, item in enumerate(l):
                if callable(item):
                    l[i] = item(cls)
            new_metadata["location"] = tuple(l)
            # print(new_metadata)
            fields[index] = field.evolve(metadata=new_metadata)

    # TODO: something more sophisticated might be necessary
    # fields.sort(key=lambda attr: attr.name)
    # print([field.name for field in fields])
    return fields
