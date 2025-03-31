# serialization.py

import attrs
import cattrs

import functools
from typing import Any, Callable

MASTER_CONVERTER = cattrs.Converter(omit_if_default=False)
MASTER_CONVERTER_OMIT_NONE = cattrs.Converter(omit_if_default=False)
MASTER_CONVERTER_OMIT_DEFAULTS = cattrs.Converter(omit_if_default=True)
MASTER_CONVERTER_OMIT_NONE_DEFAULTS = cattrs.Converter(omit_if_default=True)

# TODO: minimize boilerplate here

@MASTER_CONVERTER.register_structure_hook_factory(attrs.has)
def regular_structure_factory(cls):
    nonstandard_attrs = {attr.name: attr for attr in attrs.fields(cls) if "location" in attr.metadata}
    def structure_hook(d, _):
        res = {}
        for attr in attrs.fields(cls):
            attr: attrs.Attribute
            if not attr.init:
                continue
            location = attr.metadata.get("location", (attr.name,))
            if location is None:
                continue
            sd = d
            while len(location) > 1:
                sd = sd[location[0]]
                location = location[1:]
            res[attr.name] = sd[location[0]]
        return cls(**res)

    return structure_hook

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
            if not (is_default(inst, attr, value) and not attr.metadata.get("omit", None) is False):
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
def omit_none_default_unstructure_factory(cls: Any, converter: cattrs.Converter) -> Callable:
    def unstructure_hook(inst: attrs.AttrsInstance) -> dict:
        res = {}
        for attr in attrs.fields(type(inst)):
            attr: attrs.Attribute
            cattrs_hook = converter.get_unstructure_hook(attr.type)
            value = getattr(inst, attr.name)
            unstructured_value = cattrs_hook(value)
            if attr.metadata.get("omit", None) is False or (value is not None and not is_default(inst, attr, value)):
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
        self.converters : dict[tuple[tuple, bool, bool], cattrs.Converter] = {}

    def add_version(self, version) -> cattrs.Converter:
        # (version, exclude_none, exclude_defaults)
        self.converters[(version, False, False)] = MASTER_CONVERTER.copy()
        self.converters[(version, True, False)] = MASTER_CONVERTER_OMIT_NONE.copy()
        self.converters[(version, False, True)] = MASTER_CONVERTER_OMIT_DEFAULTS.copy()
        self.converters[(version, True, True)] = MASTER_CONVERTER_OMIT_NONE_DEFAULTS.copy()
        # return self.converters[version]

    def register_unstructure_hook(self, *args, **kwargs):
        for converter in self.converters.values():
            converter.register_unstructure_hook(*args, **kwargs)

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
    def get(self, version: tuple, exclude_none: bool, exclude_defaults: bool):
        sig = (version, exclude_none, exclude_defaults)
        if sig not in self.converters:
            # Get the version just "below" the specified version
            sorted_versions = list(sorted([*self.converters.keys(), sig]))
            sig = sorted_versions[sorted_versions.index(sig) - 1]
        return self.converters[sig]

draftsman_converters = DraftsmanConverters()
draftsman_converters.add_version((1, 0))
draftsman_converters.add_version((2, 0))