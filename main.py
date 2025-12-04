import functools
import logging
import sys
from math import sin, cos, tan, radians, sqrt
from time import time

import pygame
import pymunk.pygame_util
from pymunk import Arbiter, Space, Vec2d, Body

VERSION = "1.0 BETA"
RESOLUTION = (800, 800)

D = 1e-10

UNIT_VELOCITY = "m/s"
UNIT_TILT = "rad"
UNIT_ACCELERATION = "m/s^2"
UNIT_MASS = "kg"
UNIT_DISTANCE = "m"
UNIT_TIME = "s"

SIM_SCALE = 10
SIM_GRAVITY = (0, 9.81 * SIM_SCALE)
SIM_PRECISION = 0.1 * SIM_SCALE
SIM_BLOCK_SIZE = 40
SIM_FPS = 60

log = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG


@functools.total_ordering
class Scalar:
    def __init__(self, _value: float, _unit: str):
        self.value = _value if abs(_value) > D else 0
        self.unit = _unit

    @classmethod
    def nan(cls):
        return Scalar(float("nan"), "")

    @staticmethod
    def is_number(o) -> bool:
        """
        Checks if operand is a number.
        :param o: Operand.
        :return: True if o is number, False otherwise.
        """
        if type(o) == int or type(o) == float:
            return True
        return False

    @staticmethod
    def is_scalar(o):
        """
        Checks if operand is a Scalar.
        :param o: Operand.
        :return: True if o is Scalar, False otherwise.
        """
        if hasattr(o, "value") and hasattr(o, "unit"):
            return True
        return False

    def __add__(self, other):
        """
        Defines addition.
        :param other: Operand.
        """
        if self.is_number(other):
            return Scalar(self.value + other, self.unit)
        elif self.is_scalar(other):
            return Scalar(self.value + other.value, self.unit)
        else:
            return NotImplemented

    def __sub__(self, other):
        """
        Defines substraction.
        :param other: Operand.
        """
        if self.is_number(other):
            return Scalar(self.value - other, self.unit)
        elif self.is_scalar(other):
            return Scalar(self.value - other.value, self.unit)
        else:
            return NotImplemented

    def __mul__(self, other):
        """
        Defines multiplication.
        :param other: Operand.
        """
        if self.is_number(other):
            return Scalar(self.value * other, self.unit)
        elif self.is_scalar(other):
            return Scalar(self.value * other.value, self.unit)
        else:
            return NotImplemented

    def __abs__(self):
        """
        Defines absolute value.
        """
        return Scalar(abs(self.value), self.unit)

    def __truediv__(self, other):
        """
        Defines division.
        :param other: Operand.
        """
        if self.is_number(other):
            return Scalar(self.value / other, self.unit)
        elif self.is_scalar(other):
            return Scalar(self.value / other.value, self.unit)
        else:
            return NotImplemented

    def __eq__(self, other):
        """
        Defines equality.
        :param other: Operand.
        """
        if self.is_number(other):
            return self.value == other
        elif self.is_scalar(other):
            return self.value == other.value and self.unit == other.unit
        else:
            return NotImplemented

    def __lt__(self, other):
        """
        Defines ordering.
        :param other: Operand.
        """
        if self.is_number(other):
            return self.value < other
        elif self.is_scalar(other):
            return self.value < other.value
        else:
            return NotImplemented


    def __str__(self):
        return f"{self.value}{self.unit}"


def translate_abs(x: Scalar | float, y: Scalar | float) -> tuple[Scalar | float, Scalar | float]:
    """
    Translates point in coordinate system starting in bottom-left screen corner
    to point in pygame coordinate system and vice versa. (x, y) vector changes sense, direction and value.
    :param x: point x-coordinate
    :param y: point y-coordinate
    :return: (x, y) - translated coordinate
    :rtype: tuple[float, float]
    """
    return x, - y + RESOLUTION[1]


def translate(x: Scalar | float, y: Scalar | float) -> tuple[Scalar | float, Scalar | float]:
    """
    Translates point in coordinate system starting in bottom-left screen corner
    to point in pygame coordinate system and vice versa. (x, y) vector changes only sense and direction.
    :param x: vector x-coordinate
    :param y: vector y-coordinate
    :return: (x, y) - translated coordinate
    :rtype: tuple[float, float]
    """
    return x, y * (-1)


class Vector:
    """
    A class representing a vector.

    Attributes
    ----------
    x : Scalar
        vector x-coordinate
    y : Scalar
        vector y-coordinate
    value : Scalar
        vector value
    """

    def __init__(self, _x: Scalar, _y: Scalar):
        val = sqrt(_x.value ** 2 + _y.value ** 2)
        if val > D:
            self.x = _x
            self.y = _y
            self.value = Scalar(val, _x.unit)
        else:
            self.x = Scalar(0, _x.unit)
            self.y = Scalar(0, _x.unit)
            self.value = Scalar(0, _x.unit)

    @classmethod
    def from_float(cls, _x: float, _y: float, _unit: str):
        return cls(Scalar(_x, _unit), Scalar(_y, _unit))

    def translated(self):
        """
        Translates vector in coordinate system starting in bottom-left screen corner
        to point in pygame coordinate system and vice versa. Vector changes sense, direction and value.
        :returns:Translated Vector.
        """
        x, y = translate(self.x, self.y)
        return Vector(x, y)

    def translated_abs(self):
        """
        Translates vector in coordinate system starting in bottom-left screen corner
        to point in pygame coordinate system and vice versa. Vector changes only sense and direction.
        :returns: Translated Vector.
        """
        x, y = translate_abs(self.x, self.y)
        return Vector(x, y)

    def __str__(self) -> str:
        """
        Converts to string.
        """
        return f"Vector({self.x}, {self.y} -> {self.value})"

    def __mul__(self, other: int | float):
        """
        Defines multiplication of a vector.
        :param other: Scalar multiplier.
        """
        return Vector(self.x * other, self.y * other)


class Input:
    """
    A class storing not constant properties of simulation.
    Attributes
    ----------
    tilt : float
        Tilt of the plane (radians).
    mass : float
        Mass of the block.
    velocity : Vector
        Starting velocity of the block.
    friction : float
        Coulomb friction coefficient between block and plane.
    """

    @staticmethod
    def parse_tilt(tilt: str) -> Scalar:
        """
        Parses tilt from user input.

        Parameters
        ----------
        tilt: str
            User's tilt input.

        Returns
        -------
        tilt: Scalar
            Parsed Scalar tilt.
        """
        return Scalar(float(tilt), UNIT_TILT)

    @staticmethod
    def parse_mass(mass: str) -> Scalar:
        """
        Parses mass from user input.
        Parameters
        ----------
        mass: str
            User's input.

        Returns
        -------
        mass: Scalar
            Parsed Scalar mass.
        """
        return Scalar(float(mass), UNIT_MASS)

    @staticmethod
    def parse_velocity(velocity: str, tilt: Scalar) -> Vector:
        """
        Parses velocity from user input.
        Parameters
        ----------
        velocity: str
            User's input (velocity parallel to plane).
        tilt: Scalar
            Tilt of plane (radians).

                Returns
        -------
        velocity: Vector
            Parsed Vector velocity.
        """
        v = float(velocity)
        return Vector.from_float(cos(tilt.value) * v, sin(tilt.value) * v, UNIT_VELOCITY)

    @staticmethod
    def parse_friction(friction: str) -> Scalar:
        """
        Parses friction from user input.
        Parameters
        ----------
        friction: str
            User's input.

                Returns
        -------
        friction: Scalar
            Parsed Scalar friction.
        """
        return Scalar(float(friction), "")

    def __init__(self, _tilt: Scalar, _mass: Scalar, _velocity: Vector, _friction: Scalar):
        """
        Class constructor.
        Parameters
        ----------
        _tilt: Scalar
        _mass: Scalar
        _velocity: Vector
        _friction: Scalar
        """
        self.tilt = _tilt
        self.mass = _mass
        self.velocity = _velocity
        self.friction = _friction

    @classmethod
    def user(cls, _tilt: str, _mass: str, _velocity: str, _friction: str):
        """
        Creates Input instance from user input.
        Parameters
        ----------
        _tilt: str
            Tilt from user's input.
        _mass: str
            Mass from user's input.
        _velocity: str
            Velocity from user's input.
        _friction: str
            Friction from user's input.

        Returns
        -------
        input: Input
            Parsed Input instance.
        """
        tilt = cls.parse_tilt(_tilt)
        return cls(tilt, cls.parse_mass(_mass), cls.parse_velocity(_velocity, tilt),
                   cls.parse_friction(_friction))

    @classmethod
    def simulation(cls, _user_input):
        """
        Converts Input object so it is ready for simulation.
        Parameters
        ----------
        _user_input: Input
            User's Input.

        Returns
        -------
        input: Input
            Parsed Input instance.
        """
        return cls(
            _user_input.tilt,
            _user_input.mass * SIM_SCALE,
            _user_input.velocity * SIM_SCALE,
            _user_input.friction
        )

    def __str__(self):
        """
        Converts to string.
        """
        return (f"Input(tilt={self.tilt}, "
                f"mass={self.mass}, "
                f"velocity={self.velocity}, "
                f"friction={self.friction})")


class Measurement:
    """
    A class representing a measurement in simulation.
    It stores data about time of measurement and block parameters.
    It can be one of two simulation events:
    - Complete stop of the block,
    - Collision between the wall and the block.

    Attributes
    ----------
    time : Scalar
        Timestamp of the measurement.
    position : Vector
        Measured position of the block.
    velocity : Vector
        Measured velocity of the block.
    """

    def __init__(self, _time: float, _position: Vec2d, _velocity: Vec2d):
        """
        Parameters
        ----------
        _time: float
            Timestamp of the measurement.
        _position: Vec2d
            Measured position of the block (Vec2d pymunk object)
        _velocity: Vec2d
            Measured velocity of the block (Vec2d pymunk object)
        """
        self.time = Scalar(_time, UNIT_TIME)
        x, y = translate_abs(_position.x, _position.y)
        self.position = Vector.from_float(x, y, UNIT_DISTANCE)
        x, y = translate(_velocity.x, _velocity.y)
        self.velocity = Vector.from_float(x, y, UNIT_VELOCITY)

    def __str__(self):
        """
        Converts to string.
        """
        return f"Measurement(time={self.time}, position={self.position}, velocity={self.velocity})"


class Cycle:
    """
    A class representing a cycle of the simulation.
    One cycle is defined as three Measurements:
    1. Block collides with the wall (then bounces off the wall and starts sliding up the plane).
    2. Block stops in one point of the plane (then starts sliding down).
    3. Block collides with the wall (also beginning of a new cycle).
    Attributes
    ----------
    number: float
        Number of the cycle.
    start: Measurement
        First point of the cycle (collision with the wall).
    middle: Measurement
        Second point of the cycle (stop).
    end: Measurement
        Third point of the cycle (collision with the wall).
    """

    def __init__(self, _number: int, _start_collision: Measurement, _middle_measurement: Measurement,
                 _end_collision: Measurement):
        """
        Class constructor.
        :param _number: Number of the cycle.
        :param _start_collision: Measurement of the block when ending last cycle (or first ever measurement).
        :param _middle_measurement: Measurement of the block when closest to complete stop.
        :param _end_collision: Measurement of the block when colliding with the wall.
        """
        self.number = _number
        self.start = _start_collision
        self.middle = _middle_measurement
        self.end = _end_collision

    def __str__(self):
        return f"Cycle(number={self.number}, start={self.start}, middle={self.middle}, end={self.end})"


class Result:
    """
    A class containing results of each cycle.
    Attributes
    ----------
    number: int
        Number of the result (cycle).
    is_full: bool
        True if the cycle is full.
        Cycle is not full only if 3rd point of cycle did not happen (block stopped in 2nd point).
    duration1: Scalar
        Time measured from 1st point of cycle to 2nd point of cycle.
    duration2: Scalar
        Time measured from 2nd point of cycle to 3rd point of cycle. If cycle isn't full is NaN.
    duration: Scalar
        Time of full cycle. If cycle isn't full is duration1.
    start_velocity: Vector
        Velocity at the 1st point of cycle (always directed up the slope).
    end_velocity: Vector
        Velocity at the 3rd point of cycle.
    reach: Vector
        Block displacement vector between 1st and 2nd point of cycle.
    """

    def __init__(self, number: int, is_full: bool, duration1: Scalar, duration2: Scalar, start_velocity: Vector,
                 end_velocity: Vector, reach: Vector):
        self.number = number
        self.is_full = is_full
        self.duration1 = duration1
        self.duration2 = duration2
        self.duration = duration1 + duration2 if is_full else duration1
        self.start_velocity = start_velocity
        self.end_velocity = end_velocity
        self.reach = reach

    @classmethod
    def measured(cls, cycle: Cycle, is_full: bool):
        """
        Parses measured Cycle object to create result.
        Parameters
        ----------
        cycle: Cycle
            Cycle object.
        is_full: bool
            True if the cycle is full.
            Cycle is not full only if 3rd point of cycle did not happen (block stopped in 2nd point).

        Returns
        -------
        Result object
        """
        return cls(cycle.number,
                   is_full,
                   cycle.middle.time - cycle.start.time,
                   cycle.end.time - cycle.middle.time if is_full else Scalar.nan(),
                   Vector(abs(cycle.start.velocity.x / SIM_SCALE), abs(cycle.start.velocity.y / SIM_SCALE)),
                   Vector(cycle.end.velocity.x / SIM_SCALE, cycle.end.velocity.y / SIM_SCALE),
                   Vector(abs(cycle.start.position.x - cycle.middle.position.x) / SIM_SCALE,
                          abs(cycle.start.position.y - cycle.middle.position.y) / SIM_SCALE))

    @classmethod
    def model(cls, number: int, start_velocity: Vector, tilt: float, f: float, g: float, is_full: bool):
        """
        Creates model Result using physical formulas.
        Parameters
        ----------
        number: int
        Number of the cycle.
        start_velocity: Vector
        Velocity at the 1st point of cycle (meters per second).
        tilt: float
            Tilt of plane (radians).
        f: float
            Coulomb's friction coefficient.
        g: float
            Value of gravitational acceleration (Vector is parallel to Y axis).
        is_full: bool
            True if the cycle is full.
            Cycle is not full only if 3rd point of cycle did not happen (block stopped in 2nd point).
        Returns
        -------
        Result object
        """
        v1 = start_velocity.value.value
        reach_value = (v1 * v1) / (2 * g * (f * cos(tilt) + sin(tilt)))
        end_velocity_co = (2 * tan(tilt) - f) / (2 * (f + tan(tilt)))

        if not is_full:
            end_velocity = Vector.from_float(0, 0, UNIT_VELOCITY)
        else:
            end_velocity_co = v1 * sqrt(end_velocity_co)
            end_velocity = Vector.from_float(-cos(tilt) * end_velocity_co, -sin(tilt) * end_velocity_co, UNIT_VELOCITY)

        d1 = Scalar(v1 / (g * (sin(tilt) + f * cos(tilt))), UNIT_TIME)
        d2 = Scalar(end_velocity.value.value / (g * (sin(tilt) - f * cos(tilt))), UNIT_TIME)

        reach = Vector.from_float(cos(tilt) * reach_value, sin(tilt) * reach_value, UNIT_DISTANCE)

        return cls(number, is_full, d1, d2 if is_full else Scalar.nan(), start_velocity, end_velocity, reach)

    def __str__(self):
        return (f"Result(number={self.number}, "
                f"is_full={self.is_full}, "
                f"duration1={self.duration1}, "
                f"duration2={self.duration2}), "
                f"duration={self.duration}, "
                f"start_velocity={self.start_velocity}, "
                f"end_velocity={self.end_velocity}, "
                f"reach={self.reach})")


class ScalarError:
    """
    A class containing measurement errors for given scalars.
    Attributes
    ----------
    abs: Scalar
        Absolute error.
    rel: Scalar
        Relative error (NaN if measured value is 0).
    """

    def __init__(self, x: float, x0: float):
        """
        Class constructor.
        Parameters
        ----------
        x: Scalar
            Measured value.
        x0: Scalar
            Model value.
        """
        self.abs = abs(x - x0)
        self.rel = self.abs / x if x != 0 else Scalar.nan()

    def __str__(self):
        return f"SError(abs={self.abs}, rel={self.rel})"


class VectorError:
    """
    A class containing measurement errors for given vectors.
    Attributes
    ----------
    x: ScalarError
        X cord error.
    y: ScalarError
        Y cord error.
    value: ScalarError
        Value error.
    """

    def __init__(self, vec: Vector, vec0: Vector):
        """
        Class constructor.
        Parameters
        ----------
        vec: Vector
            Measured Vector.
        vec0: Vector
            Model Vector.
        """
        self.x = ScalarError(vec.x, vec0.x)
        self.y = ScalarError(vec.y, vec0.y)
        self.value = ScalarError(vec.value, vec0.value)

    def __str__(self):
        return f"VError(x={self.x}, y={self.y}, value={self.value})"


class Error:
    """
    A class containing measurement errors for one cycle.
    Attributes
    ----------
    duration: ScalarError
        Full duration error.
    duration1: ScalarError
        1st to 2nd cycle point duration error.
    duration2: ScalarError
        2nd to 3rd cycle point duration error.
    start_velocity: VectorError
        Start velocity error.
    end_velocity: VectorError
        End velocity error.
    """

    def __init__(self, measure: Result, model: Result):
        self.duration = ScalarError(measure.duration, model.duration)
        self.duration1 = ScalarError(measure.duration1, model.duration1)
        self.duration2 = ScalarError(measure.duration2, model.duration2)
        self.start_velocity = VectorError(measure.start_velocity, model.start_velocity)
        self.end_velocity = VectorError(measure.end_velocity, model.end_velocity)

    def __str__(self):
        return (f"Error(duration={self.duration}, "
                f"duration1={self.duration1}, "
                f"duration2={self.duration2}, "
                f"start_velocity={self.start_velocity}, "
                f"end_velocity={self.end_velocity})")


def init_space(inp: Input) -> tuple[Space, Body]:
    """
    Function initializes Pymunk Space object for simulation.
    :param inp: Input data.
    :return: Set up Space object and Body object of block.
    :rtype: tuple[Space, Body]
    """
    space = pymunk.Space()
    space.gravity = SIM_GRAVITY

    plane = pymunk.Segment(space.static_body, translate_abs(50, 0),
                           translate_abs(5000, tan(inp.tilt.value) * 5000), 4)
    plane.friction = 1

    wall = pymunk.Segment(space.static_body, translate_abs(100, 0),
                          translate_abs(0, (100 / tan(inp.tilt.value))), 4)
    wall.elasticity = 1
    wall.collision_type = 1

    block_body = pymunk.Body(mass=inp.mass.value,
                             moment=pymunk.moment_for_box(sys.float_info.max,
                                                          (SIM_BLOCK_SIZE, SIM_BLOCK_SIZE)))
    block_body.angle = radians(270) - inp.tilt.value
    block_body.position = translate_abs(100 - 50 * sin(inp.tilt.value) ** 2, 50 * sin(inp.tilt.value) * cos(inp.tilt.value))

    block = pymunk.Poly(block_body, [(0, 0), (0, SIM_BLOCK_SIZE),
                                     (SIM_BLOCK_SIZE, 0), (SIM_BLOCK_SIZE, SIM_BLOCK_SIZE)])
    block.elasticity = 1
    block.friction = inp.friction.value
    block.collision_type = 1

    space.add(block_body, block, plane, wall)
    return space, block_body


def handle_block_wall_collision(arbiter: Arbiter, space: Space, data: list[Measurement]) -> None:
    """
    Handler of block-wall collision. Saves the Measurement object and logs the collision.
    :param arbiter: Pymunk Arbiter - collision data object.
    :param space: Pymunk Space object.
    :param data: List of Measurements (one of results of simulation).
    """
    data.append(Measurement(round(time(), 2), arbiter.shapes[1].body.position, arbiter.shapes[1].body.velocity))
    log.info(f"Block-wall collision detected, {data[-1]}")


def simulate(space: Space, block: Body, inp: Input, model_cycles_amount: int, is_full: bool) -> \
        tuple[list[Measurement], list[Measurement], Scalar]:
    """
    Simulates the scenario for given data using Pymunk physics engine.
    :param space: Pymunk Space object.
    :param block: Pymunk Body object of block.
    :param inp: Input data.
    :param model_cycles_amount: Expected amount of cycles based on model results.
    :param is_full: True if cycle is full in model results.
    Cycle is not full only if 3rd point of cycle did not happen (block stopped in 2nd point).
    :return: Two lists of Measurement objects - first one with detected wall-block collision events,
    second one with detected block stop events - and duration of simulation.
    Second list also contains measures taken at start and end of the simulation.
    """
    display = pygame.display.set_mode(RESOLUTION)
    draw_options = pymunk.pygame_util.DrawOptions(display)
    clock = pygame.time.Clock()
    log.debug(f"Set up pygame display. resolution={RESOLUTION} fps={SIM_FPS}")

    vel = inp.velocity.translated()
    block.apply_impulse_at_world_point((vel.x.value * inp.mass.value, vel.y.value * inp.mass.value), translate_abs(0, 0))

    collision_events: list[Measurement] = []
    stop_events: list[Measurement] = []
    space.on_collision(
        1,
        1,
        handle_block_wall_collision,
        None,
        None,
        None,
        data=collision_events
    )

    pygame.init()

    log.info("Running simulation.")
    start_time = Scalar(round(time(), 2), UNIT_TIME)
    start_measurement = Measurement(start_time.value, block.position, block.velocity)
    log.debug(f"Simulation info: start_time={start_time} "
              f"start_measurement={start_measurement} "
              f"start_pos=[{block.position.x}, {block.position.y}] "
              f"start_velocity=[{block.velocity.x}, {block.velocity.y}]")

    running = True
    while running:
        curr_time = round(time(), 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if (not is_full and len(stop_events) > 10) or (is_full and len(collision_events) > model_cycles_amount):
            running = False

        if abs(block.velocity[0]) < SIM_PRECISION and abs(block.velocity[1]) < SIM_PRECISION:
            stop_events.append(Measurement(curr_time, block.position, block.velocity))
            log.info(f"Block stop detected, {stop_events[-1]}")

        display.fill((65, 65, 65))
        space.debug_draw(draw_options)
        pygame.display.update()
        clock.tick(SIM_FPS)
        space.step(1 / SIM_FPS)
    pygame.quit()

    end_time = Scalar(round(time(), 2), UNIT_TIME)
    end_measurement = Measurement(end_time.value, block.position, block.velocity)
    log.info(f"Simulation finished. duration={end_time - start_time}")
    log.debug(f"Simulation info: end_time={end_time} "
              f"end_measurement={end_measurement} "
              f"detected wall-block collisions n={len(collision_events)} events={collision_events} "
              f"detected block stops n={len(stop_events)} events={stop_events} ")

    collision_events.insert(0, start_measurement)
    collision_events.append(end_measurement)

    return collision_events, stop_events, end_time - start_time


def collect_cycles(stop_events: list[Measurement], collision_events: list[Measurement]) -> list[Cycle]:
    """
    Parses measurements from simulation and converts them to list of Cycle objects.
    :param stop_events: Measurements of block stop events from simulation.
    :param collision_events: Measurements of block-wall collision events from simulation.
    :return: List of Cycle objects based on simulation events.
    :rtype: list[Cycle]
    """
    log.debug(f"Collecting cycles. stop_events={stop_events} collision_events={collision_events}")
    cycles = []
    measurement_ndx = 0
    cycle_i = 0
    for i in range(0, len(collision_events) - 1):
        event = Measurement(-1, Vec2d(1E50, 1E50),
                            Vec2d(1E50, 1E50))
        start = collision_events[i]
        end = collision_events[i + 1]
        while measurement_ndx < len(stop_events) and stop_events[measurement_ndx].time < end.time:
            if stop_events[measurement_ndx].velocity.value < event.velocity.value:
                event = stop_events[measurement_ndx]
            measurement_ndx += 1
        if event.time != -1:
            cycles.append(Cycle(cycle_i, start, event, end))
            log.debug(f"Collected cycle, {cycles[-1]}")
            cycle_i += 1
    log.debug(f"Collected cycles, n={len(cycles)}")
    return cycles


def prepare_results(stop_events: list[Measurement], collision_events: list[Measurement], is_full: bool) \
        -> list[Result]:
    """
    Parses measurements from simulation, divides them to cycles and prepares results.
    :param stop_events: Measurements of block stop events from simulation.
    :param collision_events: Measurements of block-wall collision events from simulation.
    :param is_full: True if cycle is full.
    Cycle is not full only if 3rd point of cycle did not happen (block stopped in 2nd point).
    :return: List with Result object for each cycle.
    """
    log.info(f"Preparing results, stop_events={stop_events} collision_events={collision_events} is_full={is_full}")
    results = []
    cycles = collect_cycles(stop_events, collision_events)
    for cycle in cycles:
        results.append(Result.measured(cycle, is_full))
        log.info(f"Prepared result, result={results[-1]}")
    log.info(f"Prepared results, n={len(results)}")
    return results


def calculate_theoretical_model(user_input: Input) -> list[Result]:
    """
    Prepares model results based on physics formulas.
    :param user_input: Input data.
    :return: List with Result object for each cycle.
    """
    log.debug(f"Calculating model: input={user_input}")
    g = abs(SIM_GRAVITY[1] / SIM_SCALE)
    results = [Result.model(0,
                            user_input.velocity,
                            user_input.tilt.value,
                            user_input.friction.value,
                            g,
                            False)]
    if (user_input.friction * cos(user_input.tilt.value)) / (sin(user_input.tilt.value)) >= 1:
        log.debug(f"Not full cycle detected! result={results[0]}")
        log.info(f"Calculated model: N={len(results)} results={results}")

    results = [Result.model(0,
                            user_input.velocity,
                            user_input.tilt.value,
                            user_input.friction.value,
                            g,
                            True)]
    log.debug(f"Calculated model result: n={0} result={results[-1]}")
    i = 1
    while results[-1].end_velocity.value > SIM_PRECISION / SIM_SCALE:
        results.append(Result.model(i,
                                    results[-1].end_velocity,
                                    user_input.tilt.value,
                                    user_input.friction.value,
                                    g,
                                    True))
        log.debug(f"Calculated model result: n={i} result={results[-1]}")
        i += 1

    log.info(f"Calculated model: N={len(results)} results={results}")
    return results


def read_console() -> Input:
    angle = input("Tilt of plane (rad) (0; pi/2) = ")
    friction = input("Friction coefficient (Coulomb friction) (0;inf) = ")
    mass = input("Block's mass (kg) (0;inf) = ")
    velocity = input("Starting velocity (m/s) (parallel to slope) (0;inf) = ")
    inp = Input.user(angle, mass, velocity, friction)
    log.debug("Read user's input: ", inp)
    return inp


def gen_ascii():
    return fr"""
 _____           _ _                _  ______ _                   ______          _           _   
|_   _|         | (_)              | | | ___ \ |                  | ___ \        (_)         | |  
  | | _ __   ___| |_ _ __   ___  __| | | |_/ / | __ _ _ __   ___  | |_/ / __ ___  _  ___  ___| |_ 
  | || '_ \ / __| | | '_ \ / _ \/ _` | |  __/| |/ _` | '_ \ / _ \ |  __/ '__/ _ \| |/ _ \/ __| __|
 _| || | | | (__| | | | | |  __/ (_| | | |   | | (_| | | | |  __/ | |  | | | (_) | |  __/ (__| |_ 
 \___/_| |_|\___|_|_|_| |_|\___|\__,_| \_|   |_|\__,_|_| |_|\___| \_|  |_|  \___/| |\___|\___|\__|
                                                                                _/ |              
                                                                               |__/                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
InclinedPlaneProject v{VERSION}
    """


def main():
    print(gen_ascii())

    log.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(logging.Formatter('[%(asctime)s] (%(funcName)s) %(levelname)s - %(message)s'))
    log.addHandler(handler)

    log.info(f"Logger start. level={LOG_LEVEL}")

    user_input = read_console()
    # user_input = Input.user("0.7854", "1", "20", "0.5")
    simulation_input = Input.simulation(user_input)

    models = calculate_theoretical_model(user_input)
    is_full = models[0].is_full

    space, block = init_space(simulation_input)
    collisions, measurements, sim_duration = simulate(space, block, simulation_input, len(models), is_full)
    results = prepare_results(measurements, collisions, is_full)


main()
