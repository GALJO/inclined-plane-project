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
from math import sin, cos, sqrt

from pymunk import Vec2d

from application.math.math_util import translate_abs, translate
from application.math.scalar import Scalar
from application.math.vector import Vector
from infrastructure.config.config import CONFIG


class Measurement:
    """A class representing a measurement in simulation.
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
        self.time = Scalar(_time, CONFIG.unit.time)
        x, y = translate_abs(_position.x, _position.y)
        self.position = Vector.from_float(x, y, CONFIG.unit.distance)
        x, y = translate(_velocity.x, _velocity.y)
        self.velocity = Vector.from_float(x, y, CONFIG.unit.velocity)

    def __str__(self):
        """
        Converts to string.
        """
        return f"Measurement(time={self.time} position={self.position} velocity={self.velocity})"


class Cycle:
    """A class representing a cycle of the simulation.
    One cycle is defined as three Measurements:

    1. The point just after (then bounces off the wall and starts sliding up the plane).\n
    2. The point stops.\n
    3. The point just before collision with the wall (after collision new cycle begin).

    Attributes
    ----------
    number:
        int: Number of the cycle.
    start:
        Measurement: First step of the cycle.
    middle:
        Measurement: Second step of the cycle.
    end:
        Measurement: Third step of the cycle.
    is_full:
        bool: Is cycle full?
    """

    def __init__(self, number: int, start_collision: Measurement, middle_measurement: Measurement,
                 end_collision: Measurement, is_full: bool):
        """
        Class constructor.
        :param number: Number of the cycle.
        :param start_collision: Measurement of the block when ending last cycle (or first ever measurement).
        :param middle_measurement: Measurement of the block when closest to complete stop.
        :param end_collision: Measurement of the block when colliding with the wall.
        """
        self.number: int = number
        self.start: Measurement = start_collision
        self.middle: Measurement = middle_measurement
        self.end: Measurement = end_collision
        self.is_full: bool = is_full

    def __str__(self):
        return f"Cycle(number={self.number} start={self.start} middle={self.middle} end={self.end})"


class Result:

    def __init__(self, number: int, is_full: bool, duration1: Scalar, duration2: Scalar, start_velocity: Vector,
                 end_velocity: Vector, reach: Vector):
        """
        Class constructor

        Attributes
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
    def measured(cls, cycle: Cycle):
        """Parses a cycle to readable results.

        :param cycle: Cycle
        :returns: Result.
        :rtype: Result

        """
        return cls(cycle.number,
                   cycle.is_full,
                   cycle.middle.time - cycle.start.time,
                   cycle.end.time - cycle.middle.time if cycle.is_full else Scalar.nan(),
                   Vector(abs(cycle.start.velocity.x / CONFIG.scale),
                          abs(cycle.start.velocity.y / CONFIG.scale)),
                   Vector(cycle.end.velocity.x / CONFIG.scale, cycle.end.velocity.y / CONFIG.scale),
                   Vector(abs(cycle.start.position.x - cycle.middle.position.x) / CONFIG.scale,
                          abs(cycle.start.position.y - cycle.middle.position.y) / CONFIG.scale))

    @classmethod
    def model(cls, number: int, start_velocity: Vector, tilt: float, f: float, g: float, is_full: bool):
        """Creates model Result using physical formulas.

        :param number: 
        :type number: int
        :param Number of the cycle.: 
        :param start_velocity: 
        :type start_velocity: Vector
        :param Velocity at the 1st point of cycle (meters per second).: 
        :param tilt: Tilt of plane (radians).
        :type tilt: float
        :param f: Coulomb's friction coefficient.
        :type f: float
        :param g: Value of gravitational acceleration (Vector is parallel to Y axis).
        :type g: float
        :param is_full: True if the cycle is full.
        :type is_full: bool
        :param number: int: 
        :param start_velocity: Vector: 
        :param tilt: float: 
        :param f: float: 
        :param g: float: 
        :param is_full: bool: 

        
        """
        v0 = start_velocity.value.value
        reach_value = (v0 * v0) / (2 * g * (f * cos(tilt) + sin(tilt)))

        if not is_full:
            end_velocity = Vector.from_float(0, 0, CONFIG.unit.velocity)
        else:
            v1 = v0 * sqrt((sin(tilt) - f * cos(tilt)) / (sin(tilt) + f * cos(tilt)))
            end_velocity = Vector.from_float(-cos(tilt) * v1, -sin(tilt) * v1,
                                             CONFIG.unit.velocity)

        d1 = Scalar(v0 / (g * (sin(tilt) + f * cos(tilt))), CONFIG.unit.time)
        d2 = Scalar(end_velocity.value.value / (g * (sin(tilt) - f * cos(tilt))), CONFIG.unit.time)

        reach = Vector.from_float(cos(tilt) * reach_value, sin(tilt) * reach_value, CONFIG.unit.distance)

        return cls(number, is_full, d1, d2 if is_full else Scalar.nan(), start_velocity, end_velocity, reach)

    def __str__(self):
        """
        Converts to string.
        """
        return (f"Result(number={self.number} "
                f"is_full={self.is_full} "
                f"duration1={self.duration1} "
                f"duration2={self.duration2} "
                f"duration={self.duration} "
                f"start_velocity={self.start_velocity} "
                f"end_velocity={self.end_velocity} "
                f"reach={self.reach})")
