# schemas.py

from draftsman import __factorio_version_info__
from draftsman.serialization import MASTER_CONVERTER_OMIT_NONE_DEFAULTS

from typing import Optional


import copy
import jsonschema
import referencing

_schemas: dict[str, referencing.Resource] = {}
_cls_schemas: dict[type, referencing.Resource] = {}


def add_schema(cls, version, schema):
    # finialize the schema by traversing the MRO
    res = referencing.Resource.from_contents(schema)
    _schemas[schema["$id"]] = res
    _cls_schemas[cls] = res


def get_schema(cls):
    return _cls_schemas[cls], referencing.Registry().with_resources(_schemas.items())


# def resolve_schema(schema):
#     """Reduce a schema so that it contains no references to other schemas."""
#     resolved_schema = copy.deepcopy(schema)  # TODO: does this deepcopy?

#     if "$ref" in resolved_schema:
#         # print(resolved_schema["$ref"])
#         resolved_schema = merge(
#             resolve_schema(schemas[schema["$ref"]]), resolved_schema
#         )
#         # print(resolved_schema)
#         del resolved_schema["$ref"]
#     if "allOf" in resolved_schema:
#         for subschema in resolved_schema["allOf"]:
#             # print(subschema)
#             # print(resolve_schema(subschema))
#             resolved_schema = merge(resolve_schema(subschema), resolved_schema)
#         del resolved_schema["allOf"]
#     if "properties" in resolved_schema:
#         for property_name, property in resolved_schema["properties"].items():
#             # print(property_name, property)
#             resolved_subschema = resolved_schema["properties"][property_name]
#             resolved_schema["properties"][property_name] = merge(
#                 resolve_schema(property), resolved_subschema
#             )
#     # if "items" in schema:
#     # TODO

#     # print("resolved schema:", resolved_schema)

#     return resolved_schema


# schemas = {}


# class DraftsmanSchemas:
#     def __init__(self):
#         self._uri_schemas = {}
#         self._class_schemas = {}

#     def add_schema(self, schema, cls: Optional[type] = None):
#         if "$id" not in schema:
#             raise ValueError("invalid schema!")
#         resolved_schema = resolve_schema(schema)
#         self._uri_schemas[schema["$id"]] = resolved_schema
#         if cls is not None:
#             self._class_schemas[cls] = schema

#     def get_class_schema(
#         self, cls, version: tuple[int, ...] = __factorio_version_info__
#     ):
#         return self._class_schemas[cls]

#     def __getitem__(self, uri):
#         return self._schemas[uri]


# def add_schema(schema, cls: Optional[type] = None, mapping=None):
#     if "$id" not in schema:
#         raise ValueError("invalid schema!")
#     # resolved_schema = resolve_schema(schema)
#     schemas[schema["$id"]] = schema
#     if cls is not None:
#         schemas[cls] = schema


# def get_schema(cls, version: tuple[int, ...] = __factorio_version_info__):
#     return schemas[cls]


# def make_structure_from_JSON_schema(cls, format_dict):
#     def traverse_format(format: dict, input: dict):
#         # print("format:", format)
#         # print("d:", input)
#         res = {}
#         if "properties" in format:
#             for property_name, property in format["properties"].items():
#                 # print("\t", property_name, property)
#                 # location = property["location"]
#                 if "location" in property and property["location"] is None:
#                     input.pop(property_name)
#                     continue
#                 if property_name in input:
#                     # print(property)
#                     # If "location" is detected, set the attribute and avoid
#                     # travelling deeper into the tree
#                     if "location" in property:
#                         res[property["location"].name] = input[property_name]
#                         input.pop(property_name)
#                     elif property["type"] == "object":
#                         res.update(traverse_format(property, input[property_name]))
#                         # If the result dict becomes empty after traversal, delete it
#                         if not input[property_name]:
#                             input.pop(property_name)
#                     # else:
#                     #     res[property["location"].name] = input[property_name]
#                     #     input.pop(property_name)
#         # print("d exit:", input)
#         return res

#     def structure_hook(d: dict, t: type):
#         res = traverse_format(format_dict, d)

#         # print("test")
#         # print(res)
#         # print(d)

#         # If there's anything left in d, that is our unknown keys
#         if len(d) != 0:
#             res["unknown"] = d

#         return cls(**res)

#     return structure_hook


# def make_unstructure_from_JSON_schema(cls, format_dict):
#     parent_hook = MASTER_CONVERTER_OMIT_NONE_DEFAULTS.get_unstructure_hook(cls)

#     def unstructure_hook(inst):
#         res = parent_hook(inst)
#         print("res", res)
#         if inst.unknown:
#             merge(res, inst.unknown)
#         res.pop("unknown", None)
#         print("res after merge", res)
#         return res

#     return unstructure_hook


# add_schema(
#     {
#         "$schema": "http://json-schema.org/draft-07/schema#",
#         "$id": "factorio:color",
#         "type": "object",
#         "properties": {
#             "r": {"type": "number"},
#             "g": {"type": "number"},
#             "b": {"type": "number"},
#             "a": {"type": "number", "default": 1.0},
#         },
#         "requiredProperties": ["r", "g", "b"],
#     }
# )


# add_schema(
#     {
#         "$schema": "http://json-schema.org/draft-07/schema#",
#         "$id": "factorio:position",
#         "type": "object",
#         "properties": {"x": {"type": "number"}, "y": {"type": "number"}},
#         "requiredProperties": ["x", "y"],
#     }
# )
