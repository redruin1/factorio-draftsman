# # railplanner.py

# from draftsman.classes.group import Group
# from draftsman.classes.entity_like import EntityLike
# from draftsman.classes.vector import Vector, PrimitiveVector
# from draftsman.constants import LegacyDirection
# from draftsman.error import DraftsmanError
# from draftsman.data import items
# from draftsman.prototypes.legacy_straight_rail import LegacyStraightRail
# from draftsman.prototypes.legacy_curved_rail import LegacyCurvedRail

# from typing import Optional, Union
# from typing import cast as typing_cast
# import weakref
# from weakref import ReferenceType as Ref


# class RailPlanner(Group):
#     """
#     Allows the user to specify rails in a pen-drawing or turtle-based manner,
#     similar to the item in the game.
#     """

#     def __init__(
#         self,
#         name: str = "rail",
#         head_position: Union[Vector, PrimitiveVector] = (0, 0),
#         head_direction: LegacyDirection = LegacyDirection.NORTH,
#         **kwargs
#     ):
#         """
#         TODO
#         """
#         super(RailPlanner, self).__init__(**kwargs)
#         if name in items.raw and items.raw[name]["type"] == "rail-planner":
#             self.name = name
#         else:
#             raise DraftsmanError("'{}' is not a valid rail-planner")
#         # TODO: reimplement
#         # self.straight_rail = items.raw[name]["straight_rail"]
#         # self.curved_rail = items.raw[name]["curved_rail"]
#         self.straight_rail = "legacy-straight-rail"
#         self.curved_rail = "legacy-curved-rail"

#         self._head_position = Vector(0, 0)

#         self.head_position = head_position  # type: ignore
#         self.head_direction = head_direction
#         self._last_rail_added: Optional[Ref] = None

#         self.diagonal_side = 0  # left

#     # =========================================================================

#     @property
#     def head_position(self) -> Vector:
#         """
#         The turtle "head" of the rail planner. This is the rail-tile position
#         where the next placed rail will go.

#         .. seealso::

#             :py:attr:`.head_direction`
#         """
#         return self._head_position

#     @head_position.setter
#     def head_position(self, value: Union[Vector, PrimitiveVector]) -> None:
#         # TODO: issue rail alignment warning if not on rail grid
#         self._head_position.update_from_other(value, int)
#         self.diagonal_side = 0

#     # =========================================================================

#     @property
#     def head_direction(self) -> LegacyDirection:
#         """
#         The :py:enum:`.LegacyDirection` that the user intends to build the next rails
#         in. Note that this direction is not necessarily equal to the direction
#         of the placed rail entities themselves.

#         .. seealso::

#             :py:attr:`.head_position`
#         """
#         return self._head_direction

#     @head_direction.setter
#     def head_direction(self, value: LegacyDirection) -> None:
#         self._head_direction = LegacyDirection(value)
#         self._direction = self._head_direction.next(eight_way=False)

#     # =========================================================================

#     @property
#     def last_rail_added(self) -> Optional[Ref[LegacyStraightRail | LegacyCurvedRail]]:
#         """
#         Reference to the last rail entity that was added in the RailPlanner, or
#         ``None`` if no entities have been added yet. Used internally, but
#         provided for the user. Read only.
#         """
#         if self._last_rail_added is not None:
#             return self._last_rail_added()
#         else:
#             return self._last_rail_added

#     # =========================================================================

#     def move_forward(self, amount: int = 1) -> None:
#         """
#         Moves the :py:class:`.RailPlanner`'s head ``amount`` rail-tiles in the
#         direction :py:attr:`.head_direction`.

#         Note that the distance travelled by this function is measured with the
#         Manhattan-distance, meaning travelling across diagonals will take twice
#         as many rails:

#         .. doctest::

#             >>> rail_planner = RailPlanner()
#             >>> rail_planner.direction = LegacyDirection.SOUTH
#             >>> rail_planner.move_forward(10)
#             >>> rail_planner.head_position
#             Vector(0, 10)
#             >>> rail_planner.head_position = (0, 0)
#             >>> rail_planner.direction = LegacyDirection.SOUTHEAST
#             >>> rail_planner.move_forward(10)
#             >>> rail_planner.head_position
#             Vector(5, 5)

#         :param amount: The amount of rails to place going in that direction.
#         """
#         if self.head_direction in {LegacyDirection.NORTH, LegacyDirection.EAST, LegacyDirection.SOUTH, LegacyDirection.WEST}:  
#             # Straight rails, easy
#             cardinal_matrix = {
#                 LegacyDirection.NORTH: (0, -2),
#                 LegacyDirection.EAST: (2, 0),
#                 LegacyDirection.SOUTH: (0, 2),
#                 LegacyDirection.WEST: (-2, 0),
#             }
#             cardinal_offset = cardinal_matrix[self.head_direction]
#             for _ in range(amount):
#                 self.entities.append(
#                     self.straight_rail,
#                     tile_position=self.head_position,
#                     direction=self.head_direction,
#                     merge=True,
#                 )
#                 self._last_rail_added = weakref.ref(self.entities[-1])
#                 self.head_position.x += cardinal_offset[0]
#                 self.head_position.y += cardinal_offset[1]
#         else:  
#             # Diagonal rails, hard
#             diagonal_matrix: dict[
#                 LegacyDirection, dict[LegacyDirection, tuple[int, int, LegacyDirection]]
#             ] = {
#                 LegacyDirection.NORTHEAST: {
#                     LegacyDirection.NORTHWEST: (0, -2, LegacyDirection.SOUTHEAST),
#                     LegacyDirection.SOUTHEAST: (2, 0, LegacyDirection.NORTHWEST),
#                 },
#                 LegacyDirection.SOUTHEAST: {
#                     LegacyDirection.NORTHEAST: (2, 0, LegacyDirection.SOUTHWEST),
#                     LegacyDirection.SOUTHWEST: (0, 2, LegacyDirection.NORTHEAST),
#                 },
#                 LegacyDirection.SOUTHWEST: {
#                     LegacyDirection.SOUTHEAST: (0, 2, LegacyDirection.NORTHWEST),
#                     LegacyDirection.NORTHWEST: (-2, 0, LegacyDirection.SOUTHEAST),
#                 },
#                 LegacyDirection.NORTHWEST: {
#                     LegacyDirection.SOUTHWEST: (-2, 0, LegacyDirection.NORTHEAST),
#                     LegacyDirection.NORTHEAST: (0, -2, LegacyDirection.SOUTHWEST),
#                 },
#             }
#             if self.diagonal_side == 0:
#                 real_direction = self.head_direction.previous(eight_way=False)
#             else:
#                 real_direction = self.head_direction.next(eight_way=False)
#             for _ in range(amount):
#                 print(_)
#                 diagonal_offset = diagonal_matrix[self.head_direction][real_direction]
#                 print(real_direction)
#                 self.entities.append(
#                     self.straight_rail,
#                     tile_position=self.head_position,
#                     direction=real_direction.to_modern(),
#                     merge=True,
#                 )
#                 self._last_rail_added = weakref.ref(self.entities[-1])
#                 self.head_position.x += diagonal_offset[0]
#                 self.head_position.y += diagonal_offset[1]
#                 print(self.head_position)
#                 real_direction = diagonal_offset[2]
#                 self.diagonal_side = int(not self.diagonal_side)

#     def turn_left(self, amount: int = 1) -> None:
#         """
#         Places ``amount`` curved rails turning left from :py:attr:`head_position`,
#         and places the head at the point just after the rails. Each increment of
#         ``amount`` is equivalent to a turn of 45 degrees.

#         90-degree bends in Factorio need a intermediary straight rail in-between
#         the curved rail segements; this function automatically takes care of
#         this for you, so manual management is not needed.

#         :param amount: The amount of rails to place going in that direction.
#         """
#         matrix: dict[LegacyDirection, tuple[Vector, Vector, LegacyDirection]] = {
#             LegacyDirection.NORTH: (
#                 Vector(0, -2),  # "offset"
#                 Vector(-4, -6),  # "head_offset"
#                 LegacyDirection.NORTH,  # "direction"
#             ),
#             LegacyDirection.NORTHEAST: (
#                 Vector(2, -2),
#                 Vector(2, -8),
#                 LegacyDirection.SOUTHWEST,
#             ),
#             LegacyDirection.EAST: (
#                 Vector(4, 0),
#                 Vector(6, -4),
#                 LegacyDirection.EAST,
#             ),
#             LegacyDirection.SOUTHEAST: (
#                 Vector(4, 2),
#                 Vector(8, 2),
#                 LegacyDirection.NORTHWEST,
#             ),
#             LegacyDirection.SOUTH: (
#                 Vector(2, 4),
#                 Vector(4, 6),
#                 LegacyDirection.SOUTH,
#             ),
#             LegacyDirection.SOUTHWEST: (
#                 Vector(0, 4),
#                 Vector(-2, 8),
#                 LegacyDirection.NORTHEAST,
#             ),
#             LegacyDirection.WEST: (
#                 Vector(-2, 2),
#                 Vector(-6, 4),
#                 LegacyDirection.WEST,
#             ),
#             LegacyDirection.NORTHWEST: (
#                 Vector(-2, 0),
#                 Vector(-8, -2),
#                 LegacyDirection.SOUTHEAST,
#             ),
#         }
#         diagonals = {
#             LegacyDirection.NORTHEAST,
#             LegacyDirection.SOUTHEAST,
#             LegacyDirection.SOUTHWEST,
#             LegacyDirection.NORTHWEST,
#         }
#         for _ in range(amount):
#             # If we're diagonal and turning left, we need to ensure that there
#             # is at least one straight rail between curved rails
#             if (
#                 self.head_direction in diagonals and self.diagonal_side == 1
#             ):  # next side is right
#                 self.move_forward()
#             entry = matrix[self.head_direction]
#             self.head_direction = self.head_direction.previous(eight_way=True)
#             self.entities.append(
#                 self.curved_rail,
#                 position=self.head_position + entry[0],
#                 direction=entry[2].to_modern(),
#                 merge=True,
#             )
#             self._last_rail_added = weakref.ref(self.entities[-1])
#             self.head_position += entry[1]
#             if self.head_direction in diagonals:
#                 self.diagonal_side = 1  # right

#     def turn_right(self, amount: int = 1) -> None:
#         """
#         TODO
#         """
#         matrix: dict[LegacyDirection, tuple[Vector, Vector, LegacyDirection]] = {
#             LegacyDirection.NORTH: (
#                 Vector(2, -2),  # "offset"
#                 Vector(4, -6),  # "head_offset"
#                 LegacyDirection.NORTHEAST,  # "direction"
#             ),
#             LegacyDirection.NORTHEAST: (
#                 Vector(4, 0),
#                 Vector(8, -2),
#                 LegacyDirection.WEST,
#             ),
#             LegacyDirection.EAST: (
#                 Vector(4, 2),
#                 Vector(6, 4),
#                 LegacyDirection.SOUTHEAST,
#             ),
#             LegacyDirection.SOUTHEAST: (
#                 Vector(2, 4),
#                 Vector(2, 8),
#                 LegacyDirection.NORTH,
#             ),
#             LegacyDirection.SOUTH: (
#                 Vector(0, 4),
#                 Vector(-4, 6),
#                 LegacyDirection.SOUTHWEST,
#             ),
#             LegacyDirection.SOUTHWEST: (
#                 Vector(-2, 2),
#                 Vector(-8, 2),
#                 LegacyDirection.EAST,
#             ),
#             LegacyDirection.WEST: (
#                 Vector(-2, 0),
#                 Vector(-6, -4),
#                 LegacyDirection.NORTHWEST,
#             ),
#             LegacyDirection.NORTHWEST: (
#                 Vector(0, -2),
#                 Vector(-2, -8),
#                 LegacyDirection.SOUTH,
#             ),
#         }
#         diagonals = {
#             LegacyDirection.NORTHEAST,
#             LegacyDirection.SOUTHEAST,
#             LegacyDirection.SOUTHWEST,
#             LegacyDirection.NORTHWEST,
#         }
#         for _ in range(amount):
#             # If we're diagonal and turning left, we need to ensure that there
#             # is at least one straight rail between curved rails
#             if (
#                 self.head_direction in diagonals and self.diagonal_side == 0
#             ):  # next side is left
#                 self.move_forward()
#             entry = matrix[self.head_direction]
#             self.head_direction = self.head_direction.next(eight_way=True)
#             self.entities.append(
#                 self.curved_rail,
#                 position=self.head_position + entry[0],
#                 direction=entry[2].to_modern(),
#                 merge=True,
#             )
#             self._last_rail_added = weakref.ref(self.entities[-1])
#             self.head_position += entry[1]
#             if self.head_direction in diagonals:
#                 self.diagonal_side = 0  # left

#     def add_signal(
#         self, entity: Union[str, EntityLike], right: bool = True, front: bool = True
#     ) -> None:
#         """
#         Adds a rail signal to the last placed rail. Defaults to the front right
#         side of the last placed rail entity, determined by the current
#         :py:attr:`head_direction`.

#         .. NOTE::

#             On diagonal rails, there is only two valid spots to place rail
#             signals instead of four; specifying ``front`` on these rails will
#             have no effect.

#         Defaults to right because that's the side that trains read signals from
#         when going in :py:attr:`head_direction`.

#         :param entity: Either the name of the entity to construct at the
#             position, or a :py:class:`EntityLike` object to copy into the rail
#             planner. This is useful if you want to specify a modded signal
#             entity (e.g. ``"my-modded-rail-signal"``), or if you want to use a
#             custom signal entity with customized attributes to use as a template.
#         :param right: Which side to place the signal on. Defaults to the
#             right, as that's the side that trains use when determining their
#             pathing when heading in :py:attr:`head_direction`.
#         :param front: Which end of the track to place the signal on. Horizontal
#             and vertical straight rails and curved rails can recieve signals on
#             either end of the entity. This option in conjunction with
#             ``right_side`` gives you full control of the signals exact position
#             on the rail.
#         """
#         # Gaurd against silly cases where the user tries to place a signal
#         # before placing any rail
#         if self.last_rail_added is None:
#             return

#         last_rail_added = typing_cast(
#             Union[LegacyCurvedRail, LegacyStraightRail], self.last_rail_added
#         )

#         diagonals = {
#             LegacyDirection.NORTHEAST,
#             LegacyDirection.SOUTHEAST,
#             LegacyDirection.SOUTHWEST,
#             LegacyDirection.NORTHWEST,
#         }
#         rail_pos = last_rail_added.position
#         rail_dir = last_rail_added.direction.to_legacy()
#         print(rail_dir)
#         if last_rail_added.name == self.straight_rail:
#             print(rail_dir in diagonals)
#             if rail_dir in diagonals:
#                 # Diagonal Straight Rail
#                 # `front` has no effect, since there's only two valid spots
#                 # diagonal_offset = (1, 0)
#                 diagonal_matrix = {
#                     LegacyDirection.NORTHEAST: {
#                         LegacyDirection.SOUTHEAST: [Vector(-1, -1), Vector(1, 1)],
#                         LegacyDirection.NORTHWEST: [Vector(-2, -2), Vector(0, 0)],
#                     },
#                     LegacyDirection.SOUTHEAST: {
#                         LegacyDirection.NORTHEAST: [Vector(1, -2), Vector(-1, 0)],
#                         LegacyDirection.SOUTHWEST: [Vector(0, -1), Vector(-2, 1)],
#                     },
#                     LegacyDirection.SOUTHWEST: {
#                         LegacyDirection.SOUTHEAST: [Vector(1, 1), Vector(-1, -1)],
#                         LegacyDirection.NORTHWEST: [Vector(0, 0), Vector(-2, -2)],
#                     },
#                     LegacyDirection.NORTHWEST: {
#                         LegacyDirection.NORTHEAST: [Vector(-1, 0), Vector(1, -2)],
#                         LegacyDirection.SOUTHWEST: [Vector(-2, 1), Vector(0, -1)],
#                     },
#                 }

#                 diagonal_index = int(right)
#                 diagonal_offset = diagonal_matrix[self.head_direction][rail_dir][
#                     diagonal_index
#                 ]

#                 if right:
#                     diagonal_signal_dir = self.head_direction.opposite()
#                 else:
#                     diagonal_signal_dir = self.head_direction

#                 self.entities.append(
#                     entity,
#                     tile_position=rail_pos + diagonal_offset,
#                     direction=diagonal_signal_dir.to_modern(),
#                 )
#             else:
#                 # Horizontal/Vertical straight rail
#                 straight_matrix = {
#                     LegacyDirection.NORTH: [
#                         Vector(-2, 0),
#                         Vector(-2, -1),
#                         Vector(1, 0),
#                         Vector(1, -1),
#                     ],
#                     LegacyDirection.EAST: [
#                         Vector(-1, -2),
#                         Vector(0, -2),
#                         Vector(-1, 1),
#                         Vector(0, 1),
#                     ],
#                     LegacyDirection.SOUTH: [
#                         Vector(1, -1),
#                         Vector(1, 0),
#                         Vector(-2, -1),
#                         Vector(-2, 0),
#                     ],
#                     LegacyDirection.WEST: [
#                         Vector(0, 1),
#                         Vector(-1, 1),
#                         Vector(0, -2),
#                         Vector(-1, -2),
#                     ],
#                 }

#                 straight_index = (int(right) << 1) | int(front)
#                 straight_offset = straight_matrix[rail_dir][straight_index]

#                 if right:
#                     straight_signal_dir = rail_dir.opposite()
#                 else:
#                     straight_signal_dir = rail_dir

#                 self.entities.append(
#                     entity,
#                     tile_position=rail_pos + straight_offset,
#                     direction=straight_signal_dir.to_modern(),
#                 )
#         else:
#             # Curved rail
#             # fmt: off
#             curved_matrix = {
#                 (LegacyDirection.NORTH, LegacyDirection.SOUTH): [
#                     {"offset": Vector(-1, -4), "direction": LegacyDirection.SOUTHEAST},
#                     {"offset": Vector(2, 3), "direction": LegacyDirection.SOUTH},
#                     {"offset": Vector(-3, -2), "direction": LegacyDirection.NORTHWEST},
#                     {"offset": Vector(-1, 3), "direction": LegacyDirection.NORTH},
#                 ],
#                 (LegacyDirection.NORTH, LegacyDirection.NORTHWEST): [
#                     {"offset": Vector(-1, 3), "direction": LegacyDirection.NORTH},
#                     {"offset": Vector(-3, -2), "direction": LegacyDirection.NORTHWEST},
#                     {"offset": Vector(2, 3), "direction": LegacyDirection.SOUTH},
#                     {"offset": Vector(-1, -4), "direction": LegacyDirection.SOUTHEAST},
#                 ],
#                 (LegacyDirection.NORTHEAST, LegacyDirection.NORTHEAST): [
#                     {"offset": Vector(-3, 3), "direction": LegacyDirection.NORTH},
#                     {"offset": Vector(0, -4), "direction": LegacyDirection.NORTHEAST},
#                     {"offset": Vector(0, 3), "direction": LegacyDirection.SOUTH},
#                     {"offset": Vector(2, -2), "direction": LegacyDirection.SOUTHWEST},
#                 ],
#                 (LegacyDirection.NORTHEAST, LegacyDirection.SOUTH): [
#                     {"offset": Vector(2, -2), "direction": LegacyDirection.SOUTHWEST},
#                     {"offset": Vector(0, 3), "direction": LegacyDirection.SOUTH},
#                     {"offset": Vector(0, -4), "direction": LegacyDirection.NORTHEAST},
#                     {"offset": Vector(-3, 3), "direction": LegacyDirection.NORTH},
#                 ],
#                 (LegacyDirection.EAST, LegacyDirection.WEST): [
#                     {"offset": Vector(3, -1), "direction": LegacyDirection.SOUTHWEST},
#                     {"offset": Vector(-4, 2), "direction": LegacyDirection.WEST},
#                     {"offset": Vector(1, -3), "direction": LegacyDirection.NORTHEAST},
#                     {"offset": Vector(-4, -1), "direction": LegacyDirection.EAST},
#                 ],
#                 (LegacyDirection.EAST, LegacyDirection.NORTHEAST): [
#                     {"offset": Vector(-4, -1), "direction": LegacyDirection.EAST},
#                     {"offset": Vector(1, -3), "direction": LegacyDirection.NORTHEAST},
#                     {"offset": Vector(-4, 2), "direction": LegacyDirection.WEST},
#                     {"offset": Vector(3, -1), "direction": LegacyDirection.SOUTHWEST},
#                 ],
#                 (LegacyDirection.SOUTHEAST, LegacyDirection.SOUTHEAST): [
#                     {"offset": Vector(-4, -3), "direction": LegacyDirection.EAST},
#                     {"offset": Vector(3, 0), "direction": LegacyDirection.SOUTHEAST},
#                     {"offset": Vector(-4, 0), "direction": LegacyDirection.WEST},
#                     {"offset": Vector(1, 2), "direction": LegacyDirection.NORTHWEST},
#                 ],
#                 (LegacyDirection.SOUTHEAST, LegacyDirection.WEST): [
#                     {"offset": Vector(1, 2), "direction": LegacyDirection.NORTHWEST},
#                     {"offset": Vector(-4, 0), "direction": LegacyDirection.WEST},
#                     {"offset": Vector(3, 0), "direction": LegacyDirection.SOUTHEAST},
#                     {"offset": Vector(-4, -3), "direction": LegacyDirection.EAST},
#                 ],
#                 (LegacyDirection.SOUTH, LegacyDirection.NORTH): [
#                     {"offset": Vector(0, 3), "direction": LegacyDirection.NORTHWEST},
#                     {"offset": Vector(-3, -4), "direction": LegacyDirection.NORTH},
#                     {"offset": Vector(2, 1), "direction": LegacyDirection.SOUTHEAST},
#                     {"offset": Vector(0, -4), "direction": LegacyDirection.SOUTH},
#                 ],
#                 (LegacyDirection.SOUTH, LegacyDirection.SOUTHEAST): [
#                     {"offset": Vector(0, -4), "direction": LegacyDirection.SOUTH},
#                     {"offset": Vector(2, 1), "direction": LegacyDirection.SOUTHEAST},
#                     {"offset": Vector(-3, -4), "direction": LegacyDirection.NORTH},
#                     {"offset": Vector(0, 3), "direction": LegacyDirection.NORTHWEST},
#                 ],
#                 (LegacyDirection.SOUTHWEST, LegacyDirection.SOUTHWEST): [
#                     {"offset": Vector(2, -4), "direction": LegacyDirection.SOUTH},
#                     {"offset": Vector(-1, 3), "direction": LegacyDirection.SOUTHWEST},
#                     {"offset": Vector(-1, -4), "direction": LegacyDirection.NORTH},
#                     {"offset": Vector(-3, 1), "direction": LegacyDirection.NORTHEAST},
#                 ],
#                 (LegacyDirection.SOUTHWEST, LegacyDirection.NORTH): [
#                     {"offset": Vector(-3, 1), "direction": LegacyDirection.NORTHEAST},
#                     {"offset": Vector(-1, -4), "direction": LegacyDirection.NORTH},
#                     {"offset": Vector(-1, 3), "direction": LegacyDirection.SOUTHWEST},
#                     {"offset": Vector(2, -4), "direction": LegacyDirection.SOUTH},
#                 ],
#                 (LegacyDirection.WEST, LegacyDirection.EAST): [
#                     {"offset": Vector(-4, 0), "direction": LegacyDirection.NORTHEAST},
#                     {"offset": Vector(3, -3), "direction": LegacyDirection.EAST},
#                     {"offset": Vector(-2, 2), "direction": LegacyDirection.SOUTHWEST},
#                     {"offset": Vector(3, 0), "direction": LegacyDirection.WEST},
#                 ],
#                 (LegacyDirection.WEST, LegacyDirection.SOUTHWEST): [
#                     {"offset": Vector(3, 0), "direction": LegacyDirection.WEST},
#                     {"offset": Vector(-2, 2), "direction": LegacyDirection.SOUTHWEST},
#                     {"offset": Vector(3, -3), "direction": LegacyDirection.EAST},
#                     {"offset": Vector(-4, 0), "direction": LegacyDirection.NORTHEAST},
#                 ],
#                 (LegacyDirection.NORTHWEST, LegacyDirection.NORTHWEST): [
#                     {"offset": Vector(3, 2), "direction": LegacyDirection.WEST},
#                     {"offset": Vector(-4, -1), "direction": LegacyDirection.NORTHWEST},
#                     {"offset": Vector(3, -1), "direction": LegacyDirection.EAST},
#                     {"offset": Vector(-2, -3), "direction": LegacyDirection.SOUTHEAST},
#                 ],
#                 (LegacyDirection.NORTHWEST, LegacyDirection.EAST): [
#                     {"offset": Vector(-2, -3), "direction": LegacyDirection.SOUTHEAST},
#                     {"offset": Vector(3, -1), "direction": LegacyDirection.EAST},
#                     {"offset": Vector(-4, -1), "direction": LegacyDirection.NORTHWEST},
#                     {"offset": Vector(3, 2), "direction": LegacyDirection.WEST},
#                 ],
#             }
#             # fmt: on

#             curved_index = (int(right) << 1) | int(front)
#             permutation = (rail_dir, self.head_direction)

#             curved_offset = curved_matrix[permutation][curved_index]["offset"]
#             curved_signal_dir = curved_matrix[permutation][curved_index]["direction"]
#             self.entities.append(
#                 entity,
#                 tile_position=rail_pos + curved_offset,
#                 direction=curved_signal_dir.to_modern(),
#             )

#     def add_station(
#         self,
#         entity: Union[str, EntityLike],
#         station: Optional[str] = None,
#         right: bool = True,
#     ) -> None:
#         """
#         Adds a train station at the :py:attr:`head_position` on the specified
#         side.

#         :param entity: Either the name of the entity to construct at the
#             position, or a :py:class:`EntityLike` object to copy into the rail
#             planner. This is useful if you want to specify a modded train stop
#             entity (e.g. ``"my-modded-train-stop"``), or if you want to use a
#             custom train stop with customized attributes to use as a template.
#         :param station: The name to give to this train station. If left as
#             ``None``, the game will automatically generate a valid train stop
#             name on import.
#         :param right: Which side to place the stop on. Defaults to the
#             right, as that's the side that trains use when pathing to a station
#             in :py:attr:`head_direction`.
#         """
#         # Gaurd against silly cases where the user tries to place a station
#         # before placing any rail
#         if self.last_rail_added is None:
#             return

#         last_rail_added = typing_cast(
#             Union[LegacyCurvedRail, LegacyStraightRail], self.last_rail_added
#         )

#         if last_rail_added.name == self.curved_rail:
#             raise DraftsmanError(  # TODO: more descriptive error
#                 "Cannot place train stop on a curved rail"
#             )
#         diagonals = {
#             LegacyDirection.NORTHEAST,
#             LegacyDirection.SOUTHEAST,
#             LegacyDirection.SOUTHWEST,
#             LegacyDirection.NORTHWEST,
#         }
#         if last_rail_added.direction.to_legacy() in diagonals:
#             raise DraftsmanError(  # TODO: more descriptive error
#                 "Cannot place train stop on a diagonal rail"
#             )

#         matrix = {
#             LegacyDirection.NORTH: Vector(2, 0),
#             LegacyDirection.EAST: Vector(0, 2),
#             LegacyDirection.SOUTH: Vector(-2, 0),
#             LegacyDirection.WEST: Vector(0, -2),
#         }
#         if right:
#             rail_dir = last_rail_added.direction
#         else:
#             rail_dir = last_rail_added.direction.opposite()

#         offset = matrix[rail_dir]

#         self.entities.append(
#             entity,
#             position=last_rail_added.position + offset,
#             direction=rail_dir,
#             station=station,
#         )
