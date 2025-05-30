# serialization.py

import attrs
import cattrs
from cattrs.gen._shared import find_structure_handler
from cattrs._compat import is_bare_final
from cattrs.fns import identity
from cattrs.gen._lc import generate_unique_filename

import functools
from typing import Any, Callable, Optional, TypeVar

T = TypeVar('T')

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
        for attr in attrs.fields(cls):
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
            except (KeyError, TypeError):
                continue
            # If the input object has its own special structuring hook, use that
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


class ConverterVersion:
    def __init__(self):
        self.converters: dict[tuple[bool, bool], cattrs.Converter] = {
            # (exclude_none, exclude_defaults)
            (False, False): MASTER_CONVERTER.copy(),
            (True, False): MASTER_CONVERTER_OMIT_NONE.copy(),
            (False, True): MASTER_CONVERTER_OMIT_DEFAULTS.copy(),
            (True, True): MASTER_CONVERTER_OMIT_NONE_DEFAULTS.copy(),
        }
        self.structure_funcs = {}
        self.unstructure_funcs = {}
        self.schemas = {}
        self.cls_schemas = {}

    def register_structure_hook(self, *args, **kwargs):
        for _, converter in self.converters.items():
            converter.register_structure_hook(*args, **kwargs)

    def register_structure_hook_factory(self, *args, **kwargs):
        for _, converter in self.converters.items():
            converter.register_structure_hook_factory(*args, **kwargs)

    def register_unstructure_hook(self, *args, **kwargs):
        for _, converter in self.converters.items():
            converter.register_unstructure_hook(*args, **kwargs)

    def register_unstructure_hook_factory(self, *args, **kwargs):
        for _, converter in self.converters.items():
            converter.register_unstructure_hook_factory(*args, **kwargs)

    def get_converter(self, exclude_none: bool = False, exclude_defaults: bool = False):
        return self.converters[(exclude_none, exclude_defaults)]

    def add_schema(
        self,
        schema: dict,
        cls: Optional[type] = None,
    ):
        if "$schema" not in schema:
            schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        if "$id" in schema:
            self.schemas[schema["$id"]] = schema
        if cls:
            self.cls_schemas[cls] = schema

    def add_hook_fns(
        self,
        cls: type,
        structure_func: Optional[Callable],
        unstructure_func: Optional[Callable] = None,
    ):
        self.structure_funcs[cls] = structure_func
        if unstructure_func is not None:
            self.unstructure_funcs[cls] = unstructure_func

    def get_schema(self, cls):
        return self.cls_schemas[cls]

    def get_structure_dict(self, cls: type) -> dict:
        res = {}
        for subcls in reversed(cls.mro()):
            if subcls in self.structure_funcs:
                call_value = self.structure_funcs[subcls](attrs.fields(subcls))
                res.update(
                    {
                        (k,) if isinstance(k, str) else k: v
                        for k, v in call_value.items()
                    }
                )
        return res

    def get_unstructure_dict(self, cls: type, converter: cattrs.Converter) -> dict:
        res = {}
        for subcls in reversed(cls.mro()):
            if subcls in self.unstructure_funcs:
                res.update(
                    {
                        (k,) if isinstance(k, str) else k: v
                        for k, v in self.unstructure_funcs[subcls](
                            attrs.fields(subcls), converter
                        ).items()
                    }
                )
            elif subcls in self.structure_funcs:
                # use the reverse of the structure fuction
                res.update(
                    {
                        (k,) if isinstance(k, str) else k: v
                        for k, v in self.structure_funcs[subcls](
                            attrs.fields(subcls)
                        ).items()
                    }
                )
        return res


class DraftsmanConverters:
    def __init__(self):
        self.versions: dict[tuple[int, ...], ConverterVersion] = {}
        # self.external_formats: dict[tuple[int, ...], Callable] = {}

    def add_version(self, version) -> ConverterVersion:
        self.versions[version] = ConverterVersion()
        return self.versions[version]

    def register_structure_hook(self, *args, **kwargs):
        for version in self.versions.values():
            version.register_structure_hook(*args, **kwargs)

    def register_structure_hook_factory(self, *args, **kwargs):
        for version in self.versions.values():
            version.register_structure_hook_factory(*args, **kwargs)

    def register_unstructure_hook(self, *args, **kwargs):
        for version in self.versions.values():
            version.register_unstructure_hook(*args, **kwargs)

    def register_unstructure_hook_factory(self, *args, **kwargs):
        for version in self.versions.values():
            version.register_unstructure_hook_factory(*args, **kwargs)

    def add_schema(
        self,
        schema: dict[str, Any],
        cls: Optional[type] = None,
    ):
        # Normalize references and IDs to always use versions at end
        for version in self.versions.values():
            version.add_schema(schema, cls)

    def add_hook_fns(
        self,
        cls: type,
        structure_func: Callable[[tuple[attrs.Attribute, ...]], dict[str | tuple[str, ...], str]],
        unstructure_func: Optional[Callable[..., dict[str, str]]] = None,
    ):
        for version in self.versions.values():
            version.add_hook_fns(cls, structure_func, unstructure_func)

    # @functools.cache
    # def __getitem__(self, item: tuple[int, ...]) -> cattrs.Converter:
    #     if item in self.converters:
    #         return self.converters[item]
    #     # Otherwise, get the version just "below" the specified version
    #     converters_with_item = [*self.converters.keys(), item]
    #     sorted_versions = list(sorted(converters_with_item))
    #     converter_to_use = sorted_versions[sorted_versions.index(item) - 1]
    #     return self.converters[converter_to_use]

    # def register_external_format(self, cls, func, schema=None):
    #     self.external_formats[cls] = func

    # def get_location_dict(self, cls) -> dict:
    #     location_dict = {}
    #     for subcls in reversed(cls.mro()):
    #         if subcls in self.external_formats:
    #             location_dict.update(
    #                 {
    #                     k: (v,) if isinstance(v, str) else v
    #                     for k, v in self.external_formats[subcls](
    #                         attrs.fields(subcls)
    #                     ).items()
    #                 }
    #             )
    #     return location_dict

    @functools.cache
    def get_version(self, version: tuple[int, ...]):
        if version not in self.versions:
            # Get the version just "below" the specified version
            sorted_versions = list(sorted([*self.versions.keys(), version]))
            prev_version_index = sorted_versions.index(version) - 1
            # If this index is negative, it means there is no version below to use
            if prev_version_index < 0:
                msg = "No converter exists for version {}".format(version)
                raise ValueError(msg)
            version = sorted_versions[sorted_versions.index(version) - 1]

        return self.versions[version]


draftsman_converters = DraftsmanConverters()
draftsman_converters.add_version((1, 0))
draftsman_converters.add_version((2, 0))


# def finalize_fields(cls, fields: list[attrs.Attribute]) -> list[attrs.Attribute]:
#     """
#     Iterate over the "locations" in each field metadata and resolve any lambdas
#     to fixed values.
#     """
#     # TODO: better
#     # print([field.name for field in fields])
#     for index, field in enumerate(fields):
#         # print(field)
#         if (
#             not field.validator and not field.converter and not field.metadata
#         ):  # FIXME: scuffed
#             origin = get_origin(field.type)
#             t = origin if origin else field.type
#             # print(t)
#             converter = None
#             validators = []
#             if isinstance(t, Enum):
#                 converter = t
#                 validators.append(instance_of(t))
#             elif t is Union:
#                 union_validators = []
#                 # print("union")
#                 args = get_args(field.type)
#                 for arg in args:
#                     if get_origin(arg) is Annotated:
#                         # print("annotated")
#                         ano_args = get_args(arg)
#                         # print(ano_args)
#                         union_validators.append(ano_args[1])
#                     else:
#                         union_validators.append(instance_of(arg))
#                 validators = or_(*union_validators)
#             else:
#                 validators.append(instance_of(t))
#             if converter is None:
#                 fields[index] = field.evolve(validator=validators)
#             else:
#                 fields[index] = field.evolve(converter=converter, validators=validators)

#         # Shouldn't need this anymore
#         # if field.metadata is not None and "location" in field.metadata:
#         #     if field.metadata["location"] is None:
#         #         continue
#         #     new_metadata = dict(field.metadata)
#         #     # print(new_metadata)
#         #     l = list(new_metadata["location"])
#         #     for i, item in enumerate(l):
#         #         if callable(item):
#         #             l[i] = item(cls)
#         #     new_metadata["location"] = tuple(l)
#         #     # print(new_metadata)
#         #     fields[index] = field.evolve(metadata=new_metadata)
#         # if issubclass(field.type, Enum):
#         #     print(field.name)

#     # TODO: something more sophisticated might be necessary
#     # fields.sort(key=lambda attr: attr.name)
#     # print([field.name for field in fields])
#     return fields


# def make_structure_function_from_schema(
#     cls: type, converter: cattrs.Converter, schema: dict
# ):
#     def try_pop_location(subdict, loc):
#         """
#         Traverse loc and try to pop that item, as well as any subdicts that
#         become empty in the process.
#         """
#         if loc is None:
#             return None
#         if len(loc) == 1:
#             try:
#                 return subdict.pop(loc[0], None)
#             except AttributeError:
#                 return None
#         if loc[0] not in subdict:
#             return None
#         result = try_pop_location(subdict[loc[0]], loc[1:])
#         if subdict[loc[0]] == {}:
#             subdict.pop(loc[0])
#         return result

#     class_attrs = attrs.fields(cls)
#     # version_data = draftsman_converters.get_version(version_tuple)
#     # location_dict = version_data.get_location_dict(cls)

#     def structure_hook(input_dict: dict, _: type):
#         res = {}
#         for attr in class_attrs:
#             # attr_name = attr.alias if attr.alias is not None else attr.name
#             # print("attr name:", attr.name, attr.alias)
#             if attr.name not in schema:
#                 continue
#             loc = schema[attr.name]

#             value = try_pop_location(input_dict, loc)
#             # print(value)
#             if value is None:
#                 continue
#             handler = find_structure_handler(attr, attr.type, converter)
#             if handler is not None:
#                 # import inspect
#                 # print(inspect.getsource(handler))
#                 try:
#                     res[attr.name] = handler(value, attr.type)
#                 except Exception as e:
#                     raise DataFormatError(e) from None
#             else:
#                 res[attr.name] = value

#         if input_dict:
#             res["extra_keys"] = input_dict

#         # print(location_dict)
#         # print(res)
#         return res
#         # return cls(**res)

#     return structure_hook


def make_unstructure_function_from_schema(
    cls: type,
    converter: cattrs.Converter,
    schema: dict,
    exclude_none: bool,
    exclude_defaults: bool,
    version: tuple,
):
    """
    Generates an unstructure function based on an input-output mapping dictionary.
    """
    fn_name = "unstructure_" + cls.__name__
    globs = {}
    lines = []
    invocation_tree = {"lines": []}
    internal_arg_parts = {}

    def populate_invocate_tree(invocation_tree: dict, loc: tuple[str], invoke: str):
        if "lines" not in invocation_tree:
            invocation_tree["lines"] = []
        if "children" not in invocation_tree:
            invocation_tree["children"] = {}
        if len(loc) == 1:
            invocation_tree["lines"].append(f"'{loc[0]}': {invoke},")
        else:
            if loc[0] not in invocation_tree["children"]:
                invocation_tree["children"][loc[0]] = {"name": loc[0]}
                invocation_tree["lines"].append(invocation_tree["children"][loc[0]])
            populate_invocate_tree(invocation_tree["children"][loc[0]], loc[1:], invoke)

    def calc_getitem(loc):
        return "".join([f"['{l}']" for l in loc])

    for dict_loc, inst_loc in schema.items():
        # print(dict_loc, inst_loc)
        if dict_loc is None or inst_loc is None:
            continue
        handler = None
        user_handler = False
        if isinstance(inst_loc, attrs.Attribute):  # TODO: make this baseline
            # handler = inst_loc
            # attr_name = "_".join(dict_loc)
            # print("\t", attr_name)
            a = inst_loc
            attr_name = a.name
        elif isinstance(inst_loc, tuple):
            a: attrs.Attribute = inst_loc[0]
            attr_name = a.name
            handler = inst_loc[1]
            user_handler = True
        else:
            a: attrs.Attribute = getattr(attrs.fields(cls), inst_loc)
            attr_name = a.name
            # source_attr_name = a.name

        omittable = a.metadata.get("omit", True)
        never_null = a.metadata.get("never_null", False)

        # override = kwargs.get(attr_name, neutral)
        # if override.omit:
        #     continue
        # if override.omit is None and not a.init and not _cattrs_include_init_false:
        #     continue
        # if override.rename is None:
        #     kn = attr_name if not _cattrs_use_alias else a.alias
        # else:
        #     kn = override.rename

        d = a.default

        # For each attribute, we try resolving the type here and now.
        # If a type is manually overwritten, this function should be
        # regenerated.
        if handler is None:
            if a.type is not None:
                t = a.type

                # if handler is None:
                if (
                    is_bare_final(t)
                    and a.default is not attrs.NOTHING
                    and not isinstance(a.default, attrs.Factory)
                ):  # pragma: no branch
                    # This is a special case where we can use the
                    # type of the default to dispatch on.
                    t = a.default.__class__  # pragma: no coverage
                try:
                    handler = converter.get_unstructure_hook(t, cache_result=False)
                except RecursionError:  # pragma: no coverage
                    # There's a circular reference somewhere down the line
                    handler = converter.unstructure
            else:
                handler = converter.unstructure

        is_identity = handler == identity

        if not is_identity:
            unstruct_handler_name = f"__c_unstr_{attr_name}"
            globs[unstruct_handler_name] = handler
            internal_arg_parts[unstruct_handler_name] = handler
            if user_handler:
                invoke = f"{unstruct_handler_name}(instance)"
            else:
                invoke = f"{unstruct_handler_name}(instance.{attr_name})"
        else:
            invoke = f"instance.{attr_name}"

        if (
            exclude_none or (d is not attrs.NOTHING and exclude_defaults)
        ) and omittable:
            # write to local val
            if user_handler:
                lines.append(f"  val = {invoke}")
                value = "val"
            else:
                value = f"instance.{attr_name}"

            conditions = []
            if exclude_none or never_null:
                conditions.append(f"{value} is not None")
            if exclude_defaults:
                def_name = f"__c_def_{attr_name}"
                if isinstance(d, attrs.Factory):
                    globs[def_name] = d.factory
                    internal_arg_parts[def_name] = d.factory
                    if d.takes_self:
                        conditions.append(f"{value} != {def_name}(instance)")
                    else:
                        conditions.append(f"{value} != {def_name}()")
                else:
                    globs[def_name] = d
                    internal_arg_parts[def_name] = d
                    conditions.append(f"{value} != {def_name}")

            conditions = " and ".join(conditions)
            lines.append(f"  if {conditions}:")
            subloc = []

            for i, l in enumerate(dict_loc):
                subloc.append(l)
                if i != len(dict_loc) - 1:
                    lines.append(f"    if '{l}' not in res{calc_getitem(subloc[:-1])}:")
                    lines.append(f"      res{calc_getitem(subloc)} = {{}}")
                else:
                    if user_handler:
                        lines.append(f"    res{calc_getitem(subloc)} = val")
                    else:
                        lines.append(f"    res{calc_getitem(subloc)} = {invoke}")
        else:
            # If `never_null` is True, it means that (even if exclude_none/
            # defaults is `False`) then we still have to only add the key if it's
            # not None:
            if never_null:
                lines.append(f"  if instance.{attr_name} is not None:")
                subloc = []

                for i, l in enumerate(dict_loc):
                    subloc.append(l)
                    if i != len(dict_loc) - 1:
                        lines.append(
                            f"    if '{l}' not in res{calc_getitem(subloc[:-1])}:"
                        )
                        lines.append(f"      res{calc_getitem(subloc)} = {{}}")
                    else:
                        lines.append(f"    res{calc_getitem(subloc)} = {invoke}")
            else:
                # No default or no override.
                populate_invocate_tree(invocation_tree, dict_loc, invoke)

    internal_arg_line = ", ".join([f"{i}={i}" for i in internal_arg_parts])
    if internal_arg_line:
        internal_arg_line = f", {internal_arg_line}"
    for k, v in internal_arg_parts.items():
        globs[k] = v

    def resolve_tree(tree, indent=4):
        res = []
        for line in tree["lines"]:
            if isinstance(line, dict):
                key = line["name"]
                res += [(" " * indent) + f"'{key}': {{"]
                res += resolve_tree(line, indent + 2)
                res += [(" " * indent) + "},"]
            else:
                res += [(" " * indent) + line]
        return res

    total_lines = (
        [f"def {fn_name}(instance{internal_arg_line}):"]
        + ["  res = {"]
        + resolve_tree(invocation_tree)
        + ["  }"]
        + lines
        + ["  return res"]
    )
    script = "\n".join(total_lines)
    # print(cls.__name__)
    # print(script)
    fname = generate_unique_filename(
        cls, "unstructure {}".format(version), lines=total_lines
    )

    eval(compile(script, fname, "exec"), globs)

    res = globs[fn_name]

    return res
