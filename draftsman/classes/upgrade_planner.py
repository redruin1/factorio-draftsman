# upgrade_planner.py

"""
.. code-block:: python

    >>> from draftsman.blueprintable import UpgradePlanner
    >>> UpgradePlanner.Format.schema_json(indent=4)
"""

from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.exportable import Exportable
from draftsman.constants import ValidationMode
from draftsman.data import entities, items, signals
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    Comparator,
    QualityID,
    ItemID,
    EntityFilter,
    normalize_comparator,
    uint8,
    uint16,
    uint64,
)
from draftsman.utils import reissue_warnings
from draftsman.validators import conditional, instance_of, one_of, try_convert
from draftsman.warning import (
    IndexWarning,
    NoEffectWarning,
    UnknownElementWarning,
    UpgradeProhibitedWarning,
)

import attrs
import bisect
from typing import Literal, Optional, Sequence, Union
import warnings


@attrs.define
class UpgradeMapperSource(Exportable):
    type: Literal["entity", "item"] = attrs.field(validator=one_of("entity", "item"))
    """
    The type of this particular mapping, either ``"entity"`` or ``"item"``.
    """
    name: Optional[str] = attrs.field(validator=instance_of(Optional[str]))
    """
    Name of the item or entity being upgraded from.
    """
    quality: Literal[None, QualityID] = attrs.field(
        default=None,
        validator=one_of(Literal[None, QualityID]),
        metadata={"never_null": True},
    )
    """
    The item/entity quality to compare against.
    """
    comparator: Comparator = attrs.field(
        default="=",
        converter=try_convert(normalize_comparator),
        validator=one_of(Comparator),
    )
    """
    The comparison operation to use when determining which items/entities to 
    upgrade.
    """
    module_filter: Optional[EntityFilter] = attrs.field(
        default=None,
        converter=EntityFilter.converter,
        validator=instance_of(Optional[EntityFilter]),
    )
    """
    When upgrading modules, this defines the specific entities to apply the 
    upgrade to. ``None`` applies it to all entities.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, str):
            return cls(name=value, type=signals.get_mapper_type(value))
        elif isinstance(value, dict):
            return cls(**value)
        return value


draftsman_converters.get_version((1, 0)).add_hook_fns(
    UpgradeMapperSource,
    lambda fields: {
        "type": fields.type.name,
        "name": fields.name.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    UpgradeMapperSource,
    lambda fields: {
        "type": fields.type.name,
        "name": fields.name.name,
        "quality": fields.quality.name,
        "comparator": fields.comparator.name,
        "module_filter": fields.module_filter.name,
    },
)


@attrs.define
class UpgradeMapperDestination(Exportable):
    type: Literal["entity", "item"] = attrs.field(validator=one_of("entity", "item"))
    """
    The type of this particular mapping, either ``"entity"`` or ``"item"``.
    """
    name: Optional[str] = attrs.field(
        default=None, validator=instance_of(Optional[str])
    )
    """
    Name of the item or entity being upgraded to.
    """
    quality: Literal[None, QualityID] = attrs.field(
        default=None,
        validator=one_of(Literal[None, QualityID]),
        metadata={"never_null": True},
    )
    """
    The entity quality to upgrade to.
    """
    module_limit: Optional[uint16] = attrs.field(
        default=None, validator=instance_of(Optional[uint16])
    )
    """
    When upgrading modules, this defines the maximum number of this module to be 
    installed in the destination entity. ``0`` or ``None`` means no limit.
    """
    module_slots: Optional[list[ItemID]] = attrs.field(
        default=[], validator=instance_of(Optional[list[ItemID]])
    )
    """
    When upgrading entities, this defines which modules to be installed in 
    the destination entity.
    """

    @classmethod
    def converter(cls, value):
        if isinstance(value, str):
            return cls(name=value, type=signals.get_mapper_type(value))
        elif isinstance(value, dict):
            return cls(**value)
        return value


draftsman_converters.get_version((1, 0)).add_hook_fns(
    UpgradeMapperDestination,
    lambda fields: {
        "type": fields.type.name,
        "name": fields.name.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    UpgradeMapperDestination,
    lambda fields: {
        "type": fields.type.name,
        "name": fields.name.name,
        "quality": fields.quality.name,
        "module_limit": fields.module_limit.name,
        "module_slots": fields.module_slots.name,
    },
)


@attrs.define
class Mapper(Exportable):
    index: uint64 = attrs.field(validator=instance_of(uint64))
    """
    Index of this mapper in the upgrade planner's GUI.
    """
    from_: Optional[UpgradeMapperSource] = attrs.field(
        default=None,
        converter=UpgradeMapperSource.converter,
        validator=instance_of(Optional[UpgradeMapperSource]),
    )
    """
    Which item/entity to upgrade from.
    """
    to: Optional[UpgradeMapperDestination] = attrs.field(
        default=None,
        converter=UpgradeMapperDestination.converter,
        validator=instance_of(Optional[UpgradeMapperDestination]),
    )
    """
    Which item/entity to upgrade to.
    """

    @classmethod
    def converter(cls, value):
        try:
            return cls(
                index=value["index"],
                from_=value.get("from", None),
                to=value.get("to", None),
            )
        except TypeError:
            return value


draftsman_converters.add_hook_fns(
    Mapper,
    lambda fields: {
        "index": fields.index.name,
        "from": fields.from_.name,
        "to": fields.to.name,
    },
)


def check_valid_upgrade_pair(
    from_obj: UpgradeMapperSource | None, to_obj: UpgradeMapperDestination | None
) -> list[Warning]:
    """
    Checks two :py:data:`MAPPING_ID` objects to see if it's possible for
    ``from_obj`` to upgrade into ``to_obj``.

    :param from_obj: A ``dict`` containing a ``"name"`` and ``"type"`` key, or
        ``None`` if that entry was null.
    :param to_obj: A ``dict`` containing a ``"name"`` and ``"type"`` key , or
        ``None`` if that entry was null.

    :returns: A list of one or more Warning objects containing the reason why
        the mapping would be invalid, or ``None`` if no reason could be deduced.
    """

    # First we need to check if Draftsman even recognizes both from and to,
    # because if not then Draftsman cannot possibly expect to know whether the
    # upgrade pair is valid or not; hence, we early exit with a simple
    # "unrecognized entity/item" warning:
    unrecognized = []
    if (
        from_obj is not None
        and from_obj.name not in entities.raw
        and from_obj.name not in items.raw
    ):
        unrecognized.append(
            UnknownElementWarning("Unrecognized entity/item '{}'".format(from_obj.name))
        )
    if (
        to_obj is not None
        and to_obj.name not in entities.raw
        and to_obj.name not in items.raw
    ):
        unrecognized.append(
            UnknownElementWarning("Unrecognized entity/item '{}'".format(to_obj.name))
        )
    if unrecognized:
        return unrecognized

    # If one (or both) of from and to are empty, then there's also no reason to
    # check if a mapping between them is valid because there's just simply not
    # enough information
    if from_obj is None or to_obj is None:
        return None

    # If both from and to are the same, the game will allow it; but the GUI
    # prevents the user from doing it and it ends up being functionally useless,
    # so we warn the user since this is likely not intentional
    if from_obj.name == to_obj.name:
        return [
            NoEffectWarning(
                "Mapping entity/item '{}' to itself has no effect".format(from_obj.name)
            )
        ]

    # The types of both need to match in order to make sense
    if from_obj.type != to_obj.type:
        return [
            UpgradeProhibitedWarning(
                "'{}' is an {} but '{}' is an {}".format(
                    from_obj.name,
                    from_obj.type,
                    to_obj.name,
                    to_obj.type,
                )
            )
        ]

    # TODO: currently we don't check for item mapping correctness
    # For now we just ignore it and early exit
    if from_obj.type == "item" and to_obj.type == "item":
        return None

    # To quote Entity prototype documentation for the "next_upgrade" key:

    # > "This entity may not have 'not-upgradable' flag set and must be
    # > minable. This entity mining result must not contain item product
    # > with "hidden" flag set. Mining results with no item products are
    # > allowed. The entity may not be a Prototype/RollingStock. The
    # > upgrade target entity needs to have the same bounding box,
    # > collision mask, and fast replaceable group as this entity. The
    # > upgrade target entity must have least 1 item that builds it that
    # > isn't hidden.

    from_entity = entities.raw[from_obj.name]
    to_entity = entities.raw[to_obj.name]

    # from must be upgradable
    if "not-upgradable" in from_entity.get("flags", set()):
        return [
            UpgradeProhibitedWarning("'{}' is not upgradable".format(from_obj.name))
        ]

    # from must be minable
    if not from_entity.get("minable", False):
        return [UpgradeProhibitedWarning("'{}' is not minable".format(from_obj.name))]

    # Mining results from the upgrade must not be hidden
    if "results" in from_entity["minable"]:
        mined_items = [r["name"] for r in from_entity["minable"]["results"]]
    else:
        mined_items = [from_entity["minable"]["result"]]
    # I assume that it means ALL of the items have to be not hidden
    for mined_item in mined_items:
        if "hidden" in items.raw[mined_item].get("flags", set()):
            return [
                UpgradeProhibitedWarning(
                    "Returned item '{}' when upgrading '{}' is hidden".format(
                        mined_item, from_obj.name
                    ),
                )
            ]

    # Cannot upgrade rolling stock (train cars)
    if "type" in from_entity and from_entity["type"] in {
        "locomotive",
        "cargo-wagon",
        "fluid-wagon",
        "artillery-wagon",
    }:
        return [
            UpgradeProhibitedWarning(
                "Cannot upgrade '{}' because it is RollingStock".format(from_obj.name),
            )
        ]

    # Collision boxes must match (assuming None is valid)
    if from_entity.get("collision_box", None) != to_entity.get("collision_box", None):
        return [
            UpgradeProhibitedWarning(
                "Cannot upgrade '{}' to '{}'; collision boxes differ".format(
                    from_obj.name, to_obj.name
                ),
            )
        ]

    # Collision masks must match (assuming None is valid)
    if from_entity["collision_mask"]["layers"] != to_entity["collision_mask"]["layers"]:
        return [
            UpgradeProhibitedWarning(
                "Cannot upgrade '{}' to '{}'; collision masks differ".format(
                    from_obj.name, to_obj.name
                ),
            )
        ]

    # Fast replacable groups must match (assuming None is valid)
    ffrg = from_entity.get("fast_replaceable_group", None)
    tfrg = to_entity.get("fast_replaceable_group", None)
    if ffrg != tfrg:
        return [
            UpgradeProhibitedWarning(
                "Cannot upgrade '{}' to '{}'; fast replacable groups differ".format(
                    from_obj.name, to_obj.name
                ),
            )
        ]

    # Otherwise, we must conclude that the mapping makes sense
    return None


@attrs.define
class UpgradePlanner(Blueprintable):
    """
    A :py:class:`.Blueprintable` used to upgrade and downgrade entities and
    items.
    """

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def root_item(self) -> Literal["upgrade_planner"]:
        return "upgrade_planner"

    # =========================================================================

    # TODO: this should be an evolve
    item: str = attrs.field(
        default="upgrade-planner",
        validator=instance_of(str),
        metadata={
            "omit": False,
        },
    )
    # TODO: description

    # =========================================================================

    @property
    def mapper_count(self) -> uint8:
        """
        The total number of unique mappings that this :py:attr:`.UpgradePlanner`
        can have. Read only.
        """
        return items.raw[self.item].get("mapper_count", 1000)

    # =========================================================================

    def _convert_mappers(value):
        if isinstance(value, Sequence) and not isinstance(value, str):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                if isinstance(elem, Sequence) and not isinstance(elem, str):
                    res[i] = Mapper(index=i, from_=elem[0], to=elem[1])
                else:
                    res[i] = Mapper.converter(elem)
            return res
        else:
            return value

    mappers: list[Mapper] = attrs.field(
        factory=list,
        converter=_convert_mappers,
        validator=instance_of(list[Mapper]),
    )
    """
    The list of mappings of one entity or item type to the other entity or
    item type.

    Using :py:meth:`.set_mapping()` will attempt to keep this list sorted
    by each mapping's internal ``"index"``, but outside of this function
    this  behavior is not required or enforced.

    :getter: Gets the mappers dictionary, or ``None`` if not set.
    :setter: Sets the mappers dictionary, or deletes the dictionary if set
        to ``None``
    """

    @mappers.validator
    @conditional(ValidationMode.STRICT)
    def _mappers_validator(self, attr: attrs.Attribute, value: list[Mapper]):
        """
        Ensure the given mappings are correct, and that there aren't any mappers
        that occupy the same indices.
        """
        occupied_indices = {}
        # warning_list = []
        for mapper in value:
            # Ensure that "from" and "to" are a valid pair
            # We assert that index must exist in each mapper, but both "from"
            # and "to" may be omitted
            reasons = check_valid_upgrade_pair(mapper.from_, mapper.to)
            if reasons is not None:
                [warnings.warn(w) for w in reasons]  # :)

            # 1.0
            # # If the index is greater than mapper_count, then the mapping will
            # # be redundant
            # if not mapper["index"] < upgrade_planner.mapper_count:
            #     warning_list.append(
            #         IndexWarning(
            #             "'index' ({}) for mapping '{}' to '{}' must be in range [0, {}) or else it will have no effect".format(
            #                 mapper["index"],
            #                 mapper["from"]["name"],
            #                 mapper["to"]["name"],
            #                 upgrade_planner.mapper_count,
            #             )
            #         )
            #     )

            # Keep track of entries that occupy the same index (only the last
            # mapping is used)
            if mapper.index in occupied_indices:
                occupied_indices[mapper.index]["count"] += 1
                occupied_indices[mapper.index]["mapper"] = mapper
            else:
                occupied_indices[mapper.index] = {
                    "count": 0,
                    "mapper": mapper,
                }

        # Issue warnings if multiple mappers occupy the same index
        for spot in occupied_indices:
            entry = occupied_indices[spot]
            if entry["count"] > 0:
                from_name = entry["mapper"].from_
                from_name = from_name.name if from_name is not None else from_name
                to_name = entry["mapper"].to
                to_name = to_name.name if to_name is not None else to_name
                warnings.warn(
                    IndexWarning(
                        "Mapping at index {} was overwritten {} time(s); final mapping is '{}' to '{}'".format(
                            spot,
                            entry["count"],
                            from_name,
                            to_name,
                        )
                    )
                )

    # =========================================================================

    @reissue_warnings
    def set_mapping(
        self,
        source: Union[str, UpgradeMapperSource],
        destination: Union[str, UpgradeMapperDestination],
        index: int,
    ):
        """
        Sets a single mapping in the :py:class:`.UpgradePlanner`. Setting
        multiple mappers at the same index overwrites the entry at that index
        with the last set value. Both ``from_obj`` and ``to_obj`` can be set to
        ``None`` which will create an unset mapping (and the resulting spot on
        the in-game GUI will be blank).

        This function will also attempt to keep the list sorted by each mapper's
        ``index`` key. This behavior is not enforced anywhere else, and if the
        :py:attr:`.mappers` list is ever made unsorted, calling this function
        does not resort said list and does not guarantee a correct sorted result.

        :param from_obj: The :py:data:`.MAPPING_ID` to convert entities/items
            from. Can be set to ``None`` which will leave it blank.
        :param to_obj: The :py:data:`.MAPPING_ID` to convert entities/items to.
            Can be set to ``None`` which will leave it blank.
        :param index: The location in the upgrade planner's mappers list.
        """
        new_mapping = Mapper(index=index, from_=source, to=destination)

        # Iterate over indexes to see where we should place the new mapping
        for i, current_mapping in enumerate(self.mappers):
            # If we find an exact index match, replace it
            if current_mapping.index == index:
                self.mappers[i] = new_mapping
                return

        # Otherwise, insert it sorted by index
        # TODO: make backwards compatible
        bisect.insort(self.mappers, new_mapping, key=lambda x: x.index)

    def remove_mapping(
        self,
        source: Union[str, UpgradeMapperSource],
        destination: Union[str, UpgradeMapperDestination],
        index: Optional[int] = None,
    ):
        """
        Removes a specified upgrade planner mapping. If ``index`` is not
        specified, the function searches for the first occurrence where both
        ``from_obj`` and ``to_obj`` match. If ``index`` is also specified, the
        algorithm will try to remove the first occurrence where all 3 criteria
        match.

        .. NOTE::

            ``index`` in this case refers to the index of the mapper in the
            **UpgradePlanner's GUI**, *not* it's position in the
            :py:attr:`.mappers` list; these two numbers are potentially disjunct.
            For example, `upgrade_planner.mappers[0]["index"]` is not
            necessarily ``0``. If you want to remove the first entry in the
            mappers list, then you can simply do `del upgrade_planner.mappers[0]`.

        :raises ValueError: If the specified mapping does not currently exist
            in the :py:attr:`.mappers` list.

        :param from_obj: The :py:data:`.MAPPING_ID` to to convert entities/items
            from.
        :param to_obj: The :py:data:`.MAPPING_ID` to convert entities/items to.
        :param index: The index of the mapping in the mapper to search.
        """
        source = UpgradeMapperSource.converter(source)
        destination = UpgradeMapperDestination.converter(destination)
        index = int(index) if index is not None else None

        if index is None:
            # Remove the first occurence of the mapping, if there are multiple
            for i, mapping in enumerate(self.mappers):
                if mapping.from_ == source and mapping.to == destination:
                    self.mappers.pop(i)
                    return
            # Otherwise, raise ValueError if we didn't find a match
            raise ValueError(
                "Unable to find mapper from '{}' to '{}'".format(source, destination)
            )
        else:
            # mapper = {"from": from_obj, "to": to_obj, "index": index}
            mapper = Mapper(index=index, from_=source, to=destination)
            self.mappers.remove(mapper)

    def pop_mapping(self, index: int) -> Mapper:
        """
        Removes a mapping at a specific mapper index. Note that this is not the
        position of the mapper in the :py:attr:`.mappers` list; it is the value
        if ``"index"`` key associated with one or more mappers. If there are
        multiple mapper objects that share the same index, then the only the
        first one is removed.

        :raises ValueError: If no matching mappers could be found that have a
            matching index.

        :param index: The index of the mapping in the mapper to search.
        """
        # Simple search and pop
        for i, mapping in enumerate(self.mappers):
            if mapping.index == index:
                return self.mappers.pop(i)

        raise ValueError("Unable to find mapper with index '{}'".format(index))


draftsman_converters.add_hook_fns(
    UpgradePlanner,
    lambda fields: {
        ("upgrade_planner", "item"): fields.item.name,
        ("upgrade_planner", "label"): fields.label.name,
        ("upgrade_planner", "label_color"): fields.label_color.name,
        ("upgrade_planner", "settings", "description"): fields.description.name,
        ("upgrade_planner", "settings", "icons"): fields.icons.name,
        ("upgrade_planner", "settings", "mappers"): fields.mappers.name,
        ("upgrade_planner", "settings"): None,  # Delete settings key if null
        ("upgrade_planner", "version"): fields.version.name,
    },
)
