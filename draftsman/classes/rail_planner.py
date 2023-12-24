# railplanner.py

from draftsman.classes.group import Group
from draftsman.classes.entity_like import EntityLike
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction
from draftsman.error import DraftsmanError
from draftsman.data import items
from draftsman.prototypes.straight_rail import StraightRail
from draftsman.prototypes.curved_rail import CurvedRail

from typing import Optional, Union
from typing import cast as typing_cast
import weakref
from weakref import ReferenceType as Ref


class RailPlanner(Group):
    """
    Allows the user to specify rails in a pen-drawing or turtle-based manner,
    similar to the item in the game.
    """

    def __init__(
        self,
        name: str = "rail",
        head_position: Union[Vector, PrimitiveVector] = (0, 0),
        head_direction: Direction = Direction.NORTH,
        **kwargs
    ):
        """
        TODO
        """
        super(RailPlanner, self).__init__(**kwargs)
        if name in items.raw and items.raw[name]["type"] == "rail-planner":
            self.name = name
        else:
            raise DraftsmanError("'{}' is not a valid rail-planner")
        self.straight_rail = items.raw[name]["straight_rail"]
        self.curved_rail = items.raw[name]["curved_rail"]

        self._head_position = Vector(0, 0)

        self.head_position = head_position  # type: ignore
        self.head_direction = head_direction
        self._last_rail_added: Optional[Ref] = None

        self.diagonal_side = 0  # left

    # =========================================================================

    @property
    def head_position(self) -> Vector:
        """
        The turtle "head" of the rail planner. This is the rail-tile position
        where the next placed rail will go.

        .. see-also::

            :py:attr:`.head_direction`

        :getter: TODO
        :setter: TODO
        :type: :py:class:`Vector`
        """
        return self._head_position

    @head_position.setter
    def head_position(self, value: Union[Vector, PrimitiveVector]) -> None:
        # TODO: issue rail alignment warning if not on rail grid
        self._head_position.update_from_other(value, int)
        self.diagonal_side = 0

    # =========================================================================

    @property
    def head_direction(self) -> Direction:
        """
        The :py:enum:`.Direction` that the user intends to build the next rails
        in. Note that this direction is not necessarily equal to the direction
        of the placed rail entities themselves.

        .. see-also::

            :py:attr:`.head_direction`

        :getter: TODO
        :setter: TODO
        :type: :py:enum:`.Direction`
        """
        return self._head_direction

    @head_direction.setter
    def head_direction(self, value: Direction) -> None:
        self._head_direction = Direction(value)
        self._direction = self._head_direction.next(eight_way=False)

    # =========================================================================

    @property
    def last_rail_added(self) -> Optional[Ref[StraightRail | CurvedRail]]:
        """
        Reference to the last rail entity that was added in the RailPlanner, or
        ``None`` if no entities have been added yet. Used internally, but
        provided for the user. Read only.
        """
        if self._last_rail_added is not None:
            return self._last_rail_added()
        else:
            return self._last_rail_added

    # =========================================================================

    def move_forward(self, amount: int = 1) -> None:
        """
        Moves the :py:class:`.RailPlanner`'s head ``amount`` rail-tiles in the
        direction :py:attr:`.head_direction`.

        Note that the distance travelled by this function is measured with the
        Manhattan-distance, meaning travelling across diagonals will take twice
        as many rails:

        .. doctest::

            >>> rail_planner = RailPlanner()
            >>> rail_planner.direction = Direction.SOUTH
            >>> rail_planner.move_forward(10)
            >>> rail_planner.head_position
            Vector(0, 10)
            >>> rail_planner.head_position = (0, 0)
            >>> rail_planner.direction = Direction.SOUTHEAST
            >>> rail_planner.move_forward(10)
            >>> rail_planner.head_position
            Vector(5, 5)

        :param amount: The amount of rails to place going in that direction.
        """
        if self.head_direction in {0, 2, 4, 6}:  # Straight rails, easy
            cardinal_matrix = {
                Direction.NORTH: (0, -2),
                Direction.EAST: (2, 0),
                Direction.SOUTH: (0, 2),
                Direction.WEST: (-2, 0),
            }
            cardinal_offset = cardinal_matrix[self.head_direction]
            for _ in range(amount):
                self.entities.append(
                    self.straight_rail,
                    tile_position=self.head_position,
                    direction=self.head_direction,
                    merge=True,
                )
                self._last_rail_added = weakref.ref(self.entities[-1])
                self.head_position.x += cardinal_offset[0]
                self.head_position.y += cardinal_offset[1]
        else:  # Diagonal rails, hard
            diagonal_matrix: dict[
                Direction, dict[Direction, tuple[int, int, Direction]]
            ] = {
                Direction.NORTHEAST: {
                    Direction.NORTHWEST: (0, -2, Direction.SOUTHEAST),
                    Direction.SOUTHEAST: (2, 0, Direction.NORTHWEST),
                },
                Direction.SOUTHEAST: {
                    Direction.NORTHEAST: (2, 0, Direction.SOUTHWEST),
                    Direction.SOUTHWEST: (0, 2, Direction.NORTHEAST),
                },
                Direction.SOUTHWEST: {
                    Direction.SOUTHEAST: (0, 2, Direction.NORTHWEST),
                    Direction.NORTHWEST: (-2, 0, Direction.SOUTHEAST),
                },
                Direction.NORTHWEST: {
                    Direction.SOUTHWEST: (-2, 0, Direction.NORTHEAST),
                    Direction.NORTHEAST: (0, -2, Direction.SOUTHWEST),
                },
            }
            if self.diagonal_side == 0:
                real_direction = self.head_direction.previous(eight_way=False)
            else:
                real_direction = self.head_direction.next(eight_way=False)
            for _ in range(amount):
                diagonal_offset = diagonal_matrix[self.head_direction][real_direction]
                self.entities.append(
                    self.straight_rail,
                    tile_position=self.head_position,
                    direction=real_direction,
                    merge=True,
                )
                self._last_rail_added = weakref.ref(self.entities[-1])
                self.head_position.x += diagonal_offset[0]
                self.head_position.y += diagonal_offset[1]
                real_direction = diagonal_offset[2]
                self.diagonal_side = int(not self.diagonal_side)

    def turn_left(self, amount: int = 1) -> None:
        """
        Places ``amount`` curved rails turning left from :py:attr:`head_position`,
        and places the head at the point just after the rails. Each increment of
        ``amount`` is equivalent to a turn of 45 degrees.

        90-degree bends in Factorio need a intermediary straight rail in-between
        the curved rail segements; this function automatically takes care of
        this for you, so manual management is not needed.

        :param amount: The amount of rails to place going in that direction.
        """
        matrix: dict[Direction, tuple[Vector, Vector, Direction]] = {
            Direction.NORTH: (
                Vector(0, -2),  # "offset"
                Vector(-4, -6),  # "head_offset"
                Direction.NORTH,  # "direction"
            ),
            Direction.NORTHEAST: (
                Vector(2, -2),
                Vector(2, -8),
                Direction.SOUTHWEST,
            ),
            Direction.EAST: (
                Vector(4, 0),
                Vector(6, -4),
                Direction.EAST,
            ),
            Direction.SOUTHEAST: (
                Vector(4, 2),
                Vector(8, 2),
                Direction.NORTHWEST,
            ),
            Direction.SOUTH: (
                Vector(2, 4),
                Vector(4, 6),
                Direction.SOUTH,
            ),
            Direction.SOUTHWEST: (
                Vector(0, 4),
                Vector(-2, 8),
                Direction.NORTHEAST,
            ),
            Direction.WEST: (
                Vector(-2, 2),
                Vector(-6, 4),
                Direction.WEST,
            ),
            Direction.NORTHWEST: (
                Vector(-2, 0),
                Vector(-8, -2),
                Direction.SOUTHEAST,
            ),
        }
        diagonals = {
            Direction.NORTHEAST,
            Direction.SOUTHEAST,
            Direction.SOUTHWEST,
            Direction.NORTHWEST,
        }
        for _ in range(amount):
            # If we're diagonal and turning left, we need to ensure that there
            # is at least one straight rail between curved rails
            if (
                self.head_direction in diagonals and self.diagonal_side == 1
            ):  # next side is right
                self.move_forward()
            entry = matrix[self.head_direction]
            self.head_direction = self.head_direction.previous(eight_way=True)
            self.entities.append(
                self.curved_rail,
                position=self.head_position + entry[0],
                direction=entry[2],
                merge=True,
            )
            self._last_rail_added = weakref.ref(self.entities[-1])
            self.head_position += entry[1]
            if self.head_direction in diagonals:
                self.diagonal_side = 1  # right

    def turn_right(self, amount: int = 1) -> None:
        """
        TODO
        """
        matrix: dict[Direction, tuple[Vector, Vector, Direction]] = {
            Direction.NORTH: (
                Vector(2, -2),  # "offset"
                Vector(4, -6),  # "head_offset"
                Direction.NORTHEAST,  # "direction"
            ),
            Direction.NORTHEAST: (
                Vector(4, 0),
                Vector(8, -2),
                Direction.WEST,
            ),
            Direction.EAST: (
                Vector(4, 2),
                Vector(6, 4),
                Direction.SOUTHEAST,
            ),
            Direction.SOUTHEAST: (
                Vector(2, 4),
                Vector(2, 8),
                Direction.NORTH,
            ),
            Direction.SOUTH: (
                Vector(0, 4),
                Vector(-4, 6),
                Direction.SOUTHWEST,
            ),
            Direction.SOUTHWEST: (
                Vector(-2, 2),
                Vector(-8, 2),
                Direction.EAST,
            ),
            Direction.WEST: (
                Vector(-2, 0),
                Vector(-6, -4),
                Direction.NORTHWEST,
            ),
            Direction.NORTHWEST: (
                Vector(0, -2),
                Vector(-2, -8),
                Direction.SOUTH,
            ),
        }
        diagonals = {
            Direction.NORTHEAST,
            Direction.SOUTHEAST,
            Direction.SOUTHWEST,
            Direction.NORTHWEST,
        }
        for _ in range(amount):
            # If we're diagonal and turning left, we need to ensure that there
            # is at least one straight rail between curved rails
            if (
                self.head_direction in diagonals and self.diagonal_side == 0
            ):  # next side is left
                self.move_forward()
            entry = matrix[self.head_direction]
            self.head_direction = self.head_direction.next(eight_way=True)
            self.entities.append(
                self.curved_rail,
                position=self.head_position + entry[0],
                direction=entry[2],
                merge=True,
            )
            self._last_rail_added = weakref.ref(self.entities[-1])
            self.head_position += entry[1]
            if self.head_direction in diagonals:
                self.diagonal_side = 0  # left

    def add_signal(
        self, entity: Union[str, EntityLike], right: bool = True, front: bool = True
    ) -> None:
        """
        Adds a rail signal to the last placed rail. Defaults to the front right
        side of the last placed rail entity, determined by the current
        :py:attr:`head_direction`.

        .. NOTE::

            On diagonal rails, there is only two valid spots to place rail
            signals instead of four; specifying ``front`` on these rails will
            have no effect.

        Defaults to right because that's the side that trains read signals from
        when going in :py:attr:`head_direction`.

        :param entity: Either the name of the entity to construct at the
            position, or a :py:class:`EntityLike` object to copy into the rail
            planner. This is useful if you want to specify a modded signal
            entity (e.g. ``"my-modded-rail-signal"``), or if you want to use a
            custom signal entity with customized attributes to use as a template.
        :param right: Which side to place the signal on. Defaults to the
            right, as that's the side that trains use when determining their
            pathing when heading in :py:attr:`head_direction`.
        :param front: Which end of the track to place the signal on. Horizontal
            and vertical straight rails and curved rails can recieve signals on
            either end of the entity. This option in conjunction with
            ``right_side`` gives you full control of the signals exact position
            on the rail.
        """
        # Gaurd against silly cases where the user tries to place a signal
        # before placing any rail
        if self.last_rail_added is None:
            return

        last_rail_added = typing_cast(
            Union[CurvedRail, StraightRail], self.last_rail_added
        )

        diagonals = {
            Direction.NORTHEAST,
            Direction.SOUTHEAST,
            Direction.SOUTHWEST,
            Direction.NORTHWEST,
        }
        rail_pos = last_rail_added.position
        rail_dir = last_rail_added.direction
        if last_rail_added.name == self.straight_rail:
            if rail_dir in diagonals:
                # Diagonal Straight Rail
                # `front` has no effect, since there's only two valid spots
                # diagonal_offset = (1, 0)
                diagonal_matrix = {
                    Direction.NORTHEAST: {
                        Direction.SOUTHEAST: [Vector(-1, -1), Vector(1, 1)],
                        Direction.NORTHWEST: [Vector(-2, -2), Vector(0, 0)],
                    },
                    Direction.SOUTHEAST: {
                        Direction.NORTHEAST: [Vector(1, -2), Vector(-1, 0)],
                        Direction.SOUTHWEST: [Vector(0, -1), Vector(-2, 1)],
                    },
                    Direction.SOUTHWEST: {
                        Direction.SOUTHEAST: [Vector(1, 1), Vector(-1, -1)],
                        Direction.NORTHWEST: [Vector(0, 0), Vector(-2, -2)],
                    },
                    Direction.NORTHWEST: {
                        Direction.NORTHEAST: [Vector(-1, 0), Vector(1, -2)],
                        Direction.SOUTHWEST: [Vector(-2, 1), Vector(0, -1)],
                    },
                }

                diagonal_index = int(right)
                diagonal_offset = diagonal_matrix[self.head_direction][rail_dir][
                    diagonal_index
                ]

                if right:
                    diagonal_signal_dir = self.head_direction.opposite()
                else:
                    diagonal_signal_dir = self.head_direction

                self.entities.append(
                    entity,
                    tile_position=rail_pos + diagonal_offset,
                    direction=diagonal_signal_dir,
                )
            else:
                # Horizontal/Vertical straight rail
                straight_matrix = {
                    Direction.NORTH: [
                        Vector(-2, 0),
                        Vector(-2, -1),
                        Vector(1, 0),
                        Vector(1, -1),
                    ],
                    Direction.EAST: [
                        Vector(-1, -2),
                        Vector(0, -2),
                        Vector(-1, 1),
                        Vector(0, 1),
                    ],
                    Direction.SOUTH: [
                        Vector(1, -1),
                        Vector(1, 0),
                        Vector(-2, -1),
                        Vector(-2, 0),
                    ],
                    Direction.WEST: [
                        Vector(0, 1),
                        Vector(-1, 1),
                        Vector(0, -2),
                        Vector(-1, -2),
                    ],
                }

                straight_index = (int(right) << 1) | int(front)
                straight_offset = straight_matrix[rail_dir][straight_index]

                if right:
                    straight_signal_dir = rail_dir.opposite()
                else:
                    straight_signal_dir = rail_dir

                self.entities.append(
                    entity,
                    tile_position=rail_pos + straight_offset,
                    direction=straight_signal_dir,
                )
        else:
            # Curved rail
            # fmt: off
            curved_matrix = {
                (Direction.NORTH, Direction.SOUTH): [
                    {"offset": Vector(-1, -4), "direction": Direction.SOUTHEAST},
                    {"offset": Vector(2, 3), "direction": Direction.SOUTH},
                    {"offset": Vector(-3, -2), "direction": Direction.NORTHWEST},
                    {"offset": Vector(-1, 3), "direction": Direction.NORTH},
                ],
                (Direction.NORTH, Direction.NORTHWEST): [
                    {"offset": Vector(-1, 3), "direction": Direction.NORTH},
                    {"offset": Vector(-3, -2), "direction": Direction.NORTHWEST},
                    {"offset": Vector(2, 3), "direction": Direction.SOUTH},
                    {"offset": Vector(-1, -4), "direction": Direction.SOUTHEAST},
                ],
                (Direction.NORTHEAST, Direction.NORTHEAST): [
                    {"offset": Vector(-3, 3), "direction": Direction.NORTH},
                    {"offset": Vector(0, -4), "direction": Direction.NORTHEAST},
                    {"offset": Vector(0, 3), "direction": Direction.SOUTH},
                    {"offset": Vector(2, -2), "direction": Direction.SOUTHWEST},
                ],
                (Direction.NORTHEAST, Direction.SOUTH): [
                    {"offset": Vector(2, -2), "direction": Direction.SOUTHWEST},
                    {"offset": Vector(0, 3), "direction": Direction.SOUTH},
                    {"offset": Vector(0, -4), "direction": Direction.NORTHEAST},
                    {"offset": Vector(-3, 3), "direction": Direction.NORTH},
                ],
                (Direction.EAST, Direction.WEST): [
                    {"offset": Vector(3, -1), "direction": Direction.SOUTHWEST},
                    {"offset": Vector(-4, 2), "direction": Direction.WEST},
                    {"offset": Vector(1, -3), "direction": Direction.NORTHEAST},
                    {"offset": Vector(-4, -1), "direction": Direction.EAST},
                ],
                (Direction.EAST, Direction.NORTHEAST): [
                    {"offset": Vector(-4, -1), "direction": Direction.EAST},
                    {"offset": Vector(1, -3), "direction": Direction.NORTHEAST},
                    {"offset": Vector(-4, 2), "direction": Direction.WEST},
                    {"offset": Vector(3, -1), "direction": Direction.SOUTHWEST},
                ],
                (Direction.SOUTHEAST, Direction.SOUTHEAST): [
                    {"offset": Vector(-4, -3), "direction": Direction.EAST},
                    {"offset": Vector(3, 0), "direction": Direction.SOUTHEAST},
                    {"offset": Vector(-4, 0), "direction": Direction.WEST},
                    {"offset": Vector(1, 2), "direction": Direction.NORTHWEST},
                ],
                (Direction.SOUTHEAST, Direction.WEST): [
                    {"offset": Vector(1, 2), "direction": Direction.NORTHWEST},
                    {"offset": Vector(-4, 0), "direction": Direction.WEST},
                    {"offset": Vector(3, 0), "direction": Direction.SOUTHEAST},
                    {"offset": Vector(-4, -3), "direction": Direction.EAST},
                ],
                (Direction.SOUTH, Direction.NORTH): [
                    {"offset": Vector(0, 3), "direction": Direction.NORTHWEST},
                    {"offset": Vector(-3, -4), "direction": Direction.NORTH},
                    {"offset": Vector(2, 1), "direction": Direction.SOUTHEAST},
                    {"offset": Vector(0, -4), "direction": Direction.SOUTH},
                ],
                (Direction.SOUTH, Direction.SOUTHEAST): [
                    {"offset": Vector(0, -4), "direction": Direction.SOUTH},
                    {"offset": Vector(2, 1), "direction": Direction.SOUTHEAST},
                    {"offset": Vector(-3, -4), "direction": Direction.NORTH},
                    {"offset": Vector(0, 3), "direction": Direction.NORTHWEST},
                ],
                (Direction.SOUTHWEST, Direction.SOUTHWEST): [
                    {"offset": Vector(2, -4), "direction": Direction.SOUTH},
                    {"offset": Vector(-1, 3), "direction": Direction.SOUTHWEST},
                    {"offset": Vector(-1, -4), "direction": Direction.NORTH},
                    {"offset": Vector(-3, 1), "direction": Direction.NORTHEAST},
                ],
                (Direction.SOUTHWEST, Direction.NORTH): [
                    {"offset": Vector(-3, 1), "direction": Direction.NORTHEAST},
                    {"offset": Vector(-1, -4), "direction": Direction.NORTH},
                    {"offset": Vector(-1, 3), "direction": Direction.SOUTHWEST},
                    {"offset": Vector(2, -4), "direction": Direction.SOUTH},
                ],
                (Direction.WEST, Direction.EAST): [
                    {"offset": Vector(-4, 0), "direction": Direction.NORTHEAST},
                    {"offset": Vector(3, -3), "direction": Direction.EAST},
                    {"offset": Vector(-2, 2), "direction": Direction.SOUTHWEST},
                    {"offset": Vector(3, 0), "direction": Direction.WEST},
                ],
                (Direction.WEST, Direction.SOUTHWEST): [
                    {"offset": Vector(3, 0), "direction": Direction.WEST},
                    {"offset": Vector(-2, 2), "direction": Direction.SOUTHWEST},
                    {"offset": Vector(3, -3), "direction": Direction.EAST},
                    {"offset": Vector(-4, 0), "direction": Direction.NORTHEAST},
                ],
                (Direction.NORTHWEST, Direction.NORTHWEST): [
                    {"offset": Vector(3, 2), "direction": Direction.WEST},
                    {"offset": Vector(-4, -1), "direction": Direction.NORTHWEST},
                    {"offset": Vector(3, -1), "direction": Direction.EAST},
                    {"offset": Vector(-2, -3), "direction": Direction.SOUTHEAST},
                ],
                (Direction.NORTHWEST, Direction.EAST): [
                    {"offset": Vector(-2, -3), "direction": Direction.SOUTHEAST},
                    {"offset": Vector(3, -1), "direction": Direction.EAST},
                    {"offset": Vector(-4, -1), "direction": Direction.NORTHWEST},
                    {"offset": Vector(3, 2), "direction": Direction.WEST},
                ],
            }
            # fmt: on

            curved_index = (int(right) << 1) | int(front)
            permutation = (rail_dir, self.head_direction)

            curved_offset = curved_matrix[permutation][curved_index]["offset"]
            curved_signal_dir = curved_matrix[permutation][curved_index]["direction"]
            self.entities.append(
                entity,
                tile_position=rail_pos + curved_offset,
                direction=curved_signal_dir,
            )

    def add_station(
        self,
        entity: Union[str, EntityLike],
        station: Optional[str] = None,
        right: bool = True,
    ) -> None:
        """
        Adds a train station at the :py:attr:`head_position` on the specified
        side.

        :param entity: Either the name of the entity to construct at the
            position, or a :py:class:`EntityLike` object to copy into the rail
            planner. This is useful if you want to specify a modded train stop
            entity (e.g. ``"my-modded-train-stop"``), or if you want to use a
            custom train stop with customized attributes to use as a template.
        :param station: The name to give to this train station. If left as
            ``None``, the game will automatically generate a valid train stop
            name on import.
        :param right: Which side to place the stop on. Defaults to the
            right, as that's the side that trains use when pathing to a station
            in :py:attr:`head_direction`.
        """
        # Gaurd against silly cases where the user tries to place a station
        # before placing any rail
        if self.last_rail_added is None:
            return

        last_rail_added = typing_cast(
            Union[CurvedRail, StraightRail], self.last_rail_added
        )

        if last_rail_added.name == self.curved_rail:
            raise DraftsmanError(  # TODO: more descriptive error
                "Cannot place train stop on a curved rail"
            )
        diagonals = {
            Direction.NORTHEAST,
            Direction.SOUTHEAST,
            Direction.SOUTHWEST,
            Direction.NORTHWEST,
        }
        if last_rail_added.direction in diagonals:
            raise DraftsmanError(  # TODO: more descriptive error
                "Cannot place train stop on a diagonal rail"
            )

        matrix = {
            Direction.NORTH: Vector(2, 0),
            Direction.EAST: Vector(0, 2),
            Direction.SOUTH: Vector(-2, 0),
            Direction.WEST: Vector(0, -2),
        }
        if right:
            rail_dir = last_rail_added.direction
        else:
            rail_dir = last_rail_added.direction.opposite()

        offset = matrix[rail_dir]

        self.entities.append(
            entity,
            position=last_rail_added.position + offset,
            direction=rail_dir,
            station=station,
        )
