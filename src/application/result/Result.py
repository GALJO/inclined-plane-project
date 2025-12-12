"""
Copyright 2025 Jan Oleński

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing
permissions and limitations under the License.
"""
from math import sin, cos, sqrt, tan

from pymunk import Vec2d

from application.math_objects.Scalar import Scalar
from application.math_objects.Vector import translate_abs, Vector, translate
from infrastructure.constants import UNIT_TIME, UNIT_VELOCITY, UNIT_DISTANCE, SIM_SCALE


class Measurement:
    """
    A class representing a measurement in simulation.
    It stores data about time of measurement and block parameters.
    It can be one of two simulation events:\n
    - Complete stop of the block,\n
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
        Class constructor.
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
    One cycle is defined as three Measurements:\n
    1. Block collides with the wall (then bounces off the wall and starts sliding up the plane).\n
    2. Block stops in one point of the plane (then starts sliding down).\n
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
        Velocity at the 1st point of cycle (always positive coordinates).
    end_velocity: Vector
        Velocity at the 3rd point of cycle.
    reach: Vector
        Block displacement vector between 1st and 2nd point of cycle.
    """

    def __init__(self, number: int, is_full: bool, duration1: Scalar, duration2: Scalar, start_velocity: Vector,
                 end_velocity: Vector, reach: Vector):
        """
        Class constructor
        Parameters
        ----------
        number: int
        is_full: bool
        duration1: Scalar
        duration2: Scalar
        start_velocity: Vector
        end_velocity: Vector
        reach
        """
        self.number = number
        self.is_full = is_full
        self.duration1 = duration1
        self.duration2 = duration2
        self.duration = duration1 + duration2 if is_full else duration1
        self.start_velocity = abs(start_velocity)
        self.end_velocity = end_velocity
        self.reach = reach

    @classmethod
    def measured(cls, cycle: Cycle, is_full: bool):
        """
        Parses measured Cycle object to create result.
        :param cycle: Cycle object.
        :param is_full: True if the cycle is full.
        Cycle is not full only if 3rd point of cycle did not happen (block stopped in 2nd point).
        :returns: Result object
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
        result: Result
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
        """
        Converts to string.
        """
        return (f"Result(number={self.number}, "
                f"is_full={self.is_full}, "
                f"duration1={self.duration1}, "
                f"duration2={self.duration2}), "
                f"duration={self.duration}, "
                f"start_velocity={self.start_velocity}, "
                f"end_velocity={self.end_velocity}, "
                f"reach={self.reach})")
